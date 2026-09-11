import unittest

from google.protobuf import any_pb2
from google.protobuf.wrappers_pb2 import StringValue
from idl.game.dto.command_pb2 import ApplyCommandRequest
from idl.game.dto.session_pb2 import CreateSessionRequest
from idl.game.model.command_result_pb2 import CommandOutcome, CommandResult
from idl.game.model.game_result_pb2 import GameResult, ParticipantOutcome, ParticipantResult
from idl.game.model.game_state_pb2 import GameState
from idl.game.model.game_type_pb2 import GameType
from idl.game.model.participant_pb2 import Participant
from idl.game.model.session_pb2 import Session, SessionView
from idl_fastapi.idl.game.dto import ApplyCommandRequest as ApplyCommandRequestModel

from game.adapters.session_adapters import SessionAdapters

SESSION_ID = "t-1"
PLAYER_ID = "p-1"
COMMAND_ID = "c-1"
VERSION = 3
EXPECTED_VERSION = 3
PARTICIPANT = 1
PARTICIPANT_TO_ACT = 2
WORD = "move"


def packed(word: str) -> any_pb2.Any:
    payload = any_pb2.Any()
    payload.Pack(StringValue(value=word))
    return payload


def a_session() -> Session:
    return Session(
        id=SESSION_ID,
        game_type=GameType.GAME_TYPE_CHESS,
        participants=[Participant(number=PARTICIPANT, player_id=PLAYER_ID)],
        state=GameState(payload=packed("whole"), participant_to_act=PARTICIPANT_TO_ACT),
        last_command_id=COMMAND_ID,
        version=VERSION,
    )


class StoredShapeTest(unittest.TestCase):
    def test_a_session_survives_the_trip_through_its_stored_shape(self) -> None:
        session = a_session()

        stored = SessionAdapters.session_to_session_obj(session)
        back = SessionAdapters.session_obj_to_session(stored)

        self.assertEqual(stored.metadata.id, SESSION_ID)
        self.assertEqual(stored.metadata.version, VERSION)
        self.assertEqual(back, session)


class ViewTest(unittest.TestCase):
    def test_a_view_carries_the_projection_in_place_of_the_whole_game(self) -> None:
        view = SessionAdapters.session_to_session_view(a_session(), PARTICIPANT, packed("mine"))

        self.assertEqual(view.participant, PARTICIPANT)
        self.assertEqual(view.state.payload, packed("mine"))
        self.assertEqual(view.state.participant_to_act, PARTICIPANT_TO_ACT)
        self.assertEqual(view.version, VERSION)
        self.assertEqual(view.last_command_id, COMMAND_ID)

    def test_a_game_without_a_result_projects_to_a_view_without_one(self) -> None:
        view = SessionAdapters.session_to_session_view(a_session(), PARTICIPANT, packed("mine"))

        self.assertFalse(view.state.HasField("result"))

    def test_a_result_is_carried_into_the_view(self) -> None:
        finished = a_session()
        finished.state.result.CopyFrom(
            GameResult(
                participant_items=[
                    ParticipantResult(
                        participant=PARTICIPANT,
                        outcome=ParticipantOutcome.PARTICIPANT_OUTCOME_WON,
                    )
                ]
            )
        )

        view = SessionAdapters.session_to_session_view(finished, PARTICIPANT, packed("mine"))

        self.assertTrue(view.state.HasField("result"))
        self.assertEqual(
            view.state.result.participant_items[0].outcome,
            ParticipantOutcome.PARTICIPANT_OUTCOME_WON,
        )


