import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

import type { BoardFrameProps } from "../board_skin";
import { useBoardSkin } from "../board_skin_context";
import { CoordinateLabels } from "./CoordinateLabels";
import { FRAME_GRID_SX } from "./frame_layout";

const GRAIN_SHADE = "rgba(0, 0, 0, 0.10)";
const GRAIN_IMAGE = `repeating-linear-gradient(0deg, ${GRAIN_SHADE} 0px, ${GRAIN_SHADE} 1px, transparent 1px, transparent 6px)`;

const BAND_SX = {
  p: 1.5,
  borderRadius: 1.5,
  borderWidth: 2,
  borderStyle: "solid",
  boxShadow: "0 0.5em 1.5em rgba(0, 0, 0, 0.35)",
} as const;

/**
 * A thick wooden rim, grained along its length.
 */
export const WoodBoardFrame = memo(function WoodBoardFrame(props: BoardFrameProps): ReactElement {
  const { fileLetters, rankDigits, children } = props;
  const { skin } = useBoardSkin();
  const { palette } = skin;

  const bandSx = useMemo(
    () => ({
      ...BAND_SX,
      backgroundColor: palette.frame,
      backgroundImage: `linear-gradient(135deg, ${palette.frame}, ${palette.frameEdge}), ${GRAIN_IMAGE}`,
      backgroundBlendMode: "multiply",
      borderColor: palette.frameEdge,
    }),
    [palette.frame, palette.frameEdge],
  );

  const rankLabels = <CoordinateLabels axis="ranks" labels={rankDigits} color={palette.coordinate} />;
  const fileLabels = <CoordinateLabels axis="files" labels={fileLetters} color={palette.coordinate} />;

  return (
    <Box sx={bandSx}>
      <Box sx={FRAME_GRID_SX}>
        {rankLabels}
        {children}
        <Box />
        {fileLabels}
      </Box>
    </Box>
  );
});
