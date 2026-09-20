"use client";

import { createContext, useState } from "react";
import Errors from "./Errors";

export type AddErrorContext = (error: string | { message: string }) => void;

export const AddErrorContext = createContext<AddErrorContext>((error) => {
  console.log(error);
});

export function ErrorWrapper({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<string[]>([]);

  return (
    <AddErrorContext
      value={(error) => {
        if (typeof error === "string") {
          setErrors([...errors, error]);
        } else {
          setErrors([...errors, error.message]);
        }
      }}
    >
      <Errors errors={errors} setErrors={setErrors} />
      {children}
    </AddErrorContext>
  );
}
