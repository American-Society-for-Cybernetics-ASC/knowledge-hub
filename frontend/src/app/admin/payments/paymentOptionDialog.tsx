import {
  PaymentOption,
  PaymentProvider,
  StripePaymentProvider,
} from "@/types/payments";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

export default function PaymentOptionDialog({
  isOpen,
  onClose,
  option,
  onSubmit,
}: {
  isOpen: boolean;
  onClose: () => void;
  option: PaymentOption | undefined;
  onSubmit: (value: PaymentOption) => void;
}) {
  const [providerType, setProviderType] = useState<
    PaymentProvider["provider_type"]
  >(option?.provider.provider_type || "stripe");
  const [provider, setProvider] = useState<PaymentProvider | undefined>(
    option?.provider,
  );
  const [name, setName] = useState<string>(option?.name || "");
  const [description, setDescription] = useState<string>(
    option?.description || "",
  );

  const readyToSubmit = provider && name && description;

  const handleSubmit = () => {
    if (readyToSubmit) {
      onSubmit({
        name,
        description,
        provider,
      });
    }
  };

  let form;
  switch (providerType) {
    case "stripe":
      form = <StripeForm provider={provider} setProvider={setProvider} />;
      break;
    default:
      form = <></>;
      break;
  }

  return (
    <Dialog open={isOpen} onClose={onClose} fullWidth>
      <DialogTitle>Configure Payment Option</DialogTitle>
      <DialogContent dividers={true}>
        <form id="provider-form" action={handleSubmit}>
          <Stack spacing={1}>
            <FormControl fullWidth required>
              <InputLabel id="provider-type-label">Provider</InputLabel>
              <Select
                labelId="provider-type-label"
                label="Provider"
                value={providerType}
                onChange={(e) =>
                  setProviderType(
                    e.target.value as PaymentProvider["provider_type"],
                  )
                }
              >
                <MenuItem value={"stripe"}>Stripe</MenuItem>
              </Select>
            </FormControl>
            <TextField
              required
              name="name"
              type="text"
              value={name}
              slotProps={{ htmlInput: { maxLength: 16 } }}
              onChange={(e) => setName(e.target.value)}
              label="Name"
              variant="outlined"
            />
            <TextField
              required
              name="description"
              type="text"
              fullWidth
              value={description}
              slotProps={{ htmlInput: { maxLength: 100 } }}
              onChange={(e) => setDescription(e.target.value)}
              label="Description"
              multiline
              rows={4}
              variant="outlined"
            />
            {form}
          </Stack>
        </form>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" color="error" onClick={onClose}>
          Cancel
        </Button>
        <Button
          variant="contained"
          disabled={!readyToSubmit}
          type={"submit"}
          form="provider-form"
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function StripeForm({
  provider,
  setProvider,
}: {
  provider: PaymentProvider | undefined;
  setProvider: (value?: PaymentProvider) => void;
}) {
  const asStripeProvider = (
    provider && provider.provider_type === "stripe" ? provider : {}
  ) as Partial<StripePaymentProvider>;

  const [api_key, setApiKey] = useState(asStripeProvider.api_key || "");
  const [publishable_key, setPublishableKey] = useState(
    asStripeProvider.publishable_key || "",
  );
  const [webhook_secret, setWebhookSecret] = useState(
    asStripeProvider.webhook_secret || "",
  );

  useEffect(() => {
    const provider: PaymentProvider | undefined =
      (api_key &&
        publishable_key &&
        webhook_secret && {
          provider_type: "stripe",
          api_key,
          publishable_key,
          webhook_secret,
        }) ||
      undefined;
    setProvider(provider);
  }, [api_key, publishable_key, webhook_secret, setProvider]);

  return (
    <>
      <TextField
        required
        name="api_key"
        value={api_key}
        onChange={(e) => {
          setApiKey(e.target.value);
        }}
        label="Api Key"
        variant="outlined"
      />
      <TextField
        required
        name="publishable_key"
        value={publishable_key}
        onChange={(e) => {
          setPublishableKey(e.target.value);
        }}
        label="Publishable Key"
        variant="outlined"
      />
      <TextField
        required
        name="webhook_secret"
        value={webhook_secret}
        onChange={(e) => {
          setWebhookSecret(e.target.value);
        }}
        label="Webhook Secret"
        variant="outlined"
      />
    </>
  );
}
