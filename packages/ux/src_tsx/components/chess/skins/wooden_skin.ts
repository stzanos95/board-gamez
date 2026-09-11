import { Color } from "@board-gamez/idl/chess/model/piece_pb";

import type { BoardSkin } from "./board_skin";
import { WoodBoardFrame } from "./frames/WoodBoardFrame";
import { GrainSquareGround } from "./grounds/GrainSquareGround";
import { SILHOUETTE_PIECES } from "./pieces/silhouette/silhouette_pieces";

/**
 * Ivory and brown pieces on a board of bright and dark wood.
 */
export const WOODEN_SKIN: BoardSkin = {
  label: "Wooden",
  palette: {
    lightSquare: "#e8c69c",
    darkSquare: "#9a6a3e",
    selectedOverlay: "rgba(255, 232, 120, 0.6)",
    lastMoveOverlay: "rgba(255, 220, 100, 0.32)",
    checkOverlay: "rgba(200, 40, 30, 0.7)",
    targetMarker: "rgba(60, 30, 10, 0.45)",
    frame: "#6b4423",
    frameEdge: "#3c2412",
    coordinate: "#e8c69c",
  },
  sides: {
    [Color.UNSPECIFIED]: { body: "#b39b7d", outline: "#3c2412", accent: "#3c2412" },
    [Color.WHITE]: { body: "#f5e9d2", outline: "#6b4a2a", accent: "#6b4a2a" },
    [Color.BLACK]: { body: "#5a3419", outline: "#f5e9d2", accent: "#f5e9d2" },
  },
  pieces: SILHOUETTE_PIECES,
  Square: GrainSquareGround,
  Board: WoodBoardFrame,
};
