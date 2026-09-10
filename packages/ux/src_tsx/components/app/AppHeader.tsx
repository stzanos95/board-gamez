import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import { PlayerChip } from "./PlayerChip";

const HEADER_SX = {
  py: 2,
  mb: 3,
  borderBottom: 1,
  borderColor: "divider",
} as const;

export type AppHeaderProps = {
  readonly displayName: string;
  readonly shortId: string;
  readonly onRename: (displayName: string) => void;
};

export const AppHeader = memo(function AppHeader(props: AppHeaderProps): ReactElement {
  const { displayName, shortId, onRename } = props;

  const title = (
    <Stack>
      <Typography variant="h2">board-gamez</Typography>
      <Typography variant="caption" color="text.secondary">
        Every browser tab is a different player
      </Typography>
    </Stack>
  );

  return (
    <Box sx={HEADER_SX}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        {title}
        <PlayerChip displayName={displayName} shortId={shortId} onRename={onRename} />
      </Stack>
    </Box>
  );
});
