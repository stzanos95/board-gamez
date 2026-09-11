import type { ChessSeatChoice } from "@board-gamez/idl/chess/model/table_pb";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import type { ChessSeatView } from "../../chess/seat_views";
import { ChessSeatRow } from "./ChessSeatRow";

const PANEL_SX = { p: 3, border: 1, borderColor: "divider" } as const;

const READY_DETAIL = "Both sides are taken.";
const WAITING_DETAIL = "The game begins once both sides are taken.";
const WATCHING_DETAIL = "Take a side to play, or stay and watch.";

export type PreGamePanelProps = {
  readonly seats: readonly ChessSeatView[];
  readonly canStart: boolean;
  readonly isSeated: boolean;
  readonly isStarting: boolean;
  readonly busyChoice: ChessSeatChoice | null;
  readonly onTakeSeat: (choice: ChessSeatChoice) => void;
  readonly onStart: () => void;
};

/**
 * The table before its game has begun: who plays which side, the sides still
 * on offer, and the button that begins the game once both are taken.
 */
export const PreGamePanel = memo(function PreGamePanel(props: PreGamePanelProps): ReactElement {
  const { seats, canStart, isSeated, isStarting, busyChoice, onTakeSeat, onStart } = props;

  const rows = seats.map((seat: ChessSeatView) => (
    <ChessSeatRow
      key={seat.number}
      colorLabel={seat.colorLabel}
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
