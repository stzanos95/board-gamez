import type { SeatResult } from "@board-gamez/idl/lobby/model/seat_result_pb";
import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { SeatService } from "@board-gamez/idl/lobby/service/seat_pb";
import { TableService } from "@board-gamez/idl/lobby/service/table_pb";

import type { GatewayClient } from "../transport/gateway_client";

/**
 * The operations a lobby answers, as this application calls them: the table
 * store, and the two ways a player gives up their place at a table.
 *
 * Each answers with the domain's own type rather than the response that
 * carried it. An unset table means the table is not there, or that a write was
 * refused, and reaches a caller as null.
 */
export class TableGateway {
  private readonly client: GatewayClient;

  constructor(client: GatewayClient) {
    this.client = client;
  }

  async list(): Promise<readonly Table[]> {
    const response = await this.client.unary(TableService.method.listTable, {});
    return response.collection?.tableItems ?? [];
  }

  async read(tableId: string): Promise<Table | null> {
    const response = await this.client.unary(TableService.method.readTable, { tableId });
    return response.table ?? null;
  }

  /**
   * Write a table, and answer it as stored.
   *
   * Null means the table carried a version that is no longer the stored one and
   * nothing was written. Read the table again and build the write on what comes
   * back.
   */
  async upsert(table: Table): Promise<Table | null> {
    const response = await this.client.unary(TableService.method.upsertTable, { table });
    return response.table ?? null;
  }

  /**
   * Give up the seat and stay at the table. A player in a game being played is
   * withdrawn from it; what that does to the game is the game's.
   */
  async vacateSeat(tableId: string, playerId: string): Promise<SeatResult | null> {
    const response = await this.client.unary(SeatService.method.vacateSeat, {
      tableId,
      playerId,
    });
    return response.result ?? null;
  }

  /**
   * Leave the table, giving up a seat on the way out.
   */
  async leaveTable(tableId: string, playerId: string): Promise<SeatResult | null> {
    const response = await this.client.unary(SeatService.method.leaveTable, {
      tableId,
      playerId,
    });
    return response.result ?? null;
  }

  async remove(tableId: string, expectedVersion: bigint): Promise<string> {
    const response = await this.client.unary(TableService.method.deleteTable, {
      tableId,
      expectedVersion,
    });
    return response.tableId;
  }
}
