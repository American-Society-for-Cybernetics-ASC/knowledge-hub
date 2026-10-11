"use client";

import { useState, useEffect } from "react";
import { getCurrentUser } from "@/lib/api/me";
import { backendFetch } from "@/lib/api/client";
import { useAddError } from "@/components/layout/ErrorContext";
import { getErrorMessage } from "@/lib/errors";

export default function ProfileSettingsPage() {
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState("");
  const addError = useAddError();

  useEffect(() => {
    async function loadUser() {
      try {
        const user = await getCurrentUser();
        setDisplayName(user.name ?? "");
      } catch {
        addError("Failed to load profile.");
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSuccess("");

    try {
      await backendFetch("/members/me", {
        method: "PATCH",
        body: JSON.stringify({
          identity: { display_name: displayName },
        }),
      });
      setSuccess("Display name updated successfully.");
    } catch (err: unknown) {
      addError(getErrorMessage(err, "Failed to update display name."));
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-gray-600 p-4">Loading...</p>;
  }

  return (
    <div className="max-w-md p-6">
      <h2 className="text-lg font-semibold mb-4">Profile</h2>

      {success && (
        <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Display Name
          </label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Your display name"
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save changes"}
        </button>
      </form>
    </div>
  );
}
