import { Color } from "@board-gamez/idl/chess/model/piece_pb";

import type { BoardSkin } from "./board_skin";
import { BubbleBoardFrame } from "./frames/BubbleBoardFrame";
import { TileSquareGround } from "./grounds/TileSquareGround";
import { CARTOON_PIECES } from "./pieces/cartoon/cartoon_pieces";

/**
 * Round pieces with faces: a bright yellow side and a dark violet side on
 * butter and mint tiles.
 */
export const CARTOON_SKIN: BoardSkin = {
  label: "Cartoon",
  palette: {
    lightSquare: "#fff1b5",
    darkSquare: "#7fd1b9",
    selectedOverlay: "rgba(255, 105, 180, 0.5)",
    lastMoveOverlay: "rgba(255, 160, 60, 0.4)",
    checkOverlay: "rgba(255, 60, 60, 0.65)",
    targetMarker: "rgba(90, 60, 200, 0.55)",
    frame: "#ff8fab",
    frameEdge: "#c9184a",
    coordinate: "#5a189a",
  },
  sides: {
    [Color.UNSPECIFIED]: { body: "#c0c0c0", outline: "#3a3a3a", accent: "#ffffff" },
    [Color.WHITE]: { body: "#ffd166", outline: "#3a2a1a", accent: "#ffffff" },
    [Color.BLACK]: { body: "#5b4bd6", outline: "#1a1440", accent: "#ffffff" },
  },
  pieces: CARTOON_PIECES,
  Square: TileSquareGround,
  Board: BubbleBoardFrame,
};
