import type { DescFile, Registry } from "@bufbuild/protobuf";
import { createRegistry } from "@bufbuild/protobuf";
import { GameType } from "@board-gamez/idl/game/model/game_type_pb";

import { CHESS_PACKED_FILES } from "../chess/chess_packed_types";
import { UNO_PACKED_FILES } from "../uno/uno_packed_types";

const NO_PACKED_FILES: readonly DescFile[] = [];

/**
 * The types each game packs into a payload the platform carries opaquely.
 *
 * Keyed by the enum, so a game added to the schema does not compile until it
 * has said what it packs.
 */
const PACKED_FILES_BY_GAME_TYPE: Record<GameType, readonly DescFile[]> = {
  [GameType.UNSPECIFIED]: NO_PACKED_FILES,
  [GameType.CHESS]: CHESS_PACKED_FILES,
  [GameType.UNO]: UNO_PACKED_FILES,
};

/**
 * Every type a payload on the wire may carry, from every game this build
 * knows.
 */
export function buildPackedTypeRegistry(): Registry {
  return createRegistry(...Object.values(PACKED_FILES_BY_GAME_TYPE).flat());
}
