import type { UnoSeatChoice } from "@board-gamez/idl/uno/model/table_pb";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type ReactElement } from "react";

const ROW_SX = { minHeight: 40 } as const;
const SEAT_SX = { width: 72, fontWeight: 700 } as const;
const OPEN_SX = { color: "text.secondary", fontStyle: "italic" } as const;

const OPEN_LABEL = "Open";

export type UnoSeatRowProps = {
  readonly seatLabel: string;
  readonly occupantLabel: string;
  readonly isMine: boolean;
  readonly isOpen: boolean;
  readonly choice: UnoSeatChoice | null;
  readonly isBusy: boolean;
  readonly onTakeSeat: (choice: UnoSeatChoice) => void;
};

/**
 * One seat at the table, and who holds it.
 *
 * The button appears only when the game offered this seat to the viewer; the
 * choice it sends is the one that was offered, unchanged.
 */
export const UnoSeatRow = memo(function UnoSeatRow(props: UnoSeatRowProps): ReactElement {
  const { seatLabel, occupantLabel, isMine, isOpen, choice, isBusy, onTakeSeat } = props;

  const handleTakeSeatClick = useCallback(() => {
    if (choice !== null) {
      onTakeSeat(choice);
    }
  }, [choice, onTakeSeat]);

  const seat = (
    <Typography variant="body2" sx={SEAT_SX}>
      {seatLabel}
    </Typography>
  );

  const occupant = isOpen ? (
    <Typography variant="body2" sx={OPEN_SX}>
      {OPEN_LABEL}
    </Typography>
  ) : (
    <Typography variant="body2" fontWeight={isMine ? 700 : 400}>
      {occupantLabel}
    </Typography>
  );

  const takeButton =
    choice === null ? null : (
      <Button size="small" variant="contained" onClick={handleTakeSeatClick} disabled={isBusy}>
        Sit here
      </Button>
    );

  return (
    <Stack direction="row" spacing={2} alignItems="center" sx={ROW_SX}>
      {seat}
      {occupant}
      {takeButton}
    </Stack>
  );
});
