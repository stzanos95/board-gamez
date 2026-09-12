import type { CardColor } from "@board-gamez/idl/uno/model/card_pb";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Stack from "@mui/material/Stack";
import { memo, type ReactElement } from "react";

import { CARD_COLOR_LABELS, COLOR_CHOICES } from "../../uno/uno_labels";
import { ColorChoiceOption } from "./ColorChoiceOption";

const CONTENT_SX = { pb: 3 } as const;

export type ColorChoiceDialogProps = {
  readonly isOpen: boolean;
  readonly onChoose: (color: CardColor) => void;
  readonly onClose: () => void;
};

/**
 * The colour a wild names, asked for when one is played.
 */
export const ColorChoiceDialog = memo(function ColorChoiceDialog(
  props: ColorChoiceDialogProps,
): ReactElement {
  const { isOpen, onChoose, onClose } = props;

  const options = COLOR_CHOICES.map((color: CardColor) => (
    <ColorChoiceOption
      key={color}
      color={color}
      label={CARD_COLOR_LABELS[color]}
      onChoose={onChoose}
    />
  ));

  return (
    <Dialog open={isOpen} onClose={onClose} maxWidth="xs">
      <DialogTitle>Choose a colour</DialogTitle>
      <DialogContent sx={CONTENT_SX}>
        <Stack direction="row" spacing={1.5}>
          {options}
        </Stack>
      </DialogContent>
    </Dialog>
  );
});
