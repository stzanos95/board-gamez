import type { TableStatus } from "@board-gamez/idl/lobby/model/table_pb";
import Chip from "@mui/material/Chip";
import { memo, type ReactElement } from "react";

import { TABLE_STATUS_LABELS, TABLE_STATUS_TONES } from "../../lobby/table_labels";

export type TableStatusChipProps = {
  readonly status: TableStatus;
};

export const TableStatusChip = memo(function TableStatusChip(
  props: TableStatusChipProps,
): ReactElement {
  const { status } = props;

  return (
    <Chip
      label={TABLE_STATUS_LABELS[status]}
      color={TABLE_STATUS_TONES[status]}
      variant="outlined"
    />
  );
});
