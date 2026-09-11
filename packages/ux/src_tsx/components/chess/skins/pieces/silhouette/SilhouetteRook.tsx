import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { SILHOUETTE_STROKE_WIDTH } from "../piece_stroke";

export const SilhouetteRook = memo(function SilhouetteRook(props: PieceShapeProps): ReactElement {
  const { body, outline } = props;

  return (
    <g
      fill={body}
      stroke={outline}
      strokeWidth={SILHOUETTE_STROKE_WIDTH}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      <path d="M26 16 H38 V26 H45 V16 H55 V26 H62 V16 H74 V36 L68 42 V72 L74 78 H26 L32 72 V42 L26 36 Z" />
      <path d="M32 42 H68" fill="none" />
      <path d="M32 72 H68" fill="none" />
      <rect x="22" y="78" width="56" height="12" rx="2" />
    </g>
  );
});
