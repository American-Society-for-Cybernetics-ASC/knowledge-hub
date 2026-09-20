import { Alert, Snackbar } from "@mui/material";

export default function Errors({
  errors,
  setErrors,
}: {
  errors: string[];
  setErrors: (newErrors: string[]) => void;
}) {
  function onClose() {
    setErrors(errors.toSpliced(0, 1));
  }

  return (
    <Snackbar
      open={errors.length > 0}
      autoHideDuration={6000}
      onClose={(_, reason) => {
        if (reason !== "clickaway") {
          onClose();
        }
      }}
    >
      <Alert severity="error" onClose={onClose}>
        {errors.at(0) || ""}
      </Alert>
    </Snackbar>
  );
}
