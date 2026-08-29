"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext, useEffect } from "react";
import { Box, Button, Typography } from "@mui/material";
import useSWR from "swr";

interface PaymentRecord {
    payment_id: number;
    date: string;
    status: string;
    amount: number;
}

export default function Page() {
    const publicEnv = useContext(PublicEnv);

    const fetcher = (url: string) => fetch(url, { credentials: "include" }).then((r) => r.json());

    const { data: payments, mutate: fetchPayments } = useSWR<PaymentRecord[]>(`${publicEnv?.backendUrl}/payments`, fetcher);

    useEffect(() => {
        fetchPayments();
    }, [fetchPayments, publicEnv?.backendUrl]);

    return (
        <Box sx = {{ maxWidth: 500, display: "flex", flexDirection: "column", gap: 2 }}>
            <Typography variant="h5">Payment Log</Typography>

            {payments?.map((p) => (
                <Typography key={p.payment_id}>
                    {p.date}  |  {(p.amount / 100).toFixed(2)}  |  {p.status}
                </Typography>
            ))}

            <Button variant="contained" onClick={() => fetchPayments()}>
                Refresh
            </Button>
        </Box>
    );
}