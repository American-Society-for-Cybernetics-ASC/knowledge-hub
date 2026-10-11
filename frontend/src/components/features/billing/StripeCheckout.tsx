"use client";

import { Alert, Box, Button } from "@mui/material";
import {
  Elements,
  PaymentElement,
  useElements,
  useStripe,
} from "@stripe/react-stripe-js";
import { SyntheticEvent, useState } from "react";
import stripePromise from "@/lib/stripe";

function PaymentForm({ transactionId }: { transactionId: string }) {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: SyntheticEvent) {
    e.preventDefault();
    if (!stripe || !elements) return;

    setSubmitting(true);
    setError(null);

    const result = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/billing/confirmed/${transactionId}`,
      },
    });

    if (result.error) {
      setError(result.error.message ?? "Payment failed");
      setSubmitting(false);
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      <PaymentElement />
      {error && <Alert severity="error">{error}</Alert>}
      <Button
        type="submit"
        variant="contained"
        disabled={!stripe || submitting}
      >
        {submitting ? "Processing..." : "Pay"}
      </Button>
    </Box>
  );
}

export default function StripeCheckout({
  clientSecret,
  transactionId,
}: {
  clientSecret: string;
  transactionId: string;
}) {
  return (
    <Elements
      key={clientSecret}
      stripe={stripePromise}
      options={{ clientSecret }}
    >
      <PaymentForm transactionId={transactionId} />
    </Elements>
  );
}
