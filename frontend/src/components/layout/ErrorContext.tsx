"use client";

import { createContext, useState } from "react";
import Errors from "./Errors";

export type AddErrorContext = (error: string) => void;

export const AddErrorContext = createContext<AddErrorContext>((error) => {
  console.log(error);
});

export function ErrorWrapper({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<string[]>([]);

  return (
    <AddErrorContext value={(error) => setErrors([...errors, error])}>
      <Errors errors={errors} setErrors={setErrors} />
      {children}
    </AddErrorContext>
  );
}
