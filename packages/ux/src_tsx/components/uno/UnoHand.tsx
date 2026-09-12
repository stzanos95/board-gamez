import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import type { HandCardView } from "../../uno/uno_views";
import { UnoHandCard } from "./UnoHandCard";

const HAND_SX = { flexWrap: "wrap", gap: 1, pt: 1 } as const;

export type UnoHandProps = {
  readonly hand: readonly HandCardView[];
  readonly isBusy: boolean;
  readonly onPlay: (index: number) => void;
};

/**
 * The viewer's cards, in the order the game holds them.
 */
export const UnoHand = memo(function UnoHand(props: UnoHandProps): ReactElement {
  const { hand, isBusy, onPlay } = props;

  const cards = hand.map((shown: HandCardView) => (
    <UnoHandCard
      key={shown.index}
      index={shown.index}
      view={shown.view}
      isPlayable={shown.isPlayable}
      isBusy={isBusy}
      onPlay={onPlay}
    />
  ));

  const empty =
    hand.length === 0 ? (
      <Typography variant="body2" color="text.secondary">
        No cards in hand.
      </Typography>
    ) : null;

  return (
    <Stack spacing={1}>
      <Typography variant="caption" color="text.secondary">
        Your hand · {hand.length}
      </Typography>
      <Stack direction="row" sx={HAND_SX}>
        {cards}
      </Stack>
      {empty}
    </Stack>
  );
});
