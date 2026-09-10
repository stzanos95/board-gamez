import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, type ReactElement } from "react";

import { useDeleteTable } from "../../lobby/use_delete_table";
import { useLeaveSeat, useTakeSeat } from "../../lobby/use_seat_actions";
import { useTable } from "../../lobby/use_table";
import { GameArtwork } from "../common/GameArtwork";
import { LoadingPanel, PanelMessage } from "../common/PanelMessage";
import { TableStatusChip } from "../common/TableStatusChip";
import { SeatList } from "./SeatList";

const LAYOUT_SX = {
  display: "grid",
  gap: 3,
  gridTemplateColumns: { xs: "1fr", md: "minmax(0, 1fr) 300px" },
  alignItems: "start",
} as const;

export type TableScreenProps = {
  readonly tableId: string;
  readonly onLeft: () => void;
};

/**
 * The table this player is sitting at.
 *
 * Reached by taking a seat, and left by giving one up. A player who is not
 * seated here is sent back to the list, so this screen only ever shows a table
 * its viewer is at.
 */
export function TableScreen(props: TableScreenProps): ReactElement {
  const { tableId, onLeft } = props;
  const { summary, seats, isLoading, isMissing, error } = useTable(tableId);
  const { run: takeSeat, pendingInput: takingSeat, problem: takeProblem } = useTakeSeat();
  const { run: leaveSeat, isPending: isLeaving, problem: leaveProblem } = useLeaveSeat();
  const { run: deleteTable, isPending: isClosing, problem: closeProblem } = useDeleteTable();

  const handleTakeSeat = useCallback(
    (seatNumber: number) => takeSeat({ tableId, seatNumber }),
    [takeSeat, tableId],
  );
  const handleLeaveSeat = useCallback(() => leaveSeat(tableId), [leaveSeat, tableId]);
  const handleClose = useCallback(
    () => deleteTable(tableId, onLeft),
    [deleteTable, tableId, onLeft],
  );

  const hasLeft = summary !== null && !summary.isSeated;
  useEffect(() => {
    if (hasLeft) {
      onLeft();
    }
  }, [hasLeft, onLeft]);

  const problem =
    takeProblem ?? leaveProblem ?? closeProblem ?? (error === null ? null : error.message);

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
            {summary.gameLabel} · {summary.seatsLabel} seated
          </Typography>
        </Stack>
        <TableStatusChip status={summary.status} />
      </Stack>
    );

  const closeButton =
    summary === null ? null : (
      <Button variant="outlined" color="error" onClick={handleClose} disabled={isClosing}>
        Close this table
      </Button>
    );

  const seated =
    summary === null ? null : (
      <>
        {heading}
        {problemPanel}
        <Box sx={LAYOUT_SX}>
          <Stack spacing={2}>
            <SeatList
              seats={seats}
              canTakeSeat={summary.canTakeSeat}
              busySeatNumber={takingSeat?.seatNumber ?? null}
              isLeaving={isLeaving}
              onTakeSeat={handleTakeSeat}
              onLeaveSeat={handleLeaveSeat}
            />
            <Stack direction="row">{closeButton}</Stack>
          </Stack>
          <GameArtwork gameType={summary.gameType} />
        </Box>
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
