import type {
  ParticipantState,
  ParticipantStateKind,
  ParticipantStatus,
} from "@board-gamez/idl/game/model/participant_state_pb";

import type { ChipTone } from "../lobby/table_labels";
import { PARTICIPANT_STATE_TONES, type ParticipantStateLabels } from "./participant_state_labels";

/**
 * A participant's states, in the shape a row of chips draws them.
 *
 * A derivation over data already in hand: the wording a game chose for each
 * kind, and the tone the platform gives it. Nothing here decides a state; the
 * game's rules did.
 */
export type ParticipantStateView = {
  readonly key: string;
  readonly kind: ParticipantStateKind;
  readonly label: string;
  readonly tone: ChipTone;
};

/**
 * The states of one participant, in the order the game listed them, minus
 * any the wording leaves unshown.
 */
export function toParticipantStateViews(
  statuses: readonly ParticipantStatus[],
  participant: number,
  labels: ParticipantStateLabels,
): readonly ParticipantStateView[] {
  const status = statuses.find((entry: ParticipantStatus) => entry.participant === participant);
  if (status === undefined) {
    return [];
  }
  return status.states
    .map((state: ParticipantState, index: number) => toParticipantStateView(state, index, labels))
    .filter((view: ParticipantStateView) => view.label.length > 0);
}

function toParticipantStateView(
  state: ParticipantState,
  index: number,
  labels: ParticipantStateLabels,
): ParticipantStateView {
  return {
    key: `${index}-${state.kind}`,
    kind: state.kind,
    label: labels[state.kind](state.count),
    tone: PARTICIPANT_STATE_TONES[state.kind],
  };
}
