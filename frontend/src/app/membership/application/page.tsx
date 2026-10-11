"use client";
import { backendFetch } from "@/lib/api/client";
import {
  PurchaseMembership,
  ReadMember,
  ReadMembershipApplication,
  UpdateMembership,
} from "@/types/membership";
import { Add, Settings } from "@mui/icons-material";
import {
  Button,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@mui/material";
import { useContext, useState } from "react";
import useSWR, { useSWRConfig } from "swr";
import CreateApplicationDialog from "./CreateApplicationDialog";
import EditApplicationDialog from "./EditApplicationDialog";
import ApplicationStatusChip from "@/components/features/membership/ApplicationStatusChip";
import { useRouter } from "next/navigation";
import { AddErrorContext } from "@/components/layout/ErrorContext";
import { ReadPayment } from "@/types/payments";

export default function Page() {
  const [application, setApplication] = useState<
    ReadMembershipApplication | "new"
  >();

  const { data, isLoading, mutate } = useSWR<ReadMembershipApplication[]>(
    "/membership/application/",
    backendFetch,
  );

  if (isLoading) {
    return <Skeleton />;
  }
  return (
    <>
      {application === "new" ? (
        <CreateApplicationDialog
          onClose={() => setApplication(undefined)}
          onSubmit={() => {
            setApplication(undefined);
            mutate();
          }}
        />
      ) : (
        application !== undefined && (
          <EditApplicationDialog
            application={application}
            onClose={() => setApplication(undefined)}
            onSubmit={() => {
              setApplication(undefined);
              mutate();
            }}
          />
        )
      )}
      <Button onClick={() => setApplication("new")}>
        <Add />
      </Button>
      <ApplicationTable
        data={data || []}
        edit={(application) => setApplication(application)}
      />
    </>
  );
}

function ApplicationTable({
  data,
  edit,
}: {
  data: ReadMembershipApplication[];
  edit: (application: ReadMembershipApplication) => void;
}) {
  const { data: memberData } = useSWR<ReadMember | null>(
    "/membership",
    backendFetch,
  );

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Membership Type</TableCell>
          <TableCell>Submitted At</TableCell>
          <TableCell>Last Edited</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Edit</TableCell>
          <TableCell>Action</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {data.map((application) => {
          const submittedAt = new Date(application.last_edited);
          const lastEdited = new Date(application.last_edited);
          return (
            <TableRow key={`application-row-${application.application_id}`}>
              <TableCell>{application.member_type}</TableCell>
              <TableCell>{submittedAt.toLocaleString()}</TableCell>
              <TableCell>{lastEdited.toLocaleString()}</TableCell>
              <TableCell>
                <ApplicationStatusChip status={application.status} />
              </TableCell>
              <TableCell>
                {(application.status === "pending" ||
                  application.status === "revision_required") && (
                  <Button
                    title="Revise application"
                    onClick={() => edit(application)}
                  >
                    <Settings />
                  </Button>
                )}
              </TableCell>
              <TableCell>
                {memberData !== undefined &&
                  application.status === "approved" && (
                    <ActionButton
                      application={application}
                      member={memberData}
                    />
                  )}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

function ActionButton({
  application,
  member,
}: {
  application: ReadMembershipApplication;
  member: ReadMember | null;
}) {
  const router = useRouter();
  const { mutate } = useSWRConfig();
  const addError = useContext(AddErrorContext);

  if (member === null) {
    async function createMembership() {
      const purchaseMembership: PurchaseMembership = {
        application_id: application.application_id,
      };
      await backendFetch<ReadPayment>("/membership/purchase", {
        method: "POST",
        body: JSON.stringify(purchaseMembership),
      })
        .then((payment) => router.push(`/billing/selectProvider/${payment.id}`))
        .catch(addError);
    }

    return (
      <Button variant="contained" onClick={createMembership}>
        Create Membership
      </Button>
    );
  }

  async function updateMembershipType() {
    const updateMembership: UpdateMembership = {
      application_id: application.application_id,
    };
    await backendFetch<ReadPayment>("/membership/update", {
      method: "POST",
      body: JSON.stringify(updateMembership),
    })
      .then(() => {
        mutate("/membership");
        router.push(`/membership`);
      })
      .catch(addError);
  }

  return (
    <Button variant="contained" onClick={updateMembershipType}>
      Set Member Type
    </Button>
  );
}
