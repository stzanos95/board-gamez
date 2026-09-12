import type { UnoSeatChoice } from "@board-gamez/idl/uno/model/table_pb";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import type { UnoSeatView } from "../../uno/seat_views";
import { UnoSeatRow } from "./UnoSeatRow";

const PANEL_SX = { p: 3, border: 1, borderColor: "divider" } as const;

const READY_DETAIL = "Every seat is taken.";
const WAITING_DETAIL = "The game begins once every seat is taken.";
const WATCHING_DETAIL = "Take a seat to play, or stay and watch.";

export type UnoPreGamePanelProps = {
  readonly seats: readonly UnoSeatView[];
  readonly canStart: boolean;
  readonly isSeated: boolean;
  readonly isStarting: boolean;
  readonly busyChoice: UnoSeatChoice | null;
  readonly onTakeSeat: (choice: UnoSeatChoice) => void;
  readonly onStart: () => void;
};

/**
 * The table before its game has begun: who sits where, the seats still on
 * offer, and the button that begins the game once every seat is taken.
 */
export const UnoPreGamePanel = memo(function UnoPreGamePanel(
  props: UnoPreGamePanelProps,
): ReactElement {
  const { seats, canStart, isSeated, isStarting, busyChoice, onTakeSeat, onStart } = props;

  const rows = seats.map((seat: UnoSeatView) => (
    <UnoSeatRow
      key={seat.number}
      seatLabel={seat.seatLabel}
      occupantLabel={seat.occupantLabel}
      isMine={seat.isMine}
      isOpen={seat.isOpen}
      choice={seat.choice}
      isBusy={busyChoice !== null && busyChoice.number === seat.number}
      onTakeSeat={onTakeSeat}
    />
  ));

  const startButton = canStart ? (
    <Button variant="contained" onClick={onStart} disabled={isStarting}>
      Start game
    </Button>
  ) : null;

  const detail = detailOf(canStart, isSeated);

  return (
    <Paper sx={PANEL_SX}>
      <Stack spacing={2} alignItems="flex-start">
        <Typography variant="h3">No game yet</Typography>
        <Stack spacing={0.5}>{rows}</Stack>
        <Typography variant="body2" color="text.secondary">
          {detail}
        </Typography>
        {startButton}
      </Stack>
    </Paper>
  );
});

function detailOf(canStart: boolean, isSeated: boolean): string {
  if (canStart) {
    return READY_DETAIL;
  }
  return isSeated ? WAITING_DETAIL : WATCHING_DETAIL;
}
