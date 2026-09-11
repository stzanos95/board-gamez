import Stack from "@mui/material/Stack";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type MouseEvent, type ReactElement } from "react";

import { useBoardSkin } from "./skins/board_skin_context";
import { BOARD_SKIN_NAMES, isBoardSkinName, type BoardSkinName } from "./skins/board_skin_name";
import { BOARD_SKINS_BY_NAME } from "./skins/board_skin_registry";

/**
 * Which skin the board is drawn in. The choice is this browser's and changes
 * nothing about the game.
 */
export const BoardSkinPicker = memo(function BoardSkinPicker(): ReactElement {
  const { name, select } = useBoardSkin();

  const handleChange = useCallback(
    (_event: MouseEvent<HTMLElement>, next: unknown) => {
      if (typeof next === "string" && isBoardSkinName(next)) {
        select(next);
      }
    },
    [select],
  );

  const options = BOARD_SKIN_NAMES.map((option: BoardSkinName) => (
    <ToggleButton key={option} value={option}>
      {BOARD_SKINS_BY_NAME[option].label}
    </ToggleButton>
  ));

  return (
    <Stack spacing={0.5}>
      <Typography variant="caption" color="text.secondary">
        Board skin
      </Typography>
      <ToggleButtonGroup value={name} exclusive size="small" onChange={handleChange} fullWidth>
        {options}
      </ToggleButtonGroup>
    </Stack>
  );
});
