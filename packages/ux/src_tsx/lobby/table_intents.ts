import { create } from "@bufbuild/protobuf";
import type { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import { SeatSchema, SeatStatus, type Seat } from "@board-gamez/idl/lobby/model/seat_pb";
import { TableSchema, TableStatus, type Table } from "@board-gamez/idl/lobby/model/table_pb";

/**
 * The only place in this application that produces a new table.
 *
 * TableService is a store: it writes whole tables, guarded by the version they
 * were read at, and has no verb for joining a table or taking a seat. Nothing
 * between it and a browser decides today, so the decision is made here — a
 * read, a change, and a write.
 *
 * This is business logic in the presentation layer. It is confined to this file
 * so that JoinTable and TakeSeat operations on the lobby replace it: every
 * function below becomes one call, and no component changes.
 *
 * Joining and sitting are two different changes. Anyone may join, and a seat is
 * taken only by asking for that seat: nothing here chooses a seat on a player's
 * behalf. A seated player is always at the table, and leaving the table gives
 * up the seat.
 *
 * Every function is pure. Nothing here reads the network, the clock, or a
 * cache, and a table handed in is never changed.
 */

const FIRST_SEAT_NUMBER = 1;
const NEVER_STORED_VERSION = 0n;
const VACANT = "";

export const TableRefusal = {
  NO_SUCH_SEAT: "no_such_seat",
  SEAT_TAKEN: "seat_taken",
  ALREADY_SEATED: "already_seated",
  NOT_SEATED: "not_seated",
  ALREADY_AT_TABLE: "already_at_table",
  NOT_AT_TABLE: "not_at_table",
  NOT_ACCEPTING_PLAYERS: "not_accepting_players",
} as const;

export type TableRefusal = (typeof TableRefusal)[keyof typeof TableRefusal];

export const TABLE_REFUSAL_MESSAGES: Record<TableRefusal, string> = {
  [TableRefusal.NO_SUCH_SEAT]: "That seat is not at this table.",
  [TableRefusal.SEAT_TAKEN]: "Someone took that seat first.",
  [TableRefusal.ALREADY_SEATED]: "You are already seated at this table.",
  [TableRefusal.NOT_SEATED]: "You are not seated at this table.",
  [TableRefusal.ALREADY_AT_TABLE]: "You are already at this table.",
  [TableRefusal.NOT_AT_TABLE]: "You are not at this table.",
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
    id: globalThis.crypto.randomUUID(),
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
    table: withPlayers(table, table.seats, [...table.playerIds, playerId]),
  };
}

/**
 * Seat this player in the seat they asked for. Taking a seat puts a player at
 * the table if they were not already there.
 */
export function withPlayerSeated(table: Table, playerId: string, seatNumber: number): TableIntent {
  if (table.status !== TableStatus.WAITING) {
    return { kind: "refused", refusal: TableRefusal.NOT_ACCEPTING_PLAYERS };
  }
  if (seatOf(table, playerId) !== null) {
    return { kind: "refused", refusal: TableRefusal.ALREADY_SEATED };
  }
  const target = table.seats.find(matchesNumber(seatNumber));
  if (target === undefined) {
    return { kind: "refused", refusal: TableRefusal.NO_SUCH_SEAT };
  }
  if (target.status !== SeatStatus.OPEN) {
    return { kind: "refused", refusal: TableRefusal.SEAT_TAKEN };
  }
  return {
    kind: "changed",
    table: withPlayers(
      table,
      table.seats.map((seat) => (seat.number === seatNumber ? occupiedBy(seat, playerId) : seat)),
      isAtTable(table, playerId) ? table.playerIds : [...table.playerIds, playerId],
    ),
  };
}

/**
 * Give up the seat and stay at the table.
 */
export function withPlayerStood(table: Table, playerId: string): TableIntent {
  if (seatOf(table, playerId) === null) {
    return { kind: "refused", refusal: TableRefusal.NOT_SEATED };
  }
  return {
    kind: "changed",
    table: withPlayers(table, seatsWithout(table, playerId), table.playerIds),
  };
}

/**
 * Leave the table, giving up a seat on the way out.
 */
export function withPlayerLeft(table: Table, playerId: string): TableIntent {
  if (!isAtTable(table, playerId)) {
    return { kind: "refused", refusal: TableRefusal.NOT_AT_TABLE };
  }
  return {
    kind: "changed",
    table: withPlayers(
      table,
      seatsWithout(table, playerId),
      table.playerIds.filter((atTable: string) => atTable !== playerId),
    ),
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

function matchesNumber(seatNumber: number): (seat: Seat) => boolean {
  return (seat: Seat) => seat.number === seatNumber;
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

function seatsWithout(table: Table, playerId: string): Seat[] {
  return table.seats.map((seat) => (seat.playerId === playerId ? vacated(seat) : seat));
}

function occupiedBy(seat: Seat, playerId: string): Seat {
  return create(SeatSchema, {
    number: seat.number,
    status: SeatStatus.OCCUPIED,
    playerId,
  });
}

function vacated(seat: Seat): Seat {
  return create(SeatSchema, {
    number: seat.number,
    status: SeatStatus.OPEN,
    playerId: VACANT,
  });
}

function withPlayers(table: Table, seats: readonly Seat[], playerIds: readonly string[]): Table {
  return create(TableSchema, {
    id: table.id,
    gameType: table.gameType,
    status: table.status,
    seats: [...seats],
    version: table.version,
    playerIds: [...playerIds],
  });
}
