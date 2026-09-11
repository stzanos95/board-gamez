import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

import type { SquareGroundProps } from "../board_skin";
import { useBoardSkin } from "../board_skin_context";
import { GROUND_SX, OVERLAY_SX, PIECE_SLOT_SX } from "./ground_layout";
import { overlayColorOf } from "./overlay_color";
import { TargetMarker } from "./TargetMarker";

/**
 * The gap between tiles shows the frame colour through, and a shade along the
 * bottom edge gives each tile its thickness.
 */
const TILE_SHAPE_SX = {
  position: "absolute",
  inset: "4%",
  borderRadius: "18%",
} as const;

const TILE_SX = {
  ...TILE_SHAPE_SX,
  boxShadow: "inset 0 -0.25em 0 rgba(0, 0, 0, 0.14), inset 0 0.15em 0 rgba(255, 255, 255, 0.35)",
} as const;

/**
 * A square drawn as a rounded tile sitting on the board.
 */
export const TileSquareGround = memo(function TileSquareGround(
  props: SquareGroundProps,
): ReactElement {
  const { isLight, isLegalTarget, isCaptureTarget, children } = props;
  const { skin } = useBoardSkin();
  const { palette } = skin;

  const groundSx = useMemo(() => ({ ...GROUND_SX, bgcolor: palette.frame }), [palette.frame]);

  const tileColor = isLight ? palette.lightSquare : palette.darkSquare;
  const tileSx = useMemo(() => ({ ...TILE_SX, bgcolor: tileColor }), [tileColor]);

  const overlayColor = overlayColorOf(props, palette);
  const overlaySx = useMemo(
    () => (overlayColor === null ? null : { ...OVERLAY_SX, ...TILE_SHAPE_SX, bgcolor: overlayColor }),
    [overlayColor],
  );

  const overlay = overlaySx === null ? null : <Box sx={overlaySx} />;
  const marker = isLegalTarget ? (
    <TargetMarker isCapture={isCaptureTarget} color={palette.targetMarker} />
  ) : null;

  return (
    <Box sx={groundSx}>
      <Box sx={tileSx} />
      {overlay}
      <Box sx={PIECE_SLOT_SX}>{children}</Box>
      {marker}
    </Box>
  );
});
