import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

const BANNER_SX = { p: 2, border: 1, borderColor: "divider" } as const;
const ACTIVE_BANNER_SX = { ...BANNER_SX, borderColor: "primary.main" } as const;

export type GameStatusBannerProps = {
  readonly viewerLabel: string;
  readonly headline: string;
  readonly detail: string | null;
  readonly canAct: boolean;
  readonly isOver: boolean;
};

/**
 * Whose move it is, and how the game stands.
 *
 * The banner is outlined in the primary colour while it is this viewer's turn,
 * which is what tells a player their turn has come.
 */
export const GameStatusBanner = memo(function GameStatusBanner(
  props: GameStatusBannerProps,
): ReactElement {
  const { viewerLabel, headline, detail, canAct, isOver } = props;

  const detailChip = detail === null ? null : <Chip label={detail} color="warning" />;

  const headlineText = (
    <Typography variant="h3" color={headlineColorOf(canAct, isOver)}>
      {headline}
    </Typography>
  );

  return (
    <Paper sx={canAct ? ACTIVE_BANNER_SX : BANNER_SX}>
      <Stack spacing={0.5}>
        <Typography variant="caption" color="text.secondary">
          {viewerLabel}
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center">
          {headlineText}
          {detailChip}
        </Stack>
      </Stack>
    </Paper>
  );
});

function headlineColorOf(canAct: boolean, isOver: boolean): string {
  if (isOver) {
    return "text.primary";
  }
  return canAct ? "primary" : "text.secondary";
}
