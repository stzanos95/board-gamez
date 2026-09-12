import { ParticipantStateKind } from "@board-gamez/idl/game/model/participant_state_pb";

import {
  DEFAULT_PARTICIPANT_STATE_LABELS,
  type ParticipantStateLabels,
} from "../game/participant_state_labels";

const ONE_CARD = 1;

/**
 * What a participant's states are called at a UNO table.
 */
export const UNO_PARTICIPANT_STATE_LABELS: ParticipantStateLabels = {
  ...DEFAULT_PARTICIPANT_STATE_LABELS,
  [ParticipantStateKind.HOLDING]: (count: number) =>
    count === ONE_CARD ? "1 card" : `${count} cards`,
  [ParticipantStateKind.LAST_ONE]: () => "UNO!",
};
