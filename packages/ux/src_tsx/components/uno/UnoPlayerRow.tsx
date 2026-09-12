import Stack from "@mui/material/Stack";
import { memo, type ReactElement } from "react";

import type { ParticipantStateView } from "../../game/participant_state_views";
import { ParticipantNameBubble } from "../game/ParticipantNameBubble";
import { ParticipantStateChips } from "../game/ParticipantStateChips";

const ROW_SX = { minHeight: 36 } as const;

export type UnoPlayerRowProps = {
  readonly label: string;
  readonly isYou: boolean;
  readonly isToAct: boolean;
  readonly states: readonly ParticipantStateView[];
};

/**
 * One participant: their name, in a bubble while it is their turn, and every
 * state the game says they are in, to the right of it.
 */
export const UnoPlayerRow = memo(function UnoPlayerRow(props: UnoPlayerRowProps): ReactElement {
  const { label, isYou, isToAct, states } = props;

  const name = <ParticipantNameBubble label={label} isYou={isYou} isToAct={isToAct} />;

  const stateChips = <ParticipantStateChips states={states} />;

  return (
    <Stack direction="row" spacing={1.5} alignItems="center" sx={ROW_SX}>
      {name}
      {stateChips}
    </Stack>
  );
});
