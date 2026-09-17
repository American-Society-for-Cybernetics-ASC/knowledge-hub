"use client";

import { NavTabs } from "@/components/layout/NavTabs";

export default function SettingsNav({ children }: { children: React.ReactNode }) {
    return (
        <>
            <h1 className="text-2xl font-bold mb-2 p-4">Settings</h1>
            <NavTabs
                links={[
                    { label: "Profile", href: "/settings" },
                    { label: "Auth", href: "/settings/auth" },
                    { label: "Member Matching", href: "/settings/matching" },
                ]}
            />
            {children}
        </>
    );
}