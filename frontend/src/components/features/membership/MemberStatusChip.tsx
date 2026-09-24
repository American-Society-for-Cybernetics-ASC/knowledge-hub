import { Chip } from "@mui/material";

export default function MemberStatusChip({ active, cancelling }: { active: boolean, cancelling: boolean }) {
  if (!active) {
      return <Chip label="Inactive" color="error" />; 
  }

  if (cancelling) {
      return <Chip label="Cancelling" color="warning" />; 
  }

  return <Chip label="Current" color="success" />;
}
