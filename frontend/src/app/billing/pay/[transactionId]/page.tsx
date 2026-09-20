"use client";

import Link from "next/link";
import { Alert, Box, Button, Typography } from "@mui/material";
import { use, useEffect, useState } from "react";
import { getTransaction, ReadTransaction } from "@/lib/api/billing";
// import { createTransaction } from "@/lib/api/payments";

interface PayPageProps {
  params: Promise<{ transactionId: string }>;
}

const formatAmount = (cents: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "usd" }).format(cents / 100);

export default function PayPage({ params }: PayPageProps) {
  const { transactionId } = use(params);
  const [transaction, setTransaction] = useState<ReadTransaction | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTransaction(transactionId).then(setTransaction).catch((e) => setError(e.message));
  }, [transactionId]);

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>"
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 480 }}>
      <Typography variant="h5">Pay for your Membership</Typography>
      <Typography variant="h6">Collaborative Knowledge Hub Membership</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3}}>
        Amount: {transaction ? formatAmount(transaction.data.amount_value) : "Invalid amount"}
      </Typography>

      <Button variant="contained" component={Link} href={`/billing/confirmed/${transactionId}`}>
        Confirm
      </Button>
    </Box>
  );
}
