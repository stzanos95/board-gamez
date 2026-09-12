import type { CardColor } from "@board-gamez/idl/uno/model/card_pb";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import { CARD_PALETTES_BY_COLOR, WILD_QUADRANT_COLORS } from "./card_palette";

const CARD_WIDTH = 64;
const CARD_HEIGHT = 96;
const CORNER_RADIUS = 8;
const FRAME_WIDTH = 3;
const GLYPH_FONT_SIZE = 26;

const FRAME_SX = {
  width: CARD_WIDTH,
  height: CARD_HEIGHT,
  borderRadius: `${CORNER_RADIUS}px`,
  border: `${FRAME_WIDTH}px solid`,
  borderColor: "background.paper",
  boxShadow: 1,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  position: "relative",
  overflow: "hidden",
  flexShrink: 0,
  userSelect: "none",
} as const;

const QUADRANT_SX = { position: "absolute", width: "50%", height: "50%" } as const;

const GLYPH_SX = {
  fontSize: GLYPH_FONT_SIZE,
  fontWeight: 800,
  lineHeight: 1,
  position: "relative",
  textShadow: "0 1px 2px rgba(0, 0, 0, 0.35)",
} as const;

export type UnoCardProps = {
  readonly color: CardColor;
  readonly glyph: string;
  readonly label: string;
  readonly isWild: boolean;
  readonly isDimmed: boolean;
};

/**
 * One card face.
 *
 * A coloured card is its colour with the glyph on it. A wild is painted in
 * four quadrants, and its glyph sits over them. Dimmed is how a card the
 * viewer may not play is told apart from one they may.
 */
export const UnoCard = memo(function UnoCard(props: UnoCardProps): ReactElement {
  const { color, glyph, label, isWild, isDimmed } = props;
  const palette = CARD_PALETTES_BY_COLOR[color];

  const quadrants = isWild ? WILD_QUADRANT_COLORS.map(toQuadrant) : null;

  const glyphText = (
    <Typography component="span" sx={{ ...GLYPH_SX, color: palette.ink }}>
      {glyph}
    </Typography>
  );

  return (
    <Box
      role="img"
      aria-label={label}
      sx={{ ...FRAME_SX, bgcolor: palette.face, opacity: isDimmed ? 0.45 : 1 }}
    >
      {quadrants}
      {glyphText}
    </Box>
  );
});

function toQuadrant(color: CardColor, index: number): ReactElement {
  const isRight = index % 2 === 1;
  const isBottom = index >= 2;
  return (
    <Box
      key={color}
      sx={{
        ...QUADRANT_SX,
        left: isRight ? "50%" : 0,
        top: isBottom ? "50%" : 0,
        bgcolor: CARD_PALETTES_BY_COLOR[color].face,
      }}
    />
  );
}
