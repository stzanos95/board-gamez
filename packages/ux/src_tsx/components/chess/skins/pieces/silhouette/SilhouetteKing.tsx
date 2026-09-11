import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "../piece_stroke";

export const SilhouetteKing = memo(function SilhouetteKing(props: PieceShapeProps): ReactElement {
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
      <path d="M46 24 H54 V30 C64 30 72 36 72 48 L66 64 H34 L28 48 C28 36 36 30 46 30 Z" />
      <path d="M46 6 H54 V12 H60 V20 H54 V26 H46 V20 H40 V12 H46 Z" />
      <path d="M31 54 H69" fill="none" />
      <rect x="22" y="78" width="56" height="12" rx="2" />
    </g>
  );
});
