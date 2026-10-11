"use client";

import { backendFetch } from "@/lib/api/client";
import {
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Skeleton,
} from "@mui/material";
import { useState } from "react";
import useSWR from "swr";
import PaymentOptionDialog from "./paymentOptionDialog";
import { Settings } from "@mui/icons-material";
import PaymentLog from "@/components/features/billing/PaymentLog";
import { useAddError } from "@/components/layout/ErrorContext";
import { AdminReadPaymentOption } from "@/types/payments";

export default function Page() {
  return (
    <>
      <Typography variant={"h4"}>Payments</Typography>

      <Typography variant={"h5"}>Config</Typography>
      <FormSection />

      <Typography variant={"h5"}>Payment Log</Typography>
      <PaymentLog />
    </>
  );
}

function FormSection() {
  const addError = useAddError();
  const { data, mutate } = useSWR<AdminReadPaymentOption[]>(
    "/payments/providers/admin",
    backendFetch,
    {
      onError: addError,
    },
  );

  if (data === undefined) {
    return <Skeleton sx={{ minHeight: 100 }} />;
  } else {
    return <ConfigForm data={data} mutate={mutate} />;
  }
}

function ConfigForm({
  data,
  mutate,
}: {
  data: AdminReadPaymentOption[];
  mutate: () => void;
}) {
  const [option, setOption] = useState<
    AdminReadPaymentOption | "new" | undefined
  >(undefined);

  return (
    <>
      {option !== undefined && (
        <PaymentOptionDialog
          option={option}
          isOpen
          onClose={() => setOption(undefined)}
          mutate={mutate}
        />
      )}
      <Grid container sx={{ width: "50%" }}>
        <Grid container direction={"row"} size={12} spacing={5}>
          <Typography variant={"h6"}>Payment Options</Typography>
          <Button
            title="New"
            variant="contained"
            onClick={() => setOption("new")}
          >
            New
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
              {data.map((option) => (
                <TableRow key={`payment-option-${option.id}`}>
                  <TableCell>{option.name}</TableCell>
                  <TableCell>{option.description}</TableCell>
                  <TableCell>{option.provider.provider_type}</TableCell>
                  <TableCell>
                    <Button
                      title={`Edit payment option: ${option.name}`}
                      onClick={() => setOption(option)}
                    >
                      <Settings />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Grid>
      </Grid>
    </>
  );
}
