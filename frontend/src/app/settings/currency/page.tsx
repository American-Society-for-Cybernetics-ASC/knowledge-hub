"use client";

import { AddErrorContext } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { ReadCurrency } from "@/types/payments";
import { MenuItem, Select, Skeleton } from "@mui/material";
import { useContext } from "react";
import useSWR from "swr";

export default function CurrencySettingsPage() {
  const addError = useContext(AddErrorContext);
  const { data, mutate } = useSWR<ReadCurrency>(
    "/payments/currency",
    backendFetch,
    { onError: addError },
  );

  function handleChange(currency: string) {
    backendFetch<ReadCurrency>("/payments/currency", {
      method: "PUT",
      body: JSON.stringify({ currency }),
    })
      .then((updated) => mutate(updated, false))
      .catch(addError);
  }

  return (
    <div className="max-w-md p-6">
      <h2 className="text-lg font-semibold mb-4">Currency</h2>
      {data ? (
        <Select
          fullWidth
          value={data.currency}
          onChange={(e) => handleChange(e.target.value)}
        >
          {data.supported_currencies.map((label) => (
            <MenuItem key={label} value={label}>
              {label.toUpperCase()}
            </MenuItem>
          ))}
        </Select>
      ) : (
        <Skeleton />
      )}
    </div>
  );
}
