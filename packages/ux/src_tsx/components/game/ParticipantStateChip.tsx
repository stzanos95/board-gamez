import Chip from "@mui/material/Chip";
import { memo, type ReactElement } from "react";

import type { ChipTone } from "../../lobby/table_labels";

export type ParticipantStateChipProps = {
  readonly label: string;
  readonly tone: ChipTone;
};

/**
 * One state a participant is in, as a rounded chip.
 */
export const ParticipantStateChip = memo(function ParticipantStateChip(
  props: ParticipantStateChipProps,
): ReactElement {
  const { label, tone } = props;

  return <Chip size="small" label={label} color={tone} variant="outlined" />;
});
