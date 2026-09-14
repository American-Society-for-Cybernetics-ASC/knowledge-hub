"use client";

import React, { useEffect, useState } from "react";
import { backendFetch } from "@/lib/api/client";
import { getCurrentUser } from "@/lib/api/me";

export default function AuthSettingsPage() {
  const [newEmail, setNewEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [emailSuccess, setEmailSuccess] = useState("");
  const [emailSaving, setEmailSaving] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [totpEnabled, setTotpEnabled] = useState(false);
  const [totpLoading, setTotpLoading] = useState(true);
  const [totpError, setTotpError] = useState("");
  const [totpSuccess, setTotpSuccess] = useState("");
  const [totpActionLoading, setTotpActionLoading] = useState(false);
  const [qrUri, setQrUri] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [showQr, setShowQr] = useState(false);

  useEffect(() => {
    async function loadUser() {
      try {
        const user = await getCurrentUser();
        setTotpEnabled(user.totp_enabled ?? false);
      } catch {
        setTotpError("Failed to load 2FA status.");
      } finally {
        setTotpLoading(false);
      }
    }
    loadUser();
  }, []);

  async function handleChangeEmail(e: React.FormEvent) {
    e.preventDefault();
    setEmailError("");
    setEmailSuccess("");
    setEmailSaving(true);

    try {
      await backendFetch("/auth/change-email", {
        method: "POST",
        body: JSON.stringify({ new_email: newEmail }),
      });
      setEmailSuccess("Email updated successfully.");
      setNewEmail("");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setEmailError(err.message);
      } else {
        setEmailError("Failed to update email.");
      }
    } finally {
      setEmailSaving(false);
    }
  }

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

  async function handleEnable2FA() {
    setTotpError("");
    setTotpActionLoading(true);
    try {
      const user = await getCurrentUser();
      const response = await backendFetch<{ qr_uri: string }>(
        `/auth/totp-setup?email=${user.email}`,
      );
      setQrUri(response.qr_uri);
      setShowQr(true);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setTotpError(err.message);
      } else {
        setTotpError("Failed to enable 2FA.");
      }
    } finally {
      setTotpActionLoading(false);
    }
  }

  async function handleConfirmTotp(e: React.FormEvent) {
    e.preventDefault();
    setTotpError("");
    setTotpActionLoading(true);
    try {
      const user = await getCurrentUser();
      await backendFetch("/auth/confirm-totp", {
        method: "POST",
        body: JSON.stringify({ email: user.email, code: totpCode }),
      });
      setTotpEnabled(true);
      setShowQr(false);
      setTotpCode("");
      setTotpSuccess("Two-factor authentication enabled.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setTotpError(err.message);
      } else {
        setTotpError("Invalid code. Please try again.");
      }
    } finally {
      setTotpActionLoading(false);
    }
  }

  async function handleDisable2FA() {
    setTotpError("");
    setTotpActionLoading(true);
    try {
      await backendFetch("/auth/disable-totp", {
        method: "POST",
      });
      setTotpEnabled(false);
      setTotpSuccess("Two-factor authentication disabled.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setTotpError(err.message);
      } else {
        setTotpError("Failed to disable 2FA.");
      }
    } finally {
      setTotpActionLoading(false);
    }
  }

  return (
    <div className="max-w-md p-6 space-y-8">
      {/* Change Email */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Change Email</h2>
        {emailError && (
          <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
            {emailError}
          </div>
        )}
        {emailSuccess && (
          <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
            {emailSuccess}
          </div>
        )}
        <form onSubmit={handleChangeEmail} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Email
            </label>
            <input
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              required
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="new@example.com"
            />
          </div>
          <button
            type="submit"
            disabled={emailSaving}
            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {emailSaving ? "Updating..." : "Update Email"}
          </button>
        </form>
      </section>

      {/* change Password */}
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

      {/* 2FA */}
      <section className="border-t pt-6">
        <h2 className="text-lg font-semibold mb-2">
          Two-Factor Authentication
        </h2>
        {totpError && (
          <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
            {totpError}
          </div>
        )}
        {totpSuccess && (
          <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
            {totpSuccess}
          </div>
        )}
        {totpLoading ? (
          <p className="text-gray-600 text-sm">Loading...</p>
        ) : totpEnabled ? (
          <div>
            <p className="text-sm text-green-700 mb-4">
              ✓ Two-factor authentication is enabled.
            </p>
            <button
              type="button"
              onClick={handleDisable2FA}
              disabled={totpActionLoading}
              className="bg-red-600 text-white px-4 py-2 rounded font-medium hover:bg-red-700 disabled:opacity-50 text-sm"
            >
              {totpActionLoading ? "Disabling..." : "Disable 2FA"}
            </button>
          </div>
        ) : showQr ? (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Scan the QR code with your authenticator app.
            </p>
            <div className="flex justify-center mb-4">
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrUri)}`}
                alt="TOTP QR Code"
                width={200}
                height={200}
              />
            </div>
            <form onSubmit={handleConfirmTotp} className="space-y-4">
              <input
                type="text"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                required
                maxLength={6}
                placeholder="000000"
                className="w-full border border-gray-300 rounded px-3 py-2 text-center text-lg tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={totpActionLoading}
                className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {totpActionLoading ? "Verifying..." : "Confirm"}
              </button>
            </form>
          </div>
        ) : (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Two-factor authentication is not enabled.
            </p>
            <button
              type="button"
              onClick={handleEnable2FA}
              disabled={totpActionLoading}
              className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50 text-sm"
            >
              {totpActionLoading ? "Loading..." : "Enable 2FA"}
            </button>
          </div>
        )}
      </section>
      <section className="border-t pt-6">
        <h2 className="text-lg font-semibold mb-2 text-red-700">
          Delete Account
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          This action is permanent and cannot be undone.
        </p>
        {/* TODO: Implement delete account once relationships between AuthUser, Member, Membership and Notification tables are establshid */}
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
