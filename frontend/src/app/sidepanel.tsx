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
import { useEffect, useState } from "react";
import { logout } from "@/lib/api/auth";
import { getCurrentUser } from "@/lib/api/me";
import { useAddError } from "@/components/layout/ErrorContext";

export const SIDEPANEL_WIDTH = 240;

export default function SidePanel() {
  const router = useRouter();
  const addError = useAddError();
  const [userId, setUserId] = useState<number | null>(null);
  const [tier, setTier] = useState<string | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        if (user) {
          setUserId(user.user_id);
          setTier(user.tier);
        }
      })
      .catch(() => {});
  }, []);

  async function handleLogout() {
    try {
      await logout();
      router.push("/auth/login");
    } catch {
      //If the request fails, an error message will be shown on the page.
      addError("Failed to log out. Please try again.");
    }
  }

  const isLoggedIn = userId !== null;
  const isAdminOrMod =
    tier === "administrator" || tier === "manager" || tier === "moderator";

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
      <Box sx={{ overflow: "auto" }}>
        <List>
          {/* Always visible */}
          <ListItemButton component={Link} href="/">
            <ListItemText primary="Home" />
          </ListItemButton>

          {/* Not logged in */}
          {!isLoggedIn && (
            <ListItemButton component={Link} href="/auth/login">
              <ListItemText primary="Login" />
            </ListItemButton>
          )}

          {/* Logged in users */}
          {isLoggedIn && (
            <>
              <ListItemButton component={Link} href="/groups">
                <ListItemText primary="Mailing Lists" />
              </ListItemButton>

              <ListItemButton component={Link} href="/membership">
                <ListItemText primary="Your Membership" />
              </ListItemButton>

              <ListItemButton component={Link} href="/notifications">
                <ListItemText primary="Notifications" />
              </ListItemButton>

              <ListItemButton component={Link} href="/settings">
                <ListItemText primary="Settings" />
              </ListItemButton>

              <ListItemButton component={Link} href="/member-matching">
                <ListItemText primary="Member Matching" />
              </ListItemButton>

              <ListItemButton component={Link} href="/members/me">
                <ListItemText primary="Profile" />
              </ListItemButton>

              {/* Admin/moderator only */}
              {isAdminOrMod && (
                <ListItemButton component={Link} href="/admin">
                  <ListItemText primary="Admin" />
                </ListItemButton>
              )}

              <ListItemButton onClick={handleLogout}>
                <ListItemText primary="Logout" />
              </ListItemButton>
            </>
          )}
        </List>
      </Box>
    </Drawer>
  );
}
