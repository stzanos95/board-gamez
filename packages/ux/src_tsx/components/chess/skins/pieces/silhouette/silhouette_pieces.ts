import { PieceType } from "@board-gamez/idl/chess/model/piece_pb";

import type { PieceShape } from "../../board_skin";
import { UnknownPiece } from "../UnknownPiece";
import { SilhouetteBishop } from "./SilhouetteBishop";
import { SilhouetteKing } from "./SilhouetteKing";
import { SilhouetteKnight } from "./SilhouetteKnight";
import { SilhouettePawn } from "./SilhouettePawn";
import { SilhouetteQueen } from "./SilhouetteQueen";
import { SilhouetteRook } from "./SilhouetteRook";

/**
 * Plain, flat-sided pieces in the shape of a tournament set.
 */
export const SILHOUETTE_PIECES: Record<PieceType, PieceShape> = {
  [PieceType.UNSPECIFIED]: UnknownPiece,
  [PieceType.PAWN]: SilhouettePawn,
  [PieceType.KNIGHT]: SilhouetteKnight,
  [PieceType.BISHOP]: SilhouetteBishop,
  [PieceType.ROOK]: SilhouetteRook,
  [PieceType.QUEEN]: SilhouetteQueen,
  [PieceType.KING]: SilhouetteKing,
};
