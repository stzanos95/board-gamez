"""
What is done to a game being played.

The one place the platform decides anything about a game: who may act, whether a
command already applied, whether the caller read the current state, and what an
outcome is called. What the action means inside the game is the game's rules'.
"""

from google.protobuf import any_pb2
from idl.game.model.action_pb2 import Action
from idl.game.model.command_result_pb2 import CommandOutcome, CommandResult
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import Session, SessionView
from idl.game.model.withdrawal_result_pb2 import WithdrawalOutcome, WithdrawalResult

from game.adapters.session_adapters import SessionAdapters
from game.controller.rules_registry import RulesRegistry
from game.repository.base_session_repository import BaseSessionRepository

UNSTORED_VERSION = 0
NO_COMMAND_ID = ""
NOT_PLAYING = 0
FIRST_PARTICIPANT = 1
WITHDRAWAL_ATTEMPTS = 3


class SessionController:
    """
    Every operation a game being played has, and the collaborators they need.

    Takes and answers with the domain's own types. A request is the shape one
    transport carries an argument in, and unpacking it belongs to whatever
    received it, so nothing from `idl.game.dto` reaches this far.

    Built once at the entry point and passed to whatever serves it.
    """

    def __init__(self, repository: BaseSessionRepository, rules: RulesRegistry) -> None:
        self._repository = repository
        self._rules = rules

    async def create_session(
        self,
        table_id: str,
        game_type: GameType,
        participants: tuple[Participant, ...],
        player_id: str,
    ) -> SessionView | None:
        """
        Start a game at this table and answer it as the caller may see it.

        A table already playing a game is answered that game. None comes back
        when the participants are not numbered from 1 without a gap, or when the
        game does not take them.
        """
        existing = await self._repository.read(table_id)
        if existing is not None:
            session = SessionAdapters.session_obj_to_session(existing)
            return await self._get_session_view(session, player_id)
        if not SessionController._is_numbered_without_gaps(participants):
            return None
        state = await self._rules.get_rules(game_type).create_game(
            SessionAdapters.participants_to_participant_roles(participants)
        )
        if state is None:
            return None
        opening = Session(
            id=table_id,
            game_type=game_type,
            participants=participants,
            state=state,
            last_command_id=NO_COMMAND_ID,
            version=UNSTORED_VERSION,
        )
        stored = await self._repository.upsert(SessionAdapters.session_to_session_obj(opening))
        if stored is None:
            # Another caller started the game between the read and the write.
            # Theirs is the game at this table.
            return await self.read_session(table_id, player_id)
        session = SessionAdapters.session_obj_to_session(stored)
        return await self._get_session_view(session, player_id)

    async def read_session(self, session_id: str, player_id: str) -> SessionView | None:
        """
        One game as the caller may see it, or None when no game has that id.
        """
        stored = await self._repository.read(session_id)
        if stored is None:
            return None
        session = SessionAdapters.session_obj_to_session(stored)
        return await self._get_session_view(session, player_id)

    async def apply_command(
        self,
        session_id: str,
        player_id: str,
        command_id: str,
        action: any_pb2.Any,
        expected_version: int,
    ) -> CommandResult:
        """
        Do one thing in a game, and say how it went.

        The checks run in the order the outcomes are numbered. A repeat of the
        command that produced the current state is recognised before the
        version is compared, because a retry carries the version it was first
        sent with.
        """
        stored = await self._repository.read(session_id)
        if stored is None:
            return CommandResult(outcome=CommandOutcome.COMMAND_OUTCOME_SESSION_NOT_FOUND)
        session = SessionAdapters.session_obj_to_session(stored)
        if command_id != NO_COMMAND_ID and command_id == session.last_command_id:
            return await self._get_command_result(
                CommandOutcome.COMMAND_OUTCOME_ALREADY_APPLIED, session, player_id
            )
        participant = SessionController._get_participant(session, player_id)
        if participant == NOT_PLAYING:
            return await self._get_command_result(
                CommandOutcome.COMMAND_OUTCOME_NOT_A_PARTICIPANT, session, player_id
            )
        if session.state.HasField("result"):
            return await self._get_command_result(
                CommandOutcome.COMMAND_OUTCOME_GAME_OVER, session, player_id
            )
        if expected_version != session.version:
            return await self._get_command_result(
                CommandOutcome.COMMAND_OUTCOME_VERSION_MOVED, session, player_id
            )
        if participant != session.state.participant_to_act:
            return await self._get_command_result(
                CommandOutcome.COMMAND_OUTCOME_OUT_OF_TURN, session, player_id
            )

        rules = self._rules.get_rules(session.game_type)
        next_state = await rules.apply_action(
            session.state, Action(participant=participant, payload=action)
        )
        if next_state is None:
            return await self._get_command_result(
                CommandOutcome.COMMAND_OUTCOME_ILLEGAL_ACTION, session, player_id
            )

        advanced = Session(
            id=session.id,
            game_type=session.game_type,
            participants=session.participants,
            state=next_state,
            last_command_id=command_id,
            version=session.version,
        )
        stored = await self._repository.upsert(SessionAdapters.session_to_session_obj(advanced))
        if stored is None:
            # The version moved between the read and the write. What is stored
            # now is what the caller builds the next command on.
            return CommandResult(
                outcome=CommandOutcome.COMMAND_OUTCOME_VERSION_MOVED,
                session=await self.read_session(session_id, player_id),
            )
        return await self._get_command_result(
            CommandOutcome.COMMAND_OUTCOME_APPLIED,
            SessionAdapters.session_obj_to_session(stored),
            player_id,
        )

    async def withdraw_player(self, session_id: str, player_id: str) -> WithdrawalResult:
        """
        Take a player out of the game, and say how it went.

        Nothing is built against a version here, so a write that loses to a
        command is read and made again, up to WITHDRAWAL_ATTEMPTS times.
        """
        result = await self._withdraw_player_once(session_id, player_id)
        attempts = 1
        while (
            result.outcome == WithdrawalOutcome.WITHDRAWAL_OUTCOME_VERSION_MOVED
            and attempts < WITHDRAWAL_ATTEMPTS
        ):
            result = await self._withdraw_player_once(session_id, player_id)
            attempts += 1
        return result

    async def _withdraw_player_once(self, session_id: str, player_id: str) -> WithdrawalResult:
        """
        One read, one ask of the rules, one write.
        """
        stored = await self._repository.read(session_id)
        if stored is None:
            return WithdrawalResult(outcome=WithdrawalOutcome.WITHDRAWAL_OUTCOME_SESSION_NOT_FOUND)
        session = SessionAdapters.session_obj_to_session(stored)
        participant = SessionController._get_participant(session, player_id)
        if participant == NOT_PLAYING:
            return await self._get_withdrawal_result(
                WithdrawalOutcome.WITHDRAWAL_OUTCOME_NOT_A_PARTICIPANT, session, player_id
            )
        if session.state.HasField("result"):
            return await self._get_withdrawal_result(
                WithdrawalOutcome.WITHDRAWAL_OUTCOME_GAME_OVER, session, player_id
            )

        rules = self._rules.get_rules(session.game_type)
        next_state = await rules.withdraw_participant(session.state, participant)
        if next_state is None:
            return await self._get_withdrawal_result(
                WithdrawalOutcome.WITHDRAWAL_OUTCOME_NOT_IN_GAME, session, player_id
            )

        withdrawn = Session(
            id=session.id,
            game_type=session.game_type,
            participants=session.participants,
            state=next_state,
            last_command_id=session.last_command_id,
            version=session.version,
        )
        stored = await self._repository.upsert(SessionAdapters.session_to_session_obj(withdrawn))
        if stored is None:
            return WithdrawalResult(
                outcome=WithdrawalOutcome.WITHDRAWAL_OUTCOME_VERSION_MOVED,
                session=await self.read_session(session_id, player_id),
            )
        return await self._get_withdrawal_result(
            WithdrawalOutcome.WITHDRAWAL_OUTCOME_WITHDRAWN,
            SessionAdapters.session_obj_to_session(stored),
            player_id,
        )

    async def _get_withdrawal_result(
        self, outcome: WithdrawalOutcome, session: Session, player_id: str
    ) -> WithdrawalResult:
        return WithdrawalResult(
            outcome=outcome, session=await self._get_session_view(session, player_id)
        )

    async def _get_command_result(
        self, outcome: CommandOutcome, session: Session, player_id: str
    ) -> CommandResult:
        """
        This outcome, carrying the game as it stands for the caller.
        """
        return CommandResult(
            outcome=outcome, session=await self._get_session_view(session, player_id)
        )

    async def _get_session_view(self, session: Session, player_id: str) -> SessionView:
        """
        The game projected for this player, by the rules that play it.
        """
        participant = SessionController._get_participant(session, player_id)
        rules = self._rules.get_rules(session.game_type)
        projected = await rules.read_view(session.state, participant)
        return SessionAdapters.session_to_session_view(session, participant, projected)

    @staticmethod
    def _get_participant(session: Session, player_id: str) -> int:
        """
        The number this player holds in the game, or 0 when they are not in it.
        """
        for participant in session.participants:
            if participant.player_id == player_id:
                return participant.number
        return NOT_PLAYING

    @staticmethod
    def _is_numbered_without_gaps(participants: tuple[Participant, ...]) -> bool:
        """
        Whether the participants are exactly 1 through N, in any order.
        """
        numbers = sorted(participant.number for participant in participants)
        return numbers == list(range(FIRST_PARTICIPANT, FIRST_PARTICIPANT + len(participants)))