class RequestTest(unittest.TestCase):
    def test_a_create_request_is_taken_apart_into_its_arguments(self) -> None:
        request = CreateSessionRequest(
            table_id=SESSION_ID,
            player_id=PLAYER_ID,
            game_type=GameType.GAME_TYPE_CHESS,
            participants=[Participant(number=PARTICIPANT, player_id=PLAYER_ID)],
        )

        self.assertEqual(SessionAdapters.create_request_to_table_id(request), SESSION_ID)
        self.assertEqual(SessionAdapters.create_request_to_player_id(request), PLAYER_ID)
        self.assertEqual(
            SessionAdapters.create_request_to_game_type(request), GameType.GAME_TYPE_CHESS
        )
        self.assertEqual(
            SessionAdapters.create_request_to_participants(request),
            (Participant(number=PARTICIPANT, player_id=PLAYER_ID),),
        )

    def test_an_apply_request_is_taken_apart_into_its_arguments(self) -> None:
        request = ApplyCommandRequest(
            session_id=SESSION_ID,
            command_id=COMMAND_ID,
            player_id=PLAYER_ID,
            action=packed(WORD),
            expected_version=EXPECTED_VERSION,
        )

        self.assertEqual(SessionAdapters.apply_request_to_session_id(request), SESSION_ID)
        self.assertEqual(SessionAdapters.apply_request_to_player_id(request), PLAYER_ID)
        self.assertEqual(SessionAdapters.apply_request_to_command_id(request), COMMAND_ID)
        self.assertEqual(SessionAdapters.apply_request_to_action(request), packed(WORD))
        self.assertEqual(
            SessionAdapters.apply_request_to_expected_version(request), EXPECTED_VERSION
        )

    def test_a_command_result_becomes_the_response_the_schema_declares(self) -> None:
        view = SessionView(id=SESSION_ID, version=VERSION)

        response = SessionAdapters.command_result_to_apply_response(
            CommandResult(outcome=CommandOutcome.COMMAND_OUTCOME_APPLIED, session=view)
        )

        self.assertEqual(response.result.outcome, CommandOutcome.COMMAND_OUTCOME_APPLIED)
        self.assertEqual(response.result.session, view)

    def test_a_result_without_a_session_leaves_the_field_unset(self) -> None:
        response = SessionAdapters.command_result_to_apply_response(
            CommandResult(outcome=CommandOutcome.COMMAND_OUTCOME_SESSION_NOT_FOUND)
        )

        self.assertFalse(response.result.HasField("session"))


class HttpShapeTest(unittest.TestCase):
    """
    The pydantic model and the message are one contract, joined by proto3 JSON.
    A packed payload crosses as a typed object, which is what makes the type
    the gateway resolves it against load-bearing.
    """

    def test_an_apply_request_crosses_from_its_json_shape_with_its_payload(self) -> None:
        model = ApplyCommandRequestModel.model_validate(
            {
                "sessionId": SESSION_ID,
                "commandId": COMMAND_ID,
                "playerId": PLAYER_ID,
                "action": {
                    "@type": "type.googleapis.com/google.protobuf.StringValue",
                    "value": WORD,
                },
                "expectedVersion": str(EXPECTED_VERSION),
            }
        )

        message = SessionAdapters.apply_request_model_to_message(model)

        self.assertEqual(message.session_id, SESSION_ID)
        self.assertEqual(message.player_id, PLAYER_ID)
        self.assertEqual(message.expected_version, EXPECTED_VERSION)
        self.assertEqual(message.action, packed(WORD))

    def test_a_view_crosses_back_to_its_json_shape(self) -> None:
        response = SessionAdapters.session_view_to_read_response(
            SessionView(
                id=SESSION_ID,
                participant=PARTICIPANT,
                state=GameState(payload=packed(WORD), participant_to_act=PARTICIPANT_TO_ACT),
                version=VERSION,
            )
        )

        model = SessionAdapters.read_response_message_to_model(response)

        assert model.session is not None and model.session.state is not None
        self.assertEqual(model.session.id, SESSION_ID)
        self.assertEqual(model.session.version, str(VERSION))
        self.assertEqual(model.session.state.participant_to_act, PARTICIPANT_TO_ACT)
