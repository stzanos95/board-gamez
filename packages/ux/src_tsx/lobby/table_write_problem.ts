import type { TableWrite } from "./table_writer";
import { TABLE_REFUSAL_MESSAGES } from "./table_intents";

type UnwrittenKind = Exclude<TableWrite["kind"], "written" | "refused">;

const UNWRITTEN_MESSAGES: Record<UnwrittenKind, string> = {
  contended: "The table changed while you were acting. Try again.",
  gone: "That table is no longer there.",
};

/**
 * What to tell the player about a change to a table, or null when it worked.
 */
export function tableWriteProblem(write: TableWrite): string | null {
  if (write.kind === "written") {
    return null;
  }
  if (write.kind === "refused") {
    return TABLE_REFUSAL_MESSAGES[write.refusal];
  }
  return UNWRITTEN_MESSAGES[write.kind];
}
