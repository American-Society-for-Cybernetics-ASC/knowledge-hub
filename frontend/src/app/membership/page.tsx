"use client";

import MemberStatusChip from "@/components/features/membership/MemberStatusChip";
import {
  DescriptionList,
  DescriptionListData,
  DescriptionListLabel,
  DescriptionListRow,
} from "@/components/ui/DescriptionList";
import { backendFetch } from "@/lib/api/client";
import { CurrentUser } from "@/lib/api/me";
import { ReadMember } from "@/types/membership";
import { ReadPayment } from "@/types/payments";
import { Info } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Skeleton,
  Tooltip,
  Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import useSWR from "swr";

export default function MembershipCard() {
  const router = useRouter();
  const { error: authError, isLoading: authIsLoading } = useSWR<CurrentUser>(
    "/auth/me",
    backendFetch,
  );

  useEffect(() => {
    if (authError) {
      router.push("/auth/login");
    }
  }, [router, authError]);

  const { data: memberData, isLoading } = useSWR<ReadMember | null>(
    "/membership",
    backendFetch,
    {
      onError: (err) => setError(err.message),
      onSuccess: (data) => {
        if (data == null) {
          setError("You aren't a member");
        }
      },
    },
  );

  const [error, setError] = useState<string>();

  async function handleRenew() {
    const payment = await backendFetch<ReadPayment>("/membership/renew", {
      method: "POST",
    }).catch((err) => {
      setError(err.message);
      throw err;
    });
    router.push(`/pay/${payment.id}`);
  }

  return (
    <>
      <Typography variant="h5">Your Membership</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      {(authIsLoading || isLoading) && (
        <Skeleton variant="rectangular" sx={{ minHeight: 300 }} />
      )}
      {memberData && (
        <MembershipInner memberData={memberData} handleRenew={handleRenew} />
      )}
    </>
  );
}

function MembershipInner({
  memberData,
  handleRenew,
}: {
  memberData: ReadMember;
  handleRenew: () => void;
}) {
  const expiryDate = new Date(memberData.membership_expires);
  const now = new Date();
  const expired = now > expiryDate;
  const diffMillis = expiryDate.valueOf() - now.valueOf();
  const diffDays = Math.floor(diffMillis / 1000 / 3600 / 24);
  const diffHours = Math.floor(diffMillis / 1000 / 3600) % 24;
  return (
    <>
      <DescriptionList>
        <DescriptionListRow>
          <DescriptionListLabel>Membership Status</DescriptionListLabel>
          <DescriptionListData>
            <MemberStatusChip status={memberData.status} />
          </DescriptionListData>
        </DescriptionListRow>
        <DescriptionListRow>
          <DescriptionListLabel>
            <Typography noWrap>Membership Type</Typography>
            <Tooltip title="Apply for a different membership type below">
              <Info></Info>
            </Tooltip>
          </DescriptionListLabel>
          <DescriptionListData>
            {memberData.member_type || "<None Selected>"}
          </DescriptionListData>
        </DescriptionListRow>
        <DescriptionListRow>
          <DescriptionListLabel>
            {expired ? "Expiry" : "Expired"}
          </DescriptionListLabel>
          <DescriptionListData>
            {expiryDate.toLocaleString()}
          </DescriptionListData>
        </DescriptionListRow>
        {!expired && (
          <DescriptionListRow>
            <DescriptionListLabel>Time till expiry</DescriptionListLabel>
            <DescriptionListData>
              {diffDays} days, {diffHours} hours
            </DescriptionListData>
          </DescriptionListRow>
        )}
      </DescriptionList>
      <Box>
        <Button
          title="Renew membership"
          disabled={!memberData.member_type}
          variant="contained"
          onClick={handleRenew}
        >
          Renew Membership
        </Button>
        {expired && (
          <Tooltip title="The renewal duration starts from today, not when your membership exired.">
            <Info></Info>
          </Tooltip>
        )}
      </Box>
    </>
  );
}
