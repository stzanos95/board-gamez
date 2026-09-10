import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {
  memo,
  useCallback,
  useState,
  type ChangeEvent,
  type FormEvent,
  type ReactElement,
} from "react";

export type PlayerChipProps = {
  readonly displayName: string;
  readonly shortId: string;
  readonly onRename: (displayName: string) => void;
};

/**
 * Who this browser tab is playing as.
 *
 * A second tab is a second player, so the identifier is shown beside the name.
 */
export const PlayerChip = memo(function PlayerChip(props: PlayerChipProps): ReactElement {
  const { displayName, shortId, onRename } = props;
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(displayName);

  const handleEditClick = useCallback(() => {
    setDraft(displayName);
    setIsEditing(true);
  }, [displayName]);

  const handleDraftChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setDraft(event.target.value);
  }, []);

  const handleSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      onRename(draft);
      setIsEditing(false);
    },
    [draft, onRename],
  );

  const nameLabel = (
    <Typography variant="body2" fontWeight={600}>
      {displayName}
    </Typography>
  );

  const identifierLabel = (
    <Typography variant="caption" color="text.secondary">
      tab {shortId}
    </Typography>
  );

  const editButton = (
    <Button size="small" variant="text" onClick={handleEditClick}>
      Rename
    </Button>
  );

  const editForm = (
    <Stack component="form" direction="row" spacing={1} onSubmit={handleSubmit}>
      <TextField
        value={draft}
        onChange={handleDraftChange}
        label="Display name"
        autoFocus
        sx={{ width: 180 }}
      />
      <Button size="small" type="submit" variant="contained">
        Save
      </Button>
    </Stack>
  );

  if (isEditing) {
    return editForm;
  }

  return (
    <Stack direction="row" spacing={1.5} alignItems="center">
      <Stack>
        {nameLabel}
        {identifierLabel}
      </Stack>
      {editButton}
    </Stack>
  );
});
