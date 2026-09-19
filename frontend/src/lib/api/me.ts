import { backendFetch } from "./client";

export interface CurrentUser {
  user_id: number;
  email: string;
  name: string | null;
  totp_enabled: boolean;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  return backendFetch<CurrentUser>("/auth/me");
}
