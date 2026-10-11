"use client";

import { useCallback, useEffect, useState } from "react";
import {
  dismissMemberMatch,
  getMemberMatching,
  optIntoMemberMatching,
  optOutOfMemberMatching,
} from "@/lib/api/member-matching";
import { useAddError } from "@/components/layout/ErrorContext";
import { getErrorMessage } from "@/lib/errors";
import type { MemberMatchingSuggestion } from "@/types/member-matching";

export function useMemberMatching() {
  const addError = useAddError();
  const [suggestions, setSuggestions] = useState<MemberMatchingSuggestion[]>(
    [],
  );
  const [optedOut, setOptedOut] = useState(false);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  // Only set when the initial load fails. Action failures use the snackbar.
  const [error, setError] = useState<string | null>(null);

  // Loads the current member's matching preference and suggestions.
  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await getMemberMatching();

      setSuggestions(result.suggestions);
      setOptedOut(result.opted_out);
    } catch (error) {
      setError(getErrorMessage(error, "Unable to load member matching data."));
    } finally {
      setLoading(false);
    }
  }, []);

  // Load suggestions when a component first uses this hook.
  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Removes a dismissed suggestion from the list after success.
  const dismiss = useCallback(
    async (suggestedMemberId: number) => {
      setActionLoading(true);

      try {
        await dismissMemberMatch(suggestedMemberId);

        setSuggestions((currentSuggestions) =>
          currentSuggestions.filter(
            (suggestion) => suggestion.member_id !== suggestedMemberId,
          ),
        );
      } catch (error) {
        addError(error);
      } finally {
        setActionLoading(false);
      }
    },
    [addError],
  );

  const optOut = useCallback(async () => {
    setActionLoading(true);

    try {
      const result = await optOutOfMemberMatching();

      setOptedOut(result.matching_opt_out);
      await refresh();
    } catch (error) {
      addError(error);
    } finally {
      setActionLoading(false);
    }
  }, [refresh, addError]);

  const optIn = useCallback(async () => {
    setActionLoading(true);

    try {
      const result = await optIntoMemberMatching();

      setOptedOut(result.matching_opt_out);
      await refresh();
    } catch (error) {
      addError(error);
    } finally {
      setActionLoading(false);
    }
  }, [refresh, addError]);

  return {
    suggestions,
    optedOut,
    loading,
    actionLoading,
    error,
    refresh,
    dismiss,
    optOut,
    optIn,
  };
}
