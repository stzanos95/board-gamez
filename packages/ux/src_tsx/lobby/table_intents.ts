import { create } from "@bufbuild/protobuf";
import type { GameType } from "@board-gamez/idl/lobby/model/game_type_pb";
import { SeatSchema, SeatStatus, type Seat } from "@board-gamez/idl/lobby/model/seat_pb";
import { TableSchema, TableStatus, type Table } from "@board-gamez/idl/lobby/model/table_pb";

/**
 * The only place in this application that produces a new table.
 *
 * TableService is a store: it writes whole tables, guarded by the version they
 * were read at, and has no verb for taking a seat. Nothing between it and a
 * browser decides today, so the decision is made here — a read, a change, and a
 * write.
 *
 * This is business logic in the presentation layer. It is confined to this file
 * so that a JoinSeat operation on the lobby replaces it: every function below
 * becomes one call, and no component changes.
 *
 * Every function is pure. Nothing here reads the network, the clock, or a
 * cache, and a table handed in is never changed.
 */

const FIRST_SEAT_NUMBER = 1;
const NEVER_STORED_VERSION = 0n;
const VACANT = "";

export const SeatRefusal = {
  NO_SUCH_SEAT: "no_such_seat",
  SEAT_TAKEN: "seat_taken",
  ALREADY_SEATED: "already_seated",
  NOT_SEATED: "not_seated",
  NOT_ACCEPTING_PLAYERS: "not_accepting_players",
  TABLE_FULL: "table_full",
} as const;

export type SeatRefusal = (typeof SeatRefusal)[keyof typeof SeatRefusal];

export const SEAT_REFUSAL_MESSAGES: Record<SeatRefusal, string> = {
  [SeatRefusal.NO_SUCH_SEAT]: "That seat is not at this table.",
  [SeatRefusal.SEAT_TAKEN]: "Someone took that seat first.",
  [SeatRefusal.ALREADY_SEATED]: "You are already seated at this table.",
  [SeatRefusal.NOT_SEATED]: "You are not seated at this table.",
  [SeatRefusal.NOT_ACCEPTING_PLAYERS]: "This table is no longer taking players.",
  [SeatRefusal.TABLE_FULL]: "Every seat at this table is taken.",
};

export type SeatIntent =
  | { readonly kind: "changed"; readonly table: Table }
  | { readonly kind: "refused"; readonly refusal: SeatRefusal };

/**
 * A table nobody has stored yet, with the player who opened it in the first
 * seat.
 *
 * Version 0 is what tells the store this is a creation. The identifier is
 * minted here because an upsert is addressed by one; a CreateTable operation
 * would mint it server-side instead.
 */
export function newTable(gameType: GameType, seatCount: number, hostPlayerId: string): Table {
  const seats = openSeats(seatCount);
  const [firstSeat, ...remaining] = seats;
  return create(TableSchema, {
    id: globalThis.crypto.randomUUID(),
    gameType,
    status: TableStatus.WAITING,
    seats:
      firstSeat === undefined ? seats : [occupiedBy(firstSeat, hostPlayerId), ...remaining],
    version: NEVER_STORED_VERSION,
  });
}

export function withPlayerSeated(table: Table, playerId: string, seatNumber: number): SeatIntent {
  if (table.status !== TableStatus.WAITING) {
    return { kind: "refused", refusal: SeatRefusal.NOT_ACCEPTING_PLAYERS };
  }
  if (seatOf(table, playerId) !== null) {
    return { kind: "refused", refusal: SeatRefusal.ALREADY_SEATED };
  }
  const target = table.seats.find(matchesNumber(seatNumber));
  if (target === undefined) {
    return { kind: "refused", refusal: SeatRefusal.NO_SUCH_SEAT };
  }
  if (target.status !== SeatStatus.OPEN) {
    return { kind: "refused", refusal: SeatRefusal.SEAT_TAKEN };
  }
  return {
    kind: "changed",
    table: withSeats(
      table,
      table.seats.map((seat) =>
        seat.number === seatNumber ? occupiedBy(seat, playerId) : seat,
      ),
    ),
  };
}

/**
 * Seat this player at the lowest-numbered open seat.
 *
 * The seat is chosen from the table handed in, so a caller that re-reads before
 * writing chooses from what is currently open rather than from what was open
 * when a button was drawn.
 */
export function withPlayerSeatedAnywhere(table: Table, playerId: string): SeatIntent {
  const openSeat = firstOpenSeatNumber(table);
  if (openSeat === null) {
    return { kind: "refused", refusal: SeatRefusal.TABLE_FULL };
  }
  return withPlayerSeated(table, playerId, openSeat);
}

export function withPlayerRemoved(table: Table, playerId: string): SeatIntent {
  if (seatOf(table, playerId) === null) {
    return { kind: "refused", refusal: SeatRefusal.NOT_SEATED };
  }
  return {
    kind: "changed",
    table: withSeats(
      table,
      table.seats.map((seat) => (seat.playerId === playerId ? vacated(seat) : seat)),
    ),
  };
}

/**
 * The seat this player is in, or null when they are not at this table.
 */
export function seatOf(table: Table, playerId: string): Seat | null {
  return table.seats.find((seat) => seat.playerId === playerId) ?? null;
}

/**
 * The lowest-numbered seat nobody is in, or null when the table is full.
 */
export function firstOpenSeatNumber(table: Table): number | null {
  return table.seats.find((seat) => seat.status === SeatStatus.OPEN)?.number ?? null;
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

function withSeats(table: Table, seats: readonly Seat[]): Table {
  return create(TableSchema, {
    id: table.id,
    gameType: table.gameType,
    status: table.status,
    seats: [...seats],
    version: table.version,
  });
}
