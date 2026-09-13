"use client";

import { useContext, useState } from "react";
import { Box, Button, TextField, Typography } from "@mui/material"
import { mutate } from "swr";
import PaymentLog from "@/components/features/billing/PaymentLog";
import { backendFetch } from "@/lib/api/client";

export default function MembershipPage() {
    const [amount, setAmount] = useState("");
    const [memberId, setMemberId] = useState("00000000-0000-4000-8000-000000000000");
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    const handleCreatePaymentIntent = async () => {
        setLoading(true);
        setStatus("Creating payment intent...");
        try {
            const data = await backendFetch("/payments", {
                method: "POST",
                body: JSON.stringify({ member_id: memberId, amount: Number(amount) })
            })
            setStatus(JSON.stringify(data, null, 2));
            mutate("/payments");
        } catch (err) {
            setStatus(`Request failed: ${err instanceof Error ? err.message : String(err)}`);
        } finally {
            setLoading(false)
        }
        
    }

    return (
        <Box sx = {{ maxWidth: 700, display: "flex", flexDirection: "column", gap: 4 }}>
            <Box sx = {{ maxWidth: 500, display: "flex", flexDirection: "column", gap: 2 }}>
                <Typography variant="h5">Donate</Typography>
                
                <TextField
                    label="Amount" 
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    type="number"            
                />

                <Button variant="contained" onClick={handleCreatePaymentIntent} disabled={loading}>
                    {loading ? "Processing..." : "Donate"}
                </Button>

                <TextField label="Status" value={status} multiline minRows={4} fullWidth/>
            </Box>

            <PaymentLog/>
        </Box>
    );
}
