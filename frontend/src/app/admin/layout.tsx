"use client";
import { Link, Tab, Tabs, Typography } from "@mui/material";
import { usePathname } from "next/navigation";
import { JSX } from "react";

function LinkTab(props: { label: string; href: string }): JSX.Element {
  return (
    <Tab
      value={props.href}
      component={Link}
      label={props.label}
      href={props.href}
      aria-current={usePathname() === props.href && "page"}
    />
  );
}

export default function AdminNav({ children }: { children: React.ReactNode }) {
  const tabs = [
    LinkTab({
      label: "Sitewide",
      href: "/admin",
    }),
    LinkTab({
      label: "Audit Log",
      href: "/admin/audit",
    }),
    LinkTab({
      label: "Mail",
      href: "/admin/mail",
    }),
    LinkTab({
      label: "Payments",
      href: "/admin/payments",
    }),
    LinkTab({
      label: "Email Templates",
      href: "/admin/email-templates",
    }),
  ];
  return (
    <>
      <Typography variant="h4">Admin</Typography>
      <Tabs value={usePathname()} role="navigation">
        {tabs}
      </Tabs>
      {children}
    </>
  );
}
