"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext, useState } from "react";
import { Box, Button, TextField, Typography, Chip, CircularProgress, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
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

export default function MembershipPage() {
    const publicEnv = useContext(PublicEnv);
    const [amount, setAmount] = useState("");
    const [memberId, setMemberId] = useState("00000000-0000-4000-8000-000000000000");
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    const { data: payments, error: paymentsError, isLoading: paymentsLoading, mutate: fetchPayments } = useSWR<PaymentRecord[]>(`${publicEnv?.backendUrl}/payments`, fetcher);

    const handleCreatePaymentIntent = async () => {
        console.log("publicEnv:", publicEnv)
        setLoading(true);
        setStatus("Creating payment intent...");
        try {
            const res = await fetch(`${publicEnv?.backendUrl}/payments`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    member_id: memberId,
                    amount: Number(amount)
                })
            });
            const data = await res.json();
            if (!res.ok) {
                setStatus(`Error (${res.status}): ${JSON.stringify(data)}`)
            } else {
                setStatus(JSON.stringify(data, null, 2));
                fetchPayments();
            }
        } catch (err) {
            setStatus(`Request failed: ${err instanceof Error ? err.message : String(err)}`);
        } finally {
            setLoading(false)
        }
        
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

    return (
        <Box sx = {{ maxWidth: 700, display: "flex", flexDirection: "column", gap: 4 }}>
            <Box sx = {{ maxWidth: 500, display: "flex", flexDirection: "column", gap: 2 }}>
                <Typography variant="h5">Donate</Typography>
                
                <TextField
                    label="Amount" 
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    type="number"            
                />

                <Button variant="contained" onClick={handleCreatePaymentIntent} disabled={loading}>
                    {loading ? "Processing..." : "Donate"}
                </Button>

                <TextField label="Status" value={status} multiline minRows={4} fullWidth/>
            </Box>

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