import { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import { CardColor, type Card } from "@board-gamez/idl/uno/model/card_pb";
import type { UnoSeatChoice } from "@board-gamez/idl/uno/model/table_pb";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import { useCallback, useEffect, useState, type ReactElement } from "react";

import { usePlayAction } from "../../uno/use_play_action";
import { useStartGame } from "../../uno/use_start_game";
import { useTakeSeat } from "../../uno/use_take_seat";
import { useUnoSession } from "../../uno/use_uno_session";
import { useUnoTable } from "../../uno/use_uno_table";
import { GameArtwork } from "../common/GameArtwork";
import { LoadingPanel, PanelMessage } from "../common/PanelMessage";
import type { GameScreenProps } from "../table/game_screen_props";
import { ColorChoiceDialog } from "./ColorChoiceDialog";
import { UnoHand } from "./UnoHand";
import { UnoPlayerList } from "./UnoPlayerList";
import { UnoPreGamePanel } from "./UnoPreGamePanel";
import { UnoStatusBanner } from "./UnoStatusBanner";
import { UnoTableCenter } from "./UnoTableCenter";

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

/**
 * The UNO table and, once it has begun, the game at it.
 *
 * Before the game, the seats and who holds them are drawn from UNO's own view
 * of the table, and a seat is taken as one of the choices the game offered.
 * Which wild is waiting for its colour is the only state this screen holds.
 * What may be played comes from the view the game answered; clicking a card
 * it marked playable sends that card.
 */
export function UnoScreen(props: GameScreenProps): ReactElement {
  const { tableId, canStart, isSeated } = props;
  const { game, isLoading, error } = useUnoSession(tableId);
  const { seats, version: tableVersion, error: tableError } = useUnoTable(tableId);
  const { run: startGame, isPending: isStarting, problem: startProblem } = useStartGame();
  const { run: takeSeat, pendingChoice: busyChoice, problem: seatProblem } = useTakeSeat();
  const { playCard, drawCard, passTurn, isPending: isPlaying, problem: playProblem, dismissProblem } =
    usePlayAction();
  const [pendingWild, setPendingWild] = useState<Card | null>(null);

  const version = game?.version ?? null;
  useEffect(() => {
    setPendingWild(null);
  }, [version]);

  const handleStart = useCallback(() => startGame(tableId), [startGame, tableId]);

  const handleTakeSeat = useCallback(
    (choice: UnoSeatChoice) => {
      if (tableVersion !== null) {
        takeSeat({ tableId, choice, expectedVersion: tableVersion });
      }
    },
    [takeSeat, tableId, tableVersion],
  );

  const handlePlay = useCallback(
    (index: number) => {
      if (game === null || !game.status.canAct || isPlaying) {
        return;
      }
      const shown = game.hand[index];
      if (shown === undefined || !shown.isPlayable) {
        return;
      }
      dismissProblem();
      if (shown.view.isWild) {
        setPendingWild(shown.card);
        return;
      }
      playCard({
        tableId,
        card: shown.card,
        chosenColor: CardColor.UNSPECIFIED,
        expectedVersion: game.version,
      });
    },
    [game, isPlaying, dismissProblem, playCard, tableId],
  );

  const handleColorChoice = useCallback(
    (color: CardColor) => {
      if (game === null || pendingWild === null) {
        return;
      }
      playCard({ tableId, card: pendingWild, chosenColor: color, expectedVersion: game.version });
      setPendingWild(null);
    },
    [game, pendingWild, playCard, tableId],
  );
  const handleColorClose = useCallback(() => setPendingWild(null), []);

  const handleDraw = useCallback(() => {
    if (game !== null) {
      dismissProblem();
      drawCard({ tableId, expectedVersion: game.version });
    }
  }, [game, dismissProblem, drawCard, tableId]);

  const handlePass = useCallback(() => {
    if (game !== null) {
      dismissProblem();
      passTurn({ tableId, expectedVersion: game.version });
    }
  }, [game, dismissProblem, passTurn, tableId]);

  const problem =
    playProblem ??
    startProblem ??
    seatProblem ??
    (error === null ? null : error.message) ??
    (tableError === null ? null : tableError.message);
  const problemPanel =
    problem === null ? null : (
      <PanelMessage severity="warning" title="That did not work" detail={problem} />
    );

  const preGame = (
    <Box sx={PRE_GAME_LAYOUT_SX}>
      <UnoPreGamePanel
        seats={seats}
        canStart={canStart}
        isSeated={isSeated}
        isStarting={isStarting}
        busyChoice={busyChoice}
        onTakeSeat={handleTakeSeat}
        onStart={handleStart}
      />
      <GameArtwork gameType={GameType.UNO} />
    </Box>
  );

  const hand =
    game === null || game.status.isSpectator ? null : (
      <UnoHand hand={game.hand} isBusy={isPlaying || !game.status.canAct} onPlay={handlePlay} />
    );

  const colorDialog = (
    <ColorChoiceDialog
      isOpen={pendingWild !== null}
      onChoose={handleColorChoice}
      onClose={handleColorClose}
    />
  );

  const inGame =
    game === null ? null : (
      <Box sx={GAME_LAYOUT_SX}>
        <Stack spacing={2}>
          <UnoTableCenter
            topCard={game.topCard}
            activeColor={game.activeColor}
            activeColorLabel={game.activeColorLabel}
            directionGlyph={game.directionGlyph}
            drawPileCount={game.drawPileCount}
            mayDraw={game.status.mayDraw}
            mayPass={game.status.mayPass}
            isBusy={isPlaying}
            onDraw={handleDraw}
            onPass={handlePass}
          />
          {hand}
        </Stack>
        <Stack spacing={2}>
          <UnoStatusBanner
            viewerLabel={game.status.viewerLabel}
            headline={game.status.headline}
            detail={game.status.detail}
            canAct={game.status.canAct}
            isOver={game.status.isOver}
          />
          <UnoPlayerList players={game.players} />
        </Stack>
        {colorDialog}
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
