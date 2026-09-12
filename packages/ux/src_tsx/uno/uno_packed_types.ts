import type { DescFile } from "@bufbuild/protobuf";
import { file_idl_uno_model_action } from "@board-gamez/idl/uno/model/action_pb";
import { file_idl_uno_model_game } from "@board-gamez/idl/uno/model/game_pb";
import { file_idl_uno_model_view } from "@board-gamez/idl/uno/model/view_pb";

/**
 * The files declaring every type UNO packs into a payload the platform
 * carries opaquely: an action, a game, and a viewer's projection of one. A
 * UNO seat carries no role. A type not listed here cannot cross the wire
 * inside an `Any`, in either direction.
 */
export const UNO_PACKED_FILES: readonly DescFile[] = [
  file_idl_uno_model_action,
  file_idl_uno_model_game,
  file_idl_uno_model_view,
];
