import type { CardColor } from "@board-gamez/idl/uno/model/card_pb";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import type { CardView } from "../../uno/uno_views";
import { CARD_BACK_FACE, CARD_BACK_INK, CARD_PALETTES_BY_COLOR } from "./card_palette";
import { UnoCard } from "./UnoCard";

const PILE_WIDTH = 64;
const PILE_HEIGHT = 96;

const CENTER_SX = { p: 3, border: 1, borderColor: "divider", borderRadius: 1 } as const;

const DRAW_PILE_SX = {
  width: PILE_WIDTH,
  height: PILE_HEIGHT,
  borderRadius: 2,
  bgcolor: CARD_BACK_FACE,
  color: CARD_BACK_INK,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  boxShadow: 1,
  flexShrink: 0,
} as const;

export type UnoTableCenterProps = {
  readonly topCard: CardView | null;
  readonly activeColor: CardColor;
  readonly activeColorLabel: string;
  readonly directionGlyph: string;
  readonly drawPileCount: number;
  readonly mayDraw: boolean;
  readonly mayPass: boolean;
  readonly isBusy: boolean;
  readonly onDraw: () => void;
  readonly onPass: () => void;
};

/**
 * The middle of the table: the discard pile's top card, the colour in play,
 * the direction, and the draw pile with the two things a turn may do
 * besides playing a card.
 */
export const UnoTableCenter = memo(function UnoTableCenter(
  props: UnoTableCenterProps,
): ReactElement {
  const {
    topCard,
    activeColor,
    activeColorLabel,
    directionGlyph,
    drawPileCount,
    mayDraw,
    mayPass,
    isBusy,
    onDraw,
    onPass,
  } = props;

  const discard =
    topCard === null ? null : (
      <UnoCard
        color={topCard.color}
        glyph={topCard.glyph}
        label={`Top of the discard pile: ${topCard.label}`}
        isWild={topCard.isWild}
        isDimmed={false}
      />
    );

  const drawPile = (
    <Box sx={DRAW_PILE_SX} role="img" aria-label={`Draw pile, ${drawPileCount} cards`}>
      <Typography variant="h3" component="span">
        {drawPileCount}
      </Typography>
    </Box>
  );

  const colorChip = (
    <Chip
      label={`${activeColorLabel} in play ${directionGlyph}`}
      sx={{
        bgcolor: CARD_PALETTES_BY_COLOR[activeColor].face,
        color: CARD_PALETTES_BY_COLOR[activeColor].ink,
        fontWeight: 700,
      }}
    />
  );

  const drawButton = mayDraw ? (
    <Button variant="contained" onClick={onDraw} disabled={isBusy}>
      Draw a card
    </Button>
  ) : null;

  const passButton = mayPass ? (
    <Button variant="outlined" onClick={onPass} disabled={isBusy}>
      Pass
    </Button>
  ) : null;

  return (
    <Stack sx={CENTER_SX} spacing={2} alignItems="center">
      <Stack direction="row" spacing={3} alignItems="center">
        {drawPile}
        {discard}
      </Stack>
      {colorChip}
      <Stack direction="row" spacing={1}>
        {drawButton}
        {passButton}
      </Stack>
    </Stack>
  );
});
