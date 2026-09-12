import type { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import { SeatStatus, type Seat } from "@board-gamez/idl/lobby/model/seat_pb";
import { TableStatus, type Table } from "@board-gamez/idl/lobby/model/table_pb";

import { shortIdentifier } from "../format/short_identifier";
import { GAME_TYPE_LABELS } from "./table_labels";

/**
 * Tables and seats, in the shape a component draws them.
 *
 * These are derivations over data already in hand: a label, a count, a
 * comparison against who is looking. Nothing here is a decision, and nothing
 * here is sent anywhere.
 *
 * An occupant is drawn from a player identifier because the lobby stores one.
 * A display name belongs to the identity domain and is joined into a view when
 * that domain answers; until it does, another player is shown by a short form
 * of their identifier.
 */

const YOU = "You";
const TABLE_NAME_PREFIX = "Table";

/**
 * Whether a join is offered for a table in each status. The lobby decides
 * whether a join is accepted; this only says whether to show the way in.
 */
const IS_JOIN_OFFERED_BY_STATUS: Record<TableStatus, boolean> = {
  [TableStatus.UNSPECIFIED]: false,
  [TableStatus.WAITING]: true,
  [TableStatus.IN_PROGRESS]: true,
  [TableStatus.FINISHED]: false,
  [TableStatus.ABANDONED]: false,
};

export type SeatView = {
  readonly number: number;
  readonly status: SeatStatus;
  readonly occupantLabel: string;
  readonly isMine: boolean;
  readonly isOpen: boolean;
};

export type TableSummaryView = {
  readonly id: string;
  readonly shortId: string;
  readonly name: string;
  readonly seatsLabel: string;
  readonly gameType: GameType;
  readonly gameLabel: string;
  readonly status: TableStatus;
  readonly seatCount: number;
  readonly occupiedCount: number;
  readonly openCount: number;
  readonly playerCount: number;
  readonly isAtTable: boolean;
  readonly isSeated: boolean;
  readonly isFull: boolean;
  readonly canJoin: boolean;
};

export function toSeatViews(
  table: Table,
  viewerId: string,
  viewerName: string,
): readonly SeatView[] {
  return table.seats.map((seat: Seat) => toSeatView(seat, viewerId, viewerName));
}

export function toTableSummaryView(table: Table, viewerId: string): TableSummaryView {
  const seatCount = table.seats.length;
  const occupiedCount = table.seats.filter(isOccupied).length;
  const atTable = table.playerIds.includes(viewerId);
  const isSeated = table.seats.some((seat: Seat) => seat.playerId === viewerId);
  const isFull = occupiedCount >= seatCount;

  return {
    id: table.id,
    shortId: shortIdentifier(table.id),
    name: `${TABLE_NAME_PREFIX} ${shortIdentifier(table.id)}`,
    seatsLabel: `${occupiedCount}/${seatCount}`,
    gameType: table.gameType,
    gameLabel: GAME_TYPE_LABELS[table.gameType],
    status: table.status,
    seatCount,
    occupiedCount,
    openCount: seatCount - occupiedCount,
    playerCount: table.playerIds.length,
    isAtTable: atTable,
    isSeated,
    isFull,
    canJoin: IS_JOIN_OFFERED_BY_STATUS[table.status] && !atTable,
  };
}

function toSeatView(seat: Seat, viewerId: string, viewerName: string): SeatView {
  const isMine = seat.playerId === viewerId;
  return {
    number: seat.number,
    status: seat.status,
    isMine,
    isOpen: seat.status === SeatStatus.OPEN,
    occupantLabel: occupantLabelOf(seat, isMine, viewerName),
  };
}

function occupantLabelOf(seat: Seat, isMine: boolean, viewerName: string): string {
  if (seat.status === SeatStatus.OPEN) {
    return "";
  }
  if (isMine) {
    return `${viewerName} (${YOU})`;
  }
  return `Player ${shortIdentifier(seat.playerId)}`;
}

function isOccupied(seat: Seat): boolean {
  return seat.status === SeatStatus.OCCUPIED;
}
