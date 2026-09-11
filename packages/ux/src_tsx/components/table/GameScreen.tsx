import { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import { memo, type ComponentType, type ReactElement } from "react";

import { ChessScreen } from "../chess/ChessScreen";
import { PanelMessage } from "../common/PanelMessage";
import type { GameScreenProps } from "./game_screen_props";

const UnknownGameScreen = memo(function UnknownGameScreen(): ReactElement {
  return (
    <PanelMessage
      severity="info"
      title="No screen for this game"
      detail="This build does not know how to draw the game at this table."
    />
  );
});

/**
 * The screen each game is played on.
 *
 * Keyed by the enum, so a game added to the schema does not compile until it
 * has been given a screen.
 */
const SCREEN_BY_GAME_TYPE: Record<GameType, ComponentType<GameScreenProps>> = {
  [GameType.UNSPECIFIED]: UnknownGameScreen,
  [GameType.CHESS]: ChessScreen,
};

export type GameScreenSelectorProps = GameScreenProps & {
  readonly gameType: GameType;
};

export const GameScreen = memo(function GameScreen(props: GameScreenSelectorProps): ReactElement {
  const { gameType, tableId, canStart, isSeated } = props;
  const Screen = SCREEN_BY_GAME_TYPE[gameType];

  return <Screen tableId={tableId} canStart={canStart} isSeated={isSeated} />;
});
