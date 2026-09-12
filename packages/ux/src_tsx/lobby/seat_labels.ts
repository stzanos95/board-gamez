import { SeatOutcome } from "@board-gamez/idl/lobby/model/seat_result_pb";

/**
 * What to tell the player about a seat being taken, or null when it worked.
 */
export const SEAT_OUTCOME_PROBLEMS: Record<SeatOutcome, string | null> = {
  [SeatOutcome.UNSPECIFIED]: "The lobby did not say what happened to that seat.",
  [SeatOutcome.TAKEN]: null,
  [SeatOutcome.TABLE_NOT_FOUND]: "That table is no longer there.",
  [SeatOutcome.NOT_OFFERED]: "That seat is no longer on offer.",
  [SeatOutcome.VERSION_MOVED]: "The table changed while you were acting. Try again.",
  [SeatOutcome.VACATED]: null,
  [SeatOutcome.LEFT]: null,
  [SeatOutcome.NOT_SEATED]: "You are not seated at this table.",
  [SeatOutcome.NOT_AT_TABLE]: "You are not at this table.",
};
