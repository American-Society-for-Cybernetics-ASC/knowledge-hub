import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
import { SWRConfig } from "swr";
import { ThemeProvider, CssBaseline, Box } from "@mui/material";
import { theme } from "./theme";
import SidePanel from "./sidepanel";
import { ErrorWrapper } from "@/components/layout/ErrorContext";

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
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          <SWRConfig value={{ shouldRetryOnError: false }}>
            <ThemeProvider theme={theme}>
              <ErrorWrapper>
                <CssBaseline />
                <SidePanel />
                <Box component="main" sx={{ flexGrow: 1, ml: "240px", p: 3 }}>
                  {children}
                </Box>
              </ErrorWrapper>
            </ThemeProvider>
          </SWRConfig>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
