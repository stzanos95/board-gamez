import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

const ROW_SX = { minHeight: 36 } as const;
const WITHDRAWN_SX = { color: "text.secondary", textDecoration: "line-through" } as const;

export type UnoPlayerRowProps = {
  readonly label: string;
  readonly cardCount: number;
  readonly isYou: boolean;
  readonly isToAct: boolean;
  readonly hasWithdrawn: boolean;
};

/**
 * One participant: their seat, how many cards they hold, and whether it is
 * their turn.
 */
export const UnoPlayerRow = memo(function UnoPlayerRow(props: UnoPlayerRowProps): ReactElement {
  const { label, cardCount, isYou, isToAct, hasWithdrawn } = props;

  const name = (
    <Typography variant="body2" fontWeight={isYou ? 700 : 400} sx={hasWithdrawn ? WITHDRAWN_SX : undefined}>
      {label}
    </Typography>
  );

  const count = hasWithdrawn ? (
    <Chip size="small" label="Left" variant="outlined" />
  ) : (
    <Chip size="small" label={`${cardCount} cards`} variant="outlined" />
  );

  const turnChip = isToAct ? <Chip size="small" label="To act" color="primary" /> : null;

  return (
    <Stack direction="row" spacing={1.5} alignItems="center" sx={ROW_SX}>
      {name}
      {count}
      {turnChip}
    </Stack>
  );
});
