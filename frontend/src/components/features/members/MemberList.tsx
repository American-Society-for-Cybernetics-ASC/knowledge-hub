"use client";

import Link from "next/link";
import { useState } from "react";
import { useMemberSearch } from "@/hooks/useMemberSearch";

export default function MemberList() {
  const [query, setQuery] = useState("");
  const { results, loading, error, refresh } = useMemberSearch(query);
  const hasQuery = query.trim().length > 0;

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">Member Search</h1>
        <p className="mt-2 text-gray-600">
          Search ASC members by name, tags, or affiliation.
        </p>
      </header>

      <div className="mt-6">
        <label
          htmlFor="member-search"
          className="block text-sm font-medium text-gray-700"
        >
          Search members
        </label>
        <input
          id="member-search"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="e.g. cybernetics, Curtin University, John"
          className="mt-2 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {!hasQuery ? (
        <section className="mt-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Find a member</h2>
          <p className="mt-2 text-gray-600">
            Enter a name, tag, or affiliation to find a member.
          </p>
        </section>
      ) : error ? (
        <section
          className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4"
          role="alert"
        >
          <h2 className="font-semibold text-red-800">
            Unable to search members
          </h2>
          <p className="mt-1 text-sm text-red-700">{error}</p>

          <button
            type="button"
            onClick={() => void refresh()}
            className="mt-4 rounded bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            Retry
          </button>
        </section>
      ) : loading ? (
        <section className="mt-6" aria-busy="true">
          <p className="text-gray-600">Search members...</p>
        </section>
      ) : results.length === 0 ? (
        <section className="mt-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            No members found
          </h2>
          <p className="mt-2 text-gray-600">
            Try searching with a different name, tag, or affiliation.
          </p>
        </section>
      ) : (
        <section className="mt-6" aria-label="Member search results">
          <div className="space-y-4">
            {results.map((member) => {
              const displayName =
                member.display_name?.trim() || "Unnamed member";

              return (
                <article
                  key={member.member_id}
                  className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <h2 className="text-lg font-semibold text-gray-900">
                      <Link
                        href={`/members/${member.member_id}`}
                        className="hover:text-blue-700 hover:underline"
                      >
                        {displayName}
                      </Link>
                    </h2>

                    <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700">
                      {member.active ? "Active" : "Inactive"}
                    </span>
                  </div>

                  {member.affiliations.length > 0 && (
                    <ul className="mt-4 space-y-1 text-sm text-gray-600">
                      {member.affiliations.map((affiliation, index) => (
                        <li key={`${affiliation.organisation}-${index}`}>
                          {[affiliation.organisation, affiliation.role]
                            .filter(Boolean)
                            .join(" - ")}
                        </li>
                      ))}
                    </ul>
                  )}

                  {member.tags.length > 0 && (
                    <ul
                      className="mt-4 flex flex-wrap gap-2"
                      aria-label={`Tags for ${displayName}`}
                    >
                      {member.tags.map((tag) => (
                        <li
                          key={tag}
                          className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-800"
                        >
                          {tag}
                        </li>
                      ))}
                    </ul>
                  )}
                </article>
              );
            })}
          </div>
        </section>
      )}
    </main>
  );
}
