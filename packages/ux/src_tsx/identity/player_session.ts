import { create } from "@bufbuild/protobuf";
import { PlayerSchema, type Player } from "@board-gamez/idl/identity/model/player_pb";

const PLAYER_ID_KEY = "board-gamez.player.id";
const PLAYER_NAME_KEY = "board-gamez.player.name";
const NAME_PREFIX = "Player";
const NAME_SUFFIX_LENGTH = 4;

/**
 * Who is playing at this browser tab.
 *
 * Held in session storage, which is per-tab: a second tab is a second player,
 * which is what lets a table be filled from one browser. A reload keeps the
 * same player; closing the tab ends them.
 *
 * This is the shape an authenticated session will have. When sign-in arrives,
 * the player arrives with it and this module is what it replaces.
 */
export function readOrCreatePlayer(): Player {
  const id = readOrCreateId();
  return create(PlayerSchema, {
    id,
    displayName: window.sessionStorage.getItem(PLAYER_NAME_KEY) ?? defaultNameFor(id),
  });
}

/**
 * Record a new display name for this tab's player and answer them as renamed.
 */
export function renamePlayer(player: Player, displayName: string): Player {
  const trimmed = displayName.trim();
  if (trimmed.length === 0) {
    return player;
  }
  window.sessionStorage.setItem(PLAYER_NAME_KEY, trimmed);
  return create(PlayerSchema, { id: player.id, displayName: trimmed });
}

function readOrCreateId(): string {
  const stored = window.sessionStorage.getItem(PLAYER_ID_KEY);
  if (stored !== null && stored.length > 0) {
    return stored;
  }
  const created = window.crypto.randomUUID();
  window.sessionStorage.setItem(PLAYER_ID_KEY, created);
  return created;
}

function defaultNameFor(id: string): string {
  return `${NAME_PREFIX} ${id.slice(0, NAME_SUFFIX_LENGTH)}`;
}
