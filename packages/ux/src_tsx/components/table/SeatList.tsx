import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { memo, type ReactElement } from "react";

import type { SeatView } from "../../lobby/table_views";
import { SeatRow } from "./SeatRow";

const HEAD_CELL_SX = {
  fontWeight: 700,
  letterSpacing: "0.06em",
  textTransform: "uppercase",
} as const;
const CONTAINER_SX = { border: 1, borderColor: "divider" } as const;

export type SeatListProps = {
  readonly seats: readonly SeatView[];
  readonly canTakeSeat: boolean;
  readonly busySeatNumber: number | null;
  readonly isLeaving: boolean;
  readonly onTakeSeat: (seatNumber: number) => void;
  readonly onLeaveSeat: () => void;
};

export const SeatList = memo(function SeatList(props: SeatListProps): ReactElement {
  const { seats, canTakeSeat, busySeatNumber, isLeaving, onTakeSeat, onLeaveSeat } = props;

  const header = (
    <TableHead>
      <TableRow>
        <TableCell sx={HEAD_CELL_SX}>Seat</TableCell>
        <TableCell sx={HEAD_CELL_SX}>Player</TableCell>
        <TableCell sx={HEAD_CELL_SX} align="right" />
      </TableRow>
    </TableHead>
  );

  const rows = seats.map((seat: SeatView) => (
    <SeatRow
      key={seat.number}
      seat={seat}
      isBusy={seat.number === busySeatNumber || (seat.isMine && isLeaving)}
      canTakeSeat={canTakeSeat}
      onTakeSeat={onTakeSeat}
      onLeaveSeat={onLeaveSeat}
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
