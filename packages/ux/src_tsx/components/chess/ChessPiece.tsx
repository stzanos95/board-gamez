import type { Color, PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import { memo, type ReactElement } from "react";

import { PIECE_VIEW_BOX } from "./skins/board_skin";
import { useBoardSkin } from "./skins/board_skin_context";

export type ChessPieceProps = {
  readonly color: Color;
  readonly pieceType: PieceType;
};

/**
 * One piece, drawn by the selected skin in its side's colours. It fills
 * whatever box it is placed in.
 */
export const ChessPiece = memo(function ChessPiece(props: ChessPieceProps): ReactElement {
  const { color, pieceType } = props;
  const { skin } = useBoardSkin();
  const Shape = skin.pieces[pieceType];
  const side = skin.sides[color];

  return (
    <svg viewBox={PIECE_VIEW_BOX} width="100%" height="100%" aria-hidden="true">
      <Shape body={side.body} outline={side.outline} accent={side.accent} />
    </svg>
  );
});
