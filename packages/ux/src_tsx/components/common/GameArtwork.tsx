import { GameType } from "@board-gamez/idl/lobby/model/game_type_pb";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { memo, type ComponentType, type ReactElement } from "react";

import { GAME_TYPE_LABELS } from "../../lobby/table_labels";
import { ChessArtwork } from "./ChessArtwork";

const FRAME_SX = {
  p: 2,
  border: 1,
  borderColor: "divider",
  borderRadius: 1,
  bgcolor: "background.paper",
  color: "text.primary",
} as const;

const CAPTION_SX = { mt: 1, display: "block", textAlign: "center" } as const;

const UnknownGameArtwork = memo(function UnknownGameArtwork(): ReactElement {
  return (
    <Typography variant="body2" color="text.secondary" align="center">
      No picture for this game yet.
    </Typography>
  );
});

/**
 * What each game looks like.
 *
 * Keyed by the enum, so a game added to the schema does not compile until it has
 * been given a picture.
 */
const ARTWORK_BY_GAME_TYPE: Record<GameType, ComponentType> = {
  [GameType.UNSPECIFIED]: UnknownGameArtwork,
  [GameType.CHESS]: ChessArtwork,
};

export type GameArtworkProps = {
  readonly gameType: GameType;
};

export const GameArtwork = memo(function GameArtwork(props: GameArtworkProps): ReactElement {
  const { gameType } = props;
  const Artwork = ARTWORK_BY_GAME_TYPE[gameType];

  return (
    <Box sx={FRAME_SX}>
      <Artwork />
      <Typography variant="caption" color="text.secondary" sx={CAPTION_SX}>
        {GAME_TYPE_LABELS[gameType]}
      </Typography>
    </Box>
  );
});
