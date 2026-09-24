"use client";
import ApplicationStatusChip from "@/components/features/membership/ApplicationStatusChip";
import { AddErrorContext } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { ReadMembershipApplication } from "@/types/membership";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";
import { useContext } from "react";
import useSWR from "swr";

export default function UserApplicationModal({
  userId,
  userName,
  onClose,
}: {
  userId: number;
  userName: string;
  onClose: () => void;
}) {
  const addError = useContext(AddErrorContext);
  const { data, mutate } = useSWR<ReadMembershipApplication[]>(
    `/membership/application/admin/all/${userId}`,
    backendFetch,
    {
      onError: addError,
    },
  );

  return (
    <Dialog
      open={true}
      onClose={onClose}
      sx={{ alignSelf: "center", justifySelf: "center", minWidth: 400 }}
    >
      <DialogTitle>{userName}&apos;s Applications</DialogTitle>
      <DialogContent>
        {data !== undefined ? (
          <Stack>
            {data.map((application) => (
              <SingleApplication
                key={application.application_id}
                application={application}
                mutate={mutate}
              />
            ))}
          </Stack>
        ) : (
          <Skeleton />
        )}
      </DialogContent>
    </Dialog>
  );
}

function SingleApplication({
  application,
  mutate,
}: {
  application: ReadMembershipApplication;
  mutate: () => void;
}) {
  const lastEdited = new Date(application.last_edited);
  const addError = useContext(AddErrorContext);

  async function approve() {
    backendFetch(
      `/membership/application/${application.application_id}/approve`,
      { method: "POST" },
    )
      .then(() => mutate())
      .catch(addError);
  }
  async function deny() {
    backendFetch(`/membership/application/${application.application_id}/deny`, {
      method: "POST",
    })
      .then(() => mutate())
      .catch(addError);
  }
  async function request_revision() {
    backendFetch(
      `/membership/application/${application.application_id}/request-revision`,
      { method: "POST" },
    )
      .then(() => mutate())
      .catch(addError);
  }

  return (
    <Accordion>
      <AccordionSummary>
        <Stack direction={"row"} spacing={1}>
          <Typography>{lastEdited.toLocaleString()}</Typography>
          <Typography>
            {application.member_type || "<None Selected>"}
          </Typography>
          <ApplicationStatusChip status={application.status} />
        </Stack>
      </AccordionSummary>
      <AccordionDetails>
        <Stack direction={"row"} spacing={1}>
          <Button onClick={approve}>Approve</Button>
          <Button onClick={deny}>Deny</Button>
          <Button onClick={request_revision}>Request Revision</Button>
        </Stack>
        <Typography>{application.content}</Typography>
      </AccordionDetails>
    </Accordion>
  );
}
