import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableContainer from "@mui/material/TableContainer";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

import type { TurnView } from "../../chess/chess_views";
import { TurnRow } from "./TurnRow";

const CONTAINER_SX = { border: 1, borderColor: "divider", maxHeight: 320 } as const;
const EMPTY_SX = { p: 2, color: "text.secondary", fontStyle: "italic" } as const;

export type MoveListProps = {
  readonly turns: readonly TurnView[];
};

/**
 * The moves played so far, one turn per row, in the notation the game wrote
 * them in.
 */
export const MoveList = memo(function MoveList(props: MoveListProps): ReactElement {
  const { turns } = props;

  const rows = turns.map((turn: TurnView) => (
    <TurnRow key={turn.number} number={turn.number} white={turn.white} black={turn.black} />
  ));

  const empty =
    turns.length > 0 ? null : (
      <Typography variant="body2" sx={EMPTY_SX}>
        No moves yet
      </Typography>
    );

  return (
    <TableContainer component={Paper} sx={CONTAINER_SX}>
      <Table size="small">
        <TableBody>{rows}</TableBody>
      </Table>
      {empty}
    </TableContainer>
  );
});
