import type { ChessAction } from "@board-gamez/idl/chess/model/action_pb";
import type { ActionResult, ChessSession } from "@board-gamez/idl/chess/model/session_pb";
import type {
  ChessSeatChoice,
  ChessSeatResult,
  ChessTable,
} from "@board-gamez/idl/chess/model/table_pb";
import { ChessService } from "@board-gamez/idl/chess/service/game_pb";

import type { GatewayClient } from "../transport/gateway_client";

/**
 * One action, as this application sends it.
 *
 * `commandId` names the intent, so a repeat of the same command lands once.
 * `expectedVersion` is the version of the session that was showing when the
 * player committed, and the game refuses an action built on an older one.
 */
export type ChessCommand = {
  readonly tableId: string;
  readonly playerId: string;
  readonly commandId: string;
  readonly action: ChessAction;
  readonly expectedVersion: bigint;
};

/**
 * One seat being taken, as this application sends it.
 *
 * `expectedVersion` is the version of the table the choice was picked from, and
 * the lobby refuses a choice built on an older one.
 */
export type SeatClaim = {
  readonly tableId: string;
  readonly playerId: string;
  readonly choice: ChessSeatChoice;
  readonly expectedVersion: bigint;
};

/**
 * The operations a chess table and its game answer, as this application calls
 * them.
 *
 * Each answers with the domain's own type. An unset session means no game is
 * being played at that table, or that a start was refused, and reaches a caller
 * as null. An unset table means no chess table has that id.
 */
export class ChessGateway {
  private readonly client: GatewayClient;

  constructor(client: GatewayClient) {
    this.client = client;
  }

  async readTable(tableId: string): Promise<ChessTable | null> {
    const response = await this.client.unary(ChessService.method.readTable, { tableId });
    return response.table ?? null;
  }

  async listSeatChoices(tableId: string, playerId: string): Promise<readonly ChessSeatChoice[]> {
    const response = await this.client.unary(ChessService.method.listSeatChoice, {
      tableId,
      playerId,
    });
    return response.collection?.chessSeatChoiceItems ?? [];
  }

  /**
   * Take a seat and answer what became of it.
   *
   * The result carries the table for every outcome except a table that is not
   * there, and that table is current whatever the outcome was.
   */
  async takeSeat(claim: SeatClaim): Promise<ChessSeatResult | null> {
    const response = await this.client.unary(ChessService.method.takeSeat, {
      tableId: claim.tableId,
      playerId: claim.playerId,
      choice: claim.choice,
      expectedVersion: claim.expectedVersion,
    });
    return response.result ?? null;
  }

  async start(tableId: string, playerId: string): Promise<ChessSession | null> {
    const response = await this.client.unary(ChessService.method.startGame, { tableId, playerId });
    return response.session ?? null;
  }

  async read(tableId: string, playerId: string): Promise<ChessSession | null> {
    const response = await this.client.unary(ChessService.method.readGame, { tableId, playerId });
    return response.session ?? null;
  }

  /**
   * Send an action and answer what became of it.
   *
   * The result carries a session for every outcome except a table with no game,
   * and that session is current whatever the outcome was.
   */
  async play(command: ChessCommand): Promise<ActionResult | null> {
    const response = await this.client.unary(ChessService.method.playAction, {
      tableId: command.tableId,
      playerId: command.playerId,
      commandId: command.commandId,
      action: command.action,
      expectedVersion: command.expectedVersion,
    });
    return response.result ?? null;
  }
}
