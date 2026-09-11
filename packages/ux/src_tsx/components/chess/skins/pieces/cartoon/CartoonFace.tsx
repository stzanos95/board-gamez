import { memo, type ReactElement } from "react";

import { CARTOON_STROKE_WIDTH } from "../piece_stroke";

const EYE_RADIUS = 6;
const PUPIL_RADIUS = 3;
const PUPIL_OFFSET = 1.2;
const EYE_SPREAD = 10;
const SMILE_DROP = 9;
const SMILE_HALF_WIDTH = 9;

export type CartoonFaceProps = {
  readonly centerX: number;
  readonly eyeY: number;
  readonly outline: string;
  readonly accent: string;
};

/**
 * Two eyes and a smile, centred on a piece. Every cartoon piece wears the same
 * face so the set reads as one family.
 */
export const CartoonFace = memo(function CartoonFace(props: CartoonFaceProps): ReactElement {
  const { centerX, eyeY, outline, accent } = props;
  const leftEyeX = centerX - EYE_SPREAD;
  const rightEyeX = centerX + EYE_SPREAD;
  const smileY = eyeY + 14;
  const smile = `M${centerX - SMILE_HALF_WIDTH} ${smileY} Q${centerX} ${smileY + SMILE_DROP} ${centerX + SMILE_HALF_WIDTH} ${smileY}`;

  return (
    <g stroke={outline} strokeWidth={CARTOON_STROKE_WIDTH * 0.6} strokeLinecap="round">
      <circle cx={leftEyeX} cy={eyeY} r={EYE_RADIUS} fill={accent} />
      <circle cx={rightEyeX} cy={eyeY} r={EYE_RADIUS} fill={accent} />
      <circle cx={leftEyeX + PUPIL_OFFSET} cy={eyeY + PUPIL_OFFSET} r={PUPIL_RADIUS} fill={outline} stroke="none" />
      <circle cx={rightEyeX + PUPIL_OFFSET} cy={eyeY + PUPIL_OFFSET} r={PUPIL_RADIUS} fill={outline} stroke="none" />
      <path d={smile} fill="none" />
    </g>
  );
});
