"use client";

import { backendFetch } from "@/lib/api/client";
import useSWR from "swr";

interface FailedEmail {
  id: number;
  email: {
    sender: string;
    recipients: string[];
    subject: string;
  };
}

export default function Page() {
    const { data, error, isLoading } = useSWR<FailedEmail[]>("/mail/failed", backendFetch);

    if (isLoading) {
        return <p>Loading</p>
    }
    if (error) {
        return <p>Error: {error}</p>
    }
    if (!data) {
        return <p>???</p>
    }

    return <>
        <h2>Mail</h2>
        {data.map((email, i) => <ul key={email.id}>
                <h3>Email #{i}</h3>
                <li>Sender: {email.email.sender}</li>
                <li>Recipients: {email.email.recipients}</li>
                <li>Subject: {email.email.subject}</li>
            </ul>
        )}
    </>
}
