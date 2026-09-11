import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

const ROW_SX = {
  display: "grid",
  gridTemplateColumns: "repeat(8, 1fr)",
  justifyItems: "center",
  alignItems: "center",
  minHeight: "1.4em",
} as const;

const COLUMN_SX = {
  display: "grid",
  gridTemplateRows: "repeat(8, 1fr)",
  justifyItems: "center",
  alignItems: "center",
  minWidth: "1.4em",
} as const;

const LABEL_SX = {
  fontSize: "0.72rem",
  fontWeight: 700,
  lineHeight: 1,
  userSelect: "none",
} as const;

type CoordinateAxis = "files" | "ranks";

export type CoordinateLabelsProps = {
  readonly axis: CoordinateAxis;
  readonly labels: readonly string[];
  readonly color: string;
};

const AXIS_SX: Record<CoordinateAxis, typeof ROW_SX | typeof COLUMN_SX> = {
  files: ROW_SX,
  ranks: COLUMN_SX,
};

/**
 * The eight labels along one edge of the board, spaced to the squares.
 */
export const CoordinateLabels = memo(function CoordinateLabels(
  props: CoordinateLabelsProps,
): ReactElement {
  const { axis, labels, color } = props;

  const labelSx = useMemo(() => ({ ...LABEL_SX, color }), [color]);

  const cells = labels.map((label: string) => (
    <Box key={label} component="span" sx={labelSx}>
      {label}
    </Box>
  ));

  return <Box sx={AXIS_SX[axis]}>{cells}</Box>;
});
