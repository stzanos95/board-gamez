import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { CARTOON_STROKE_WIDTH } from "../piece_stroke";
import { CartoonFace } from "./CartoonFace";

export const CartoonPawn = memo(function CartoonPawn(props: PieceShapeProps): ReactElement {
  const { body, outline, accent } = props;

  return (
    <g fill={body} stroke={outline} strokeWidth={CARTOON_STROKE_WIDTH} strokeLinejoin="round">
      <path d="M26 92 C26 70 36 62 50 62 C64 62 74 70 74 92 Z" />
      <circle cx="50" cy="40" r="26" />
      <CartoonFace centerX={50} eyeY={38} outline={outline} accent={accent} />
    </g>
  );
});
