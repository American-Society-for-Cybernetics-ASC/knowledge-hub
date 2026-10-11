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

export interface Affiliation {
  organisation: string;
  role: string | null;
  start_year: number | null;
  end_year: number | null;
}

export interface ProfilePublication {
  title: string;
  year: number | null;
  doi: string | null;
  url: string | null;
}

export type ProfileMetadata =
  | { type: "str"; value: string }
  | { type: "int"; value: number }
  | { type: "tag_list"; value: string[] }
  | { type: "affiliation"; value: Affiliation }
  | { type: "affiliations"; value: Affiliation[] }
  | { type: "publication"; value: ProfilePublication }
  | { type: "publications"; value: ProfilePublication[] };

export interface ProfileContent {
  identity: ProfileIdentity;
  personal_statement: string | null;
  research_interests: string[];
  expertise: string[];
  metadata: Record<string, ProfileMetadata>;
}

export interface MemberProfile {
  member_id: number;
  active: boolean;
  content: ProfileContent;
  tags: string[];
}

export interface MemberSearchResult {
  member_id: number;
  display_name: string | null;
  active: boolean;
  tags: string[];
  affiliations: Affiliation[];
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
  metadata?: Record<string, ProfileMetadata> | null;
  tags?: string[] | null;
}
