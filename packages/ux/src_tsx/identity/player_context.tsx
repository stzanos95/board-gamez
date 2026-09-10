import type { Player } from "@board-gamez/idl/identity/model/player_pb";
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";

import { readOrCreatePlayer, renamePlayer } from "./player_session";

export type PlayerSession = {
  readonly player: Player;
  readonly rename: (displayName: string) => void;
};

const PlayerContext = createContext<PlayerSession | null>(null);

export type PlayerProviderProps = {
  readonly children: ReactNode;
};

/**
 * Holds this tab's player, and the one way to change their name.
 *
 * The player is read from session storage once, when the tab first renders.
 */
export function PlayerProvider(props: PlayerProviderProps): ReactElement {
  const { children } = props;
  const [player, setPlayer] = useState<Player>(readOrCreatePlayer);

  const rename = useCallback((displayName: string) => {
    setPlayer((current: Player) => renamePlayer(current, displayName));
  }, []);

  const session = useMemo<PlayerSession>(() => ({ player, rename }), [player, rename]);

  return <PlayerContext.Provider value={session}>{children}</PlayerContext.Provider>;
}

export function usePlayer(): PlayerSession {
  const session = useContext(PlayerContext);
  if (session === null) {
    throw new Error("a screen asked who is playing outside PlayerProvider");
  }
  return session;
}
