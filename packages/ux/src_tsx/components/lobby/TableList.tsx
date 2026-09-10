import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { memo, type ReactElement } from "react";

import type { TableSummaryView } from "../../lobby/table_views";
import { LobbyTableRow } from "./LobbyTableRow";

const FIRST_POSITION = 1;

const HEAD_CELL_SX = { fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" } as const;
const CONTAINER_SX = { border: 1, borderColor: "divider" } as const;

export type TableListProps = {
  readonly summaries: readonly TableSummaryView[];
  readonly busyTableId: string | null;
  readonly onJoin: (tableId: string) => void;
};

export const TableList = memo(function TableList(props: TableListProps): ReactElement {
  const { summaries, busyTableId, onJoin } = props;

  const header = (
    <TableHead>
      <TableRow>
        <TableCell sx={HEAD_CELL_SX}>#</TableCell>
        <TableCell sx={HEAD_CELL_SX}>Name</TableCell>
        <TableCell sx={HEAD_CELL_SX}>Type</TableCell>
        <TableCell sx={HEAD_CELL_SX} align="center">
          Players
        </TableCell>
        <TableCell sx={HEAD_CELL_SX}>Status</TableCell>
        <TableCell sx={HEAD_CELL_SX} align="right">
          Join
        </TableCell>
      </TableRow>
    </TableHead>
  );

  const rows = summaries.map((summary: TableSummaryView, offset: number) => (
    <LobbyTableRow
      key={summary.id}
      position={FIRST_POSITION + offset}
      summary={summary}
      isBusy={summary.id === busyTableId}
      onJoin={onJoin}
    />
  ));

  return (
    <TableContainer component={Paper} sx={CONTAINER_SX}>
      <Table size="small">
        {header}
        <TableBody>{rows}</TableBody>
      </Table>
    </TableContainer>
  );
});
