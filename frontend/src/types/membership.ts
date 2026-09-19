export type MemberStatus = "Current" | "Expired";

export interface ReadMember {
  user_id: number;
  due_date: string;
  member_type: string | null;
  status: MemberStatus;
  cancelled: boolean;
}

export interface MembershipSummary {
  email: string;
  display_name: string;
  due_date: string;
  member_type: string | null;
  status: MemberStatus;
  cancelled: boolean;
}

export interface MemberType {
  id: string;
  name: string;
  price: number;
}
