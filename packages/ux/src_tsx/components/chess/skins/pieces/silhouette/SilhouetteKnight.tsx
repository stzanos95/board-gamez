import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "../piece_stroke";

export const SilhouetteKnight = memo(function SilhouetteKnight(
  props: PieceShapeProps,
): ReactElement {
  const { body, outline } = props;

  return (
    <g
      fill={body}
      stroke={outline}
      strokeWidth={SILHOUETTE_STROKE_WIDTH}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      <path d="M30 80 C30 68 36 60 42 54 L34 52 L26 46 C28 34 38 24 48 20 L52 10 L58 20 C68 26 74 40 74 56 L72 70 L74 80 Z" />
      <path d="M60 30 L54 38 M66 40 L60 48 M70 54 L64 60" fill="none" />
      <circle cx="49" cy="30" r="2.5" fill={outline} stroke="none" />
      <circle cx="31" cy="44" r="1.8" fill={outline} stroke="none" />
      <rect x="22" y="80" width="56" height="10" rx="2" />
    </g>
  );
});
