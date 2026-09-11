import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

import type { SquareGroundProps } from "../board_skin";
import { useBoardSkin } from "../board_skin_context";
import { GROUND_SX, OVERLAY_SX, PIECE_SLOT_SX } from "./ground_layout";
import { overlayColorOf } from "./overlay_color";
import { TargetMarker } from "./TargetMarker";

/**
 * A square of one flat colour.
 */
export const FlatSquareGround = memo(function FlatSquareGround(
  props: SquareGroundProps,
): ReactElement {
  const { isLight, isLegalTarget, isCaptureTarget, children } = props;
  const { skin } = useBoardSkin();
  const { palette } = skin;

  const groundColor = isLight ? palette.lightSquare : palette.darkSquare;
  const groundSx = useMemo(() => ({ ...GROUND_SX, bgcolor: groundColor }), [groundColor]);

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
