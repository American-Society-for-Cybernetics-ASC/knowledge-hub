"use client";

import { backendFetch } from "@/lib/api/client";
import { PaymentsConfig } from "@/types/payments";
import {
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import React, { useState } from "react";
import useSWR from "swr";
import PaymentOptionDialog from "./paymentOptionDialog";
import { Add, Settings } from "@mui/icons-material";

export default function Page() {
  const { data, error, isLoading } = useSWR<PaymentsConfig>(
    "/payments/config",
    backendFetch,
  );

  if (isLoading) {
    return <p>Loading</p>;
  }
  if (error) {
    return <p>Error: {error.toString()}</p>;
  }
  if (!data) {
    return <p>Error: no data</p>;
  }
  return <ConfigForm config={data} />;
}

function ConfigForm({ config }: { config: PaymentsConfig }) {
  const [dirtyConfig, setDirtyConfig] = useState<Partial<PaymentsConfig>>({});
  const [providerModalIndex, setProviderModalIndex] = useState<
    number | undefined
  >(undefined);

  const submitEvent = (event: React.SubmitEvent) => {
    event.preventDefault();
  };

  const currentConfig = { ...config, ...dirtyConfig };
  return (
    <>
      <Typography variant={"h4"}>Payments</Typography>
      {providerModalIndex !== undefined && (
        <PaymentOptionDialog
          option={currentConfig.payment_options[providerModalIndex]}
          submit={(provider) => {
            const newPaymentOptions = currentConfig.payment_options.toSpliced(
              providerModalIndex,
              1,
              provider,
            );
            setDirtyConfig({
              ...dirtyConfig,
              payment_options: newPaymentOptions,
            });
            setProviderModalIndex(undefined);
          }}
          isOpen
          onClose={() => setProviderModalIndex(undefined)}
        />
      )}
      <Button
        onClick={() =>
          setProviderModalIndex(currentConfig.payment_options.length)
        }
      >
        <Add />
      </Button>
      <form onSubmit={submitEvent}>
        <Box sx={{ width: "50%" }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Provider</TableCell>
                <TableCell>Edit</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {currentConfig.payment_options.map((option, i) => (
                <TableRow key={`payment-option-${i}`}>
                  <TableCell>{option.name}</TableCell>
                  <TableCell>{option.description}</TableCell>
                  <TableCell>{option.provider.provider_type}</TableCell>
                  <TableCell>
                    <Button onClick={() => setProviderModalIndex(i)}>
                      <Settings />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <Button>Submit</Button>
        </Box>
      </form>
    </>
  );
}
