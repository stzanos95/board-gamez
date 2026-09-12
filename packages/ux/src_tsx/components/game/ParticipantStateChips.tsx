import Stack from "@mui/material/Stack";
import { memo, type ReactElement } from "react";

import type { ParticipantStateView } from "../../game/participant_state_views";
import { ParticipantStateChip } from "./ParticipantStateChip";

const ROW_SX = { flexWrap: "wrap", gap: 0.5 } as const;

export type ParticipantStateChipsProps = {
  readonly states: readonly ParticipantStateView[];
};

/**
 * Every state a participant is in, one chip after another to the right of
 * their name, in the order the game listed them.
 */
export const ParticipantStateChips = memo(function ParticipantStateChips(
  props: ParticipantStateChipsProps,
): ReactElement {
  const { states } = props;

  const chips = states.map((state: ParticipantStateView) => (
    <ParticipantStateChip key={state.key} label={state.label} tone={state.tone} />
  ));

  return (
    <Stack direction="row" alignItems="center" sx={ROW_SX}>
      {chips}
    </Stack>
  );
});
