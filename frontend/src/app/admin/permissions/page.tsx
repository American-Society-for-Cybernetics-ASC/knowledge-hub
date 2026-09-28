"use client"

import { useState, useEffect } from "react";
import { backendFetch } from "@/lib/api/client";
import { getCurrentUser } from "@/lib/api/me";

interface User {
    user_id: number;
    email: string;
    name: string | null;
    tier: string | null;
}

export default function PermissionPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [currentTier, setCurrentTier] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [saving, setSaving] = useState<number | null>(null);

    useEffect (() => {
        async function load() {
            try {
                const [usersData, me] = await Promise.all([
                    backendFetch<User[]>("/auth/users"),
                    getCurrentUser(),
                ]);
                setUsers(usersData);
                // Get current user's tier from users list
                const currentUser = usersData.find(u => u.user_id === me.user_id);
                setCurrentTier(currentUser?.tier ?? null);
            } catch {
                setError("Failed to load users.");
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    async function handleGrant(targetUserId: number, tier: string) {
        setSaving(targetUserId);
        setError("");
        setSuccess("");
        try {
            await backendFetch(`/auth/users/${targetUserId}/permissions`, {
                method: "POST",
                body: JSON.stringify({ tier }),
            });
            setUsers(prev =>
                prev.map(u =>
                    u.user_id === targetUserId ? { ...u, tier } : u
                )
            );
            setSuccess("Permission granted successfully.");
        } catch {
            setError("Failed to grant permission.");
        } finally {
            setSaving(null);
        }
    }

    return (
        <div className="p-4 max-w-3xl">
            <h2 className="text-lg font-semibold mb-4">User Permissions</h2>

            {error && (
                <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">{error}</div>
            )}
            {success && (
                <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">{success}</div>
            )}

            <table className="w-full text-sm border border-gray-200 rounded">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="text-left px-4 py-2">User</th>
                        <th className="text-left px-4 py-2">Current Tier</th>
                        <th className="text-left px-4 py-2">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map(user => (
                        <tr key={user.user_id} className="border-t border-gray-100">
                            <td className="px-4 py-2">
                                <div>{user.name ?? "—"}</div>
                                <div className="text-gray-500 text-xs">{user.email}</div>
                            </td>
                            <td className="px-4 py-2">
                                {user.tier ?? <span className="text-gray-400">None</span>}
                            </td>
                            <td className="px-4 py-2 space-x-2">
                                {currentTier === "administrator" && (
                                    <button
                                        onClick={() => handleGrant(user.user_id, "manager")}
                                        disabled={saving === user.user_id || user.tier === "manager"}
                                        className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        Grant Manager
                                    </button>
                                )}
                                {(currentTier === "administrator" || currentTier === "manager") && (
                                    <button
                                        onClick={() => handleGrant(user.user_id, "moderator")}
                                        disabled={saving === user.user_id || user.tier === "moderator"}
                                        className="bg-gray-600 text-white px-3 py-1 rounded text-xs hover:bg-gray-700 disabled:opacity-50"
                                    >
                                        Grant Moderator
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}