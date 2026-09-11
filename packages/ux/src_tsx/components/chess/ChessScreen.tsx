import { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import type { Move } from "@board-gamez/idl/chess/model/move_pb";
import { PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import type { Square } from "@board-gamez/idl/chess/model/square_pb";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogTitle from "@mui/material/DialogTitle";
import Stack from "@mui/material/Stack";
import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";

import { PROMOTION_CHOICES } from "../../chess/chess_labels";
import {
  fileLettersFor,
  rankDigitsFor,
  squareKeyOf,
  type SquareKey,
} from "../../chess/chess_views";
import { useBoardSquares } from "../../chess/use_board_squares";
import { useChessSession } from "../../chess/use_chess_session";
import { usePlayAction } from "../../chess/use_play_action";
import { useStartGame } from "../../chess/use_start_game";
import { GameArtwork } from "../common/GameArtwork";
import { LoadingPanel, PanelMessage } from "../common/PanelMessage";
import type { GameScreenProps } from "../table/game_screen_props";
import { BoardSkinPicker } from "./BoardSkinPicker";
import { ChessBoard } from "./ChessBoard";
import { GameStatusBanner } from "./GameStatusBanner";
import { MoveList } from "./MoveList";
import { PreGamePanel } from "./PreGamePanel";
import { PromotionDialog } from "./PromotionDialog";

const PRE_GAME_LAYOUT_SX = {
  display: "grid",
  gap: 3,
  gridTemplateColumns: { xs: "1fr", md: "minmax(0, 1fr) 300px" },
  alignItems: "start",
} as const;

const GAME_LAYOUT_SX = {
  display: "grid",
  gap: 3,
  gridTemplateColumns: { xs: "1fr", md: "minmax(0, 1fr) 300px" },
  alignItems: "start",
} as const;

const BOARD_COLUMN_SX = { maxWidth: "min(100%, 78vh)", width: "100%" } as const;

/**
 * A pawn that has reached the last rank, waiting to be told what it becomes.
 */
type PendingPromotion = {
  readonly origin: Square;
  readonly destination: Square;
  readonly choices: readonly PieceType[];
};

/**
 * The chess game at a table.
 *
 * Which square is picked up, which dialog is open and whether a resignation
 * is being confirmed are the only state this screen holds. What a piece may
 * do comes from the legal moves the game listed; clicking one of their
 * destinations sends that move.
 */
export function ChessScreen(props: GameScreenProps): ReactElement {
  const { tableId, canStart, isSeated } = props;
  const { game, isLoading, error } = useChessSession(tableId);
  const { run: startGame, isPending: isStarting, problem: startProblem } = useStartGame();
  const { playMove, resign, isPending: isPlaying, problem: playProblem, dismissProblem } =
    usePlayAction();
  const [selectedKey, setSelectedKey] = useState<SquareKey | null>(null);
  const [promotion, setPromotion] = useState<PendingPromotion | null>(null);
  const [isResignOpen, setIsResignOpen] = useState(false);
  const squares = useBoardSquares(game, selectedKey);

  const version = game?.version ?? null;
  useEffect(() => {
    setSelectedKey(null);
    setPromotion(null);
  }, [version]);

  const orientation = game?.orientation;
  const fileLetters = useMemo(
    () => (orientation === undefined ? [] : fileLettersFor(orientation)),
    [orientation],
  );
  const rankDigits = useMemo(
    () => (orientation === undefined ? [] : rankDigitsFor(orientation)),
    [orientation],
  );

  const handleStart = useCallback(() => startGame(tableId), [startGame, tableId]);

  const commitMove = useCallback(
    (move: Move, promotionType: PieceType) => {
      if (game === null || move.origin === undefined || move.destination === undefined) {
        return;
      }
      playMove({
        tableId,
        origin: move.origin,
        destination: move.destination,
        promotionType,
        expectedVersion: game.version,
      });
      setSelectedKey(null);
    },
    [game, playMove, tableId],
  );

  const handleSelect = useCallback(
    (squareKey: SquareKey) => {
      if (game === null || !game.status.canAct || isPlaying) {
        return;
      }
      dismissProblem();
      const fromSelected =
        selectedKey === null ? [] : (game.legalTargetsByOrigin.get(selectedKey) ?? []);
      const toSquare = fromSelected.filter(
        (move: Move) => squareKeyOf(move.destination) === squareKey,
      );
      const [single] = toSquare;
      if (single !== undefined && toSquare.length === 1) {
        commitMove(single, single.promotionType);
        return;
      }
      if (single?.origin !== undefined && single.destination !== undefined) {
        setPromotion({
          origin: single.origin,
          destination: single.destination,
          choices: offeredInOrder(toSquare),
        });
        return;
      }
      if (game.legalTargetsByOrigin.has(squareKey)) {
        setSelectedKey(squareKey === selectedKey ? null : squareKey);
        return;
      }
      setSelectedKey(null);
    },
    [game, isPlaying, selectedKey, commitMove, dismissProblem],
  );

  const handlePromotionChoice = useCallback(
    (pieceType: PieceType) => {
      if (game === null || promotion === null) {
        return;
      }
      playMove({
        tableId,
        origin: promotion.origin,
        destination: promotion.destination,
        promotionType: pieceType,
        expectedVersion: game.version,
      });
      setPromotion(null);
      setSelectedKey(null);
    },
    [game, promotion, playMove, tableId],
  );
  const handlePromotionClose = useCallback(() => setPromotion(null), []);

  const handleResignClick = useCallback(() => setIsResignOpen(true), []);
  const handleResignClose = useCallback(() => setIsResignOpen(false), []);
  const handleResignConfirm = useCallback(() => {
    setIsResignOpen(false);
    if (game !== null) {
      resign({ tableId, expectedVersion: game.version });
    }
  }, [game, resign, tableId]);

  const problem = playProblem ?? startProblem ?? (error === null ? null : error.message);
  const problemPanel =
    problem === null ? null : (
      <PanelMessage severity="warning" title="That did not work" detail={problem} />
    );

  const preGame = (
    <Box sx={PRE_GAME_LAYOUT_SX}>
      <PreGamePanel
        canStart={canStart}
        isSeated={isSeated}
        isStarting={isStarting}
        onStart={handleStart}
      />
      <GameArtwork gameType={GameType.CHESS} />
    </Box>
  );

  const resignButton =
    game === null || !game.status.canAct ? null : (
      <Button variant="outlined" color="error" onClick={handleResignClick} disabled={isPlaying}>
        Resign
      </Button>
    );

  const resignDialog = (
    <Dialog open={isResignOpen} onClose={handleResignClose} maxWidth="xs">
      <DialogTitle>Resign this game?</DialogTitle>
      <DialogActions>
        <Button onClick={handleResignClose} variant="text">
          Keep playing
        </Button>
        <Button onClick={handleResignConfirm} variant="contained" color="error">
          Resign
        </Button>
      </DialogActions>
    </Dialog>
  );

  const promotionDialog =
    game === null ? null : (
      <PromotionDialog
        isOpen={promotion !== null}
        color={game.status.viewerColor}
        choices={promotion?.choices ?? []}
        onChoose={handlePromotionChoice}
        onClose={handlePromotionClose}
      />
    );

  const inGame =
    game === null ? null : (
      <Box sx={GAME_LAYOUT_SX}>
        <Box sx={BOARD_COLUMN_SX}>
          <ChessBoard
            squares={squares}
            fileLetters={fileLetters}
            rankDigits={rankDigits}
            onSelect={handleSelect}
          />
        </Box>
        <Stack spacing={2}>
          <GameStatusBanner
            viewerLabel={game.status.viewerLabel}
            headline={game.status.headline}
            detail={game.status.detail}
            canAct={game.status.canAct}
            isOver={game.status.isOver}
          />
          <MoveList turns={game.turns} />
          <BoardSkinPicker />
          {resignButton}
        </Stack>
        {promotionDialog}
        {resignDialog}
      </Box>
    );

  const body = isLoading ? <LoadingPanel label="Reading the game" /> : game === null ? preGame : inGame;

  return (
    <Stack spacing={2}>
      {problemPanel}
      {body}
    </Stack>
  );
}

/**
 * The promotions among a set of moves, in the order they are offered.
 */
function offeredInOrder(moves: readonly Move[]): readonly PieceType[] {
  const offered = new Set(moves.map((move: Move) => move.promotionType));
  return PROMOTION_CHOICES.filter((pieceType: PieceType) => offered.has(pieceType));
}
