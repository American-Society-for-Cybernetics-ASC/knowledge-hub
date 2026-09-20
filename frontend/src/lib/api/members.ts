import { backendFetch } from "./client";
import type { MemberProfile, MemberSearchResult, ProfileUpdate } from "@/types/member";

/** Loads the profile belonging to the authenticated member. */
export async function getMyProfile(): Promise<MemberProfile> {
  return backendFetch<MemberProfile>("/members/me");
}

/** Loads the profile for a member visible to the authenticated user. */
export async function getMemberProfile(
  memberId: number,
): Promise<MemberProfile> {
  return backendFetch<MemberProfile>(`/members/${memberId}`);
}

/** Searches current members by name, tags, or affiliations. */
export async function searchMembers(
  query: string,
): Promise<MemberSearchResult[]> {
  const params = new URLSearchParams({ q: query });

  return backendFetch<MemberSearchResult[]>(
    `/members?${params.toString()}`,
  );
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
