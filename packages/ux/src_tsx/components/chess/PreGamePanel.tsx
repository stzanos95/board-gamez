import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

const PANEL_SX = { p: 3, border: 1, borderColor: "divider" } as const;

const READY_DETAIL = "Both seats are taken. Seat 1 plays White and seat 2 plays Black.";
const WAITING_DETAIL = "The game begins once every seat is taken.";
const WATCHING_DETAIL = "Take a seat to play, or stay and watch.";

export type PreGamePanelProps = {
  readonly canStart: boolean;
  readonly isSeated: boolean;
  readonly isStarting: boolean;
  readonly onStart: () => void;
};

/**
 * The table before its game has begun: what is still needed, or the button
 * that begins it.
 */
export const PreGamePanel = memo(function PreGamePanel(props: PreGamePanelProps): ReactElement {
  const { canStart, isSeated, isStarting, onStart } = props;

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
