"use client";

import Link from "next/link";
import { useMemberMatching } from "@/hooks/useMemberMatching";
import InlineError from "@/components/layout/InlineError";

export default function MemberMatchingView() {
  const {
    suggestions,
    optedOut,
    loading,
    actionLoading,
    error,
    refresh,
    dismiss,
    optOut,
    optIn,
  } = useMemberMatching();

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-12" aria-busy="true">
        <p className="text-gray-600">Loading member suggestions...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-12">
        <InlineError
          title="Unable to load member matching"
          message={error}
          onRetry={() => void refresh()}
        />
      </main>
    );
  }

  if (optedOut) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-12">
        <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-gray-900">
            Member matching is turned off
          </h1>
          <p className="mt-2 text-gray-600">
            You will not receive member suggestions while matching is turned
            off.
          </p>

          <button
            type="button"
            onClick={() => void optIn()}
            disabled={actionLoading}
            className="mt-5 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {actionLoading ? "Updating..." : "Opt back in"}
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">Member matching</h1>
        <p className="mt-2 text-gray-600">
          Discover ASC members who share your interests.
        </p>
      </header>

      {suggestions.length === 0 ? (
        <section className="mt-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            No suggestions yet
          </h2>
          <p className="mt-2 text-gray-600">
            Add tags to your profile to get started.
          </p>
          <Link
            href="/members/me/edit"
            className="mt-4 inline-block text-sm font-medium text-blue-600 hover:underline"
          >
            Edit your profile
          </Link>
        </section>
      ) : (
        <section className="mt-6" aria-label="Member suggestions">
          <div className="space-y-4">
            {suggestions.map((suggestion) => {
              const displayName =
                suggestion.display_name?.trim() || "Unnamed member";

              return (
                <article
                  key={suggestion.member_id}
                  className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <h2 className="text-lg font-semibold text-gray-900">
                        <Link
                          href={`/members/${suggestion.member_id}`}
                          className="hover:text-blue-700 hover:underline"
                        >
                          {displayName}
                        </Link>
                      </h2>
                      <p className="mt-1 text-sm text-gray-600">
                        {suggestion.shared_tags.length} shared{" "}
                        {suggestion.shared_tags.length === 1 ? "tag" : "tags"}
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() => void dismiss(suggestion.member_id)}
                      disabled={actionLoading}
                      className="rounded border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Dismiss
                    </button>
                  </div>

                  <ul
                    className="mt-4 flex flex-wrap gap-2"
                    aria-label={`Shared tags with ${displayName}`}
                  >
                    {suggestion.shared_tags.map((tag) => (
                      <li
                        key={tag}
                        className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-800"
                      >
                        {tag}
                      </li>
                    ))}
                  </ul>
                </article>
              );
            })}
          </div>
        </section>
      )}

      <div className="mt-8 border-t border-gray-200 pt-5">
        <button
          type="button"
          onClick={() => void optOut()}
          disabled={actionLoading}
          className="text-sm text-gray-600 underline hover:text-gray-900 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Opt out of member matching
        </button>
      </div>
    </main>
  );
}
