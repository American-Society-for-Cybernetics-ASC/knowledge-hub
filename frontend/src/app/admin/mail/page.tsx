"use client";

import { useAddError } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { FailedEmail, ReadMailSender } from "@/types/mail";
import { Settings } from "@mui/icons-material";
import {
  Button,
  Grid,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useState } from "react";
import useSWR from "swr";
import MailSenderDialog from "./MailSenderDialog";

export default function Page() {
  return (
    <>
      <Typography variant={"h4"}>Mail</Typography>
      <ProviderForm />
      <Typography variant={"h5"}>Failed Emails</Typography>
      <DeadLetters />
    </>
  );
}

function DeadLetters() {
  const addError = useAddError();
  const { data } = useSWR<FailedEmail[]>("/mail/failed", backendFetch, {
    onError: addError,
  });

  if (!data) {
    return <Skeleton />;
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Last Sent</TableCell>
          <TableCell>Retries</TableCell>
          <TableCell>Subject</TableCell>
          <TableCell>Sender</TableCell>
          <TableCell>Recipients</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {data.map((email) => {
          const last_sent = new Date(email.last_sent);
          return (
            <TableRow key={email.id}>
              <TableCell>{last_sent.toISOString()}</TableCell>
              <TableCell>{email.retries}</TableCell>
              <TableCell>{email.email.subject}</TableCell>
              <TableCell>{email.email.sender}</TableCell>
              <TableCell>{email.email.recipients.join("\n")}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

function ProviderForm() {
  const addError = useAddError();
  const { data, mutate } = useSWR<ReadMailSender[]>(
    "/mail/senders",
    backendFetch,
    {
      onError: addError,
    },
  );
  const [sender, setSender] = useState<ReadMailSender | "new" | undefined>(
    undefined,
  );

  if (data === undefined) {
    return <Skeleton sx={{ minHeight: 100 }} />;
  }

  return (
    <>
      {sender !== undefined && (
        <MailSenderDialog
          option={sender}
          isOpen
          onClose={() => setSender(undefined)}
          mutate={mutate}
        />
      )}
      <Grid container sx={{ width: "50%" }}>
        <Grid container direction={"row"} size={12} spacing={5}>
          <Typography variant={"h5"}>Mail Senders</Typography>
          <Button
            title="New"
            variant="contained"
            onClick={() => setSender("new")}
          >
            New
          </Button>
        </Grid>

        <Grid size={12}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Provider</TableCell>
                <TableCell>Edit</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((sender) => (
                <TableRow key={`payment-option-${sender.id}`}>
                  <TableCell>{sender.name}</TableCell>
                  <TableCell>{sender.description}</TableCell>
                  <TableCell>{sender.provider.provider_type}</TableCell>
                  <TableCell>
                    <Button
                      title={`Edit mail sender: ${sender.name}`}
                      onClick={() => setSender(sender)}
                    >
                      <Settings />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Grid>
      </Grid>
    </>
  );
}
