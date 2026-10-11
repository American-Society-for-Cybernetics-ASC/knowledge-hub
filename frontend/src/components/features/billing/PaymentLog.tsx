"use client";

import {
  Box,
  Button,
  Typography,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Skeleton,
  Alert,
} from "@mui/material";
import useSWR from "swr";
import { backendFetch } from "@/lib/api/client";
import { ReadPayment } from "@/types/payments";
import { formatAmount } from "@/lib/format";

const statusType: Record<string, "success" | "warning" | "error" | "default"> =
  {
    success: "success",
    pending: "warning",
    failed: "error",
  };

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

export default function PaymentLog() {
  const {
    data: payments,
    error: paymentsError,
    isLoading: paymentsLoading,
    mutate: fetchPayments,
  } = useSWR<ReadPayment[]>("/payments", backendFetch);

  return (
    <Box
      sx={{ maxWidth: 700, display: "flex", flexDirection: "column", gap: 4 }}
    >
      <Box>
        <Button variant="contained" onClick={() => fetchPayments()}>
          Refresh
        </Button>

        {paymentsError && (
          <Alert severity="error">
            Failed to load payment history: {paymentsError.message}
          </Alert>
        )}

        {paymentsLoading && <Skeleton sx={{ minHeight: 100 }} />}

        {payments && (
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {payments.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ py: 2 }}
                      >
                        No existing payments.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
                {payments.map((p) => (
                  <TableRow key={p.id} hover>
                    <TableCell>{formatDate(p.timestamp)}</TableCell>
                    <TableCell>{p.product_description}</TableCell>
                    <TableCell align="right">
                      {formatAmount(p.amount, p.currency)}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={p.status}
                        size="small"
                        color={statusType[p.status] ?? "default"}
                        sx={{ textTransform: "capitalize" }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Box>
  );
}
