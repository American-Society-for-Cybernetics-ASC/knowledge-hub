"use client";

import { useCallback, useEffect, useState } from "react";
import {
    dismissMemberMatch,
    getMemberMatching,
    optIntoMemberMatching,
    optOutOfMemberMatching,
} from "@/lib/api/member-matching";
import type { MemberMatchingSuggestion } from "@/types/member-matching";

function getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
        return error.message;
    }

    return "Unable to complete member matching request.";
}

export function useMemberMatching() {
    const [suggestions, setSuggestions] = useState<MemberMatchingSuggestion[]>([]);
    const [optedOut, setOptedOut] = useState(false);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
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
            setError(getErrorMessage(error));
        } finally {
            setLoading(false);
        }
    }, []);

    // Load suggestions when a component first uses this hook.
    useEffect(() => {
        void refresh();
    }, [refresh]);

    // Removes a dismissed suggestion from the list after success.
    const dismiss = useCallback(async (suggestedMemberId: number) => {
        setActionLoading(true);
        setError(null);

        try {
            await dismissMemberMatch(suggestedMemberId);

            setSuggestions((currentSuggestions) =>
                currentSuggestions.filter(
                    (suggestion) => suggestion.member_id !== suggestedMemberId
                )
            );
        } catch (error) {
            setError(getErrorMessage(error));
        } finally {
            setActionLoading(false);
        }
    }, []);

    const optOut = useCallback(async () => {
        setActionLoading(true);
        setError(null);

        try {
            const result = await optOutOfMemberMatching();

            setOptedOut(result.matching_opt_out);
            await refresh();
        } catch (error) {
            setError(getErrorMessage(error));
        } finally {
            setActionLoading(false);
        }
    }, [refresh]);

    const optIn = useCallback(async () => {
        setActionLoading(true);
        setError(null);

        try {
            const result = await optIntoMemberMatching();

            setOptedOut(result.matching_opt_out);
            await refresh();
        } catch (error) {
            setError(getErrorMessage(error));
        } finally {
            setActionLoading(false);
        }
    }, [refresh]);

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