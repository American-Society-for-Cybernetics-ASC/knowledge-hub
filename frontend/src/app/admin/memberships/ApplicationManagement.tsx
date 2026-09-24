"use client";

import { AddErrorContext } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { ApplicationSummary } from "@/types/membership";
import { RateReview } from "@mui/icons-material";
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
import useSWR from "swr";
import UserApplicationModal from "./UserApplicationModal";

export default function ApplicationManagement() {
  const addError = useContext(AddErrorContext);
  const [user, setUser] = useState<ApplicationSummary>();
  const { data } = useSWR<ApplicationSummary[]>(
    "/membership/application/admin/summary",
    backendFetch,
    {
      onError: addError,
    },
  );

  if (!data) {
    return <Skeleton />;
  }

  return (
    <>
      {user !== undefined && (
        <UserApplicationModal
          userId={user.user_id}
          userName={user.name || user.email}
          onClose={() => setUser(undefined)}
        ></UserApplicationModal>
      )}
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Email</TableCell>
            <TableCell>Display Name</TableCell>
            <TableCell>Last Application</TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((summary) => {
            const lastApplication = new Date(summary.last_application);
            return (
              <TableRow key={summary.user_id}>
                <TableCell>{summary.email}</TableCell>
                <TableCell>{summary.name}</TableCell>
                <TableCell>{lastApplication.toLocaleString()}</TableCell>
                <TableCell>
                  <Button onClick={() => setUser(summary)}>
                    <RateReview />
                  </Button>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </>
  );
}
