import type { Color, PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Stack from "@mui/material/Stack";
import { memo, type ReactElement } from "react";

import { PromotionOption } from "./PromotionOption";

export type PromotionDialogProps = {
  readonly isOpen: boolean;
  readonly color: Color;
  readonly choices: readonly PieceType[];
  readonly onChoose: (pieceType: PieceType) => void;
  readonly onClose: () => void;
};

/**
 * What a pawn reaching the last rank becomes. The choices are the pieces the
 * game listed a move for, in the order it is customary to offer them.
 */
export const PromotionDialog = memo(function PromotionDialog(
  props: PromotionDialogProps,
): ReactElement {
  const { isOpen, color, choices, onChoose, onClose } = props;

  const options = choices.map((pieceType: PieceType) => (
    <PromotionOption key={pieceType} color={color} pieceType={pieceType} onChoose={onChoose} />
  ));

  return (
    <Dialog open={isOpen} onClose={onClose} maxWidth="xs">
      <DialogTitle>Promote to</DialogTitle>
      <DialogContent>
        <Stack direction="row" spacing={1}>
          {options}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="text">
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
});
