import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "../piece_stroke";

export const SilhouettePawn = memo(function SilhouettePawn(props: PieceShapeProps): ReactElement {
  const { body, outline } = props;

  return (
    <g
      fill={body}
      stroke={outline}
      strokeWidth={SILHOUETTE_STROKE_WIDTH}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      <path d="M26 80 H74 L64 66 H36 Z" />
      <path d="M38 46 C42 40 58 40 62 46 L66 66 H34 Z" />
      <circle cx="50" cy="30" r="13" />
      <rect x="22" y="80" width="56" height="10" rx="2" />
    </g>
  );
});
