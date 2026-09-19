"use client";

import { Box, Typography, Alert } from "@mui/material";
import { use, useEffect } from "react";


export default function ConfirmedPage({ 
  params 
}: { 
  params: Promise<{ transactionId: string }>; 
}) {
  const { transactionId } = use(params);

  if (!transactionId) {
    return (
        <Box sx={{ p: 4 }}>
            <Alert severity="error">No transaction to confirm.</Alert>
        </Box>
    );
  }

  return (
    <Box sx={{ p: 4, maxWidth: 480 }}>
      <Typography variant="h6">Payment Confirmed!</Typography>
      <Typography variant="body2" color="text.secondary">
        Transaction ID: {transactionId}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        You may now leave this page or close this window.
      </Typography>
    </Box>
  );
}
