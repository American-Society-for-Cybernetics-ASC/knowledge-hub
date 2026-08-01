"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext } from "react";
import useSWR from "swr";

export default function Page() {
    const publicEnv = useContext(PublicEnv);
    const { data, error, isLoading } = useSWR(publicEnv.backendUrl + "/mail/failed", (url) => {
        console.log(url);
        return fetch(url).then((r) => r.json());
        });
    if (isLoading) {
        return <p>Loading</p>
    }
    return <>
        <h2>Mail</h2>
        {data}
    </>
}