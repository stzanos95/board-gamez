import Button from "@mui/material/Button";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type ReactElement } from "react";

import type { TableSummaryView } from "../../lobby/table_views";
import { TableStatusChip } from "../common/TableStatusChip";

const INDEX_SX = { color: "text.secondary", width: 64 } as const;
const SEATS_SX = { fontVariantNumeric: "tabular-nums" } as const;
const ACTION_SX = { width: 120 } as const;

export type LobbyTableRowProps = {
  readonly position: number;
  readonly summary: TableSummaryView;
  readonly isBusy: boolean;
  readonly onJoin: (tableId: string) => void;
};

/**
 * One table in the browser.
 *
 * Takes the values it draws rather than the table, so a seat filling on one row
 * leaves the rest of the list alone.
 */
export const LobbyTableRow = memo(function LobbyTableRow(
  props: LobbyTableRowProps,
): ReactElement {
  const { position, summary, isBusy, onJoin } = props;

  const handleJoinClick = useCallback(() => onJoin(summary.id), [onJoin, summary.id]);

  const index = (
    <Typography variant="body2" sx={INDEX_SX}>
      {position}
    </Typography>
  );

  const name = (
    <Typography variant="body2" fontWeight={600}>
      {summary.name}
    </Typography>
  );

  const seats = (
    <Typography variant="body2" sx={SEATS_SX}>
      {summary.seatsLabel}
    </Typography>
  );

  const joinButton = (
    <Button
      size="small"
      variant="contained"
      onClick={handleJoinClick}
      disabled={isBusy || !summary.canTakeSeat}
    >
      {summary.isFull ? "Full" : "Join"}
    </Button>
  );

  return (
    <TableRow hover>
      <TableCell>{index}</TableCell>
      <TableCell>{name}</TableCell>
      <TableCell>{summary.gameLabel}</TableCell>
      <TableCell align="center">{seats}</TableCell>
      <TableCell>
        <TableStatusChip status={summary.status} />
      </TableCell>
      <TableCell align="right" sx={ACTION_SX}>
        {joinButton}
      </TableCell>
    </TableRow>
  );
});
