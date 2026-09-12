import { ParticipantStateKind } from "@board-gamez/idl/game/model/participant_state_pb";

import type { ChipTone } from "../lobby/table_labels";

/**
 * What a participant's state is called on screen, and how it is toned.
 *
 * The platform names each kind; a game decides when it applies and may word
 * it in its own terms. Both records are keyed by the enum, so a kind added to
 * the schema and regenerated stops the build here until it has been given a
 * default wording and a tone.
 */

/**
 * The words for one kind, given the count it carries. An empty string means
 * the kind is not shown.
 */
export type ParticipantStateLabel = (count: number) => string;

export type ParticipantStateLabels = Record<ParticipantStateKind, ParticipantStateLabel>;

const NOT_SHOWN = "";

/**
 * The wording every game gets unless it supplies its own.
 */
export const DEFAULT_PARTICIPANT_STATE_LABELS: ParticipantStateLabels = {
  [ParticipantStateKind.UNSPECIFIED]: () => NOT_SHOWN,
  [ParticipantStateKind.HOLDING]: (count: number) => `${count} held`,
  [ParticipantStateKind.LAST_ONE]: () => "Last one",
  [ParticipantStateKind.WITHDRAWN]: () => "Left",
};

export const PARTICIPANT_STATE_TONES: Record<ParticipantStateKind, ChipTone> = {
  [ParticipantStateKind.UNSPECIFIED]: "default",
  [ParticipantStateKind.HOLDING]: "default",
  [ParticipantStateKind.LAST_ONE]: "warning",
  [ParticipantStateKind.WITHDRAWN]: "error",
};
