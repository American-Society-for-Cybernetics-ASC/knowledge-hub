import { MemberStatus } from "@/types/membership";
import { Chip } from "@mui/material";

export default function MemberStatusChip({ status }: { status: MemberStatus }) {
  switch (status) {
    case "Current":
      return <Chip label="Current" color="success" />;
    case "Expired":
      return <Chip label="Expired" color="error" />;
    default:
      break;
  }
}
