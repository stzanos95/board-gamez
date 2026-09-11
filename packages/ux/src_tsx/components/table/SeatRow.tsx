import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type ReactElement } from "react";

import { SEAT_STATUS_LABELS } from "../../lobby/table_labels";
import type { SeatView } from "../../lobby/table_views";

const INDEX_SX = { color: "text.secondary", width: 56 } as const;
const MARKER_SX = { width: 10, height: 10, borderRadius: "50%", flexShrink: 0 } as const;
const ACTION_SX = { width: 120 } as const;
const OPEN_SX = { color: "text.secondary", fontStyle: "italic" } as const;

export type SeatRowProps = {
  readonly seat: SeatView;
  readonly isBusy: boolean;
  readonly canTakeSeat: boolean;
  readonly onTakeSeat: (seatNumber: number) => void;
  readonly onStandUp: () => void;
};

/**
 * One place at the table.
 *
 * The marker's colour comes from `palette.seat`, so a theme decides how an
 * open, a taken and your own seat are told apart.
 */
export const SeatRow = memo(function SeatRow(props: SeatRowProps): ReactElement {
  const { seat, isBusy, canTakeSeat, onTakeSeat, onStandUp } = props;

  const handleTakeSeatClick = useCallback(() => onTakeSeat(seat.number), [onTakeSeat, seat.number]);

  const marker = <Stack component="span" sx={{ ...MARKER_SX, bgcolor: markerColorOf(seat) }} />;

  const occupant = seat.isOpen ? (
    <Typography variant="body2" sx={OPEN_SX}>
      {SEAT_STATUS_LABELS[seat.status]}
    </Typography>
  ) : (
    <Typography variant="body2" fontWeight={seat.isMine ? 700 : 400}>
      {seat.occupantLabel}
    </Typography>
  );

  const action = seat.isMine ? (
    <Button size="small" variant="outlined" color="warning" onClick={onStandUp} disabled={isBusy}>
      Stand up
    </Button>
  ) : (
    <Button
      size="small"
      variant="contained"
      onClick={handleTakeSeatClick}
      disabled={isBusy || !canTakeSeat || !seat.isOpen}
    >
      Sit here
    </Button>
  );

  return (
    <TableRow hover>
      <TableCell>
        <Typography variant="body2" sx={INDEX_SX}>
          {seat.number}
        </Typography>
      </TableCell>
      <TableCell>
        <Stack direction="row" spacing={1.5} alignItems="center">
          {marker}
          {occupant}
        </Stack>
      </TableCell>
      <TableCell align="right" sx={ACTION_SX}>
        {action}
      </TableCell>
    </TableRow>
  );
});

function markerColorOf(seat: SeatView): string {
  if (seat.isMine) {
    return "seat.mine";
  }
  return seat.isOpen ? "seat.open" : "seat.occupied";
}
