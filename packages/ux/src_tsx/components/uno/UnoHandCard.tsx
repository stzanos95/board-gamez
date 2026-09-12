import ButtonBase from "@mui/material/ButtonBase";
import { memo, useCallback, type ReactElement } from "react";

import type { CardView } from "../../uno/uno_views";
import { UnoCard } from "./UnoCard";

const BUTTON_SX = { borderRadius: 2, transition: "transform 120ms" } as const;
const PLAYABLE_SX = {
  ...BUTTON_SX,
  cursor: "pointer",
  "&:hover": { transform: "translateY(-8px)" },
} as const;

export type UnoHandCardProps = {
  readonly index: number;
  readonly view: CardView;
  readonly isPlayable: boolean;
  readonly isBusy: boolean;
  readonly onPlay: (index: number) => void;
};

/**
 * One card in the viewer's hand. Clicking a playable card reports its place
 * in the hand; a card the game marked unplayable does nothing.
 */
export const UnoHandCard = memo(function UnoHandCard(props: UnoHandCardProps): ReactElement {
  const { index, view, isPlayable, isBusy, onPlay } = props;

  const handleClick = useCallback(() => onPlay(index), [onPlay, index]);

  return (
    <ButtonBase
      onClick={handleClick}
      disabled={!isPlayable || isBusy}
      aria-label={isPlayable ? `Play ${view.label}` : view.label}
      sx={isPlayable ? PLAYABLE_SX : BUTTON_SX}
    >
      <UnoCard
        color={view.color}
        glyph={view.glyph}
        label={view.label}
        isWild={view.isWild}
        isDimmed={!isPlayable}
      />
    </ButtonBase>
  );
});
