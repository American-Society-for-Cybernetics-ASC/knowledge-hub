"use client";

import { useCallback, useEffect, useState } from "react";
import { searchMembers } from "@/lib/api/members";
import type { MemberSearchResult } from "@/types/member";

// Delay to avoid sending API request for every keystroke.
const SEARCH_DEBOUNCE_MS = 300;

function getErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Unable to search for members.";
}

/**
 * Searches members after the user pauses typing.
 * Blank queries clear results without calling API.
 */
export function useMemberSearch(query: string) {
  const [results, setResults] = useState<MemberSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setResults([]);
      setError(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const searchResults = await searchMembers(trimmedQuery);
      setResults(searchResults);
    } catch (error) {
      setResults([]);
      setError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    if (!query.trim()) {
      void refresh();
      return;
    }

    setError(null);
    setLoading(true);

    const timeoutId = window.setTimeout(() => {
      void refresh();
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timeoutId);
  }, [query, refresh]);

  return {
    results,
    loading,
    error,
    refresh,
  };
}
