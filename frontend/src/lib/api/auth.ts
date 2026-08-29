import { backendFetch } from "./client";

export interface RegisterRequest {
  email: string;
  password: string;
  display_name: string;
}

export interface RegisterResponse {
  qr_uri: string;
  message: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
    challenge_token: string | null;
    message: string;
}

export interface VerifyOTPRequest {
  email: string;
  code: string;
}

export async function register(
  data: RegisterRequest,
): Promise<RegisterResponse> {
  return backendFetch<RegisterResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  return backendFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function verifyOTP(
  data: VerifyOTPRequest,
): Promise<{ message: string }> {
  return backendFetch<{ message: string }>("/auth/verify-otp", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function confirmTOTP(
  data: VerifyOTPRequest,
): Promise<{ message: string }> {
  return backendFetch<{ message: string }>("/auth/confirm-totp", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function logout(): Promise<void> {
  return backendFetch<void>("/auth/logout", {
    method: "POST",
  });
}
