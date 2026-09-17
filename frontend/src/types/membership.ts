export type MemberStatus = "Current" | "Expired";

export interface ReadMember {
  user_id: number;
  membership_expires: string;
  member_type: string | null;
  status: MemberStatus;
  cancelled: boolean;
}
