import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { CARTOON_STROKE_WIDTH } from "../piece_stroke";
import { CartoonFace } from "./CartoonFace";

export const CartoonBishop = memo(function CartoonBishop(props: PieceShapeProps): ReactElement {
  const { body, outline, accent } = props;

  return (
    <g fill={body} stroke={outline} strokeWidth={CARTOON_STROKE_WIDTH} strokeLinejoin="round">
      <ellipse cx="50" cy="58" rx="26" ry="34" />
      <path d="M40 30 C44 24 56 24 60 30 L50 10 Z" />
      <circle cx="50" cy="9" r="5" fill={accent} />
      <CartoonFace centerX={50} eyeY={52} outline={outline} accent={accent} />
    </g>
  );
});
