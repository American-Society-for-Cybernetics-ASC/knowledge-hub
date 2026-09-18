"use client";

import { backendFetch } from "@/lib/api/client";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import useSWR from "swr";

interface AuditLog {
  category: string;
  log: string;
  time: string;
}

export default function AdminAuditPage() {
  const [before, setBefore] = useState<string | undefined>();
  const [after, setAfter] = useState<string | undefined>();
  // TODO: handle errors and loading nicer
  const { data, error, isLoading } = useSWR<AuditLog[]>(
    ["/audit_log", before, after],
    ([url, before, after]) => {
      const params = new URLSearchParams();
      if (before) {
        const beforeDate = new Date(before as string);
        params.append("before", beforeDate.toISOString());
      }
      if (after) {
        const afterDate = new Date(before as string);
        params.append("after", afterDate.toISOString());
      }
      return backendFetch(`${url}?${params}`);
    },
  );

  return (
    <>
      <Typography variant={"h5"}>Audit Logs</Typography>
      <form>
        {/* These text fields must not rerender every time we refetch */}
        <TextField
          type={"datetime-local"}
          onChange={(e) => setBefore(e.target.value)}
          label="Before"
          slotProps={{ inputLabel: { shrink: true } }}
        ></TextField>
        <TextField
          type={"datetime-local"}
          onChange={(e) => setAfter(e.target.value)}
          label="After"
          slotProps={{ inputLabel: { shrink: true } }}
        ></TextField>
      </form>
      <Inner data={data || []} />
    </>
  );
}

function Inner({ data }: { data: AuditLog[] }) {
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Category</TableCell>
          <TableCell>Time</TableCell>
          <TableCell>Log</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {data.map((log) => {
          const time = new Date(log.time);
          return (
            <TableRow key={log.time}>
              <TableCell>{log.category}</TableCell>
              <TableCell>{time.toLocaleString()}</TableCell>
              <TableCell>{log.log}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
