import { useAddError } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import {
  PatchMailSender,
  PostMailSender,
  MailProvider,
  ReadMailSender,
  GmailAppPasswordMailProvider,
  TestMailProvider,
} from "@/types/mail";
import { Info } from "@mui/icons-material";
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  LinearProgress,
  Link,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

export default function MailSenderDialog({
  isOpen,
  onClose,
  option: sender,
  mutate,
}: {
  isOpen: boolean;
  onClose: () => void;
  option: ReadMailSender | "new";
  mutate: () => void;
}) {
  const addError = useAddError();

  const base: Partial<ReadMailSender> = sender === "new" ? {} : sender;

  const [providerType, setProviderType] = useState<
    MailProvider["provider_type"]
  >(base.provider?.provider_type || "gmail_app_password");
  const [provider, setProvider] = useState<MailProvider | undefined>(
    base.provider,
  );
  const [name, setName] = useState<string | undefined>(base.name);
  const [description, setDescription] = useState<string | undefined>(
    base.description,
  );

  const [testing, setTesting] = useState<boolean>(false);

  const dirty: Partial<ReadMailSender> = {
    name,
    description,
    provider,
  };

  const current: Partial<ReadMailSender> = { ...base, ...dirty };

  const isDirty = Object.values(dirty).some((p) => p !== undefined);
  const readyToCreate = provider !== undefined && name && description;
  const readyToPatch =
    isDirty && (provider !== undefined || name || description);

  async function handleSubmit() {
    if (sender === "new" && readyToCreate) {
      const body: PostMailSender = {
        provider,
        name,
        description,
      };
      await backendFetch("/mail/senders", {
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
    if (sender !== "new" && readyToPatch) {
      const body: PatchMailSender = dirty;
      await backendFetch(`/mail/senders/${sender.id}`, {
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
    case "gmail_app_password":
      form = (
        <GmailAppPasswordForm provider={provider} setProvider={setProvider} />
      );
      break;
    default:
      form = <></>;
      break;
  }

  return (
    <Dialog open={isOpen} onClose={onClose} fullWidth>
      <DialogTitle>Configure Mail Sender</DialogTitle>
      <DialogContent dividers={true}>
        {testing && provider && (
          <TestingDialog
            onClose={() => setTesting(false)}
            provider={provider}
          ></TestingDialog>
        )}
        <form id="provider-form" action={handleSubmit}>
          <Stack spacing={1}>
            <FormControl fullWidth required>
              <InputLabel id="provider-type-label">Provider</InputLabel>
              <Select
                labelId="provider-type-label"
                label="Provider"
                value={providerType}
                disabled={sender !== "new"} // Currently can't change provider type.
                onChange={(e) =>
                  setProviderType(
                    e.target.value as MailProvider["provider_type"],
                  )
                }
              >
                <MenuItem value={"gmail_app_password"}>
                  Gmail (via App Password)
                </MenuItem>
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
          disabled={current.provider === undefined}
          form="provider-form"
          onClick={() => setTesting(true)}
        >
          Test Provider
        </Button>
        <Button
          variant="contained"
          disabled={sender == "new" ? !readyToCreate : !readyToPatch}
          type={"submit"}
          form="provider-form"
        >
          {sender === "new" ? "Create" : "Save"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function TestingDialog({
  onClose,
  provider,
}: {
  onClose: () => void;
  provider: MailProvider;
}) {
  const [email, setEmail] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [testResult, setTestResult] = useState<true | string | undefined>(
    undefined,
  );

  async function handleTest() {
    if (email !== undefined) {
      setLoading(true);
      const body: TestMailProvider = {
        email,
        provider,
      };
      await backendFetch("/mail/test_provider", {
        method: "POST",
        body: JSON.stringify(body),
      })
        .then(() => {
          setTestResult(true);
        })
        .catch((e) => setTestResult(e.message));
      setLoading(false);
    }
  }

  return (
    <Dialog open={true} onClose={onClose}>
      <DialogContent>
        <Stack spacing={6}>
          {testResult === true ? (
            <Alert variant="outlined" severity="success">
              Email sent without errors. Check your inbox, accounting for
              possible delays with the service.
            </Alert>
          ) : testResult !== undefined ? (
            <Alert variant="outlined" severity="error">
              Error sending email: {testResult}
            </Alert>
          ) : loading ? (
            <LinearProgress />
          ) : (
            <></>
          )}
          <TextField
            required
            name="email"
            type="email"
            value={email || ""}
            onChange={(e) => setEmail(e.target.value)}
            label="Email"
            variant="outlined"
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button variant="contained" color="error" onClick={onClose}>
          Cancel
        </Button>
        <Button
          variant="contained"
          disabled={email === undefined}
          onClick={handleTest}
        >
          Test
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function GmailAppPasswordForm({
  provider,
  setProvider,
}: {
  provider: MailProvider | undefined;
  setProvider: (value?: MailProvider) => void;
}) {
  const asGmailAPProvider = (
    provider && provider.provider_type === "gmail_app_password" ? provider : {}
  ) as Partial<GmailAppPasswordMailProvider>;

  const [google_username, setGoogleUsername] = useState(
    asGmailAPProvider.google_username || "",
  );
  const [app_password, setAppPassword] = useState(
    asGmailAPProvider.app_password || "",
  );

  useEffect(() => {
    const provider: MailProvider | undefined =
      (google_username &&
        app_password && {
          provider_type: "gmail_app_password",
          google_username,
          app_password,
        }) ||
      undefined;
    setProvider(provider);
  }, [google_username, app_password, setProvider]);

  return (
    <>
      <TextField
        required
        name="google_username"
        type="email"
        value={google_username}
        onChange={(e) => {
          setGoogleUsername(e.target.value);
        }}
        label="Google Username (email)"
        variant="outlined"
      />
      <Grid container direction="row">
        <Grid size={11}>
          <TextField
            required
            type="password"
            name="app_password"
            value={app_password}
            onChange={(e) => {
              setAppPassword(e.target.value);
            }}
            label="App Password"
            variant="outlined"
            fullWidth
          />
        </Grid>
        <Grid>
          <Link href="https://support.google.com/accounts/answer/185833">
            <Info></Info>
          </Link>
        </Grid>
      </Grid>
    </>
  );
}
