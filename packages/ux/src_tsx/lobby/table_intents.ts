import { create } from "@bufbuild/protobuf";
import type { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import { SeatSchema, SeatStatus, type Seat } from "@board-gamez/idl/lobby/model/seat_pb";
import { TableSchema, TableStatus, type Table } from "@board-gamez/idl/lobby/model/table_pb";

import { mintIdentifier } from "../format/mint_identifier";

/**
 * The only place in this application that produces a new table.
 *
 * TableService is a store: it writes whole tables, guarded by the version they
 * were read at, and has no verb for opening a table or joining one. Nothing
 * between it and a browser decides those today, so the decision is made here —
 * a read, a change, and a write.
 *
 * This is business logic in the presentation layer. It is confined to this file
 * so that CreateTable and JoinTable operations on the lobby replace it: every
 * function below becomes one call, and no component changes.
 *
 * Taking a seat, giving one up and leaving are not here. Each is a lobby or
 * game verb, because each has a consequence the browser must not decide: a
 * seat is taken as one of the choices the game offered, and a player who gives
 * up a seat is withdrawn from the game being played.
 *
 * Every function is pure. Nothing here reads the network, the clock, or a
 * cache, and a table handed in is never changed.
 */

const FIRST_SEAT_NUMBER = 1;
const NEVER_STORED_VERSION = 0n;
const VACANT = "";

export const TableRefusal = {
  ALREADY_AT_TABLE: "already_at_table",
  NOT_ACCEPTING_PLAYERS: "not_accepting_players",
} as const;

export type TableRefusal = (typeof TableRefusal)[keyof typeof TableRefusal];

export const TABLE_REFUSAL_MESSAGES: Record<TableRefusal, string> = {
  [TableRefusal.ALREADY_AT_TABLE]: "You are already at this table.",
  [TableRefusal.NOT_ACCEPTING_PLAYERS]: "This table is no longer taking players.",
};

export type TableIntent =
  | { readonly kind: "changed"; readonly table: Table }
  | { readonly kind: "refused"; readonly refusal: TableRefusal };

/**
 * The statuses a table takes players in. A seat is taken only while the table
 * is waiting.
 */
const JOINABLE_STATUSES: readonly TableStatus[] = [TableStatus.WAITING, TableStatus.IN_PROGRESS];

/**
 * A table nobody has stored yet, with the player who opened it at the table and
 * every seat open.
 *
 * Version 0 is what tells the store this is a creation. The identifier is
 * minted here because an upsert is addressed by one; a CreateTable operation
 * would mint it server-side instead.
 */
export function newTable(gameType: GameType, seatCount: number, hostPlayerId: string): Table {
  return create(TableSchema, {
    id: mintIdentifier(),
    gameType,
    status: TableStatus.WAITING,
    seats: openSeats(seatCount),
    version: NEVER_STORED_VERSION,
    playerIds: [hostPlayerId],
  });
}

export function withPlayerJoined(table: Table, playerId: string): TableIntent {
  if (!isAcceptingPlayers(table)) {
    return { kind: "refused", refusal: TableRefusal.NOT_ACCEPTING_PLAYERS };
  }
  if (isAtTable(table, playerId)) {
    return { kind: "refused", refusal: TableRefusal.ALREADY_AT_TABLE };
  }
  return {
    kind: "changed",
    table: create(TableSchema, {
      id: table.id,
      gameType: table.gameType,
      status: table.status,
      seats: [...table.seats],
      version: table.version,
      playerIds: [...table.playerIds, playerId],
    }),
  };
}

/**
 * The seat this player is in, or null when they are seated nowhere here.
 */
export function seatOf(table: Table, playerId: string): Seat | null {
  return table.seats.find((seat) => seat.playerId === playerId) ?? null;
}

/**
 * Whether this player is at the table, seated or not.
 */
export function isAtTable(table: Table, playerId: string): boolean {
  return table.playerIds.includes(playerId);
}

/**
 * Whether the table takes players. A finished or abandoned table takes nobody.
 */
export function isAcceptingPlayers(table: Table): boolean {
  return JOINABLE_STATUSES.includes(table.status);
}

function openSeats(seatCount: number): Seat[] {
  return Array.from({ length: seatCount }, (_unused, index) =>
    create(SeatSchema, {
      number: FIRST_SEAT_NUMBER + index,
      status: SeatStatus.OPEN,
      playerId: VACANT,
    }),
  );
}
