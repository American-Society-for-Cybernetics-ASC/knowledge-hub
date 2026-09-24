export interface ReadMember {
  user_id: number;
  due_date: string;
  member_type: string | null;
  active: boolean;
  cancelling: boolean;
}

export interface MembershipSummary {
  email: string;
  display_name: string;
  due_date: string;
  member_type: string | null;
  active: boolean;
  cancelling: boolean;
}

export interface MemberType {
  id: string;
  name: string;
  price: number;
}

export type ApplicationStatus =
  "pending" | "approved" | "denied" | "revision_required";

export interface ReadMembershipApplication {
  application_id: number;
  user_id: number;
  member_type: string | null;
  status: ApplicationStatus;
  submitted_at: string;
  last_edited: string;
  content: string;
}

export interface ReviseApplication {
  content: string;
}

export interface SubmitApplication {
  member_type_id: string;
  content: string;
}

export interface PurchaseMembership {
  application_id: number;
}

export interface UpdateMembership {
  application_id: number;
}
