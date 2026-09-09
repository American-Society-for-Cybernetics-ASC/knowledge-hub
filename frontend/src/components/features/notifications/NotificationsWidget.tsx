"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getCurrentUser } from "@/lib/api/me";
import { getNotifications } from "@/lib/api/notifications";

export default function NotificationsWidget() {
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        async function fetchUnreadCount() {
            try {
                const currentUser = await getCurrentUser();
                const notifications = await getNotifications(
                    currentUser.user_id,
                    true
                );
                setUnreadCount(notifications.length);
            } catch {
                setUnreadCount(0);
            }
        }

        fetchUnreadCount();
    }, []);

    return (
        <Link
            href="/notifications"
            className="text-sm text-gray-700 hover:text-blue-600"
        >
            Notifications{unreadCount > 0 && ` (${unreadCount})`}
        </Link>
    );
}