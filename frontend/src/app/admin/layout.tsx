"use client";

import { Typography } from "@mui/material";
import { NavTabs } from "@/components/layout/NavTabs";

export default function AdminNav({ children }: { children: React.ReactNode }) {
    return (
        <>
            <Typography variant="h4">Admin</Typography>
            <NavTabs
                links={[
                    { label: "Sitewide", href: "/admin" },
                    { label: "Audit Log", href: "/admin/audit" },
                    { label: "Mail", href: "/admin/mail" },
                    { label: "Payments", href: "/admin/payments" },
                    { label: "Email Templates", href: "/admin/email-templates" },
                ]}
            />
            {children}
        </>
    );
}