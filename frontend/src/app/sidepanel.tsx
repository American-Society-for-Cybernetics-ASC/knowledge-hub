"use client";

import {
  Drawer,
  Toolbar,
  Typography,
  List,
  ListItemButton,
  ListItemText,
  Box,
} from "@mui/material";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/api/auth";
import { useContext } from "react";
import { AddErrorContext } from "@/components/layout/ErrorContext";

export const SIDEPANEL_WIDTH = 240;

const links = [
  { label: "Home", href: "/" },
  { label: "Login", href: "/auth/login" },
  { label: "Mailing Lists", href: "/groups" },
  { label: "Your Membership", href: "/membership" },
  { label: "Notifications", href: "/notifications" },
  { label: "Admin", href: "/admin" },
  { label: "Settings", href: "/settings" },
  { label: "Member Matching", href: "/member-matching" },
  { label: "Profile", href: "/members/me" },
];

export default function SidePanel() {
  const router = useRouter();
  const addError = useContext(AddErrorContext);

  async function handleLogout() {
    try {
      await logout();
      router.push("/auth/login");
    } catch {
      //If the request fails, an error message will be shown on the page.
      addError("Failed to log out. Please try again.");
    }
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: SIDEPANEL_WIDTH,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: SIDEPANEL_WIDTH,
          boxSizing: "border-box",
          bgcolor: "surfaces.panel",
          borderRight: "1px solid",
          borderColor: "surfaces.panelBorder",
          "& .MuiTypography-root, & .MuiListItemText-primary": {
            color: "text.tertiary",
          },
        },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap>
          CKH
        </Typography>
      </Toolbar>
      <Box sx={{ overflow: "auto", display: "flex", flexDirection: "column", height: "100%" }}>
        <List>
          {links.map((link) => (
            <ListItemButton key={link.href} component={Link} href={link.href}>
              <ListItemText primary={link.label} />
            </ListItemButton>
          ))}
        </List>
        <Box sx={{ mt: "auto", p: 1}}>
          <ListItemButton onClick={handleLogout}>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </Box>
      </Box>
    </Drawer>
  );
}
