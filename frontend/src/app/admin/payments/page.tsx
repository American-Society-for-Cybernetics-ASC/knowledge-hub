"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext } from "react";
import useSWR from "swr";

export default function Page() {
    const publicEnv = useContext(PublicEnv);
    return <>
        <h2>Payments</h2>
    </>
}