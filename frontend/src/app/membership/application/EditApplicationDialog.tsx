"use client";
import { AddErrorContext } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { ReadMembershipApplication, ReviseApplication } from "@/types/membership";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  TextField,
} from "@mui/material";
import { useContext, useState } from "react";

export default function EditApplicationDialog({
  application,
  onClose,
  onSubmit
}: {
  application: ReadMembershipApplication,
  onClose: () => void;
  onSubmit: () => void;
}) {
  const addError = useContext(AddErrorContext);
  const [dirtyContent, setDirtyContent] = useState<string>();
  const content = dirtyContent ?? application.content;

  const readyToSubmit = dirtyContent !== undefined;

  async function handleSubmit() {
    if (!readyToSubmit) {
      return;
    }

    const reviseApplication: ReviseApplication = {
        content,
    };
    backendFetch(`/membership/application/${application.application_id}`, {
      method: "PATCH",
      body: JSON.stringify(reviseApplication),
    })
      .then(() => onSubmit())
      .catch((error) => addError(error.message));
  }

  return (
    <Dialog open={true} onClose={onClose}>
      <DialogTitle>Edit Membership Application</DialogTitle>
      <DialogContent>
        <form id="application-form" action={handleSubmit}>
          <Stack spacing={1}>
            <TextField
              required
              className="w-100"
              name="Content"
              type="text"
              value={content}
              onChange={(e) => setDirtyContent(e.target.value)}
              label="Content"
              variant="outlined"
              multiline
              rows={5}
            />
          </Stack>
        </form>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" color="error" onClick={onClose}>
          Cancel
        </Button>
        <Button
          disabled={!readyToSubmit}
          variant="contained"
          type={"submit"}
          form="application-form"
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
