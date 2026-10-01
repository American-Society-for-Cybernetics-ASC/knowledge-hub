"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { verifyOTP } from "@/lib/api/auth";
import InlineError from "@/components/layout/InlineError";
import { getErrorMessage } from "@/lib/errors";

export default function VerifyOTPPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [challengeToken, setChallengeToken] = useState("");

  useEffect(() => {
    const storedEmail = sessionStorage.getItem("auth_email");
    const storedToken = sessionStorage.getItem("challenge_token");
    if (!storedEmail || !storedToken) {
      router.push("/auth/login");
      return;
    }
    setEmail(storedEmail);
    setChallengeToken(storedToken);
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await verifyOTP({ email, code, challenge_token: challengeToken });
      sessionStorage.removeItem("auth_email");
      sessionStorage.removeItem("challenge_token");
      router.push("/");
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Invalid code. Please try again."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
        <h1 className="text-2xl font-bold text-center mb-2">
          Two-Factor Authentication
        </h1>
        <p className="text-sm text-gray-600 text-center mb-6">
          Enter the 6-digit code from your authenticator app
        </p>

        <InlineError message={error} />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              maxLength={6}
              className="w-full border border-gray-300 rounded px-3 py-2 text-center text-2xl tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="000000"
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Verifying..." : "Verify"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600 mt-4">
          <Link href="/auth/login" className="text-blue-600 hover:underline">
            Back to login
          </Link>
        </p>
      </div>
    </div>
  );
}
