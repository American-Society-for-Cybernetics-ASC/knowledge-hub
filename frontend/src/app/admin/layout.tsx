import { Typography } from "@mui/material";
import { NavTabs } from "./NavTabs";

export default function AdminNav({
  children,
}: {
  children: React.ReactNode
}) {
    return (
        <>
            <Typography variant="h4">Admin</Typography>
            <NavTabs
                tabs={[
                    {
                        label: "Sitewide",
                        href:"/admin"
                    },
                    {
                        label: "Payments",
                        href: "/admin/payments"
                    },
                    {
                        label: "Mail",
                        href:"/admin/mail"

                    }
                ]}
            />
            {children}
        </>
    )
}
