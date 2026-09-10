"use client"

import { useState } from "react";
import { backendFetch } from "@/lib/api/client";

export default function AuthSettingsPage() {
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [passwordSuccess, setPasswordSuccess] = useState("");
    const [passwordSaving, setPasswordSaving] = useState(false);

    async function handleChangePassword(e: React.FormEvent) {
        e.preventDefault();
        setPasswordError("");
        setPasswordSuccess("");

        if (newPassword !== confirmPassword) {
            setPasswordError("New passwords do not match.");
            return;
        }

        setPasswordSaving(true);
        try {
            await backendFetch("/auth/change-password", {
                method: "POST",
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                }),
            });
            setPasswordSuccess("Password updated successfully.");
            setCurrentPassword("");
            setNewPassword("");
            setConfirmPassword("");
        } catch (err: unknown) {
            if (err instanceof Error) {
                setPasswordError(err.message);
            } else {
                setPasswordError("Failed to update password.");
            }
        } finally {
            setPasswordSaving(false);
        }
    }

    return (
        <div className="max-w-md p-6 space-y-8">
            <section>
                <h2 className="text-lg font-semibold mb-4">Change Password</h2>

                {passwordError && (
                    <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
                        {passwordError}
                    </div>
                )}
                {passwordSuccess && (
                    <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
                        {passwordSuccess}
                    </div>
                )}

                <form onSubmit={handleChangePassword} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Current Password
                        </label>
                        <input
                            type="password"
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            required
                            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            New Password
                        </label>
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm New Password
                        </label>
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={passwordSaving}
                        className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
                    >
                        {passwordSaving ? "Updating..." : "Update Password"}
                    </button>
                </form>
            </section>

            <section className="border-t pt-6">
                <h2 className="text-lg font-semibold mb-2 text-red-700">
                    Delete Account
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                    This action is permanent and cannot be undone.
                </p>
                <button
                    type="button"
                    className="bg-red-600 text-white px-4 py-2 rounded font-medium hover:bg-red-700 text-sm"
                    onClick={() => alert("Delete account coming soon.")}
                >
                    Delete Account
                </button>
            </section>
        </div>
    );
}