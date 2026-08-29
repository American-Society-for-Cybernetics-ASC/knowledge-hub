"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register, confirmTOTP } from "@/lib/api/auth";

export default function RegisterPage() {
    const router = useRouter();
    const [step, setStep] = useState<"register" | "totp-choice" | "totp">("register");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [displayName, setDisplayName] = useState("");
    const [qrUri, setQrUri] = useState("");
    const [totpCode, setTotpCode] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

        try {
            const response = await register({ email, password, display_name: displayName });
            setQrUri(response.qr_uri);
            setStep("totp-choice");
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("Registration failed. Please try again.");
            }
        } finally {
            setLoading(false);
        }
  }

  async function handleConfirmTOTP(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await confirmTOTP({ email, code: totpCode });
      router.push("/auth/login");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Invalid code. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

    //step === "register"
    if (step === "register") {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
                    <h1 className="text-2xl font-bold text-center mb-6">
                        Create your account
                    </h1>

                    {error && (
                        <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleRegister} className="space-y-4">
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
                                placeholder="John Doe"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Email
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="you@example.com"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? "Creating account..." : "Create account"}
                        </button>
                    </form>

                    <p className="text-center text-sm text-gray-600 mt-4">
                        Already have an account?
                        <Link href="/auth/login" className="text-blue-600 hover:underline ml-1">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        );
    }

    // step === "totp-choice"
    if (step === "totp-choice") {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
                    <h1 className="text-2xl font-bold text-center mb-2">
                        Two-Factor Authentication
                    </h1>
                    <p className="text-sm text-gray-600 text-center mb-6">
                        Would you like to enable two-factor authentication?
                        You can always enable it later from your profile settings.
                    </p>

                    <div className="space-y-3">
                        <button
                            onClick={() => setStep("totp")}
                            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700"
                        >
                            Yes, enable 2FA
                        </button>
                        <button
                            onClick={() => router.push("/auth/login")}
                            className="w-full bg-gray-200 text-gray-700 py-2 rounded font-medium hover:bg-gray-300"
                        >
                            No, skip for now
                        </button>
                    </div>
                </div>
            </div>
        );
    }

  //step === "totp"
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
        <h1 className="text-2xl font-bold text-center mb-2">
          Set up Two-Factor Authentication
        </h1>
        <p className="text-sm text-gray-600 text-center mb-6">
          Scan the QR code below with your authenticator app
        </p>

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}

        <div className="flex justify-center mb-6">
          <img
            src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrUri)}`}
            alt="TOTP QR Code"
            width={200}
            height={200}
          />
        </div>

        <form onSubmit={handleConfirmTOTP} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Enter the 6-digit code from your authenticator app
            </label>
            <input
              type="text"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              required
              maxLength={6}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-lg tracking-widest"
              placeholder="000000"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Verifying..." : "Confirm"}
          </button>
        </form>
      </div>
    </div>
  );
}
