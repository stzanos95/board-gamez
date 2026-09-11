import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { CARTOON_STROKE_WIDTH } from "../piece_stroke";
import { CartoonFace } from "./CartoonFace";

export const CartoonQueen = memo(function CartoonQueen(props: PieceShapeProps): ReactElement {
  const { body, outline, accent } = props;

  return (
    <g fill={body} stroke={outline} strokeWidth={CARTOON_STROKE_WIDTH} strokeLinejoin="round">
      <circle cx="50" cy="60" r="30" />
      <path d="M26 40 L30 14 L40 28 L50 8 L60 28 L70 14 L74 40 Z" />
      <circle cx="30" cy="12" r="4" fill={accent} />
      <circle cx="50" cy="6" r="4" fill={accent} />
      <circle cx="70" cy="12" r="4" fill={accent} />
      <CartoonFace centerX={50} eyeY={56} outline={outline} accent={accent} />
    </g>
  );
});
