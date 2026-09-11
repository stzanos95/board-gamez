import type { ChessAction } from "@board-gamez/idl/chess/model/action_pb";
import type { ActionResult, ChessSession } from "@board-gamez/idl/chess/model/session_pb";
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
 * The three operations a chess game answers, as this application calls them.
 *
 * Each answers with the domain's own type. An unset session means no game is
 * being played at that table, or that a start was refused, and reaches a caller
 * as null.
 */
export class ChessGateway {
  private readonly client: GatewayClient;

  constructor(client: GatewayClient) {
    this.client = client;
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
