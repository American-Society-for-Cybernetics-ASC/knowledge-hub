"use client";

import { useState, useEffect } from "react";
import { backendFetch } from "@/lib/api/client";
import { getCurrentUser } from "@/lib/api/me";

interface User {
  user_id: number;
  email: string;
  name: string | null;
  tier: string | null;
  children: Record<string, { tier: string | null }>;
}

const CATEGORIES = ["mail", "payment", "auth", "membership", "mailing_lists"];
const TIERS = ["moderator", "manager", "administrator"];

export default function PermissionPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [currentTier, setCurrentTier] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalUser, setModalUser] = useState<User | null>(null);
  const [modalTier, setModalTier] = useState("moderator");
  const [modalCategory, setModalCategory] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [usersData, me] = await Promise.all([
          backendFetch<User[]>("/auth/users"),
          getCurrentUser(),
        ]);
        setUsers(usersData);
        // Get current user's tier from users list
        const currentUser = usersData.find((u) => u.user_id === me.user_id);
        setCurrentTier(currentUser?.tier ?? null);
      } catch {
        setError("Failed to load users.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function openModal(user: User) {
    setModalUser(user);
    setModalTier("moderator");
    setModalCategory("");
    setModalOpen(true);
    setError("");
    setSuccess("");
  }

  async function handleGrant() {
    if (!modalUser) return;
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await backendFetch(`/auth/users/${modalUser.user_id}/permissions`, {
        method: "POST",
        body: JSON.stringify({
          tier: modalTier,
          category: modalCategory || null,
        }),
      });
      setSuccess("Permission granted successfully.");
      const usersData = await backendFetch<User[]>("/auth/users");
      setUsers(usersData);
      setModalOpen(false);
    } catch {
      setError("Failed to grant permission.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="p-4 text-gray-600">Loading...</p>;
  return (
    <div className="p-4 max-w-3xl">
      <h2 className="text-lg font-semibold mb-4">User Permissions</h2>

      {error && (
        <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
          {success}
        </div>
      )}

      <table className="w-full text-sm border border-gray-200 rounded">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left px-4 py-2">User</th>
            <th className="text-left px-4 py-2">Permissions</th>
            <th className="text-left px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.user_id} className="border-t border-gray-100">
              <td className="px-4 py-2">
                <div>{user.name ?? "—"}</div>
                <div className="text-gray-500 text-xs">{user.email}</div>
              </td>
              <td className="px-4 py-2">
                <div className="space-y-1">
                  {user.tier && (
                    <span className="block text-sm capitalize">
                      {user.tier}
                    </span>
                  )}
                  {Object.entries(user.children).map(([category, perm]) =>
                    perm.tier ? (
                      <span
                        key={category}
                        className="block text-sm text-gray-600"
                      >
                        {category}.
                        {perm.tier.charAt(0).toUpperCase() + perm.tier.slice(1)}
                      </span>
                    ) : null,
                  )}
                  {!user.tier && Object.keys(user.children).length === 0 && (
                    <span className="text-gray-400 text-sm">None</span>
                  )}
                </div>
              </td>
              <td className="px-4 py-2">
                {(currentTier === "administrator" ||
                  currentTier === "manager") && (
                  <button
                    onClick={() => openModal(user)}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
                  >
                    Grant Permission
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Modal */}
      {modalOpen && modalUser && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">
              Grant Permission to {modalUser.name ?? modalUser.email}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category (leave blank for global)
                </label>
                <select
                  value={modalCategory}
                  onChange={(e) => setModalCategory(e.target.value)}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                >
                  <option value="">Global</option>
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() +
                        cat.slice(1).replace("_", " ")}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Permission Tier
                </label>
                <select
                  value={modalTier}
                  onChange={(e) => setModalTier(e.target.value)}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                >
                  {TIERS.map((tier) => (
                    <option key={tier} value={tier}>
                      {tier.charAt(0).toUpperCase() + tier.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mt-6">
              {error && (
                <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
                  {error}
                </div>
              )}
              <div className="flex gap-2">
                <button
                  onClick={handleGrant}
                  disabled={saving}
                  className="flex-1 bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50 text-sm"
                >
                  {saving ? "Saving..." : "Grant"}
                </button>
                <button
                  onClick={() => setModalOpen(false)}
                  className="flex-1 border border-gray-300 py-2 rounded font-medium hover:bg-gray-50 text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
