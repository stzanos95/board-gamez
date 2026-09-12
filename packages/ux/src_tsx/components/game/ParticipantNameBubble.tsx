import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

const BUBBLE_SX = {
  display: "inline-flex",
  alignItems: "center",
  px: 1,
  py: 0.25,
  borderRadius: 1,
  bgcolor: "success.main",
  color: "success.contrastText",
} as const;

export type ParticipantNameBubbleProps = {
  readonly label: string;
  readonly isYou: boolean;
  readonly isToAct: boolean;
};

/**
 * A participant's name.
 *
 * While it is their turn the name sits in a squared bubble in the success
 * colour, which is what says whose turn it is without a word for it. The
 * rest of the time it is plain text.
 */
export const ParticipantNameBubble = memo(function ParticipantNameBubble(
  props: ParticipantNameBubbleProps,
): ReactElement {
  const { label, isYou, isToAct } = props;

  const name = (
    <Typography variant="body2" component="span" fontWeight={isYou ? 700 : 400}>
      {label}
    </Typography>
  );

  if (!isToAct) {
    return name;
  }
  return (
    <Box component="span" sx={BUBBLE_SX} aria-label={`${label}, to act`}>
      {name}
    </Box>
  );
});
