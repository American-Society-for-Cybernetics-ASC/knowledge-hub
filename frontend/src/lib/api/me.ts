import { backendFetch } from "./client";

export interface CurrentUser {
    user_id: number;
    email: string;
    name: string | null;
}

export async function getCurrentUser(): Promise<CurrentUser> {
    return backendFetch<CurrentUser>("/auth/me");
}