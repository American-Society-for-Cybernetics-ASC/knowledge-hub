"use client";
import { useEffect, useState } from "react";
import { Typography, Card, CardContent, CardActionArea } from "@mui/material";
import { backendFetch } from "@/lib/api/client";

interface Newsletter {
  id: number;
  name: string;
  content: string;
  published_at: string;
}

export default function NewslettersPage() {
  const [newsletters, setNewsletters] = useState<Newsletter[]>([]);
  const [selected, setSelected] = useState<Newsletter | null>(null);

  useEffect(() => {
    backendFetch<Newsletter[]>("/newsletters/")
      .then(setNewsletters)
      .catch(() => {});
  }, []);

  if (selected) {
    return (
      <div className="max-w-3xl p-4">
        <button
          onClick={() => setSelected(null)}
          className="text-sm text-blue-600 hover:underline mb-4 block"
        >
          ← Back to newsletters
        </button>
        <Typography variant="h5" className="mb-4">
          {selected.name}
        </Typography>
        <Typography variant="body2" className="text-gray-500 mb-4">
          {new Date(selected.published_at).toLocaleDateString()}
        </Typography>
        <StaticRenderer content={selected.content} />
      </div>
    );
  }

  return (
    <div className="max-w-3xl p-4">
      <Typography variant="h5" className="mb-4">
        Newsletters
      </Typography>
      {newsletters.length === 0 && (
        <Typography variant="body1">No newsletters published yet.</Typography>
      )}
      {newsletters.map((n) => (
        <Card key={n.id} className="mb-3">
          <CardActionArea onClick={() => setSelected(n)}>
            <CardContent>
              <Typography variant="h6">{n.name}</Typography>
              <Typography variant="body2" className="text-gray-500">
                {new Date(n.published_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </CardActionArea>
        </Card>
      ))}
    </div>
  );
}

function StaticRenderer({ content }: { content: string }) {
  return (
    <div>
      {content.split("\n").map((line, i) => {
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
      })}
    </div>
  );
}
