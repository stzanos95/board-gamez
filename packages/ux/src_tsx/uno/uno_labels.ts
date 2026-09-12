import { CommandOutcome } from "@board-gamez/idl/game/model/command_result_pb";
import { CardColor, CardKind } from "@board-gamez/idl/uno/model/card_pb";
import { PlayDirection, UnoResultReason } from "@board-gamez/idl/uno/model/game_pb";

/**
 * What the UNO contract's values are called on screen.
 *
 * Each record is keyed by its enum, so a member added to the schema and
 * regenerated stops the build here until it has been given a name.
 */

export const CARD_COLOR_LABELS: Record<CardColor, string> = {
  [CardColor.UNSPECIFIED]: "Wild",
  [CardColor.RED]: "Red",
  [CardColor.YELLOW]: "Yellow",
  [CardColor.GREEN]: "Green",
  [CardColor.BLUE]: "Blue",
};

/**
 * The colours a wild may name, in the order a player is offered them.
 */
export const COLOR_CHOICES: readonly CardColor[] = [
  CardColor.RED,
  CardColor.YELLOW,
  CardColor.GREEN,
  CardColor.BLUE,
];

/**
 * What is printed on a card of each kind. A number card prints its number.
 */
export const CARD_KIND_GLYPHS: Record<CardKind, string> = {
  [CardKind.UNSPECIFIED]: "?",
  [CardKind.NUMBER]: "",
  [CardKind.SKIP]: "⊘",
  [CardKind.REVERSE]: "⇄",
  [CardKind.DRAW_TWO]: "+2",
  [CardKind.WILD]: "W",
  [CardKind.WILD_DRAW_FOUR]: "+4",
};

export const CARD_KIND_LABELS: Record<CardKind, string> = {
  [CardKind.UNSPECIFIED]: "card",
  [CardKind.NUMBER]: "",
  [CardKind.SKIP]: "skip",
  [CardKind.REVERSE]: "reverse",
  [CardKind.DRAW_TWO]: "draw two",
  [CardKind.WILD]: "wild",
  [CardKind.WILD_DRAW_FOUR]: "wild draw four",
};

/**
 * Whether a card of this kind names a colour when played.
 */
export const CARD_KIND_IS_WILD: Record<CardKind, boolean> = {
  [CardKind.UNSPECIFIED]: false,
  [CardKind.NUMBER]: false,
  [CardKind.SKIP]: false,
  [CardKind.REVERSE]: false,
  [CardKind.DRAW_TWO]: false,
  [CardKind.WILD]: true,
  [CardKind.WILD_DRAW_FOUR]: true,
};

export const PLAY_DIRECTION_GLYPHS: Record<PlayDirection, string> = {
  [PlayDirection.UNSPECIFIED]: "",
  [PlayDirection.CLOCKWISE]: "↻",
  [PlayDirection.COUNTERCLOCKWISE]: "↺",
};

/**
 * How a game ended, as the phrase that follows the winner.
 */
export const RESULT_REASON_LABELS: Record<UnoResultReason, string> = {
  [UnoResultReason.UNSPECIFIED]: "",
  [UnoResultReason.HAND_EMPTIED]: "by playing every card",
  [UnoResultReason.OTHERS_WITHDREW]: "as the last player at the table",
};

/**
 * What a player is told about an action, or null when there is nothing to
 * say. An action that landed, a repeat of one that had already landed, and a
 * game that moved on before the action reached it all show the session that
 * came back and nothing else.
 */
export const COMMAND_OUTCOME_MESSAGES: Record<CommandOutcome, string | null> = {
  [CommandOutcome.UNSPECIFIED]: "The game answered something this build cannot read.",
  [CommandOutcome.APPLIED]: null,
  [CommandOutcome.ALREADY_APPLIED]: null,
  [CommandOutcome.SESSION_NOT_FOUND]: "There is no game at this table.",
  [CommandOutcome.NOT_A_PARTICIPANT]: "Only the seated players may act in this game.",
  [CommandOutcome.GAME_OVER]: "The game is over.",
  [CommandOutcome.VERSION_MOVED]: null,
  [CommandOutcome.OUT_OF_TURN]: "It is not your turn.",
  [CommandOutcome.ILLEGAL_ACTION]: "The rules refused that play.",
};
