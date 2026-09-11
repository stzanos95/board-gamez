import type { Color, PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import type { ComponentType, ReactNode } from "react";

/**
 * What a chess board looks like, and the only source of a colour on it.
 *
 * A skin is a palette and three kinds of part: a shape for each piece, the
 * ground of a square, and the frame around the sixty-four squares. The board
 * composes them and never names a colour or a shape itself, so a new look is
 * a new skin and nothing else changes.
 */

/**
 * The three colours one side's pieces are drawn in. `accent` is the detail
 * colour: a cross, a jewel, the white of an eye.
 */
export type SidePalette = {
  readonly body: string;
  readonly outline: string;
  readonly accent: string;
};

/**
 * The colours of the board itself. The overlays carry their own opacity,
 * because each is painted over a square that keeps its own colour.
 */
export type BoardSkinPalette = {
  readonly lightSquare: string;
  readonly darkSquare: string;
  readonly selectedOverlay: string;
  readonly lastMoveOverlay: string;
  readonly checkOverlay: string;
  readonly targetMarker: string;
  readonly frame: string;
  readonly frameEdge: string;
  readonly coordinate: string;
};

/**
 * A piece drawn as SVG content inside PIECE_VIEW_BOX. A shape draws itself in
 * the three colours it is handed and knows nothing about which side it is on.
 */
export type PieceShapeProps = SidePalette;

export type PieceShape = ComponentType<PieceShapeProps>;

export const PIECE_VIEW_BOX = "0 0 100 100";

/**
 * The ground of one square: its colour, the overlays that mark it, and the
 * piece it carries as `children`.
 */
export type SquareGroundProps = {
  readonly isLight: boolean;
  readonly isSelected: boolean;
  readonly isLegalTarget: boolean;
  readonly isCaptureTarget: boolean;
  readonly isLastMove: boolean;
  readonly isCheckedKing: boolean;
  readonly children: ReactNode;
};

/**
 * The frame around the squares. The labels are in the order the squares are
 * drawn: files left to right along the bottom, ranks top to bottom down the
 * side.
 */
export type BoardFrameProps = {
  readonly fileLetters: readonly string[];
  readonly rankDigits: readonly string[];
  readonly children: ReactNode;
};

export type BoardSkin = {
  readonly label: string;
  readonly palette: BoardSkinPalette;
  readonly sides: Record<Color, SidePalette>;
  readonly pieces: Record<PieceType, PieceShape>;
  readonly Square: ComponentType<SquareGroundProps>;
  readonly Board: ComponentType<BoardFrameProps>;
};
