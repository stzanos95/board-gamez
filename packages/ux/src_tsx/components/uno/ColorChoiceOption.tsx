import type { CardColor } from "@board-gamez/idl/uno/model/card_pb";
import ButtonBase from "@mui/material/ButtonBase";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type ReactElement } from "react";

import { CARD_PALETTES_BY_COLOR } from "./card_palette";

const OPTION_SX = {
  width: 96,
  height: 64,
  borderRadius: 2,
  boxShadow: 1,
  "&:hover": { boxShadow: 3 },
} as const;

export type ColorChoiceOptionProps = {
  readonly color: CardColor;
  readonly label: string;
  readonly onChoose: (color: CardColor) => void;
};

/**
 * One colour a wild may name.
 */
export const ColorChoiceOption = memo(function ColorChoiceOption(
  props: ColorChoiceOptionProps,
): ReactElement {
  const { color, label, onChoose } = props;
  const palette = CARD_PALETTES_BY_COLOR[color];

  const handleClick = useCallback(() => onChoose(color), [onChoose, color]);

  return (
    <ButtonBase onClick={handleClick} sx={{ ...OPTION_SX, bgcolor: palette.face }} aria-label={label}>
      <Typography component="span" fontWeight={700} sx={{ color: palette.ink }}>
        {label}
      </Typography>
    </ButtonBase>
  );
});
