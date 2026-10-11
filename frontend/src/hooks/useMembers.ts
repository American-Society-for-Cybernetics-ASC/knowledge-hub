"use client";

import { useCallback, useEffect, useState } from "react";
import { getMemberProfile, getMyProfile } from "@/lib/api/members";
import type { MemberProfile } from "@/types/member";
import { getErrorMessage } from "@/lib/errors";

type ProfileTarget = "me" | number;

/**
 * Loads either the signed in member's profile or another member's profile.
 */
export function useMembers(target: ProfileTarget = "me") {
  const [profile, setProfile] = useState<MemberProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result =
        target === "me" ? await getMyProfile() : await getMemberProfile(target);

      setProfile(result);
    } catch (error) {
      setProfile(null);
      setError(getErrorMessage(error, "Unable to load the member profile."));
    } finally {
      setLoading(false);
    }
  }, [target]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    profile,
    loading,
    error,
    refresh,
  };
}
