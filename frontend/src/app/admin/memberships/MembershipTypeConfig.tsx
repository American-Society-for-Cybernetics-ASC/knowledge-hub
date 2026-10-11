import { useAddError } from "@/components/layout/ErrorContext";
import { backendFetch } from "@/lib/api/client";
import { MemberType } from "@/types/membership";
import { Add, Settings } from "@mui/icons-material";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from "@mui/material";
import { useState } from "react";
import useSWR from "swr";

export default function MemberTypes() {
  const { data, mutate } = useSWR<MemberType[]>(
    "/membership/member_type",
    backendFetch,
  );
  const [dialog, setDialog] = useState<MemberType | "new" | undefined>();

  return (
    <>
      {dialog && (
        <EditMemberTypeDialog
          memberType={dialog}
          onClose={() => setDialog(undefined)}
          mutate={mutate}
        />
      )}
      <Button variant="contained" size="small" onClick={() => setDialog("new")}>
        <Add />
      </Button>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Edit</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(data || []).map((type, i) => (
            <TableRow key={`member-type-${i}`}>
              <TableCell>{type.name}</TableCell>
              <TableCell>{type.price}</TableCell>
              <TableCell>
                <Button
                  title={`Edit member type: ${type.name}`}
                  onClick={() => setDialog(type)}
                >
                  <Settings />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}

function EditMemberTypeDialog({
  memberType,
  onClose,
  mutate,
}: {
  memberType: MemberType | "new";
  onClose: () => void;
  mutate: () => void;
}) {
  const addError = useAddError();
  const base: Partial<MemberType> = memberType === "new" ? {} : memberType;
  const [name, setName] = useState<string>();
  const [price, setPrice] = useState<string>();
  const dirty: Partial<MemberType> = {
    name: name,
    price: price ? Number(price) : undefined,
  };
  const current = {
    id: base.id,
    price: dirty.price || base.price,
    name: dirty.name || base.name,
  };

  const isDirty = Object.values(dirty).some((p) => p !== undefined);
  const readyToSubmit =
    isDirty &&
    current.name &&
    current.price !== undefined &&
    (memberType === "new" || current.id);

  async function handleSubmit() {
    if (readyToSubmit) {
      if (memberType === "new") {
        await backendFetch("/membership/member_type", {
          method: "POST",
          body: JSON.stringify(dirty),
        })
          .then(() => {
            onClose();
            mutate();
          })
          .catch(addError);
      } else {
        await backendFetch(`/membership/member_type/${memberType.id}`, {
          method: "PATCH",
          body: JSON.stringify(dirty),
        })
          .then(() => {
            onClose();
            mutate();
          })
          .catch(addError);
      }
    }
  }

  return (
    <Dialog open={true} onClose={onClose} fullWidth>
      <DialogTitle>Configure Member Type</DialogTitle>
      <DialogContent dividers={true}>
        <form id="member-type-form" action={handleSubmit}>
          <Stack spacing={1}>
            <TextField
              required
              name="name"
              type="text"
              value={current.name || ""}
              slotProps={{ htmlInput: { maxLength: 64 } }}
              onChange={(e) => setName(e.target.value)}
              label="Name"
              variant="outlined"
            />
            <TextField
              required
              name="price"
              type="number"
              value={current.price || ""}
              slotProps={{ htmlInput: { maxLength: 16 } }}
              onChange={(e) => setPrice(e.target.value)}
              label="Price"
              variant="outlined"
            />
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
          form="member-type-form"
        >
          {memberType === "new" ? "Create" : "Save"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
