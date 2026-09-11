import type { SquareOccupant } from "@board-gamez/idl/chess/model/board_pb";
import type { ChessGame, ChessTurn, GameResult } from "@board-gamez/idl/chess/model/game_pb";
import type { Move } from "@board-gamez/idl/chess/model/move_pb";
import { Color, PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import { File, Rank, type Square } from "@board-gamez/idl/chess/model/square_pb";
import type { ChessSession } from "@board-gamez/idl/chess/model/session_pb";

import {
  COLOR_LABELS,
  FILE_LETTERS,
  GAME_OUTCOME_LABELS,
  GAME_STATUS_IS_CHECK,
  GAME_STATUS_REASONS,
  MOVE_TYPE_CAPTURES,
  PIECE_TYPE_LABELS,
  RANK_DIGITS,
  RESIGNATION_REASON,
} from "./chess_labels";

/**
 * A chess game, in the shape a screen draws it.
 *
 * These are derivations over data already in hand: an index over the
 * occupancy list, a label, a comparison against who is looking. Which moves
 * are legal, whose turn it is and whether the game is over all come from the
 * game itself; nothing here decides any of them.
 */

/**
 * A square named in coordinate text, "e4". The key every map of squares is
 * read by.
 */
export type SquareKey = string;

const UNKNOWN_SQUARE_KEY = "?";
const EMPTY_SQUARE_LABEL = "empty";
const WATCHING_LABEL = "You are watching";

const ALL_FILES: readonly File[] = [
  File.A,
  File.B,
  File.C,
  File.D,
  File.E,
  File.F,
  File.G,
  File.H,
];

const ALL_RANKS: readonly Rank[] = [
  Rank.RANK_1,
  Rank.RANK_2,
  Rank.RANK_3,
  Rank.RANK_4,
  Rank.RANK_5,
  Rank.RANK_6,
  Rank.RANK_7,
  Rank.RANK_8,
];

export type OccupantView = {
  readonly color: Color;
  readonly pieceType: PieceType;
};

export type LastMoveView = {
  readonly origin: SquareKey;
  readonly destination: SquareKey;
};

/**
 * One turn of the move list. `black` is empty while Black has not answered.
 */
export type TurnView = {
  readonly number: number;
  readonly white: string;
  readonly black: string;
};

/**
 * Whose move it is and how the game stands, as one line and an optional
 * second one.
 *
 * `canAct` is true only for a player whose side is to move in a game that has
 * no result. Resignation is an action like any other and is gated the same way.
 */
export type GameStatusView = {
  readonly sideToMove: Color;
  readonly viewerColor: Color;
  readonly isSpectator: boolean;
  readonly isOver: boolean;
  readonly canAct: boolean;
  readonly viewerLabel: string;
  readonly headline: string;
  readonly detail: string | null;
};

export type ChessGameView = {
  readonly version: bigint;
  readonly orientation: Color;
  readonly occupants: ReadonlyMap<SquareKey, OccupantView>;
  readonly legalTargetsByOrigin: ReadonlyMap<SquareKey, readonly Move[]>;
  readonly lastMove: LastMoveView | null;
  readonly checkedKingSquare: SquareKey | null;
  readonly turns: readonly TurnView[];
  readonly status: GameStatusView;
};

/**
 * One square as it is drawn: what stands on it and how it is marked.
 *
 * `isSelectable` says the viewer may pick this square up to move from it.
 * `isCaptureTarget` is a legal target on which a piece is taken, which for en
 * passant is a square that stands empty.
 */
export type SquareView = {
  readonly key: SquareKey;
  readonly file: File;
  readonly rank: Rank;
  readonly isLight: boolean;
  readonly occupant: OccupantView | null;
  readonly label: string;
  readonly isSelected: boolean;
  readonly isSelectable: boolean;
  readonly isLegalTarget: boolean;
  readonly isCaptureTarget: boolean;
  readonly isLastMove: boolean;
  readonly isCheckedKing: boolean;
};

export function squareKeyOf(square: Square | undefined): SquareKey {
  if (square === undefined) {
    return UNKNOWN_SQUARE_KEY;
  }
  return `${FILE_LETTERS[square.file]}${RANK_DIGITS[square.rank]}`;
}

function keyOfFileAndRank(file: File, rank: Rank): SquareKey {
  return `${FILE_LETTERS[file]}${RANK_DIGITS[rank]}`;
}

export function toChessGameView(session: ChessSession): ChessGameView {
  const game = session.game;
  const occupants = indexOccupants(game?.state?.occupancy ?? []);
  const sideToMove = game?.state?.sideToMove ?? Color.UNSPECIFIED;
  const status = toGameStatusView(game, session.color);
  const isCheck = game === undefined ? false : GAME_STATUS_IS_CHECK[game.status];

  return {
    version: session.version,
    orientation: session.color === Color.BLACK ? Color.BLACK : Color.WHITE,
    occupants,
    legalTargetsByOrigin: indexLegalMoves(game?.legalMoves ?? []),
    lastMove: toLastMoveView(game?.history?.turns ?? []),
    checkedKingSquare: isCheck ? kingSquareOf(occupants, sideToMove) : null,
    turns: toTurnViews(game?.history?.turns ?? []),
    status,
  };
}

/**
 * The sixty-four squares in the order they are drawn: the viewer's own side
 * along the bottom, so rank 8 comes first for White and for a spectator, and
 * rank 1 first for Black.
 */
export function toSquareViews(
  game: ChessGameView,
  selectedKey: SquareKey | null,
): readonly SquareView[] {
  const ranks = game.orientation === Color.BLACK ? ALL_RANKS : [...ALL_RANKS].reverse();
  const files = game.orientation === Color.BLACK ? [...ALL_FILES].reverse() : ALL_FILES;
  const targets = selectedKey === null ? [] : (game.legalTargetsByOrigin.get(selectedKey) ?? []);
  const targetsByDestination = indexTargets(targets);

  const squares: SquareView[] = [];
  for (const rank of ranks) {
    for (const file of files) {
      const key = keyOfFileAndRank(file, rank);
      const occupant = game.occupants.get(key) ?? null;
      const target = targetsByDestination.get(key) ?? null;
      squares.push({
        key,
        file,
        rank,
        isLight: (file + rank) % 2 === 1,
        occupant,
        label: labelOf(key, occupant),
        isSelected: key === selectedKey,
        isSelectable: game.status.canAct && game.legalTargetsByOrigin.has(key),
        isLegalTarget: target !== null,
        isCaptureTarget: target !== null && MOVE_TYPE_CAPTURES[target.moveType],
        isLastMove: game.lastMove?.origin === key || game.lastMove?.destination === key,
        isCheckedKing: game.checkedKingSquare === key,
      });
    }
  }
  return squares;
}

/**
 * The file and rank labels along the two edges the viewer reads, in the same
 * order the squares are drawn.
 */
export function fileLettersFor(orientation: Color): readonly string[] {
  const files = orientation === Color.BLACK ? [...ALL_FILES].reverse() : ALL_FILES;
  return files.map((file: File) => FILE_LETTERS[file]);
}

export function rankDigitsFor(orientation: Color): readonly string[] {
  const ranks = orientation === Color.BLACK ? ALL_RANKS : [...ALL_RANKS].reverse();
  return ranks.map((rank: Rank) => RANK_DIGITS[rank]);
}

function indexOccupants(occupancy: readonly SquareOccupant[]): ReadonlyMap<SquareKey, OccupantView> {
  const indexed = new Map<SquareKey, OccupantView>();
  for (const entry of occupancy) {
    if (entry.occupant === undefined) {
      continue;
    }
    indexed.set(squareKeyOf(entry.square), {
      color: entry.occupant.color,
      pieceType: entry.occupant.pieceType,
    });
  }
  return indexed;
}

function indexLegalMoves(moves: readonly Move[]): ReadonlyMap<SquareKey, readonly Move[]> {
  const indexed = new Map<SquareKey, Move[]>();
  for (const move of moves) {
    const origin = squareKeyOf(move.origin);
    const fromOrigin = indexed.get(origin);
    if (fromOrigin === undefined) {
      indexed.set(origin, [move]);
    } else {
      fromOrigin.push(move);
    }
  }
  return indexed;
}

/**
 * One move per destination. A promotion offers several moves to one square,
 * and any of them says what the square looks like as a target.
 */
function indexTargets(moves: readonly Move[]): ReadonlyMap<SquareKey, Move> {
  const indexed = new Map<SquareKey, Move>();
  for (const move of moves) {
    indexed.set(squareKeyOf(move.destination), move);
  }
  return indexed;
}

function kingSquareOf(
  occupants: ReadonlyMap<SquareKey, OccupantView>,
  color: Color,
): SquareKey | null {
  for (const [key, occupant] of occupants) {
    if (occupant.color === color && occupant.pieceType === PieceType.KING) {
      return key;
    }
  }
  return null;
}

function toLastMoveView(turns: readonly ChessTurn[]): LastMoveView | null {
  const last = turns[turns.length - 1];
  if (last?.move === undefined) {
    return null;
  }
  return {
    origin: squareKeyOf(last.move.origin),
    destination: squareKeyOf(last.move.destination),
  };
}

/**
 * Turns paired by number. The history lists every half-move in the order it
 * was played, and White's and Black's share a number.
 */
function toTurnViews(turns: readonly ChessTurn[]): readonly TurnView[] {
  const paired: TurnView[] = [];
  for (const turn of turns) {
    const open = paired[paired.length - 1];
    if (open !== undefined && open.number === turn.number && open.black.length === 0) {
      paired[paired.length - 1] = { ...open, black: turn.notation };
    } else if (turn.player?.color === Color.BLACK) {
      paired.push({ number: turn.number, white: "", black: turn.notation });
    } else {
      paired.push({ number: turn.number, white: turn.notation, black: "" });
    }
  }
  return paired;
}

function toGameStatusView(game: ChessGame | undefined, viewerColor: Color): GameStatusView {
  const sideToMove = game?.state?.sideToMove ?? Color.UNSPECIFIED;
  const result = game?.result;
  const isSpectator = viewerColor === Color.UNSPECIFIED;
  const isOver = result !== undefined;
  const canAct = !isOver && !isSpectator && viewerColor === sideToMove;
  const isCheck = game === undefined ? false : GAME_STATUS_IS_CHECK[game.status];

  return {
    sideToMove,
    viewerColor,
    isSpectator,
    isOver,
    canAct,
    viewerLabel: isSpectator ? WATCHING_LABEL : `You play ${COLOR_LABELS[viewerColor]}`,
    headline: result === undefined ? turnHeadline(sideToMove, canAct, isSpectator) : resultHeadline(result),
    detail: isCheck && !isOver ? "Check" : null,
  };
}

function turnHeadline(sideToMove: Color, canAct: boolean, isSpectator: boolean): string {
  if (canAct) {
    return "Your move";
  }
  if (isSpectator) {
    return `${COLOR_LABELS[sideToMove]} to move`;
  }
  return `Waiting for ${COLOR_LABELS[sideToMove]}`;
}

function resultHeadline(result: GameResult): string {
  const reason =
    result.resigningPlayer === undefined ? GAME_STATUS_REASONS[result.status] : RESIGNATION_REASON;
  const outcome = GAME_OUTCOME_LABELS[result.outcome];
  return reason.length === 0 ? outcome : `${outcome} ${reason}`;
}

function labelOf(key: SquareKey, occupant: OccupantView | null): string {
  if (occupant === null) {
    return `${key}, ${EMPTY_SQUARE_LABEL}`;
  }
  const color = COLOR_LABELS[occupant.color].toLowerCase();
  return `${key}, ${color} ${PIECE_TYPE_LABELS[occupant.pieceType]}`;
}
