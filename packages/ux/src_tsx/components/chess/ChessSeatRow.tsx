import type { ChessSeatChoice } from "@board-gamez/idl/chess/model/table_pb";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type ReactElement } from "react";

const ROW_SX = { minHeight: 40 } as const;
const SIDE_SX = { width: 72, fontWeight: 700 } as const;
const OPEN_SX = { color: "text.secondary", fontStyle: "italic" } as const;

const OPEN_LABEL = "Open";

export type ChessSeatRowProps = {
  readonly colorLabel: string;
  readonly occupantLabel: string;
  readonly isMine: boolean;
  readonly isOpen: boolean;
  readonly choice: ChessSeatChoice | null;
  readonly isBusy: boolean;
  readonly onTakeSeat: (choice: ChessSeatChoice) => void;
};

/**
 * One side of the board, and who plays it.
 *
 * The button appears only when the game offered this seat to the viewer; the
 * choice it sends is the one that was offered, unchanged.
 */
export const ChessSeatRow = memo(function ChessSeatRow(props: ChessSeatRowProps): ReactElement {
  const { colorLabel, occupantLabel, isMine, isOpen, choice, isBusy, onTakeSeat } = props;

  const handleTakeSeatClick = useCallback(() => {
    if (choice !== null) {
      onTakeSeat(choice);
    }
  }, [choice, onTakeSeat]);

  const side = (
    <Typography variant="body2" sx={SIDE_SX}>
      {colorLabel}
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
        Play as {colorLabel}
      </Button>
    );

  return (
    <Stack direction="row" spacing={2} alignItems="center" sx={ROW_SX}>
      {side}
      {occupant}
      {takeButton}
    </Stack>
  );
});
