"use client";

import { useAddError } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { ReadMailSender } from "@/types/mail";
import { NotificationsConfig } from "@/types/notifications";
import {
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
  Typography,
} from "@mui/material";
import { useState } from "react";
import useSWR from "swr";

export default function Page() {
  return (
    <>
      <Typography variant={"h4"}>Notifications</Typography>
      <Typography variant={"h5"}>Config</Typography>
      <ConfigForm />
    </>
  );
}

function ConfigForm() {
  const addError = useAddError();
  const { data, mutate } = useSWR<NotificationsConfig>(
    "/notifications/config",
    backendFetch,
    {
      onError: addError,
    },
  );

  const { data: emailSenders } = useSWR<ReadMailSender[]>(
    "/mail/senders",
    backendFetch,
    {
      onError: addError,
    },
  );

  const [email_provider, setMailSender] = useState<string | "" | undefined>(
    undefined,
  );

  if (data === undefined) {
    return <Skeleton />;
  }
  const dirty: Partial<NotificationsConfig> = {
    email_provider,
  };
  const isDirty = Object.values(dirty).some((p) => p !== undefined);

  const current: NotificationsConfig = {
    email_provider:
      dirty.email_provider === undefined
        ? data.email_provider
        : dirty.email_provider,
  };

  function clear() {
    setMailSender(undefined);
  }
  async function handleSubmit() {
    if (isDirty) {
      const body: Partial<NotificationsConfig> = dirty;
      await backendFetch(`/notifications/config`, {
        method: "PATCH",
        body: JSON.stringify(body),
      })
        .then(async () => {
          await mutate();
          clear();
        })
        .catch(addError);
    }
  }

  return (
    <>
      <form id="config-form" action={handleSubmit}>
        <FormControl fullWidth required>
          <InputLabel id="email-sender-label">Email Sender</InputLabel>
          <Select
            labelId="email-sender-label"
            label="Email Sender"
            value={current.email_provider || "---"}
            onChange={(e) =>
              setMailSender(e.target.value === "---" ? "" : e.target.value)
            }
          >
            <MenuItem value="---">
              None (notifications will fall through!)
            </MenuItem>
            {(emailSenders || []).map((sender) => (
              <MenuItem key={`sender-option-${sender.id}`} value={sender.id}>
                {sender.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button
          variant="contained"
          disabled={!isDirty}
          type={"submit"}
          form="config-form"
        >
          Save
        </Button>
      </form>
    </>
  );
}
