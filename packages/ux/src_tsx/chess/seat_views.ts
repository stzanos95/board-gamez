import type { Color } from "@board-gamez/idl/chess/model/piece_pb";
import type { ChessSeat, ChessSeatChoice, ChessTable } from "@board-gamez/idl/chess/model/table_pb";
import { SeatStatus } from "@board-gamez/idl/lobby/model/seat_pb";

import { shortIdentifier } from "../format/short_identifier";
import { COLOR_LABELS } from "./chess_labels";

/**
 * A chess table's seats, in the shape a component draws them.
 *
 * These are derivations over data already in hand: a label, a comparison
 * against who is looking, and the choice the game offered for a seat. Nothing
 * here is a decision, and nothing here is sent anywhere except the choice,
 * which is sent back exactly as it was offered.
 */

const YOU = "You";

export type ChessSeatView = {
  readonly number: number;
  readonly color: Color;
  readonly colorLabel: string;
  readonly occupantLabel: string;
  readonly isMine: boolean;
  readonly isOpen: boolean;
  readonly choice: ChessSeatChoice | null;
};

export type ChessSeatViewsInput = {
  readonly table: ChessTable;
  readonly choices: readonly ChessSeatChoice[];
  readonly viewerId: string;
  readonly viewerName: string;
};

export function toChessSeatViews(input: ChessSeatViewsInput): readonly ChessSeatView[] {
  const { table, choices, viewerId, viewerName } = input;
  return table.seats.map((seat: ChessSeat) => {
    const isMine = seat.playerId === viewerId;
    const choice =
      choices.find((offered: ChessSeatChoice) => offered.number === seat.number) ?? null;
    return {
      number: seat.number,
      color: choice?.color ?? seat.color,
      colorLabel: COLOR_LABELS[choice?.color ?? seat.color],
      occupantLabel: occupantLabelOf(seat, isMine, viewerName),
      isMine,
      isOpen: seat.status === SeatStatus.OPEN,
      choice,
    };
  });
}

function occupantLabelOf(seat: ChessSeat, isMine: boolean, viewerName: string): string {
  if (seat.status === SeatStatus.OPEN) {
    return "";
  }
  if (isMine) {
    return `${viewerName} (${YOU})`;
  }
  return `Player ${shortIdentifier(seat.playerId)}`;
}
