const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "<CONFIGURE NEXT_PUBLIC_API_URL>";

export async function backendFetch<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const headers: Record<string, string> = options.body
    ? { "Content-Type": "application/json" }
    : {};
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "An error occurred");
  }

  return response.json();
}
