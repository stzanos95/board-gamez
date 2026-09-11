import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "../piece_stroke";

export const SilhouetteQueen = memo(function SilhouetteQueen(props: PieceShapeProps): ReactElement {
  const { body, outline } = props;

  return (
    <g
      fill={body}
      stroke={outline}
      strokeWidth={SILHOUETTE_STROKE_WIDTH}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      <path d="M28 78 H72 L66 64 H34 Z" />
      <path d="M26 46 L30 20 L42 36 L50 14 L58 36 L70 20 L74 46 L66 64 H34 Z" />
      <path d="M31 54 H69" fill="none" />
      <circle cx="30" cy="17" r="4" />
      <circle cx="50" cy="11" r="4" />
      <circle cx="70" cy="17" r="4" />
      <rect x="22" y="78" width="56" height="12" rx="2" />
    </g>
  );
});
