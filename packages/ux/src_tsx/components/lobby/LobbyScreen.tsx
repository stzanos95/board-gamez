import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState, type ReactElement } from "react";

import type { NewTableInput } from "../../lobby/use_create_table";
import { useCreateTable } from "../../lobby/use_create_table";
import { useJoinTable } from "../../lobby/use_table_actions";
import { useTables } from "../../lobby/use_tables";
import { LoadingPanel, PanelMessage } from "../common/PanelMessage";
import { CreateTableDialog } from "./CreateTableDialog";
import { TableList } from "./TableList";

export type LobbyScreenProps = {
  readonly onEnterTable: (tableId: string) => void;
};

/**
 * Every table, and the way into one.
 *
 * A player who is already at a table is sent to it: reaching this list means
 * they left it, or reloaded the page, and either way the table is where they
 * belong.
 */
export function LobbyScreen(props: LobbyScreenProps): ReactElement {
  const { onEnterTable } = props;
  const { summaries, joinedTableId, isLoading, isRefreshing, error, refresh } = useTables();
  const { run: createTable, isPending: isCreating, problem: createProblem } = useCreateTable();
  const { run: joinTable, pendingInput: joiningTableId, problem: joinProblem } = useJoinTable();
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  useEffect(() => {
    if (joinedTableId !== null) {
      onEnterTable(joinedTableId);
    }
  }, [joinedTableId, onEnterTable]);

  const handleOpenCreate = useCallback(() => setIsCreateOpen(true), []);
  const handleCloseCreate = useCallback(() => setIsCreateOpen(false), []);
  const handleCreate = useCallback(
    (input: NewTableInput) => {
      setIsCreateOpen(false);
      createTable(input);
    },
    [createTable],
  );

  const heading = (
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Stack>
        <Typography variant="h1">Tables</Typography>
        <Typography variant="caption" color="text.secondary">
          Join one, or open your own
        </Typography>
      </Stack>
      <Stack direction="row" spacing={1} alignItems="center">
        <Button variant="text" onClick={refresh} disabled={isRefreshing}>
          Refresh
        </Button>
        <Button variant="contained" onClick={handleOpenCreate} disabled={isCreating}>
          Create table
        </Button>
      </Stack>
    </Stack>
  );

  const problem = createProblem ?? joinProblem ?? (error === null ? null : error.message);

  const problemPanel =
    problem === null ? null : (
      <PanelMessage severity="error" title="That did not work" detail={problem} />
    );

  const emptyPanel =
    isLoading || summaries.length > 0 ? null : (
      <PanelMessage
        severity="info"
        title="No tables yet"
        detail="Create one, then join it from another browser tab."
      />
    );

  const list = isLoading ? (
    <LoadingPanel label="Reading the lobby" />
  ) : (
    <TableList summaries={summaries} busyTableId={joiningTableId} onJoin={joinTable} />
  );

  return (
    <Stack spacing={3}>
      {heading}
      {problemPanel}
      {emptyPanel}
      {list}
      <CreateTableDialog
        isOpen={isCreateOpen}
        isPending={isCreating}
        onCreate={handleCreate}
        onClose={handleCloseCreate}
      />
    </Stack>
  );
}
