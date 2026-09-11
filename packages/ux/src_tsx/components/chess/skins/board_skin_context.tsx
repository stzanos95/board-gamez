import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";

import type { BoardSkin } from "./board_skin";
import type { BoardSkinName } from "./board_skin_name";
import { readBoardSkinPreference, writeBoardSkinPreference } from "./board_skin_preference";
import { BOARD_SKINS_BY_NAME } from "./board_skin_registry";

export type BoardSkinSelection = {
  readonly name: BoardSkinName;
  readonly skin: BoardSkin;
  readonly select: (name: BoardSkinName) => void;
};

const BoardSkinContext = createContext<BoardSkinSelection | null>(null);

export type BoardSkinProviderProps = {
  readonly defaultSkin: BoardSkinName;
  readonly children: ReactNode;
};

function initialSkinName(defaultSkin: BoardSkinName): BoardSkinName {
  return readBoardSkinPreference() ?? defaultSkin;
}

/**
 * Holds the skin every board below it is drawn in, and the one way to change
 * it.
 *
 * The player's own choice wins over the configured default, and is recorded
 * when made.
 */
export function BoardSkinProvider(props: BoardSkinProviderProps): ReactElement {
  const { defaultSkin, children } = props;
  const [name, setName] = useState<BoardSkinName>(() => initialSkinName(defaultSkin));

  const select = useCallback((next: BoardSkinName) => {
    writeBoardSkinPreference(next);
    setName(next);
  }, []);

  const selection = useMemo<BoardSkinSelection>(
    () => ({ name, skin: BOARD_SKINS_BY_NAME[name], select }),
    [name, select],
  );

  return <BoardSkinContext.Provider value={selection}>{children}</BoardSkinContext.Provider>;
}

export function useBoardSkin(): BoardSkinSelection {
  const selection = useContext(BoardSkinContext);
  if (selection === null) {
    throw new Error("a board asked for its skin outside BoardSkinProvider");
  }
  return selection;
}
