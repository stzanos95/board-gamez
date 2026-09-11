"""
The catalogue of games, between the shapes it takes.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.game.dto import game_spec_pb2
from idl.game.model.game_spec_pb2 import GameSpecCollection
from idl_fastapi.idl.game.dto import ListGameSpecRequest, ListGameSpecResponse


class GameSpecAdapters:
    """
    Every GameSpecService message, converted to what the layer beneath it takes.
    """

    @staticmethod
    def game_spec_collection_to_list_response(
        collection: GameSpecCollection,
    ) -> game_spec_pb2.ListGameSpecResponse:
        return game_spec_pb2.ListGameSpecResponse(collection=collection)

    @staticmethod
    def list_request_model_to_message(
        model: ListGameSpecRequest,
    ) -> game_spec_pb2.ListGameSpecRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(
            model, game_spec_pb2.ListGameSpecRequest
        )

    @staticmethod
    def list_response_message_to_model(
        message: game_spec_pb2.ListGameSpecResponse,
    ) -> ListGameSpecResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ListGameSpecResponse)
