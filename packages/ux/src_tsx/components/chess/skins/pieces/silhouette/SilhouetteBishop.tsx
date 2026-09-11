import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "../piece_stroke";

export const SilhouetteBishop = memo(function SilhouetteBishop(
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
      <path d="M30 78 H70 L64 64 H36 Z" />
      <path d="M50 20 C66 32 70 48 60 64 H40 C30 48 34 32 50 20 Z" />
      <path d="M57 34 L45 50" fill="none" />
      <circle cx="50" cy="14" r="5" />
      <rect x="22" y="78" width="56" height="12" rx="2" />
    </g>
  );
});
