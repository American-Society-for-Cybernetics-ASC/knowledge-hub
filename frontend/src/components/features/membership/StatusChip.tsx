import { MemberStatus } from "@/types/membership";
import { Chip } from "@mui/material";

export default function StatusChip({ status }: { status: MemberStatus }) {
  switch (status) {
    case "Current":
      return <Chip label="current" color="success" />;
    case "Expired":
      return <Chip label="current" color="error" />;
    default:
      break;
  }
}
