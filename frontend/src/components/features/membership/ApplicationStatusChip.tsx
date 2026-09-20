import { ApplicationStatus } from "@/types/membership";
import { Chip } from "@mui/material";

export default function MemberStatusChip({
  status,
}: {
  status: ApplicationStatus;
}) {
  switch (status) {
    case "approved":
      return <Chip label="Approved" color="success" />;
    case "pending":
      return <Chip label="Pending" color="default" />;
    case "denied":
      return <Chip label="Denied" color="error" />;
    case "revision_required":
      return <Chip label="Revision Requested" color="primary" />;
    default:
      break;
  }
}
