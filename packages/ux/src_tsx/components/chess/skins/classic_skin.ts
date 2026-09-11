import { Color } from "@board-gamez/idl/chess/model/piece_pb";

import type { BoardSkin } from "./board_skin";
import { BandBoardFrame } from "./frames/BandBoardFrame";
import { FlatSquareGround } from "./grounds/FlatSquareGround";
import { SILHOUETTE_PIECES } from "./pieces/silhouette/silhouette_pieces";

/**
 * Black and white: a tournament set on a grey and white board.
 */
export const CLASSIC_SKIN: BoardSkin = {
  label: "Classic",
  palette: {
    lightSquare: "#f2f2f2",
    darkSquare: "#4d4d4d",
    selectedOverlay: "rgba(255, 214, 0, 0.55)",
    lastMoveOverlay: "rgba(255, 214, 0, 0.28)",
    checkOverlay: "rgba(220, 40, 40, 0.65)",
    targetMarker: "rgba(30, 144, 255, 0.65)",
    frame: "#262626",
    frameEdge: "#0d0d0d",
    coordinate: "#c8c8c8",
  },
  sides: {
    [Color.UNSPECIFIED]: { body: "#9a9a9a", outline: "#1a1a1a", accent: "#1a1a1a" },
    [Color.WHITE]: { body: "#ffffff", outline: "#1a1a1a", accent: "#1a1a1a" },
    [Color.BLACK]: { body: "#141414", outline: "#e8e8e8", accent: "#e8e8e8" },
  },
  pieces: SILHOUETTE_PIECES,
  Square: FlatSquareGround,
  Board: BandBoardFrame,
};
