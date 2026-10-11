"use client";

import { createContext, useCallback, useContext, useState } from "react";
import { getErrorMessage } from "@/lib/errors";
import Errors from "./Errors";

export type AddErrorContext = (error: unknown) => void;

export const AddErrorContext = createContext<AddErrorContext>((error) => {
  console.error(error);
});

export function useAddError(): AddErrorContext {
  return useContext(AddErrorContext);
}

export function ErrorWrapper({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<string[]>([]);

  const addError = useCallback((error: unknown) => {
    const message = getErrorMessage(error);
    setErrors((previous) => [...previous, message]);
  }, []);

  return (
    <AddErrorContext value={addError}>
      <Errors errors={errors} setErrors={setErrors} />
      {children}
    </AddErrorContext>
  );
}
