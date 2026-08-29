"use client";

import { PublicEnv } from "@/app/public-env-provider";
import { useContext, useState } from "react";
import { Box, Button, TextField, Typography } from "@mui/material"

export default function Page() {
    const publicEnv = useContext(PublicEnv);
    const [amount, setAmount] = useState("");
    const [memberId, setMemberId] = useState("00000000-0000-4000-8000-000000000000");
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    const handleCreatePaymentIntent = async () => {
        console.log("publicEnv:", publicEnv)
        setLoading(true);
        setStatus("Creating payment intent...");
        try {
            const res = await fetch(`${publicEnv?.backendUrl}/payments`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    member_id: memberId,
                    amount: Number(amount)
                })
            });
            const data = await res.json();
            if (!res.ok) {
                setStatus(`Error (${res.status}): ${JSON.stringify(data)}`)
            } else {
                setStatus(JSON.stringify(data, null, 2));
            }
        } catch (err) {
            setStatus(`Request failed: ${err instanceof Error ? err.message : String(err)}`);
        } finally {
            setLoading(false)
        }
        
    }

    return <>
        <Box sx = {{ maxWidth: 500, display: "flex", flexDirection: "column", gap: 2 }}>
            <Typography variant="h5">Payments</Typography>
            
            <TextField
                label="Amount" 
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                type="number"            
            />

            <Button variant="contained" onClick={handleCreatePaymentIntent} disabled={loading}>
                {loading ? "Creating..." : "Create Payment Intent"}
            </Button>

            <TextField label="Status" value={status} multiline minRows={4} fullWidth/>
        </Box>

    </>
}