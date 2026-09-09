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

export default function SettingsNav({ children }: { children: React.ReactNode }) {
  const tabs = [
    LinkTab({ label: "Profile", href: "/settings" }),
    LinkTab({ label: "Auth", href: "/settings/auth" }),
    LinkTab({ label: "Member Matching", href: "/settings/matching" }),
  ];

  return (
    <>
      <Typography variant="h4">Settings</Typography>
      <Tabs value={usePathname()} role="navigation">
        {tabs}
      </Tabs>
      {children}
    </>
  );
}