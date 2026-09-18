"use client";

import { backendFetch } from "@/lib/api/client";
import { Typography } from "@mui/material";
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
  const { data, error, isLoading } = useSWR<FailedEmail[]>(
    "/mail/failed",
    backendFetch,
  );

  let body;
  if (isLoading) {
    body = <p>Loading</p>;
  } else if (error) {
    body = <p>Error: {error.toString()}</p>;
  } else if (!data) {
    body = <p>Error: No Data</p>;
  } else {
    body = data.map((email, i) => (
      <ul key={email.id}>
        <h3>Email #{i}</h3>
        <li>Sender: {email.email.sender}</li>
        <li>Recipients: {email.email.recipients}</li>
        <li>Subject: {email.email.subject}</li>
      </ul>
    ));
  }

  return (
    <>
      <Typography variant={"h4"}>Mail</Typography>
      {body}
    </>
  );
}
