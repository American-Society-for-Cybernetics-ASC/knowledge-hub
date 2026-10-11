"use client";
import { useEffect, useState, useRef } from "react";
import { Typography, Button } from "@mui/material";
import { backendFetch } from "@/lib/api/client";

interface Newsletter {
  id: number;
  name: string;
  content: string;
  published: boolean;
}

export default function NewslettersAdmin() {
  const [newsletters, setNewsletters] = useState<Newsletter[]>([]);
  const [selected, setSelected] = useState<Newsletter | null>(null);
  const [name, setName] = useState("");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function loadAll() {
    backendFetch<Newsletter[]>("/newsletters/all")
      .then(setNewsletters)
      .catch(() => {});
  }

  useEffect(() => { loadAll(); }, []);

  function selectNewsletter(n: Newsletter) {
    setSelected(n);
    setName(n.name);
    setContent(n.content);
    setMessage("");
  }

  function newNewsletter() {
    setSelected(null);
    setName("");
    setContent("");
    setMessage("");
  }

  function wrapSelection(before: string, after: string) {
    const ta = textareaRef.current;
    if (!ta) return;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const newContent = content.slice(0, start) + before + content.slice(start, end) + after + content.slice(end);
    setContent(newContent);
    setTimeout(() => { ta.focus(); ta.setSelectionRange(start + before.length, end + before.length); }, 0);
  }

  function insertHeading(prefix: string) {
    const ta = textareaRef.current;
    if (!ta) return;
    const lineStart = content.lastIndexOf("\n", ta.selectionStart - 1) + 1;
    setContent(content.slice(0, lineStart) + prefix + content.slice(lineStart));
    setTimeout(() => ta.focus(), 0);
  }

  async function handleSave() {
    setSaving(true);
    setMessage("");
    try {
      if (selected) {
        const updated = await backendFetch<Newsletter>(`/newsletters/${selected.id}`, {
          method: "PUT",
          body: JSON.stringify({ name, content }),
        });
        setSelected(updated);
        setMessage("Saved.");
      } else {
        const created = await backendFetch<Newsletter>("/newsletters/", {
          method: "POST",
          body: JSON.stringify({ name, content }),
        });
        setSelected(created);
        setMessage("Created.");
      }
      loadAll();
    } catch {
      setMessage("Failed to save.");
    } finally {
      setSaving(false);
    }
  }

  async function handlePublish() {
    if (!selected) return;
    setPublishing(true);
    setMessage("");
    try {
      const updated = await backendFetch<Newsletter>(`/newsletters/${selected.id}/publish`, {
        method: "POST",
      });
      setSelected(updated);
      setMessage("Published! Notifications sent.");
      loadAll();
    } catch {
      setMessage("Failed to publish.");
    } finally {
      setPublishing(false);
    }
  }

  return (
    <div className="flex gap-6 p-4">
      <div className="w-64 shrink-0">
        <div className="flex justify-between items-center mb-2">
          <Typography variant="h6">Newsletters</Typography>
          <button onClick={newNewsletter} className="text-sm text-blue-600 hover:underline">+ New</button>
        </div>
        {newsletters.map((n) => (
          <div
            key={n.id}
            onClick={() => selectNewsletter(n)}
            className={`p-2 rounded cursor-pointer mb-1 text-sm ${selected?.id === n.id ? "bg-blue-50 font-medium" : "hover:bg-gray-50"}`}
          >
            {n.name || "Untitled"}
            {n.published && <span className="ml-2 text-xs text-green-600">Published</span>}
          </div>
        ))}
      </div>

      <div className="flex-1 max-w-2xl">
        <Typography variant="h6" className="mb-3">
          {selected ? (selected.published ? "View Newsletter" : "Edit Newsletter") : "New Newsletter"}
        </Typography>
        {message && <div className="mb-3 text-sm text-gray-700">{message}</div>}
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Newsletter name"
          disabled={selected?.published}
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
        />
        <div className="flex gap-2 mb-2">
          {["**", "*"].map((m, i) => (
            <button key={i} onClick={() => wrapSelection(m, m)} disabled={selected?.published}
              className="border border-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-50 disabled:opacity-40">
              {i === 0 ? <b>B</b> : <i>I</i>}
            </button>
          ))}
          {["# ", "## ", "### "].map((h, i) => (
            <button key={i} onClick={() => insertHeading(h)} disabled={selected?.published}
              className="border border-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-50 disabled:opacity-40">
              H{i + 1}
            </button>
          ))}
        </div>
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={selected?.published}
          rows={16}
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
        />
        <div className="flex gap-3 mt-3">
          {!selected?.published && (
            <Button variant="contained" onClick={handleSave} disabled={saving || !name}>
              {saving ? "Saving..." : selected ? "Save" : "Create"}
            </Button>
          )}
          {selected && !selected.published && (
            <Button variant="outlined" color="success" onClick={handlePublish} disabled={publishing}>
              {publishing ? "Publishing..." : "Publish"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}