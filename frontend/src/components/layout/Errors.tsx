import { Alert } from "@mui/material";

export default function Errors({
  errors,
  setErrors,
}: {
  errors: string[];
  setErrors: (newErrors: string[]) => void;
}) {
  return errors.map((e, i) => (
    <Alert
      key={`error-${i}`}
      severity="error"
      onClose={() => {
        setErrors(errors.toSpliced(i, 1));
      }}
    >
      {e}
    </Alert>
  ));
}
