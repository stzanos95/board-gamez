import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, type ReactElement } from "react";

import { useDeleteTable } from "../../lobby/use_delete_table";
import { useLeaveTable, useStandUp } from "../../lobby/use_table_actions";
import { useTable } from "../../lobby/use_table";
import { useTableChanges, type TableChangeHandlers } from "../../lobby/use_table_changes";
import { LoadingPanel, PanelMessage } from "../common/PanelMessage";
import { TableStatusChip } from "../common/TableStatusChip";
import { GameScreen } from "./GameScreen";
import { SeatList } from "./SeatList";

export type TableScreenProps = {
  readonly tableId: string;
  readonly onLeft: () => void;
};

/**
 * The table this player is at.
 *
 * Reached by joining, and left by leaving. Standing up happens here without
 * leaving; sitting down happens on the game's own screen, where the game says
 * what each seat is. A player who is not at this table is sent back to the
 * list, so this screen only ever shows a table its viewer is at, and so is a
 * viewer whose table is closed under them.
 *
 * The table's socket is opened here, once, for every query on the screen.
 *
 * The game's own screen sits above the seats, and is what the table becomes
 * once it is full.
 */
export function TableScreen(props: TableScreenProps): ReactElement {
  const { tableId, onLeft } = props;
  const changeHandlers = useMemo<TableChangeHandlers>(() => ({ onClosed: onLeft }), [onLeft]);
  useTableChanges(tableId, changeHandlers);
  const { summary, seats, isLoading, isMissing, error } = useTable(tableId);
  const { run: standUp, isPending: isStandingUp, problem: standProblem } = useStandUp();
  const { run: leaveTable, isPending: isLeaving, problem: leaveProblem } = useLeaveTable();
  const { run: deleteTable, isPending: isClosing, problem: closeProblem } = useDeleteTable();

  const handleStandUp = useCallback(() => standUp(tableId), [standUp, tableId]);
  const handleLeave = useCallback(() => leaveTable(tableId), [leaveTable, tableId]);
  const handleClose = useCallback(
    () => deleteTable(tableId, onLeft),
    [deleteTable, tableId, onLeft],
  );

  const hasLeft = summary !== null && !summary.isAtTable;
  useEffect(() => {
    if (hasLeft) {
      onLeft();
    }
  }, [hasLeft, onLeft]);

  const problem =
    standProblem ??
    leaveProblem ??
    closeProblem ??
    (error === null ? null : error.message);

  const problemPanel =
    problem === null ? null : (
      <PanelMessage severity="warning" title="That did not work" detail={problem} />
    );

  const heading =
    summary === null ? null : (
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Stack>
          <Typography variant="h1">{summary.name}</Typography>
          <Typography variant="caption" color="text.secondary">
            {summary.gameLabel} · {summary.seatsLabel} seated · {summary.playerCount} at the table
          </Typography>
        </Stack>
        <TableStatusChip status={summary.status} />
      </Stack>
    );

  const leaveButton =
    summary === null ? null : (
      <Button variant="outlined" onClick={handleLeave} disabled={isLeaving}>
        Leave table
      </Button>
    );

  const closeButton =
    summary === null ? null : (
      <Button variant="outlined" color="error" onClick={handleClose} disabled={isClosing}>
        Close this table
      </Button>
    );

  const gameScreen =
    summary === null ? null : (
      <GameScreen
        gameType={summary.gameType}
        tableId={tableId}
        canStart={summary.isFull && summary.isSeated}
        isSeated={summary.isSeated}
      />
    );

  const seated =
    summary === null ? null : (
      <>
        {heading}
        {problemPanel}
        {gameScreen}
        <SeatList seats={seats} isStandingUp={isStandingUp} onStandUp={handleStandUp} />
        <Stack direction="row" spacing={1}>
          {leaveButton}
          {closeButton}
        </Stack>
      </>
    );

  const missingPanel = (
    <PanelMessage
      severity="info"
      title="No table here"
      detail="It was closed, or the link names one that never existed."
    />
  );

  const body = isLoading ? (
    <LoadingPanel label="Reading the table" />
  ) : isMissing ? (
    missingPanel
  ) : (
    seated
  );

  return <Stack spacing={3}>{body}</Stack>;
}
