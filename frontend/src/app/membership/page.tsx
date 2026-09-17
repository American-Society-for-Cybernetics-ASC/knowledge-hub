"use client";

import { DescriptionList, DescriptionListData, DescriptionListLabel, DescriptionListRow } from "@/components/ui/DescriptionList";
import { backendFetch } from "@/lib/api/client";
import { CurrentUser } from "@/lib/api/me";
import { ReadMember } from "@/types/membership";
import { Alert, Button, Card, CardContent, Skeleton, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import useSWR from "swr";

export default function MembershipCard() {
  const router = useRouter();
  const {
    error: authError,
    isLoading: authIsLoading,
  } = useSWR<CurrentUser>("/auth/me", backendFetch);

  const {
    data: memberData,
    error,
    isLoading,
  } = useSWR<ReadMember>("/membership", backendFetch);

  useEffect(() => {
    if (authError) {
        router.push("/auth/login");
    }
  }, [router, authError]);

  if (authIsLoading || isLoading) {
    return (
      <>
        <Card sx={{ width: 500, height: 350 }}>
          <CardContent>
          <Typography variant="h5">Your Membership</Typography>
            <Skeleton variant="rectangular" />
          </CardContent>
        </Card>
      </>
    );
  }

  if (error) {
    console.log();
    return (
      <Card sx={{ width: 500, height: 350 }}>
        <CardContent>
          <Typography variant="h5">Your Membership</Typography>
          <Alert severity="error">{error.message}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!memberData) {
    return (
      <Card sx={{ width: 500, height: 350 }}>
        <CardContent>
          <Typography variant="h5">Your Membership</Typography>
          <Alert severity="error">Couldn&#39;t load membership data</Alert>
        </CardContent>
      </Card>
    );
  }

  const expiryDate = new Date(memberData.membership_expires);
  const now = new Date();
  const diffMillis = expiryDate.valueOf() - now.valueOf();
  const diffDays = Math.floor(diffMillis / 1000 / 3600 / 24);
  const diffHours = Math.floor(diffMillis / 1000 / 3600) % 24;

  return (
    <>
      <Card sx={{ width: 500, height: 350 }}>
        <CardContent>
          <Typography variant="h5">Your Membership</Typography>
          <DescriptionList>
            <DescriptionListRow>
              <DescriptionListLabel>Membership Status:</DescriptionListLabel>
              <DescriptionListData>{memberData.status}</DescriptionListData>
            </DescriptionListRow>
            <DescriptionListRow>
              <DescriptionListLabel>Membership Type:</DescriptionListLabel>
              <DescriptionListData>{memberData.member_type || "<None Selected>"}</DescriptionListData>
            </DescriptionListRow>
            <DescriptionListRow>
              <DescriptionListLabel>Expires:</DescriptionListLabel>
              <DescriptionListData>{expiryDate.toLocaleString()}</DescriptionListData>
            </DescriptionListRow>
            <DescriptionListRow>
              <DescriptionListLabel>Time till expiry:</DescriptionListLabel>
              <DescriptionListData>
                {diffDays} days, {diffHours} hours
              </DescriptionListData>
            </DescriptionListRow>
          </DescriptionList>
          <Button title="Renew membership" disabled={!memberData.member_type} variant="contained">Renew Membership</Button>
        </CardContent>
      </Card>
    </>
  );
}

