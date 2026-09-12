import { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import { SeatStatus } from "@board-gamez/idl/lobby/model/seat_pb";
import { TableStatus } from "@board-gamez/idl/lobby/model/table_pb";

/**
 * What the contract's values are called on screen.
 *
 * Each record is keyed by its enum, so a member added to the schema and
 * regenerated stops the build here until it has been given a name.
 */
export type ChipTone = "default" | "primary" | "secondary" | "success" | "warning" | "error";

export const TABLE_STATUS_LABELS: Record<TableStatus, string> = {
  [TableStatus.UNSPECIFIED]: "Unknown",
  [TableStatus.WAITING]: "Waiting for players",
  [TableStatus.IN_PROGRESS]: "In progress",
  [TableStatus.FINISHED]: "Finished",
  [TableStatus.ABANDONED]: "Abandoned",
};

export const TABLE_STATUS_TONES: Record<TableStatus, ChipTone> = {
  [TableStatus.UNSPECIFIED]: "default",
  [TableStatus.WAITING]: "success",
  [TableStatus.IN_PROGRESS]: "primary",
  [TableStatus.FINISHED]: "default",
  [TableStatus.ABANDONED]: "error",
};

export const SEAT_STATUS_LABELS: Record<SeatStatus, string> = {
  [SeatStatus.UNSPECIFIED]: "Unknown",
  [SeatStatus.OPEN]: "Open",
  [SeatStatus.OCCUPIED]: "Taken",
};

export const GAME_TYPE_LABELS: Record<GameType, string> = {
  [GameType.UNSPECIFIED]: "Unknown game",
  [GameType.CHESS]: "Chess",
  [GameType.UNO]: "UNO",
};

/**
 * The games a table can be opened for.
 *
 * UNSPECIFIED is what a reader sees when a newer schema has set a value this
 * build does not know. No table is ever created with it.
 */
export const CREATABLE_GAME_TYPES: readonly GameType[] = [GameType.CHESS, GameType.UNO];
