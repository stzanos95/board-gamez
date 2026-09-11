import { GameType } from "@board-gamez/idl/game/model/game_type_pb";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import {
  memo,
  useCallback,
  useState,
  type ChangeEvent,
  type FormEvent,
  type ReactElement,
} from "react";

import { CREATABLE_GAME_TYPES, GAME_TYPE_LABELS } from "../../lobby/table_labels";
import type { NewTableInput } from "../../lobby/use_create_table";

/**
 * How many seats a table may be opened with.
 *
 * The bounds are what the form offers. What a given game actually needs is the
 * lobby's to enforce, and the platform does not read a game's rules.
 */
const MINIMUM_SEATS = 2;
const MAXIMUM_SEATS = 8;
const DEFAULT_SEATS = 2;
const DEFAULT_GAME_TYPE = GameType.CHESS;

const CONTENT_SX = { pt: 1 } as const;

export type CreateTableDialogProps = {
  readonly isOpen: boolean;
  readonly isPending: boolean;
  readonly onCreate: (input: NewTableInput) => void;
  readonly onClose: () => void;
};

/**
 * Opening a table. The player who opens one takes its first seat.
 */
export const CreateTableDialog = memo(function CreateTableDialog(
  props: CreateTableDialogProps,
): ReactElement {
  const { isOpen, isPending, onCreate, onClose } = props;
  const [gameType, setGameType] = useState<GameType>(DEFAULT_GAME_TYPE);
  const [seatCount, setSeatCount] = useState(DEFAULT_SEATS);

  const handleGameTypeChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setGameType(Number(event.target.value) as GameType);
  }, []);

  const handleSeatCountChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setSeatCount(clampSeats(Number(event.target.value)));
  }, []);

  const handleSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      onCreate({ gameType, seatCount });
    },
    [gameType, seatCount, onCreate],
  );

  const gameOptions = CREATABLE_GAME_TYPES.map((option: GameType) => (
    <MenuItem key={option} value={option}>
      {GAME_TYPE_LABELS[option]}
    </MenuItem>
  ));

  const gameField = (
    <TextField select label="Game" value={gameType} onChange={handleGameTypeChange}>
      {gameOptions}
    </TextField>
  );

  const seatField = (
    <TextField
      type="number"
      label="Seats"
      value={seatCount}
      onChange={handleSeatCountChange}
      slotProps={{ htmlInput: { min: MINIMUM_SEATS, max: MAXIMUM_SEATS } }}
    />
  );

  return (
    <Dialog open={isOpen} onClose={onClose} fullWidth maxWidth="xs">
      <form onSubmit={handleSubmit}>
        <DialogTitle>New table</DialogTitle>
        <DialogContent sx={CONTENT_SX}>
          <Stack spacing={2}>
            {gameField}
            {seatField}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} variant="text">
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isPending}>
            Open table
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
});

function clampSeats(requested: number): number {
  if (!Number.isFinite(requested)) {
    return DEFAULT_SEATS;
  }
  return Math.min(MAXIMUM_SEATS, Math.max(MINIMUM_SEATS, Math.trunc(requested)));
}
