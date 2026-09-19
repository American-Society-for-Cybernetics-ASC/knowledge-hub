"use client";

import { Button, Grid, Typography } from "@mui/material";

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: "Knowledge Hub", href: "/knowledge-hub" },
  { label: "Events", href: "/events" },
  { label: "Groups", href: "/groups" },
  { label: "Knowledge Graph", href: "/knowledge-graph" },
  { label: "Membership", href: "/billing/membership" },
  { label: "Notifications", href: "/notifications" },
  { label: "Admin", href: "/admin" },
];

export default function Home() {
  return (
    <div>
      <header>
        <Typography variant="h4">Welcome to the Knowledge Hub</Typography>
        <Typography variant="body1">Jump to a section below to get started.</Typography>
      </header>

      <Grid container spacing={2} sx={{ mt: 2 }}>
        {navItems.map((item) => (
          <Button variant="contained" href={item.href} sx={{ py: 1.5 }}>
            {item.label}
          </Button>
        ))}
      </Grid>
    </div>
  );
}
