/**
 * Types for the authenticated member profile API.
 */

export interface ProfileIdentity {
    display_name: string | null;
    pronouns: string | null;
    location: string | null;
    website: string | null;
    orcid: string | null;
}

export interface ProfileContent {
    identity: ProfileIdentity;
    personal_statement: string | null;
    research_interests: string[];
    expertise: string[];

    // Not edited by initial page
    metadata: Record<string, unknown>; 
}

export interface MemberProfile {
    member_id: number;
    status: string;
    content: ProfileContent;
    tags: string[];
}

/**
 * Request body for PATCH /members/me
 * All properties are optional because of partial updates.
 */
export interface ProfileUpdate {
    identity?: Partial<ProfileIdentity>;
    personal_statement?: string | null;
    research_interests?: string[] | null;
    expertise?: string[] | null;
    tags?: string[] | null;
}