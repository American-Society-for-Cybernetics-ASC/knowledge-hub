"use client";

import MemberStatusChip from "@/components/features/membership/MemberStatusChip";
import { AddErrorContext } from "@/components/layout/ErrorContext";
import {
  DescriptionList,
  DescriptionListData,
  DescriptionListLabel,
  DescriptionListRow,
} from "@/components/ui/DescriptionList";
import { backendFetch } from "@/lib/api/client";
import { ReadMember } from "@/types/membership";
import { ReadPayment } from "@/types/payments";
import { CompareArrows, Info } from "@mui/icons-material";
import { Box, Button, Skeleton, Tooltip, Typography } from "@mui/material";
import { useRouter } from "next/navigation";
import { useContext } from "react";
import useSWR from "swr";

export default function YourMembership() {
  const addError = useContext(AddErrorContext);
  const router = useRouter();

  async function handleRenew() {
    await backendFetch<ReadPayment>("/membership/renew", {
      method: "POST",
    })
      .then((payment) => router.push(`/billing/selectProvider/${payment.id}`))
      .catch(addError);
  }

  const { data: memberData, isLoading } = useSWR<ReadMember | null>(
    "/membership",
    backendFetch,
    {
      onError: addError,
      onSuccess: (data) => {
        if (data === null) {
          router.push("/membership/application");
        }
      },
    },
  );

  if (isLoading) {
    return <Skeleton variant="rectangular" sx={{ minHeight: 300 }} />;
  }

  if (!memberData) {
    return <></>; // About to be redirected;
  }

  const expiryDate = new Date(memberData.due_date);
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
            {memberData && <MemberStatusChip status={memberData.status} />}
          </DescriptionListData>
        </DescriptionListRow>
        <DescriptionListRow>
          <DescriptionListLabel>
            <Typography noWrap>Membership Type</Typography>
            <Button
              onClick={() => router.push("/membership/application")}
              title="Change membership type"
              sx={{ padding: 0.1, minWidth: 0.05, minHeight: 0 }}
            >
              <CompareArrows color="info" fontSize="medium" />
            </Button>
          </DescriptionListLabel>
          <DescriptionListData>
            {memberData.member_type || "<None Selected>"}
          </DescriptionListData>
        </DescriptionListRow>
        <DescriptionListRow>
          <DescriptionListLabel>Due Date</DescriptionListLabel>
          <DescriptionListData>
            {expiryDate.toLocaleString()}
          </DescriptionListData>
        </DescriptionListRow>
        {!expired && (
          <DescriptionListRow>
            <DescriptionListLabel>Time till due date</DescriptionListLabel>
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
