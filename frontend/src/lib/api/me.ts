import { backendFetch } from "./client";

export interface CurrentUser {
  user_id: number;
  email: string;
  name: string | null;
  totp_enabled: boolean;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const user = await backendFetch<CurrentUser | null>("/auth/me");

  if (user == null) {
    throw Error("Not authenticated");
  }

  return user;
}
