import { PieceType } from "@board-gamez/idl/chess/model/piece_pb";

import type { PieceShape } from "../../board_skin";
import { UnknownPiece } from "../UnknownPiece";
import { CartoonBishop } from "./CartoonBishop";
import { CartoonKing } from "./CartoonKing";
import { CartoonKnight } from "./CartoonKnight";
import { CartoonPawn } from "./CartoonPawn";
import { CartoonQueen } from "./CartoonQueen";
import { CartoonRook } from "./CartoonRook";

/**
 * Round, thick-outlined pieces, each with a face.
 */
export const CARTOON_PIECES: Record<PieceType, PieceShape> = {
  [PieceType.UNSPECIFIED]: UnknownPiece,
  [PieceType.PAWN]: CartoonPawn,
  [PieceType.KNIGHT]: CartoonKnight,
  [PieceType.BISHOP]: CartoonBishop,
  [PieceType.ROOK]: CartoonRook,
  [PieceType.QUEEN]: CartoonQueen,
  [PieceType.KING]: CartoonKing,
};
