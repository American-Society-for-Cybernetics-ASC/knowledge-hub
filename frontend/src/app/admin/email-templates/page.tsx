"use client";

import { useState, useEffect } from "react";
import { backendFetch } from "@/lib/api/client";

interface EmailTemplate {
  name: string;
  subject: string;
  body: string;
  variables: string[];
}

const TEMPLATE_LABELS: Record<string, string> = {
  new_member_joins: "New Member Joins",
  membership_renewed: "Membership Renewed",
  application_approved: "Application Approved",
  payment_received: "Payment Received",
};

export default function EmailTemplatesPage() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [selected, setSelected] = useState<EmailTemplate | null>(null);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    fetchTemplates();
  }, []);

  async function fetchTemplates() {
    setLoading(true);
    try {
      const data = await backendFetch<EmailTemplate[]>("/email-templates");
      setTemplates(data);
    } catch {
      setError("Failed to load templates.");
    } finally {
      setLoading(false);
    }
  }

  function handleSelect(template: EmailTemplate) {
    setSelected(template);
    setSubject(template.subject);
    setBody(template.body);
    setError("");
    setSuccess("");
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const updated = await backendFetch<EmailTemplate>(
        `/email-templates/${selected.name}`,
        {
          method: "PATCH",
          body: JSON.stringify({ subject, body }),
        },
      );
      setTemplates((prev) =>
        prev.map((t) => (t.name === updated.name ? updated : t)),
      );
      setSelected(updated);
      setSuccess("Template saved successfully.");
    } catch {
      setError("Failed to save template.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-gray-600 p-4">Loading templates...</p>;
  }

  return (
    <div className="flex gap-6 p-4">
      {/* Template list */}
      <div className="w-64 shrink-0">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Templates</h2>
        <div className="space-y-1">
          {templates.map((template) => (
            <button
              key={template.name}
              onClick={() => handleSelect(template)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${
                selected?.name === template.name
                  ? "bg-blue-50 text-blue-700 font-medium"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              {TEMPLATE_LABELS[template.name] ?? template.name}
            </button>
          ))}
        </div>
      </div>

      {/* Editor */}
      {selected ? (
        <div className="flex-1 max-w-2xl">
          <h2 className="text-lg font-semibold mb-1">
            {TEMPLATE_LABELS[selected.name] ?? selected.name}
          </h2>

          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-1">Available variables:</p>
            <div className="flex flex-wrap gap-2">
              {selected.variables.map((v) => (
                <span
                  key={v}
                  className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded font-mono"
                >
                  {v}
                </span>
              ))}
            </div>
          </div>

          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
              {success}
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Body
              </label>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                required
                rows={10}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50 text-sm"
            >
              {saving ? "Saving..." : "Save template"}
            </button>
          </form>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
          Select a template to edit
        </div>
      )}
    </div>
  );
}
