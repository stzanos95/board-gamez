import { CardColor } from "@board-gamez/idl/uno/model/card_pb";
import { memo, type ReactElement } from "react";

import { CARD_PALETTES_BY_COLOR } from "../uno/card_palette";

/**
 * A fan of four cards, one of each colour.
 *
 * Drawn rather than fetched, in the colours the cards are printed in.
 */
const VIEW_WIDTH = 120;
const VIEW_HEIGHT = 80;
const CARD_WIDTH = 34;
const CARD_HEIGHT = 52;
const CORNER = 4;
const FAN_ORIGIN_X = 60;
const FAN_ORIGIN_Y = 90;
const FAN_STEP_DEGREES = 14;
const FAN_START_DEGREES = -21;

type FannedCard = {
  readonly color: CardColor;
  readonly glyph: string;
};

const FANNED_CARDS: readonly FannedCard[] = [
  { color: CardColor.RED, glyph: "7" },
  { color: CardColor.YELLOW, glyph: "⊘" },
  { color: CardColor.GREEN, glyph: "+2" },
  { color: CardColor.BLUE, glyph: "⇄" },
];

function fan(): readonly ReactElement[] {
  return FANNED_CARDS.map((card: FannedCard, index: number) => {
    const angle = FAN_START_DEGREES + index * FAN_STEP_DEGREES;
    const palette = CARD_PALETTES_BY_COLOR[card.color];
    return (
      <g key={card.color} transform={`rotate(${angle} ${FAN_ORIGIN_X} ${FAN_ORIGIN_Y})`}>
        <rect
          x={FAN_ORIGIN_X - CARD_WIDTH / 2}
          y={FAN_ORIGIN_Y - CARD_HEIGHT - 14}
          width={CARD_WIDTH}
          height={CARD_HEIGHT}
          rx={CORNER}
          fill={palette.face}
          stroke={palette.ink}
          strokeWidth={2}
        />
        <text
          x={FAN_ORIGIN_X}
          y={FAN_ORIGIN_Y - CARD_HEIGHT / 2 - 10}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={16}
          fontWeight={800}
          fill={palette.ink}
        >
          {card.glyph}
        </text>
      </g>
    );
  });
}

const FAN = fan();

export const UnoArtwork = memo(function UnoArtwork(): ReactElement {
  return (
    <svg
      viewBox={`0 0 ${VIEW_WIDTH} ${VIEW_HEIGHT}`}
      width="100%"
      role="img"
      aria-label="A fan of four UNO cards"
    >
      {FAN}
    </svg>
  );
});
