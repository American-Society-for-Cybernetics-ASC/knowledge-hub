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
import { ProductTypes, ReadPayment } from "@/types/payments";

const statusType: Record<string, "success" | "warning" | "error" | "default"> =
  {
    success: "success",
    pending: "warning",
    failed: "error",
  };

const formatAmount = (cents: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "usd" }).format(
    cents / 100,
  );

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

function productDescription(product: ProductTypes) {
  switch (product.product) {
    case "donation":
      return "Donation";
    case "create_membership":
      return "Initial membership";
    case "renew_membership":
      return "Membership renewal";
  }
}

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
                    <TableCell>{formatDate(p.time)}</TableCell>
                    <TableCell>{productDescription(p.product)}</TableCell>
                    <TableCell align="right">
                      {formatAmount(p.amount)}
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
