"use client";

import {
  Box,
  Button,
  FormControl,
  MenuItem,
  Select,
  Skeleton,
  Typography,
} from "@mui/material";
import { use, useContext, useState } from "react";
import {
  CreateTransaction,
  ReadPayment,
  ReadPaymentOption,
  ReadTransaction,
} from "@/types/payments";
import useSWR from "swr";
import { backendFetch } from "@/lib/api/client";
import { AddErrorContext } from "@/components/layout/ErrorContext";
import { useRouter } from "next/navigation";
import { createTransaction } from "@/lib/api/billing";
import StripeCheckout from "@/components/features/billing/StripeCheckout";

interface PayPageProps {
  params: Promise<{ paymentId: string }>;
}

const formatAmount = (cents: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "usd" }).format(
    cents / 100,
  );

export default function PayPage({ params }: PayPageProps) {
  const { paymentId } = use(params);
  const [payment, setPayment] = useState<ReadPayment | null>(null);
  const [providerId, setProviderId] = useState<string>("");
  const [stripeSession, setStripeSession] = useState<{
    providerId: string;
    transactionId: string;
    clientSecret: string;
  } | null>(null)
  const addError = useContext(AddErrorContext);
  const router = useRouter();

  useSWR<ReadPayment>(`/payments/payments/${paymentId}`, backendFetch, {
    onSuccess: setPayment,
    onError: addError,
  });

  const { data: providers, isLoading: paymentOptionsLoading } = useSWR<
    ReadPaymentOption[]
  >("/payments/providers", backendFetch, {
    onError: addError,
  });

  const selectedProvider = providers?.find((p) => p.id === providerId)

  function handleProviderChange(id: string) {
    setProviderId(id);

    const provider = providers?.find((p) => p.id === id);
    if (provider?.service_name !== "stripe") return;

    createTransaction(paymentId, provider.id)
      .then((transaction) => {
        if (transaction.data.transaction_type !== "stripe") {
          addError("Unexpected transaction type for a Stripe provider");
          return;
        }
        setStripeSession({
          providerId: provider.id,
          transactionId: transaction.id,
          clientSecret: transaction.data.client_secret,
        });
      })
      .catch(addError);
  }

  function handleMockPayment() {
    if (!providers) {
      addError("Select a payment provider");
      return;
    }

    const provider = providers.find((p) => p.id === providerId);

    if (!provider) {
      addError("Select a payment provider");
      return;
    }

    if (provider.service_name !== "mock") {
      addError(`${provider.service_name} is not supported right now`);
      return;
    }

    const body: CreateTransaction = {
      payment_id: paymentId,
      provider_id: provider.id,
    };
    backendFetch<ReadTransaction>("/payments/transactions", {
      method: "POST",
      body: JSON.stringify(body),
    })
      .then((transaction) =>
        router.push(`/billing/confirmed/${transaction.id}`),
      )
      .catch(addError);
  }

  return (
    <Box sx={{ p: 4, maxWidth: 480 }}>
      <Typography variant="h5">Pay for your Membership</Typography>
      <Typography variant="h6">
        Collaborative Knowledge Hub Membership
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Amount: {payment ? formatAmount(payment.amount) : "Invalid amount"}
      </Typography>

      {paymentOptionsLoading ? (
        <Skeleton />
      ) : (
        <FormControl fullWidth required>
          <Select
            value={providerId}
            displayEmpty
            onChange={(e) => handleProviderChange(e.target.value)}
          >
            <MenuItem value="">
              <em>Select a payment provider</em>
            </MenuItem>
            {(providers || []).map((provider) => (
              <MenuItem
                key={`provider-option-${provider.id}`}
                value={provider.id}
              >
                {provider.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {selectedProvider?.service_name === "mock" && (
        <Button variant="contained" onClick={handleMockPayment}>
          Pay
        </Button>
      )}

      {stripeSession && stripeSession.providerId === providerId && (
        <Box sx={{ mt: 3 }}>
          <StripeCheckout
            clientSecret={stripeSession.clientSecret}
            transactionId={stripeSession.transactionId}
          />
        </Box>
      )}
    </Box>
  );
}
