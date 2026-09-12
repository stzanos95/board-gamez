import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import type { PlayerView } from "../../uno/uno_views";
import { UnoPlayerRow } from "./UnoPlayerRow";

const PANEL_SX = { p: 2, border: 1, borderColor: "divider" } as const;

export type UnoPlayerListProps = {
  readonly players: readonly PlayerView[];
};

/**
 * Everyone in the game, in turn order.
 */
export const UnoPlayerList = memo(function UnoPlayerList(props: UnoPlayerListProps): ReactElement {
  const { players } = props;

  const rows = players.map((player: PlayerView) => (
    <UnoPlayerRow
      key={player.participant}
      label={player.label}
      cardCount={player.cardCount}
      isYou={player.isYou}
      isToAct={player.isToAct}
      hasWithdrawn={player.hasWithdrawn}
    />
  ));

  return (
    <Paper sx={PANEL_SX}>
      <Stack spacing={0.5}>
        <Typography variant="caption" color="text.secondary">
          Players
        </Typography>
        {rows}
      </Stack>
    </Paper>
  );
});
