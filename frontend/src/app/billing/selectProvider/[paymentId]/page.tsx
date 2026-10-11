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
import { use, useState } from "react";
import {
  ReadPayment,
  ReadPaymentOption,
} from "@/types/payments";
import useSWR from "swr";
import { backendFetch } from "@/lib/api/client";
import { useAddError } from "@/components/layout/ErrorContext";
import { useRouter } from "next/navigation";
import { createTransaction } from "@/lib/api/billing";
import { formatAmount } from "@/lib/format";

interface SelectProviderPageProps {
  params: Promise<{ paymentId: string }>;
}

export default function SelectProviderPage({ params }: SelectProviderPageProps) {
  const { paymentId } = use(params);
  const [payment, setPayment] = useState<ReadPayment | null>(null);
  const [providerId, setProviderId] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const addError = useAddError();
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

  function handleContinue() {
    const provider = providers?.find((p) => p.id === providerId);
    if (!provider) {
        addError("Select a payment provider");
        return;
    }

    setSubmitting(true);
    createTransaction(paymentId, provider.id)
        .then((transaction) =>
            router.replace(
                transaction.data.transaction_type === "stripe"
                    ? `/billing/pay/${transaction.id}`
                    : `/billing/confirmed/${transaction.id}`,
            )
        )
        .catch((e) => {
            addError(e);
            setSubmitting(false);
        });
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
            onChange={(e) => setProviderId(e.target.value)}
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

        <Button variant="contained" onClick={handleContinue} disabled={!providerId || submitting} sx={{ mt: 2}}>
            {submitting ? "Processing..." : "Continue"}
        </Button>
    </Box>
  );
}
