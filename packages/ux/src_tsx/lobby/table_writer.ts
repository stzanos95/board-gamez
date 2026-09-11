import type { Table } from "@board-gamez/idl/lobby/model/table_pb";

import type { TableGateway } from "./table_gateway";
import type { TableIntent, TableRefusal } from "./table_intents";

/**
 * How a change to a table ended.
 *
 * `contended` means the table kept moving underneath the write. `gone` means
 * no table has that identifier any more.
 */
export type TableWrite =
  | { readonly kind: "written"; readonly table: Table }
  | { readonly kind: "refused"; readonly refusal: TableRefusal }
  | { readonly kind: "contended" }
  | { readonly kind: "gone" };

/**
 * A write reaches the store built on the version it was read at, and a table
 * that has moved on since is refused. One re-read covers the ordinary race of
 * two players reaching for the same seat, or joining at the same moment.
 */
const WRITE_ATTEMPTS = 2;

/**
 * Read a table, decide the change, and write it back at the version read.
 *
 * Shared by every change to a table because the ordering it enforces is what
 * makes a contested write safe, and two copies of it would drift.
 */
export async function writeTableChange(
  gateway: TableGateway,
  tableId: string,
  decide: (table: Table) => TableIntent,
): Promise<TableWrite> {
  for (let attempt = 0; attempt < WRITE_ATTEMPTS; attempt += 1) {
    const current = await gateway.read(tableId);
    if (current === null) {
      return { kind: "gone" };
    }
    const intent = decide(current);
    if (intent.kind === "refused") {
      return { kind: "refused", refusal: intent.refusal };
    }
    const stored = await gateway.upsert(intent.table);
    if (stored !== null) {
      return { kind: "written", table: stored };
    }
  }
  return { kind: "contended" };
}
