import { SeatOutcome } from "@board-gamez/idl/lobby/model/seat_result_pb";

/**
 * What to tell the player about a change to their place at a table, or null
 * when it worked.
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
  [SeatOutcome.CREATED]: null,
  [SeatOutcome.JOINED]: null,
  [SeatOutcome.ALREADY_AT_TABLE]: "You are already at this table.",
  [SeatOutcome.NOT_ACCEPTING_PLAYERS]: "This table is no longer taking players.",
  [SeatOutcome.GAME_NOT_HOSTED]: "That game is not hosted here.",
  [SeatOutcome.SEAT_COUNT_NOT_ALLOWED]: "That game cannot be played with that many seats.",
  [SeatOutcome.TABLE_FULL]: "Every seat at this table is taken.",
};
