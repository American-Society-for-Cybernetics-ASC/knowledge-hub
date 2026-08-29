"use client";

import { useState, useEffect } from "react";
import { getNotifications, markAsRead, Notification } from "@/lib/api/notifications";
import { getCurrentUser } from "@/lib/api/me";

export default function NotificationsPage() {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);

    useEffect(() => {
        fetchNotifications();
    }, []);

    async function fetchNotifications() {
        setLoading(true);
        try {
            const CurrentUser = await getCurrentUser();
            const data = await getNotifications(CurrentUser.user_id);
            setNotifications(data);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("Failed to load notifications.");
            }
        } finally {
            setLoading(false);
        }
    }

    async function handleMarkAsRead(notification: Notification) {
        try {
            await markAsRead(notification.notification_id);
            setNotifications(prev =>
                prev.map(n =>
                    n.notification_id === notification.notification_id
                        ? { ...n, read: true }
                        : n
                )
            );
            setSelectedNotification({ ...notification, read: true });
        } catch {
            setError("Failed to mark notification as read.");
        }
    }

    const filtered = notifications.filter(n =>
        n.subject.toLowerCase().includes(search.toLowerCase()) ||
        n.message.toLowerCase().includes(search.toLowerCase())
    );

    if (selectedNotification) {
        return (
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-8">
                    <button
                        onClick={() => setSelectedNotification(null)}
                        className="text-blue-600 hover:underline text-sm mb-4 block"
                    >
                        ← Back to notifications
                    </button>
                    <div className="flex items-center justify-between mb-4">
                        <h1 className="text-xl font-bold">{selectedNotification.subject}</h1>
                        {!selectedNotification.read && (
                            <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded">
                                Unread
                            </span>
                        )}
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{selectedNotification.message}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-2xl font-bold mb-6">Notifications</h1>

                <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search notifications..."
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                {error && (
                    <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                {loading ? (
                    <p className="text-gray-500 text-sm">Loading...</p>
                ) : filtered.length === 0 ? (
                    <p className="text-gray-500 text-sm">No notifications found.</p>
                ) : (
                    <div className="space-y-2">
                        {filtered.map((notification) => (
                            <div
                                key={notification.notification_id}
                                onClick={() => {
                                    setSelectedNotification(notification);
                                    if (!notification.read) {
                                        handleMarkAsRead(notification);
                                    }
                                }}
                                className={`bg-white rounded-lg shadow p-4 cursor-pointer hover:bg-gray-50 border-l-4 ${
                                    notification.read
                                        ? "border-gray-200"
                                        : "border-blue-500"
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <p className={`text-sm font-medium ${
                                        notification.read ? "text-gray-600" : "text-gray-900"
                                    }`}>
                                        {notification.subject}
                                    </p>
                                    {!notification.read && (
                                        <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded ml-2">
                                            New
                                        </span>
                                    )}
                                </div>
                                <p className="text-xs text-gray-500 mt-1 truncate">
                                    {notification.message}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}