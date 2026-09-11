import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

const DOT_SX = {
  position: "absolute",
  top: "36%",
  left: "36%",
  width: "28%",
  height: "28%",
  borderRadius: "50%",
  pointerEvents: "none",
} as const;

const RING_SX = {
  position: "absolute",
  inset: "6%",
  borderRadius: "50%",
  borderStyle: "solid",
  borderWidth: "0.35em",
  pointerEvents: "none",
} as const;

export type TargetMarkerProps = {
  readonly isCapture: boolean;
  readonly color: string;
};

/**
 * The mark on a square the picked-up piece may move to: a dot on an empty
 * destination, a ring around one where a piece is taken.
 */
export const TargetMarker = memo(function TargetMarker(props: TargetMarkerProps): ReactElement {
  const { isCapture, color } = props;

  const sx = useMemo(
    () => (isCapture ? { ...RING_SX, borderColor: color } : { ...DOT_SX, bgcolor: color }),
    [isCapture, color],
  );

  return <Box sx={sx} />;
});
