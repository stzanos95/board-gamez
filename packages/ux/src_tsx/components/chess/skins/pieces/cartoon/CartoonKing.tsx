import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { CARTOON_STROKE_WIDTH } from "../piece_stroke";
import { CartoonFace } from "./CartoonFace";

export const CartoonKing = memo(function CartoonKing(props: PieceShapeProps): ReactElement {
  const { body, outline, accent } = props;

  return (
    <g fill={body} stroke={outline} strokeWidth={CARTOON_STROKE_WIDTH} strokeLinejoin="round">
      <circle cx="50" cy="60" r="30" />
      <path d="M26 40 V22 L38 30 L50 18 L62 30 L74 22 V40 Z" />
      <path d="M46 4 H54 V10 H60 V16 H54 V22 H46 V16 H40 V10 H46 Z" fill={accent} />
      <CartoonFace centerX={50} eyeY={56} outline={outline} accent={accent} />
    </g>
  );
});
