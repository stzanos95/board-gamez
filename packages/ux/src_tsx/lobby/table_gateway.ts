import type { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import type { SeatResult } from "@board-gamez/idl/lobby/model/seat_result_pb";
import type { Table } from "@board-gamez/idl/lobby/model/table_pb";
import { SeatService } from "@board-gamez/idl/lobby/service/seat_pb";
import { TableService } from "@board-gamez/idl/lobby/service/table_pb";

import type { GatewayClient } from "../transport/gateway_client";

/**
 * The operations a lobby answers, as this application calls them.
 *
 * Tables are read through `TableService` and never written through it: every
 * change to a player's place at a table is a `SeatService` verb, which the
 * lobby decides and records. Each answers with the domain's own type rather
 * than the response that carried it. An unset table means the table is not
 * there, and reaches a caller as null.
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
   * Open a table for a game, with the opener at it and every seat open. The
   * lobby mints the id and checks the seat count against the game.
   */
  async createTable(
    gameType: GameType,
    seatCount: number,
    playerId: string,
  ): Promise<SeatResult | null> {
    const response = await this.client.unary(SeatService.method.createTable, {
      gameType,
      seatCount,
      playerId,
    });
    return response.result ?? null;
  }

  /**
   * Come to the table without taking a seat.
   */
  async joinTable(tableId: string, playerId: string): Promise<SeatResult | null> {
    const response = await this.client.unary(SeatService.method.joinTable, {
      tableId,
      playerId,
    });
    return response.result ?? null;
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
