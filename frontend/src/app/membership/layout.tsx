"use client";

import { NavTabs } from "@/components/layout/NavTabs";
import useSWR from "swr";
import { ReadMember } from "@/types/membership";
import { backendFetch } from "@/lib/api/client";
import { useRouter } from "next/navigation";
import { CurrentUser } from "@/lib/api/me";

export default function MembershipNav({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  useSWR<CurrentUser>("/auth/me", backendFetch, {
    onSuccess: (user) => {
      if (user === null) {
        router.push("/auth/login");
      }
    },
  });

  const { data: memberData } = useSWR<ReadMember | null>(
    "/membership",
    backendFetch,
  );

  return (
    <>
      <NavTabs
        links={[
          {
            label: "Membership",
            href: "/membership",
            disabled: memberData === null,
            title:
              memberData === null ? "You aren't currently a member" : undefined,
          },
          {
            label: "Applications",
            href: "/membership/application",
          },
        ]}
      />
      {children}
    </>
  );
}
