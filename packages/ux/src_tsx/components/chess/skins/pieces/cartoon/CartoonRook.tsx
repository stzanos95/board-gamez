import { memo, type ReactElement } from "react";

import type { PieceShapeProps } from "../../board_skin";
import { CARTOON_STROKE_WIDTH } from "../piece_stroke";
import { CartoonFace } from "./CartoonFace";

export const CartoonRook = memo(function CartoonRook(props: PieceShapeProps): ReactElement {
  const { body, outline, accent } = props;

  return (
    <g fill={body} stroke={outline} strokeWidth={CARTOON_STROKE_WIDTH} strokeLinejoin="round">
      <rect x="24" y="30" width="52" height="62" rx="12" />
      <rect x="24" y="10" width="14" height="24" rx="5" />
      <rect x="43" y="10" width="14" height="24" rx="5" />
      <rect x="62" y="10" width="14" height="24" rx="5" />
      <path d="M32 72 H68" fill="none" strokeLinecap="round" />
      <CartoonFace centerX={50} eyeY={50} outline={outline} accent={accent} />
    </g>
  );
});
