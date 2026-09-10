import type { SeatWrite } from "./seat_writer";
import { SEAT_REFUSAL_MESSAGES } from "./table_intents";

type UnwrittenKind = Exclude<SeatWrite["kind"], "written" | "refused">;

const UNWRITTEN_MESSAGES: Record<UnwrittenKind, string> = {
  contended: "The table changed while you were sitting down. Try again.",
  gone: "That table is no longer there.",
};

/**
 * What to tell the player about a seat change, or null when it worked.
 */
export function seatWriteProblem(write: SeatWrite): string | null {
  if (write.kind === "written") {
    return null;
  }
  if (write.kind === "refused") {
    return SEAT_REFUSAL_MESSAGES[write.refusal];
  }
  return UNWRITTEN_MESSAGES[write.kind];
}
