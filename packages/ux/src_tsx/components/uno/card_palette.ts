import { CardColor } from "@board-gamez/idl/uno/model/card_pb";

/**
 * The colours a UNO card is printed in.
 *
 * A card's colour is the game's own and not the theme's, so this is the one
 * place under `components/uno` that writes one. Every card reads from here.
 */
export type CardPalette = {
  readonly face: string;
  readonly ink: string;
};

export const CARD_PALETTES_BY_COLOR: Record<CardColor, CardPalette> = {
  [CardColor.UNSPECIFIED]: { face: "#1f1f1f", ink: "#ffffff" },
  [CardColor.RED]: { face: "#d7263d", ink: "#ffffff" },
  [CardColor.YELLOW]: { face: "#f4c20d", ink: "#1f1f1f" },
  [CardColor.GREEN]: { face: "#2a9d4b", ink: "#ffffff" },
  [CardColor.BLUE]: { face: "#1e63c8", ink: "#ffffff" },
};

/**
 * The four colours a wild shows, in the order they are painted round it.
 */
export const WILD_QUADRANT_COLORS: readonly CardColor[] = [
  CardColor.RED,
  CardColor.BLUE,
  CardColor.GREEN,
  CardColor.YELLOW,
];

export const CARD_BACK_FACE = "#2b2b2b";
export const CARD_BACK_INK = "#e0e0e0";
