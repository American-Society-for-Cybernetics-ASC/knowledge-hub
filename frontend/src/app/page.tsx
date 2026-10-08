"use client";

import { useEffect, useState } from "react";
import { Button, Grid, Typography } from "@mui/material";
import { backendFetch } from "@/lib/api/client";

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

function renderContent(content: string) {
  if (!content) return null;
  return content.split("\n").map((line, i) => {
    if (line.startsWith("# ")) return <Typography key={i} variant="h4" sx={{ mt: 1 }}>{line.slice(2)}</Typography>;
    if (line.startsWith("## ")) return <Typography key={i} variant="h5" sx={{ mt: 1 }}>{line.slice(3)}</Typography>;
    if (line.startsWith("### ")) return <Typography key={i} variant="h6" sx={{ mt: 1 }}>{line.slice(4)}</Typography>;
    const parts = line.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
    const rendered = parts.map((part, j) => {
      if (part.startsWith("**") && part.endsWith("**")) return <strong key={j}>{part.slice(2, -2)}</strong>;
      if (part.startsWith("*") && part.endsWith("*")) return <em key={j}>{part.slice(1, -1)}</em>;
      return part;
    });
    return <Typography key={i} variant="body1">{rendered}</Typography>;
  });
}

export default function Home() {
  const [content, setContent] = useState<string | null>(null);

  useEffect(() => {
    backendFetch<{ content: string }>("/pages/home")
      .then((data) => setContent(data.content))
      .catch(() => setContent(""));
  }, []);

  return (
    <div>
      <header>
        <Typography variant="h4">Welcome to the Knowledge Hub</Typography>
        {content ? (
          <div>{renderContent(content)}</div>
        ) : (
          <Typography variant="body1">
            Jump to a section below to get started.
          </Typography>
        )}
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
