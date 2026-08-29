export interface MemberMatchingSuggestion {
    member_id: number;
    display_name: string | null;
    shared_tags: string[];
    score: number;
}

export interface MemberMatchSuggestionsResult {
    opted_out: boolean;
    suggestions: MemberMatchingSuggestion[];
}

export interface MatchingPreferenceResult {
    matching_opt_out: boolean;
}

export interface DismissMatchRequest {
    suggested_member_id: number;
}

export interface DismissMatchResult {
    suggested_member_id: number;
}