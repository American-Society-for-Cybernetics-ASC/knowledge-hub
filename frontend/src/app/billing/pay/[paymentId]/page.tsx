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
// import { createTransaction } from "@/lib/api/payments";

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
  const [providerID, setProviderID] = useState<string>("");
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

  async function handleMockPayment() {
    if (!providers) {
      addError("Select a payment provider");
      return;
    }

    const provider = providers.find((p) => p.id === providerID);

    if (!provider) {
      addError("Select a payment provider");
      return;
    }

    if (provider.provider_type !== "mock") {
      addError(`${provider.provider_type} is not supported right now`);
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
            value={providerID}
            displayEmpty
            onChange={(e) => setProviderID(e.target.value)}
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

      <Button variant="contained" onClick={handleMockPayment}>
        Pay
      </Button>
    </Box>
  );
}
