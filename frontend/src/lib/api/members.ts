import { backendFetch } from "./client";
import type { MemberProfile, ProfileUpdate } from "@/types/member";

/** Loads the profile belonging to the authenticated member. */
export async function getMyProfile(): Promise<MemberProfile> {
  return backendFetch<MemberProfile>("/members/me");
}

/** Applies the supplied changes to the authenticated member's profile. */
export async function updateMyProfile(
  update: ProfileUpdate,
): Promise<MemberProfile> {
  return backendFetch<MemberProfile>("/members/me", {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}
