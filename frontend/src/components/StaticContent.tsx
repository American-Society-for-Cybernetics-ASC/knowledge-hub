"use client";
import { useEffect, useState } from "react";
import { Typography } from "@mui/material";
import { backendFetch } from "@/lib/api/client";

function renderContent(content: string) {
  return content.split("\n").map((line, i) => {
    if (line.startsWith("# "))
      return (
        <Typography key={i} variant="h4" sx={{ mt: 1 }}>
          {line.slice(2)}
        </Typography>
      );
    if (line.startsWith("## "))
      return (
        <Typography key={i} variant="h5" sx={{ mt: 1 }}>
          {line.slice(3)}
        </Typography>
      );
    if (line.startsWith("### "))
      return (
        <Typography key={i} variant="h6" sx={{ mt: 1 }}>
          {line.slice(4)}
        </Typography>
      );
    const parts = line.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
    const rendered = parts.map((part, j) => {
      if (part.startsWith("**") && part.endsWith("**"))
        return <strong key={j}>{part.slice(2, -2)}</strong>;
      if (part.startsWith("*") && part.endsWith("*"))
        return <em key={j}>{part.slice(1, -1)}</em>;
      return part;
    });
    return (
      <Typography key={i} variant="body1">
        {rendered}
      </Typography>
    );
  });
}

interface Props {
  slug: string;
  default?: string;
}

export default function StaticContent({ slug, default: defaultText }: Props) {
  const [content, setContent] = useState<string | null>(null);

  useEffect(() => {
    backendFetch<{ content: string }>(`/pages/${slug}`)
      .then((data) => setContent(data.content))
      .catch(() => setContent(""));
  }, [slug]);

  if (content) return <div>{renderContent(content)}</div>;
  if (defaultText)
    return <Typography variant="body1">{defaultText}</Typography>;
  return null;
}
