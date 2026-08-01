"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext } from "react";
import useSWR from "swr";

interface FailedEmail {
    id: number,
    email: {
        sender: string,
        recipients: string[],
        subject: string
    }
}

export default function Page() {
    const publicEnv = useContext(PublicEnv);
    const { data, error, isLoading } = useSWR<FailedEmail[]>(publicEnv.backendUrl + "/mail/failed", (url: string) => {
        console.log(url);
        return fetch(url).then((r) => r.json());
        });
    if (!data) {
        return <p>Loading</p>
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