"""
Tables, between the shapes a table takes.

Two conversions live here, and they are not the same job.

A request carries what an operation needs; a controller takes those arguments and
answers with the domain's own types. Turning one into the other is what a servicer
delegates here, so no layer above the controller reads a field off a request.

A contract also produces two families of type — protobuf messages for gRPC and
pydantic models for HTTP — and a caller crossing between them converts here too.

A table is stored under a shape of its own, which carries identity and version in
metadata. That conversion runs at the repository's boundary and is here as well.

One method per direction, named for it. A caller reaches for the one it needs and
sees the types on both sides; nothing here is chosen at run time.
"""

from core.protobuf.message_utils import ProtobufMessageUtils
from idl.core.obj.object_metadata_pb2 import ObjectMetadata
from idl.lobby.dto import table_pb2
from idl.lobby.model.table_pb2 import Table, TableCollection
from idl.lobby.obj.table_pb2 import TableObj
from idl_fastapi.idl.lobby.dto import (
    DeleteTableRequest,
    DeleteTableResponse,
    ListTableRequest,
    ListTableResponse,
    ReadTableRequest,
    ReadTableResponse,
    UpsertTableRequest,
    UpsertTableResponse,
)


class TableAdapters:
    """
    Every TableService message, converted to what the layer beneath it takes.
    """

    # --- a request, to the arguments an operation takes ----------------------

    @staticmethod
    def upsert_request_to_table(request: table_pb2.UpsertTableRequest) -> Table:
        return request.table

    @staticmethod
    def read_request_to_table_id(request: table_pb2.ReadTableRequest) -> str:
        return request.table_id

    @staticmethod
    def delete_request_to_table_id(request: table_pb2.DeleteTableRequest) -> str:
        return request.table_id

    @staticmethod
    def delete_request_to_expected_version(request: table_pb2.DeleteTableRequest) -> int:
        return request.expected_version

    # --- what an operation answers, to a response ----------------------------

    @staticmethod
    def table_to_upsert_response(table: Table | None) -> table_pb2.UpsertTableResponse:
        """
        An unset table is how the schema says the write was refused.
        """
        return table_pb2.UpsertTableResponse(table=table)

    @staticmethod
    def table_to_read_response(table: Table | None) -> table_pb2.ReadTableResponse:
        """
        An unset table is how the schema says no table has that id.
        """
        return table_pb2.ReadTableResponse(table=table)

    @staticmethod
    def table_id_to_delete_response(table_id: str) -> table_pb2.DeleteTableResponse:
        return table_pb2.DeleteTableResponse(table_id=table_id)

    @staticmethod
    def table_collection_to_list_response(
        collection: TableCollection,
    ) -> table_pb2.ListTableResponse:
        return table_pb2.ListTableResponse(collection=collection)

    # --- a pydantic model, to the message of the same contract ---------------

    @staticmethod
    def upsert_request_model_to_message(model: UpsertTableRequest) -> table_pb2.UpsertTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, table_pb2.UpsertTableRequest)

    @staticmethod
    def upsert_response_message_to_model(
        message: table_pb2.UpsertTableResponse,
    ) -> UpsertTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, UpsertTableResponse)

    @staticmethod
    def read_request_model_to_message(model: ReadTableRequest) -> table_pb2.ReadTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, table_pb2.ReadTableRequest)

    @staticmethod
    def read_response_message_to_model(
        message: table_pb2.ReadTableResponse,
    ) -> ReadTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ReadTableResponse)

    @staticmethod
    def delete_request_model_to_message(model: DeleteTableRequest) -> table_pb2.DeleteTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, table_pb2.DeleteTableRequest)

    @staticmethod
    def delete_response_message_to_model(
        message: table_pb2.DeleteTableResponse,
    ) -> DeleteTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, DeleteTableResponse)

    @staticmethod
    def list_request_model_to_message(model: ListTableRequest) -> table_pb2.ListTableRequest:
        return ProtobufMessageUtils.message_from_pydantic_model(model, table_pb2.ListTableRequest)

    @staticmethod
    def list_response_message_to_model(
        message: table_pb2.ListTableResponse,
    ) -> ListTableResponse:
        return ProtobufMessageUtils.message_to_pydantic_model(message, ListTableResponse)

    # --- a table, to what a store holds, and back ----------------------------

    @staticmethod
    def table_to_table_obj(table: Table) -> TableObj:
        """
        The table to hand a store.

        The timestamps stay unset: a write time is known to whatever writes.
        """
        return TableObj(
            metadata=ObjectMetadata(id=table.id, version=table.version),
            game_type=table.game_type,
            status=table.status,
            seats=table.seats,
        )

    @staticmethod
    def table_obj_to_table(stored: TableObj) -> Table:
        return Table(
            id=stored.metadata.id,
            game_type=stored.game_type,
            status=stored.status,
            seats=stored.seats,
            version=stored.metadata.version,
        )

    @staticmethod
    def table_objs_to_table_collection(stored: tuple[TableObj, ...]) -> TableCollection:
        return TableCollection(
            table_items=[TableAdapters.table_obj_to_table(one) for one in stored]
        )
