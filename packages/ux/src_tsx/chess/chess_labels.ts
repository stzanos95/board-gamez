import { GameOutcome, GameStatus } from "@board-gamez/idl/chess/model/game_pb";
import { MoveType } from "@board-gamez/idl/chess/model/move_pb";
import { Color, PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import { File, Rank } from "@board-gamez/idl/chess/model/square_pb";
import { CommandOutcome } from "@board-gamez/idl/game/model/command_result_pb";

/**
 * What the chess contract's values are called on screen.
 *
 * Each record is keyed by its enum, so a member added to the schema and
 * regenerated stops the build here until it has been given a name.
 */

export const FILE_LETTERS: Record<File, string> = {
  [File.UNSPECIFIED]: "?",
  [File.A]: "a",
  [File.B]: "b",
  [File.C]: "c",
  [File.D]: "d",
  [File.E]: "e",
  [File.F]: "f",
  [File.G]: "g",
  [File.H]: "h",
};

export const RANK_DIGITS: Record<Rank, string> = {
  [Rank.RANK_UNSPECIFIED]: "?",
  [Rank.RANK_1]: "1",
  [Rank.RANK_2]: "2",
  [Rank.RANK_3]: "3",
  [Rank.RANK_4]: "4",
  [Rank.RANK_5]: "5",
  [Rank.RANK_6]: "6",
  [Rank.RANK_7]: "7",
  [Rank.RANK_8]: "8",
};

export const COLOR_LABELS: Record<Color, string> = {
  [Color.UNSPECIFIED]: "Nobody",
  [Color.WHITE]: "White",
  [Color.BLACK]: "Black",
};

export const PIECE_TYPE_LABELS: Record<PieceType, string> = {
  [PieceType.UNSPECIFIED]: "piece",
  [PieceType.PAWN]: "pawn",
  [PieceType.KNIGHT]: "knight",
  [PieceType.BISHOP]: "bishop",
  [PieceType.ROOK]: "rook",
  [PieceType.QUEEN]: "queen",
  [PieceType.KING]: "king",
};

/**
 * The pieces a pawn may become, in the order a player is offered them.
 */
export const PROMOTION_CHOICES: readonly PieceType[] = [
  PieceType.QUEEN,
  PieceType.ROOK,
  PieceType.BISHOP,
  PieceType.KNIGHT,
];

/**
 * Whether a move takes a piece. En passant takes one off a square the move
 * does not land on, so the destination is empty and the move still captures.
 */
export const MOVE_TYPE_CAPTURES: Record<MoveType, boolean> = {
  [MoveType.UNSPECIFIED]: false,
  [MoveType.QUIET]: false,
  [MoveType.CAPTURE]: true,
  [MoveType.DOUBLE_PAWN_PUSH]: false,
  [MoveType.EN_PASSANT]: true,
  [MoveType.CASTLE]: false,
  [MoveType.PROMOTION]: false,
  [MoveType.PROMOTION_CAPTURE]: true,
};

export const GAME_OUTCOME_LABELS: Record<GameOutcome, string> = {
  [GameOutcome.UNSPECIFIED]: "Game over",
  [GameOutcome.WHITE_WINS]: "White wins",
  [GameOutcome.BLACK_WINS]: "Black wins",
  [GameOutcome.DRAW]: "Draw",
};

/**
 * How a game ended, as the phrase that follows the outcome. Empty while the
 * game is still being played.
 */
export const GAME_STATUS_REASONS: Record<GameStatus, string> = {
  [GameStatus.UNSPECIFIED]: "",
  [GameStatus.IN_PROGRESS]: "",
  [GameStatus.CHECK]: "",
  [GameStatus.CHECKMATE]: "by checkmate",
  [GameStatus.STALEMATE]: "by stalemate",
  [GameStatus.DRAW_BY_FIFTY_MOVE_RULE]: "by the fifty-move rule",
  [GameStatus.DRAW_BY_REPETITION]: "by repetition",
  [GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL]: "by insufficient material",
};

export const RESIGNATION_REASON = "by resignation";

/**
 * Whether a status means the side to move is in check, mate included.
 */
export const GAME_STATUS_IS_CHECK: Record<GameStatus, boolean> = {
  [GameStatus.UNSPECIFIED]: false,
  [GameStatus.IN_PROGRESS]: false,
  [GameStatus.CHECK]: true,
  [GameStatus.CHECKMATE]: true,
  [GameStatus.STALEMATE]: false,
  [GameStatus.DRAW_BY_FIFTY_MOVE_RULE]: false,
  [GameStatus.DRAW_BY_REPETITION]: false,
  [GameStatus.DRAW_BY_INSUFFICIENT_MATERIAL]: false,
};

/**
 * What a player is told about an action, or null when there is nothing to
 * say. An action that landed, a repeat of one that had already landed, and a
 * game that moved on before the action reached it all show the session that
 * came back and nothing else.
 */
export const COMMAND_OUTCOME_MESSAGES: Record<CommandOutcome, string | null> = {
  [CommandOutcome.UNSPECIFIED]: "The game answered something this build cannot read.",
  [CommandOutcome.APPLIED]: null,
  [CommandOutcome.ALREADY_APPLIED]: null,
  [CommandOutcome.SESSION_NOT_FOUND]: "There is no game at this table.",
  [CommandOutcome.NOT_A_PARTICIPANT]: "Only the two players may act in this game.",
  [CommandOutcome.GAME_OVER]: "The game is over.",
  [CommandOutcome.VERSION_MOVED]: null,
  [CommandOutcome.OUT_OF_TURN]: "It is not your turn.",
  [CommandOutcome.ILLEGAL_ACTION]: "The rules refused that move.",
};
