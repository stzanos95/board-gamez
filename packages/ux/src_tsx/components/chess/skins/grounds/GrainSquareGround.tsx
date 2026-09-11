import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

import type { SquareGroundProps } from "../board_skin";
import { useBoardSkin } from "../board_skin_context";
import { GROUND_SX, OVERLAY_SX, PIECE_SLOT_SX } from "./ground_layout";
import { overlayColorOf } from "./overlay_color";
import { TargetMarker } from "./TargetMarker";

/**
 * The stripes of grain laid over the square's colour: a shade, not a colour,
 * so the same grain sits on both the light and the dark wood.
 */
const GRAIN_SHADE = "rgba(40, 20, 0, 0.07)";
const GRAIN_HIGHLIGHT = "rgba(255, 245, 220, 0.10)";
const GRAIN_IMAGE = `repeating-linear-gradient(97deg, ${GRAIN_SHADE} 0px, ${GRAIN_SHADE} 2px, transparent 2px, transparent 7px, ${GRAIN_HIGHLIGHT} 7px, ${GRAIN_HIGHLIGHT} 9px, transparent 9px, transparent 16px)`;

/**
 * A square of wood, with the grain running across it.
 */
export const GrainSquareGround = memo(function GrainSquareGround(
  props: SquareGroundProps,
): ReactElement {
  const { isLight, isLegalTarget, isCaptureTarget, children } = props;
  const { skin } = useBoardSkin();
  const { palette } = skin;

  const groundColor = isLight ? palette.lightSquare : palette.darkSquare;
  const groundSx = useMemo(
    () => ({ ...GROUND_SX, bgcolor: groundColor, backgroundImage: GRAIN_IMAGE }),
    [groundColor],
  );

  const overlayColor = overlayColorOf(props, palette);
  const overlaySx = useMemo(
    () => (overlayColor === null ? null : { ...OVERLAY_SX, bgcolor: overlayColor }),
    [overlayColor],
  );

  const overlay = overlaySx === null ? null : <Box sx={overlaySx} />;
  const marker = isLegalTarget ? (
    <TargetMarker isCapture={isCaptureTarget} color={palette.targetMarker} />
  ) : null;

  return (
    <Box sx={groundSx}>
      {overlay}
      <Box sx={PIECE_SLOT_SX}>{children}</Box>
      {marker}
    </Box>
  );
});
