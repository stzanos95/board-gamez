import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

const BANNER_SX = { p: 2, border: 1, borderColor: "divider" } as const;
const ACTIVE_BANNER_SX = { ...BANNER_SX, borderColor: "primary.main" } as const;

export type UnoStatusBannerProps = {
  readonly viewerLabel: string;
  readonly headline: string;
  readonly detail: string | null;
  readonly canAct: boolean;
  readonly isOver: boolean;
};

/**
 * Whose turn it is, and how the game stands.
 *
 * The banner is outlined in the primary colour while it is this viewer's turn,
 * which is what tells a player their turn has come.
 */
export const UnoStatusBanner = memo(function UnoStatusBanner(
  props: UnoStatusBannerProps,
): ReactElement {
  const { viewerLabel, headline, detail, canAct, isOver } = props;

  const detailText =
    detail === null ? null : (
      <Typography variant="body2" color="text.secondary">
        {detail}
      </Typography>
    );

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
        {headlineText}
        {detailText}
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
