"use client";

import { Button, Grid, Typography } from "@mui/material";
import StaticContent from "@/components/StaticContent";

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: "Groups", href: "/groups" },
  { label: "Membership", href: "/membership" },
  { label: "Notifications", href: "/notifications" },
  { label: "Admin", href: "/admin" },
];

export default function Home() {
  return (
    <div>
      <header>
        <Typography variant="h4">Welcome to the Knowledge Hub</Typography>
        <StaticContent
          slug="home"
          default="Jump to a section below to get started."
        />
      </header>

      <Grid container spacing={2} sx={{ mt: 2 }}>
        {navItems.map((item, i) => (
          <Button
            key={`nav-button-${i}`}
            variant="contained"
            href={item.href}
            sx={{ py: 1.5 }}
          >
            {item.label}
          </Button>
        ))}
      </Grid>
    </div>
  );
}
