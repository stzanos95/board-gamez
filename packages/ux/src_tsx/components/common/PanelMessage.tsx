import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import CircularProgress from "@mui/material/CircularProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { memo, type ReactElement } from "react";

export type PanelMessageProps = {
  readonly severity: "info" | "warning" | "error";
  readonly title: string;
  readonly detail: string | null;
};

/**
 * A screen with nothing to draw yet, or a reason it has nothing to draw.
 */
export const PanelMessage = memo(function PanelMessage(props: PanelMessageProps): ReactElement {
  const { severity, title, detail } = props;

  const body = detail === null ? null : <Typography variant="body2">{detail}</Typography>;

  return (
    <Alert severity={severity} variant="outlined">
      <AlertTitle>{title}</AlertTitle>
      {body}
    </Alert>
  );
});

export type LoadingPanelProps = {
  readonly label: string;
};

export const LoadingPanel = memo(function LoadingPanel(props: LoadingPanelProps): ReactElement {
  const { label } = props;

  return (
    <Stack direction="row" spacing={2} alignItems="center" sx={{ py: 4 }}>
      <CircularProgress size={20} />
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
    </Stack>
  );
});
