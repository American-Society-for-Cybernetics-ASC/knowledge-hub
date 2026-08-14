"use client";

import { backendFetch } from "@/lib/api/client";
import { PaymentsConfig } from "@/types/payments";
import {
  Button,
  Grid,
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

  let body;
  if (isLoading) {
    body = <p>Loading</p>;
  } else if (error) {
    body = <p>Error: {error.toString()}</p>;
  } else if (!data) {
    body = <p>Error: No Data</p>;
  } else {
    body = <ConfigForm config={data} />;
  }

  return <>
      <Typography variant={"h5"}>Payments</Typography>
      {body}
  </>
}

function ConfigForm(props: { config: PaymentsConfig }) {
  const [config, setConfig] = useState(props.config);
  const [dirtyConfig, setDirtyConfig] = useState<Partial<PaymentsConfig>>({});
  const [providerModalIndex, setProviderModalIndex] = useState<
    number | undefined
  >(undefined);

  const submitEvent = () => {
    backendFetch<PaymentsConfig>("/payments/config", {
      method: "PATCH",
      body: JSON.stringify(currentConfig),
    }).then((response) => {
      setConfig(response);
      setDirtyConfig({});
    })
  };

  const currentConfig = { ...config, ...dirtyConfig };
  return (
    <>
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
      <Typography variant={"h5"}>Config</Typography>
      <form action={submitEvent}>
        <Grid container sx={{ width: "50%" }}>
          <Grid container direction={"row"} size={12} spacing={5}>
            <Typography variant={"h6"}>Payment Options</Typography>
            <Button
              variant="contained"
              size="small"
              onClick={() =>
                setProviderModalIndex(currentConfig.payment_options.length)
              }
            >
              <Add />
            </Button>
          </Grid>

          <Grid size={12}>
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
          </Grid>

          <Grid
            container
            direction="row"
            offset={6}
            size={6}
            sx={{ justifyContent: "flex-end" }}
            spacing={5}
          >
            <Button
              color="error"
              variant="contained"
              disabled={Object.keys(dirtyConfig).length === 0}
              onClick={() => setDirtyConfig({})}
            >
              Reset
            </Button>
            <Button
              variant="contained"
              disabled={Object.keys(dirtyConfig).length === 0}
              type="submit"
            >
              Submit
            </Button>
          </Grid>
        </Grid>
      </form>
    </>
  );
}
