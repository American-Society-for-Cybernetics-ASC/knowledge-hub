"use client";

import { backendFetch } from "@/lib/api/client";
import { MembershipSummary } from "@/types/membership";
import {
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import useSWR from "swr";
import MemberTypes from "./MembershipTypeConfig";
import MemberStatusChip from "@/components/features/membership/MemberStatusChip";
import { useAddError } from "@/components/layout/ErrorContext";

export default function Page() {
  return (
    <>
      <Typography variant={"h4"}>Memberships</Typography>
      <Typography variant={"h5"}>Member Types</Typography>
      <MemberTypes />
      <Typography variant={"h5"}>Members</Typography>
      <MembershipList />
    </>
  );
}

function MembershipList() {
  const addError = useAddError();
  const { data } = useSWR<MembershipSummary[]>(
    "/membership/admin/members",
    backendFetch,
    {
      onError: addError,
    },
  );

  return <>{data ? <MembershipTable data={data} /> : <Skeleton />}</>;
}

function MembershipTable({ data }: { data: MembershipSummary[] }) {
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Email</TableCell>
          <TableCell>Display Name</TableCell>
          <TableCell>Next Payment Due</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Cancelled</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {data.map((member) => {
          const due_date = new Date(member.due_date);
          return (
            <TableRow key={`membership-row-${member.email}`}>
              <TableCell>{member.email}</TableCell>
              <TableCell>{member.display_name}</TableCell>
              <TableCell>{due_date.toLocaleString()}</TableCell>
              <TableCell>
                <MemberStatusChip status={member.status} />
              </TableCell>
              <TableCell sx={{ textTransform: "capitalize" }}>
                {member.cancelled.toString()}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
