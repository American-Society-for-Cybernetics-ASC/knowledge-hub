import { Alert, Snackbar } from "@mui/material";

export default function Errors({
  errors,
  setErrors,
}: {
  errors: string[];
  setErrors: (newErrors: string[]) => void;
}) {
  return (
    <Snackbar open={errors.length > 0}>
      <Alert
        severity="error"
        onClose={() => {
          setErrors(errors.toSpliced(0, 1));
        }}
      >
        {errors.at(0) || ""}
      </Alert>
    </Snackbar>
  );
}
