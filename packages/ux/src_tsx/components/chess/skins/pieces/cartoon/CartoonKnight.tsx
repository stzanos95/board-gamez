import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { CARTOON_STROKE_WIDTH } from "../piece_stroke";

const EYE_RADIUS = 8;
const PUPIL_RADIUS = 4;

/**
 * A horse's head, facing the viewer's left, with one large eye. The shared
 * face does not fit a profile, so this piece draws its own.
 */
export const CartoonKnight = memo(function CartoonKnight(props: PieceShapeProps): ReactElement {
  const { body, outline, accent } = props;

  return (
    <g
      fill={body}
      stroke={outline}
      strokeWidth={CARTOON_STROKE_WIDTH}
      strokeLinejoin="round"
      strokeLinecap="round"
    >
      <path d="M70 28 C84 30 86 46 72 46 Z" />
      <path d="M72 46 C86 48 88 66 74 66 Z" />
      <path d="M30 92 L30 72 C30 62 24 58 20 50 C16 40 24 30 38 30 C42 20 52 12 62 14 C72 16 76 28 74 40 C76 58 72 76 72 92 Z" />
      <path d="M50 20 L54 2 L66 16 Z" />
      <circle cx="54" cy="38" r={EYE_RADIUS} fill={accent} />
      <circle cx="55" cy="39" r={PUPIL_RADIUS} fill={outline} stroke="none" />
      <circle cx="28" cy="46" r="2.5" fill={outline} stroke="none" />
      <path d="M28 58 Q36 64 44 58" fill="none" />
    </g>
  );
});
