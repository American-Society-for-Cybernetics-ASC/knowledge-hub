"use client";
import { AddErrorContext } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { MemberType, SubmitApplication } from "@/types/membership";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  MenuItem,
  Select,
  Skeleton,
  Stack,
  TextField,
} from "@mui/material";
import { useContext, useState } from "react";
import useSWR from "swr";

export default function CreateApplicationDialog({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: () => void;
}) {
  const addError = useContext(AddErrorContext);
  const { data: memberTypes, isLoading: memberTypesIsLoading } = useSWR<
    MemberType[]
  >("/membership/member_type", backendFetch);
  const [memberTypeID, setMemberTypeID] = useState<string>("");
  const [content, setContent] = useState("");

  const readyToSubmit = memberTypeID !== "" && content.length > 0;

  async function handleSubmit() {
    if (!readyToSubmit) {
      return;
    }

    const application: SubmitApplication = {
      member_type_id: memberTypeID,
      content,
    };
    backendFetch("/membership/application", {
      method: "POST",
      body: JSON.stringify(application),
    })
      .then(() => onSubmit())
      .catch(addError);
  }

  return (
    <Dialog open={true} onClose={onClose}>
      <DialogTitle>Submit Membership Application</DialogTitle>
      <DialogContent>
        <form id="application-form" action={handleSubmit}>
          <Stack spacing={1}>
            {memberTypesIsLoading ? (
              <Skeleton />
            ) : (
              <FormControl fullWidth required>
                <Select
                  value={memberTypeID}
                  displayEmpty
                  onChange={(e) => setMemberTypeID(e.target.value)}
                >
                  <MenuItem value="">
                    <em>Select a member type</em>
                  </MenuItem>
                  {(memberTypes || []).map((member_type) => (
                    <MenuItem
                      key={`membertype-option-${member_type.id}`}
                      value={member_type.id}
                    >
                      {member_type.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <TextField
              required
              className="w-100"
              name="Content"
              type="text"
              value={content}
              onChange={(e) => setContent(e.target.value)}
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
          Submit
        </Button>
      </DialogActions>
    </Dialog>
  );
}
