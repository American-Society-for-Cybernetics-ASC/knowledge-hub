import { backendFetch } from "./client";
import type {
    DismissMatchResult,
    MatchingPreferenceResult,
    MemberMatchSuggestionsResult,
} from "@/types/member-matching";

export async function getMemberMatching(): Promise<MemberMatchSuggestionsResult> {
    return backendFetch<MemberMatchSuggestionsResult>("/member-matching");
}

export async function dismissMemberMatch(
    suggestedMemberId: number,
): Promise<DismissMatchResult> {
    return backendFetch<DismissMatchResult>("/member-matching/dismiss", {
        method: "POST",
        body: JSON.stringify({
            suggested_member_id: suggestedMemberId,
        }),
    });
}

export async function optOutOfMemberMatching(): Promise<MatchingPreferenceResult> {
    return backendFetch<MatchingPreferenceResult>("/member-matching/opt-out", {
        method: "POST",
    });
}

export async function optIntoMemberMatching(): Promise<MatchingPreferenceResult> {
    return backendFetch<MatchingPreferenceResult>("/member-matching/opt-in", {
        method: "POST",
    });
}