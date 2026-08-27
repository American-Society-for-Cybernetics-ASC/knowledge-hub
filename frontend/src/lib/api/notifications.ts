import { backendFetch } from "./client";

export interface Notification {
    notification_id: number;
    user_id: number;
    subject: string;
    message: string;
    read: boolean;
}

export async function getNotifications(
    userId: number,
    unreadOnly: boolean = false
): Promise<Notification[]> {
    const params = new URLSearchParams({
        user_id: userId.toString(),
        unread_only: unreadOnly.toString(),
    });
    return backendFetch<Notification[]>(`/notifications/?${params}`);
}

export async function markAsRead(notificationId: number): Promise<{ message: string }> {
    return backendFetch<{ message: string }>(
        `/notifications/${notificationId}/read`,
        { method: "PATCH" }
    );
}