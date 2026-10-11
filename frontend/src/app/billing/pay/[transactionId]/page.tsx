"use client";

import {
  Box,
  Skeleton,
  Typography,
} from "@mui/material";
import { use, useEffect} from "react";
import {
  ReadPayment,
  ReadTransaction,
} from "@/types/payments";
import useSWR from "swr";
import { backendFetch } from "@/lib/api/client";
import { useAddError } from "@/components/layout/ErrorContext";
import { useRouter } from "next/navigation";
import StripeCheckout from "@/components/features/billing/StripeCheckout";
import { formatAmount } from "@/lib/format";

interface PayPageProps {
  params: Promise<{ transactionId: string }>;
}

export default function PayPage({ params }: PayPageProps) {
  const { transactionId } = use(params);
  const addError = useAddError();
  const router = useRouter();

  const { data: transaction, error: transactionError } =
    useSWR<ReadTransaction>(
      `/payments/transactions/${transactionId}`,
      backendFetch,
      { shouldRetryOnError: false, onError: addError },
    );

  const { data: payment, error: paymentError } = useSWR<ReadPayment>(
    transaction ? `/payments/payments/${transaction.payment_id}` : null, 
    backendFetch, 
    { onError: addError },
  );

  const data = transaction?.data;
  const stripeData = data?.transaction_type === "stripe" ? data : null;
  const noActionRequired = payment !== undefined && payment.status !== "pending";
  const nothingToPay = transaction !== undefined && (stripeData === null || noActionRequired);

  useEffect(() => {
    if (nothingToPay) router.replace(`/billing/confirmed/${transactionId}`);
  }, [nothingToPay, transactionId, router]);

  return (
    <Box sx={{ p: 4, maxWidth: 480 }}>
      <Typography variant="h5">Pay for your Membership</Typography>
      <Typography variant="h6">
        Collaborative Knowledge Hub Membership
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Amount: {payment ? formatAmount(payment.amount) : "Invalid amount"}
      </Typography>

      {stripeData && payment?.status === "pending" ? (
        <StripeCheckout clientSecret={stripeData.client_secret} transactionId={transactionId}/>
      ) : (
        !transactionError && !paymentError && (
          <Skeleton variant="rounded" height={200} />
        )
      )}
    </Box>
  );
}
