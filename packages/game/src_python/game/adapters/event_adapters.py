"""
A game, to the record of what was just done to it.

One method per write that succeeds. Each takes the session as stored after the
write, so the version an event carries is the version after it.
"""

from google.protobuf import any_pb2
from idl.game.model.event_pb2 import CommandApplied, ParticipantWithdrawn, SessionStarted
from idl.game.model.session_pb2 import Session


class EventAdapters:
    """
    Every game event, built from the session it records.
    """

    @staticmethod
    def session_to_session_started(session: Session) -> SessionStarted:
        return SessionStarted(
            session_id=session.id,
            game_type=session.game_type,
            participants=session.participants,
            version=session.version,
        )

    @staticmethod
    def session_to_command_applied(
        session: Session, participant: int, command_id: str, action: any_pb2.Any
    ) -> CommandApplied:
        """
        `action` is the one the client sent, unopened.
        """
        return CommandApplied(
            session_id=session.id,
            participant=participant,
            command_id=command_id,
            action=action,
            is_over=session.state.HasField("result"),
            version=session.version,
        )

    @staticmethod
    def session_to_participant_withdrawn(
        session: Session, participant: int
    ) -> ParticipantWithdrawn:
        return ParticipantWithdrawn(
            session_id=session.id,
            participant=participant,
            is_over=session.state.HasField("result"),
            version=session.version,
        )
