import { NextRequest, NextResponse } from "next/server";

// TODO: Implement route protection proxy
// Check for valid JWT (HttpOnly cookie) before allowing access to protected routes
// Check subscription status before allowing access to app routes
// Check admin role before allowing access to admin routes

export function proxy(request: NextRequest) {
  // TODO: Replace with auth checks
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/admin/:path*",
    "/members/:path*",
    "/groups/:path*",
    "/knowldege-hub/:path*",
    "/notifications/:path*",
    "/billing/:path*",
    "/events/:path*",
    "/knowledge-graph/:path*",
    "/member-matching/:path*",
    "/newsletter/:path*",
  ],
};
