import type { DescFile } from "@bufbuild/protobuf";
import { file_idl_chess_model_side } from "@board-gamez/idl/chess/model/side_pb";

/**
 * The files declaring every type chess packs into a payload the platform
 * carries opaquely: a seat's role. A type not listed here cannot cross the wire
 * inside an `Any`, in either direction.
 */
export const CHESS_PACKED_FILES: readonly DescFile[] = [file_idl_chess_model_side];
