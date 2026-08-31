"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext, useEffect } from "react";
import { Box } from "@mui/material"
import useSWR from "swr";
import PaymentLog from "@/components/features/billing/PaymentLog";

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

export default function Page() {
    const publicEnv = useContext(PublicEnv);

    const { data: payments, error: paymentsError, isLoading: paymentsLoading, mutate: fetchPayments } = useSWR<PaymentRecord[]>(`${publicEnv?.backendUrl}/payments`, fetcher);

    useEffect(() => {
        fetchPayments();
    }, [fetchPayments, publicEnv?.backendUrl]);

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
            <PaymentLog/>
        </Box>
    );
}