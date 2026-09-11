import Box from "@mui/material/Box";
import { memo, useMemo, type ReactElement } from "react";

import type { BoardFrameProps } from "../board_skin";
import { useBoardSkin } from "../board_skin_context";
import { CoordinateLabels } from "./CoordinateLabels";
import { FRAME_GRID_SX } from "./frame_layout";

const BAND_SX = {
  p: 1,
  borderRadius: 1,
  borderWidth: 1,
  borderStyle: "solid",
} as const;

/**
 * A plain band around the squares.
 */
export const BandBoardFrame = memo(function BandBoardFrame(props: BoardFrameProps): ReactElement {
  const { fileLetters, rankDigits, children } = props;
  const { skin } = useBoardSkin();
  const { palette } = skin;

  const bandSx = useMemo(
    () => ({ ...BAND_SX, bgcolor: palette.frame, borderColor: palette.frameEdge }),
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
