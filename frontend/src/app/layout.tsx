import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
import PublicEnvProvider from "./public-env-provider";
import { ThemeProvider, CssBaseline} from "@mui/material";
import { theme } from "./theme";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Collaborative Knowledge Hub",
  description: "CKH web app for the ASC.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <PublicEnvProvider publicEnv={{backendUrl: process.env.BACKEND_URL || ""}}>
          <AppRouterCacheProvider options={{ enableCssLayer: true }}>
            <ThemeProvider theme={theme}>
              {children}
            </ThemeProvider>
          </AppRouterCacheProvider>
        </PublicEnvProvider>
      </body>
    </html>
  );
}
