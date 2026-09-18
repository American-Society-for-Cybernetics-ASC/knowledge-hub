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
import { useState } from "react";
import useSWR from "swr";
import MemberTypes from "./MembershipTypeConfig";
import Errors from "@/components/layout/Errors";

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
  const [errors, setErrors] = useState<string[]>([]);
  const { data } = useSWR<MembershipSummary[]>(
    "/membership/admin/members",
    backendFetch,
    {
      onError: (err) => {
        setErrors([...errors, err.message]);
      },
    },
  );

  return (
    <>
      <Errors errors={errors} setErrors={setErrors} />
      {data ? <MembershipTable data={data} /> : <Skeleton />}
    </>
  );
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
          const membership_expires = new Date(member.membership_expires);
          return (
            <TableRow key={`membership-row-${member.email}`}>
              <TableCell>{member.email}</TableCell>
              <TableCell>{member.display_name}</TableCell>
              <TableCell>{membership_expires.toLocaleString()}</TableCell>
              <TableCell>{member.status}</TableCell>
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
