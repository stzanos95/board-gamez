import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "./piece_stroke";

/**
 * A piece of a kind this build does not know, which a newer schema can send.
 */
export const UnknownPiece = memo(function UnknownPiece(props: PieceShapeProps): ReactElement {
  const { body, outline } = props;

  return (
    <g fill={body} stroke={outline} strokeWidth={SILHOUETTE_STROKE_WIDTH} strokeLinejoin="round">
      <circle cx="50" cy="50" r="30" />
      <text
        x="50"
        y="62"
        textAnchor="middle"
        fontSize="36"
        fontWeight="700"
        fill={outline}
        stroke="none"
      >
        ?
      </text>
    </g>
  );
});
