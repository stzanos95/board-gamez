import { SeatStatus } from "@board-gamez/idl/lobby/model/seat_pb";
import type { UnoSeat, UnoSeatChoice, UnoTable } from "@board-gamez/idl/uno/model/table_pb";

import { shortIdentifier } from "../format/short_identifier";

/**
 * A UNO table's seats, in the shape a component draws them.
 *
 * These are derivations over data already in hand: a label, a comparison
 * against who is looking, and the choice the game offered for a seat. Nothing
 * here is a decision, and nothing here is sent anywhere except the choice,
 * which is sent back exactly as it was offered.
 */

const YOU = "You";

export type UnoSeatView = {
  readonly number: number;
  readonly seatLabel: string;
  readonly occupantLabel: string;
  readonly isMine: boolean;
  readonly isOpen: boolean;
  readonly choice: UnoSeatChoice | null;
};

export type UnoSeatViewsInput = {
  readonly table: UnoTable;
  readonly choices: readonly UnoSeatChoice[];
  readonly viewerId: string;
  readonly viewerName: string;
};

export function toUnoSeatViews(input: UnoSeatViewsInput): readonly UnoSeatView[] {
  const { table, choices, viewerId, viewerName } = input;
  return table.seats.map((seat: UnoSeat) => {
    const isMine = seat.playerId === viewerId;
    const choice =
      choices.find((offered: UnoSeatChoice) => offered.number === seat.number) ?? null;
    return {
      number: seat.number,
      seatLabel: `Seat ${seat.number}`,
      occupantLabel: occupantLabelOf(seat, isMine, viewerName),
      isMine,
      isOpen: seat.status === SeatStatus.OPEN,
      choice,
    };
  });
}

function occupantLabelOf(seat: UnoSeat, isMine: boolean, viewerName: string): string {
  if (seat.status === SeatStatus.OPEN) {
    return "";
  }
  if (isMine) {
    return `${viewerName} (${YOU})`;
  }
  return `Player ${shortIdentifier(seat.playerId)}`;
}
