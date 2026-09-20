"use client";

import { useMemberMatching } from "@/hooks/useMemberMatching";

export default function MatchingSettingsPage() {
  const { optedOut, loading, actionLoading, error, optOut, optIn } =
    useMemberMatching();

  if (loading) {
    return <p className="text-gray-600 p-4">Loading...</p>;
  }

  return (
    <div className="max-w-md p-6">
      <h2 className="text-lg font-semibold mb-4">Member Matching</h2>

      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {optedOut ? (
        <div>
          <p className="text-sm text-gray-600 mb-4">
            You are currently opted out of member matching. You will not receive
            member suggestions.
          </p>
          <button
            type="button"
            onClick={() => void optIn()}
            disabled={actionLoading}
            className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {actionLoading ? "Updating..." : "Opt back in"}
          </button>
        </div>
      ) : (
        <div>
          <p className="text-sm text-gray-600 mb-4">
            You are currently opted in to member matching. You will receive
            suggestions based on your profile tags.
          </p>
          <button
            type="button"
            onClick={() => void optOut()}
            disabled={actionLoading}
            className="text-sm text-red-600 underline hover:text-red-900 disabled:opacity-50"
          >
            {actionLoading ? "Updating..." : "Opt out of member matching"}
          </button>
        </div>
      )}
    </div>
  );
}
