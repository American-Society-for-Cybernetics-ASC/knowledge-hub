import { AddErrorContext } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import {
  AdminPatchPaymentOption,
  AdminPostPaymentOption,
  AdminReadPaymentOption,
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
import { useContext, useEffect, useState } from "react";

export default function PaymentOptionDialog({
  isOpen,
  onClose,
  option,
  mutate,
}: {
  isOpen: boolean;
  onClose: () => void;
  option: AdminReadPaymentOption | "new";
  mutate: () => void;
}) {
  const addError = useContext(AddErrorContext);

  const base: Partial<AdminReadPaymentOption> = option === "new" ? {} : option;

  const [providerType, setProviderType] = useState<
    PaymentProvider["provider_type"]
  >(base.provider?.provider_type || "stripe");
  const [provider, setProvider] = useState<PaymentProvider | undefined>(
    base.provider,
  );
  const [name, setName] = useState<string | undefined>(base.name);
  const [description, setDescription] = useState<string | undefined>(
    base.description,
  );

  const dirty: Partial<AdminReadPaymentOption> = {
    name,
    description,
    provider,
  };

  const current: Partial<AdminReadPaymentOption> = { ...base, ...dirty };

  const isDirty = Object.values(dirty).some((p) => p !== undefined);
  const readyToCreate = provider !== undefined && name && description;
  const readyToPatch =
    isDirty && (provider !== undefined || name || description);

  async function handleSubmit() {
    if (option === "new" && readyToCreate) {
      const body: AdminPostPaymentOption = {
        provider,
        name,
        description,
      };
      await backendFetch("/payments/providers", {
        method: "POST",
        body: JSON.stringify(body),
      })
        .then(() => {
          onClose();
          mutate();
        })
        .catch(addError);
      return;
    }
    if (option !== "new" && readyToPatch) {
      const body: AdminPatchPaymentOption = dirty;
      await backendFetch(`/payments/providers/${option.id}`, {
        method: "PATCH",
        body: JSON.stringify(body),
      })
        .then(() => {
          onClose();
          mutate();
        })
        .catch(addError);
    }
  }

  let form;
  switch (providerType) {
    case "stripe":
      form = <StripeForm provider={provider} setProvider={setProvider} />;
      break;
    case "mock":
      form = <MockForm setProvider={setProvider} />;
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
                disabled={option !== "new"} // Currently can't change provider type.
                onChange={(e) =>
                  setProviderType(
                    e.target.value as PaymentProvider["provider_type"],
                  )
                }
              >
                <MenuItem value={"stripe"}>Stripe</MenuItem>
                <MenuItem value={"mock"}>Mock</MenuItem>
              </Select>
            </FormControl>
            <TextField
              required
              name="name"
              type="text"
              value={current.name || ""}
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
              value={current.description || ""}
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
          disabled={option == "new" ? !readyToCreate : !readyToPatch}
          type={"submit"}
          form="provider-form"
        >
          {option === "new" ? "Create" : "Save"}
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

function MockForm({
  setProvider,
}: {
  setProvider: (value?: PaymentProvider) => void;
}) {
  useEffect(() => {
    setProvider({
      provider_type: "mock",
    });
  }, [setProvider]);
  return <></>;
}
