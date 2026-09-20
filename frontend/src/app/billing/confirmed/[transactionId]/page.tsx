"use client";

import { confirmTransaction } from "@/lib/api/billing";
import { Box, Typography, Alert, CircularProgress } from "@mui/material";
import { use, useState, useEffect } from "react";

type State =
  | { status: "verifying" }
  | { status: "success" }
  | { status: "failed"; message: string };

export default function ConfirmedPage({
  params,
}: {
  params: Promise<{ transactionId: string }>;
}) {
  const { transactionId } = use(params);
  const [state, setState] = useState<State>({ status: "verifying" });

  useEffect(() => {
    confirmTransaction(transactionId)
      .then(() => setState({ status: "success" }))
      .catch((e) => setState({ status: "failed", message: e.message }));
  }, [transactionId]);

  return (
    <Box sx={{ p: 4, maxWidth: 480 }}>
      <Typography variant="body2" color="text.secondary">
        Transaction ID: {transactionId}
      </Typography>
      {state.status === "verifying" && <CircularProgress />}
      {state.status === "success" && (
        <>
          <Typography variant="h6">Payment Confirmed!</Typography>
          <Typography variant="body2" color="text.secondary">
            You may now leave this page or close this window.
          </Typography>
        </>
      )}
      {state.status === "failed" && (
        <Alert severity="error">{state.message}</Alert>
      )}
    </Box>
  );
}
