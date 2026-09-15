"use client";

import Link from "next/link";
import { useMembers } from "@/hooks/useMembers";
import type {
  Affiliation,
  MemberProfile as MemberProfileData,
  ProfileMetadata,
  ProfilePublication,
} from "@/types/member";

interface MemberProfileProps {
  target: "me" | number;
  isOwnProfile?: boolean;
}

function displayName(profile: MemberProfileData): string {
  return profile.content.identity.display_name?.trim() || "Unnamed member";
}

function formatMetadataLabel(key: string): string {
  return key.replace(/[_-]+/g, " ").replace(/\b\w/g, (letter) =>
    letter.toUpperCase(),
  );
}

function TagList({ tags }: { tags: string[] }) {
  if (tags.length === 0) {
    return <p className="text-sm text-gray-600">None listed.</p>;
  }

  return (
    <ul className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <li
          key={tag}
          className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-800"
        >
          {tag}
        </li>
      ))}
    </ul>
  );
}

function formatAffiliationYears(affiliation: Affiliation): string | null {
  if (affiliation.start_year && affiliation.end_year) {
    return `${affiliation.start_year} - ${affiliation.end_year}`;
  }

  if (affiliation.start_year) {
    return `${affiliation.start_year} - present`;
  }

  if (affiliation.end_year) {
    return `Until ${affiliation.end_year}`;
  }

  return null;
}

function AffiliationDetails({ affiliation }: { affiliation: Affiliation }) {
  const years = formatAffiliationYears(affiliation);

  return (
    <div>
      <p className="font-medium text-gray-900">{affiliation.organisation}</p>

      {(affiliation.role || years) && (
        <p className="mt-1 text-sm text-gray-600">
          {[affiliation.role, years].filter(Boolean).join(" . ")}
        </p>
      )}
    </div>
  );
}

function PublicationDetails({
  publication,
}: {
  publication: ProfilePublication;
}) {
  return (
    <div>
      <p className="font-medium text-gray-900">{publication.title}</p>

      {publication.year && (
        <p className="mt-1 text-sm text-gray-600">{publication.year}</p>
      )}

      <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-sm">
        {publication.doi && (
          <a
            href={`https://doi.org/${publication.doi}`}
            target="_blank"
            rel="noreferrer"
            className="text-blue-600 hover:underline"
          >
            DOI
          </a>
        )}

        {publication.url && (
          <a
            href={publication.url}
            target="_blank"
            rel="noreferrer"
            className="text-blue-600 hover:underline"
          >
            View publication
          </a>
        )}
      </div>
    </div>
  );
}

function MetadataValue({ metadata }: { metadata: ProfileMetadata }) {
  switch (metadata.type) {
    case "str":
    case "int":
      return <p className="whitespace-pre-wrap text-gray-700">{metadata.value}</p>;

    case "tag_list":
      return <TagList tags={metadata.value} />;

    case "affiliation":
      return <AffiliationDetails affiliation={metadata.value} />;

    case "affiliations":
      return (
        <div className="space-y-3">
          {metadata.value.map((affiliation, index) => (
            <AffiliationDetails
              key={`${affiliation.organisation}-${index}`}
              affiliation={affiliation}
            />
          ))}
        </div>
      );

    case "publication":
      return <PublicationDetails publication={metadata.value} />;

    case "publications":
      return (
        <div className="space-y-3">
          {metadata.value.map((publication, index) => (
            <PublicationDetails
              key={`${publication.title}-${index}`}
              publication={publication}
            />
          ))}
        </div>
      );
  }
}

function MetadataSection({
  metadata,
}: {
  metadata: Record<string, ProfileMetadata>;
}) {
  const entries = Object.entries(metadata);

  if (entries.length === 0) {
    return null;
  }

  return (
    <section className="border-t border-gray-200 pt-6">
      <h2 className="text-xl font-semibold text-gray-900">
        Additional Information
      </h2>

      <dl className="mt-4 space-y-5">
        {entries.map(([key, value]) => (
          <div key={key}>
            <dt className="text-sm font-medium text-gray-700">
              {formatMetadataLabel(key)}
            </dt>
            <dd className="mt-1">
              <MetadataValue metadata={value} />
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

/**
 * Reusable read-only member profile.
 * Can load the signed in profile or another member's profile.
 */
export default function MemberProfile({
  target,
  isOwnProfile = false,
}: MemberProfileProps) {
  const { profile, loading, error, refresh } = useMembers(target);

  if (loading) {
    return (
      <main
        className="min-h-screen bg-gray-50 px-4 py-8"
        aria-busy="true"
      >
        <p className="mx-auto max-w-3xl text-gray-600">Loading profile...</p>
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="min-h-screen bg-gray-50 px-4 py-8">
        <div
          className="mx-auto max-w-3xl rounded-lg border border-red-200 bg-red-50 p-6"
          role="alert"
        >
          <h1 className="text-xl font-semibold text-red-800">
            Unable to load profile
          </h1>
          <p className="mt-2 text-red-700">
            {error || "This member profile could not be found."}
          </p>
          <button
            type="button"
            onClick={() => void refresh()}
            className="mt-4 rounded bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  const { identity } = profile.content;

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      <article className="mx-auto max-w-3xl rounded-lg bg-white p-6 shadow sm:p-8">
        <header className="border-b border-gray-200 pb-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {displayName(profile)}
              </h1>

              {identity.pronouns && (
                <p className="mt-1 text-gray-600">{identity.pronouns}</p>
              )}

              {identity.location && (
                <p className="mt-1 text-gray-600">{identity.location}</p>
              )}
            </div>

            <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-700">
              Membership: {profile.status}
            </span>
          </div>

          {isOwnProfile && (
            <Link
              href="/members/me/edit"
              className="mt-5 inline-block rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Edit profile
            </Link>
          )}
        </header>

        <div className="space-y-8 pt-6">
          {(profile.content.personal_statement ||
            identity.website ||
            identity.orcid) && (
              <section>
                <h2 className="text-xl font-semibold text-gray-900">About</h2>

                {profile.content.personal_statement && (
                  <p className="mt-3 whitespace-pre-wrap text-gray-700">
                    {profile.content.personal_statement}
                  </p>
                )}

                {(identity.website || identity.orcid) && (
                  <ul className="mt-4 space-y-2 text-sm">
                    {identity.website && (
                      <li>
                        <a
                          href={identity.website}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          Website
                        </a>
                      </li>
                    )}

                    {identity.orcid && (
                      <li>
                        <a
                          href={`https://orcid.org/${identity.orcid}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          ORCID: {identity.orcid}
                        </a>
                      </li>
                    )}
                  </ul>
                )}
              </section>
            )}

            <section className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-semibold text-gray-900">Research interests</h2>
              <div className="mt-4">
                <TagList tags={profile.content.research_interests} />
              </div>
            </section>

            <section className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-semibold text-gray-900">Expertise</h2>
              <div className="mt-4">
                <TagList tags={profile.content.expertise} />
              </div>
            </section>

            <section className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-semibold text-gray-900">Tags</h2>
              <div className="mt-4">
                <TagList tags={profile.tags} />
              </div>
            </section>

            <MetadataSection metadata={profile.content.metadata} />
        </div>
      </article>
    </main>
  );
}
