import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import { memo, type ReactElement } from "react";

const NUMBER_SX = { color: "text.secondary", width: 40, fontVariantNumeric: "tabular-nums" } as const;
const MOVE_SX = { fontFamily: "monospace" } as const;

export type TurnRowProps = {
  readonly number: number;
  readonly white: string;
  readonly black: string;
};

export const TurnRow = memo(function TurnRow(props: TurnRowProps): ReactElement {
  const { number, white, black } = props;

  return (
    <TableRow>
      <TableCell sx={NUMBER_SX}>{number}.</TableCell>
      <TableCell sx={MOVE_SX}>{white}</TableCell>
      <TableCell sx={MOVE_SX}>{black}</TableCell>
    </TableRow>
  );
});
