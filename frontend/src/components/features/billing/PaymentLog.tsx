"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext } from "react";
import { Box, Button, Typography, Chip, CircularProgress, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import useSWR from "swr";

interface TransactionData {
    payment_id: string;
    kind: string;
    transaction_type: string;
    amount_value: number;
    currency: string;
}

interface PaymentRecord {
    payment_id: number;
    date: string;
    status: string;
    kind: string;
    transaction: TransactionData;
}

const fetcher = (url: string) => fetch(url, { credentials: "include" }).then((r) => r.json());

const statusType: Record<string, "success" | "warning" | "error" | "default"> = {
    success: "success",
    pending: "warning",
    failed: "error"
}

const formatAmount = (cents: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "usd" }).format(cents / 100);

const formatDate = (iso: string) =>
    new Date(iso).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
    });

export default function PaymentHistory() {
    const publicEnv = useContext(PublicEnv);

    const { data: payments, error: paymentsError, isLoading: paymentsLoading, mutate: fetchPayments } = useSWR<PaymentRecord[]>(`${publicEnv?.backendUrl}/payments`, fetcher);        

    return (
        <Box sx = {{ maxWidth: 700, display: "flex", flexDirection: "column", gap: 4 }}>
            <Box>
                <Typography variant="h5">Payment Log</Typography>

                <Button variant="contained" onClick={() => fetchPayments()}>
                    Refresh
                </Button>

                {paymentsError && (
                    <Typography color="error" variant="body2">
                        Failed to load payment history: {paymentsError.message}
                    </Typography>
                )}

                {paymentsLoading && (
                    <Box sx={{ display: "flex", justifyContent: "center", py: 3}}>
                        <CircularProgress size={24} />
                    </Box>
                )}

                {payments && (
                    <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Provider</TableCell>
                                    <TableCell align="right">Amount</TableCell>
                                    <TableCell>Status</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {payments.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={4} align="center">
                                            <Typography variant="body2" color="text.secondary" sx={{ py: 2 }} >
                                                No existing payments.
                                            </Typography>
                                        </TableCell>
                                    </TableRow>
                                )}
                                {payments.map((p) => (
                                    <TableRow key={p.payment_id} hover>
                                        <TableCell>{formatDate(p.date)}</TableCell>
                                        <TableCell sx={{ textTransform: "capitalize" }}>{p.transaction.transaction_type}</TableCell>
                                        <TableCell align="right">{formatAmount(p.transaction.amount_value)}</TableCell>
                                        <TableCell>
                                            <Chip label={p.status} size="small" color={statusType[p.status] ?? "default"} sx={{ textTransform: "capitalize" }}/>
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