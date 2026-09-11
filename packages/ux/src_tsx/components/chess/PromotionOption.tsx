import type { Color, PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import ButtonBase from "@mui/material/ButtonBase";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, useCallback, type ReactElement } from "react";

import { PIECE_TYPE_LABELS } from "../../chess/chess_labels";
import { ChessPiece } from "./ChessPiece";

const OPTION_SX = {
  flexDirection: "column",
  p: 1,
  borderRadius: 1,
  border: 1,
  borderColor: "divider",
  width: 88,
  "&:hover, &:focus-visible": { borderColor: "primary.main", bgcolor: "action.hover" },
} as const;

const PIECE_BOX_SX = { width: 56, height: 56 } as const;

export type PromotionOptionProps = {
  readonly color: Color;
  readonly pieceType: PieceType;
  readonly onChoose: (pieceType: PieceType) => void;
};

export const PromotionOption = memo(function PromotionOption(
  props: PromotionOptionProps,
): ReactElement {
  const { color, pieceType, onChoose } = props;
  const handleClick = useCallback(() => onChoose(pieceType), [onChoose, pieceType]);

  return (
    <ButtonBase onClick={handleClick} sx={OPTION_SX} aria-label={PIECE_TYPE_LABELS[pieceType]}>
      <Stack alignItems="center" spacing={0.5}>
        <Stack sx={PIECE_BOX_SX}>
          <ChessPiece color={color} pieceType={pieceType} />
        </Stack>
        <Typography variant="caption">{PIECE_TYPE_LABELS[pieceType]}</Typography>
      </Stack>
    </ButtonBase>
  );
});
