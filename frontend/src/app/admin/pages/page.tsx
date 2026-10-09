"use client";

import { useEffect, useState, useRef } from "react";
import { Typography, Button } from "@mui/material";
import { backendFetch } from "@/lib/api/client";

export default function PagesEditor() {
    const [content, setContent] = useState("");
    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState("");
    const [error, setError] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        backendFetch<{ content: string }>("/pages/home")
            .then((data) => setContent(data.content))
            .catch(() => {});
    }, []);

    function wrapSelection(before: string, after: string) {
        const ta = textareaRef.current;
        if (!ta) return;
        const start = ta.selectionStart;
        const end = ta.selectionEnd;
        const selected = content.slice(start, end);
        const newContent =
            content.slice(0, start) + before + selected + after + content.slice(end);
        setContent(newContent);
        setTimeout(() => {
            ta.focus();
            ta.setSelectionRange(start + before.length, end + before.length);
        }, 0);
    }

    function insertHeading(prefix: string) {
        const ta = textareaRef.current;
        if (!ta) return;
        const start = ta.selectionStart;
        const lineStart = content.lastIndexOf("\n", start - 1) + 1;
        const newContent = content.slice(0, lineStart) + prefix + content.slice(lineStart);
        setContent(newContent);
        setTimeout(() => ta.focus(), 0);
    }

    async function handleSave() {
        setSaving(true);
        setError("");
        setSuccess("");
        try {
            await backendFetch("/pages/home", {
                method: "PUT",
                body: JSON.stringify({ content }),
            });
            setSuccess("Saved successfully.");
        } catch {
            setError("Failed to save.");
        } finally {
            setSaving(false);
        }
    }

    return (
        <div className="p-4 max-w-3xl">
            <Typography variant="h5" className="mb-4">Edit Home Page</Typography>

            {error && <div className="bg-red-50 text-red-700 p-3 rounded mb-3 text-sm">{error}</div>}
            {success && <div className="bg-green-50 text-green-700 p-3 rounded mb-3 text-sm">{success}</div>}

            <div className="flex gap-2 mb-2">
                <button
                    onClick={() => wrapSelection("**", "**")}
                    className="border border-gray-300 px-3 py-1 rounded text-sm font-bold hover:bg-gray-50"
                    title="Bold"
                >B</button>
                <button
                    onClick={() => wrapSelection("*", "*")}
                    className="border border-gray-300 px-3 py-1 rounded text-sm italic hover:bg-gray-50"
                    title="Italic"
                >I</button>
                <button
                    onClick={() => insertHeading("# ")}
                    className="border border-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-50"
                    title="Heading 1"
                >H1</button>
                <button
                    onClick={() => insertHeading("## ")}
                    className="border border-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-50"
                    title="Heading 2"
                >H2</button>
                <button
                    onClick={() => insertHeading("### ")}
                    className="border border-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-50"
                    title="Heading 3"
                >H3</button>
            </div>

            <textarea
                ref={textareaRef}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={16}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <div className="mt-3">
                <Button
                    variant="contained"
                    onClick={handleSave}
                    disabled={saving}
                >
                    {saving ? "Saving..." : "Save"}
                </Button>
            </div>
        </div>
    );
}