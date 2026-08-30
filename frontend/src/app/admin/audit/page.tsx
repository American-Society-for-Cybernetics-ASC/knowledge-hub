"use client";

import { backendFetch } from "@/lib/api/client";
import {
  Input,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableSortLabel,
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
        params.append("before", before as string);
      }
      if (after) {
        params.append("after", after as string);
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
          return (
            <TableRow key={log.time}>
              <TableCell>{log.category}</TableCell>
              <TableCell>{log.time}</TableCell>
              <TableCell>{log.log}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
