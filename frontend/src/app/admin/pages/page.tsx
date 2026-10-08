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
            })
        }
    }
}