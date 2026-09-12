import type { UnoAction } from "@board-gamez/idl/uno/model/action_pb";
import type { ActionResult, UnoSession } from "@board-gamez/idl/uno/model/session_pb";
import type { UnoSeatChoice, UnoSeatResult, UnoTable } from "@board-gamez/idl/uno/model/table_pb";
import { UnoService } from "@board-gamez/idl/uno/service/game_pb";

import type { GatewayClient } from "../transport/gateway_client";

/**
 * One action, as this application sends it.
 *
 * `commandId` names the intent, so a repeat of the same command lands once.
 * `expectedVersion` is the version of the session that was showing when the
 * player committed, and the game refuses an action built on an older one.
 */
export type UnoCommand = {
  readonly tableId: string;
  readonly playerId: string;
  readonly commandId: string;
  readonly action: UnoAction;
  readonly expectedVersion: bigint;
};

/**
 * One seat being taken, as this application sends it.
 *
 * `expectedVersion` is the version of the table the choice was picked from, and
 * the lobby refuses a choice built on an older one.
 */
export type UnoSeatClaim = {
  readonly tableId: string;
  readonly playerId: string;
  readonly choice: UnoSeatChoice;
  readonly expectedVersion: bigint;
};

/**
 * The operations a UNO table and its game answer, as this application calls
 * them.
 *
 * Each answers with the domain's own type. An unset session means no game is
 * being played at that table, or that a start was refused, and reaches a caller
 * as null. An unset table means no UNO table has that id.
 */
export class UnoGateway {
  private readonly client: GatewayClient;

  constructor(client: GatewayClient) {
    this.client = client;
  }

  async readTable(tableId: string): Promise<UnoTable | null> {
    const response = await this.client.unary(UnoService.method.readTable, { tableId });
    return response.table ?? null;
  }

  async listSeatChoices(tableId: string, playerId: string): Promise<readonly UnoSeatChoice[]> {
    const response = await this.client.unary(UnoService.method.listSeatChoice, {
      tableId,
      playerId,
    });
    return response.collection?.unoSeatChoiceItems ?? [];
  }

  /**
   * Take a seat and answer what became of it.
   *
   * The result carries the table for every outcome except a table that is not
   * there, and that table is current whatever the outcome was.
   */
  async takeSeat(claim: UnoSeatClaim): Promise<UnoSeatResult | null> {
    const response = await this.client.unary(UnoService.method.takeSeat, {
      tableId: claim.tableId,
      playerId: claim.playerId,
      choice: claim.choice,
      expectedVersion: claim.expectedVersion,
    });
    return response.result ?? null;
  }

  async start(tableId: string, playerId: string): Promise<UnoSession | null> {
    const response = await this.client.unary(UnoService.method.startGame, { tableId, playerId });
    return response.session ?? null;
  }

  async read(tableId: string, playerId: string): Promise<UnoSession | null> {
    const response = await this.client.unary(UnoService.method.readGame, { tableId, playerId });
    return response.session ?? null;
  }

  /**
   * Send an action and answer what became of it.
   *
   * The result carries a session for every outcome except a table with no game,
   * and that session is current whatever the outcome was.
   */
  async play(command: UnoCommand): Promise<ActionResult | null> {
    const response = await this.client.unary(UnoService.method.playAction, {
      tableId: command.tableId,
      playerId: command.playerId,
      commandId: command.commandId,
      action: command.action,
      expectedVersion: command.expectedVersion,
    });
    return response.result ?? null;
  }
}
