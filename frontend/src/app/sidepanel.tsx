"use client";

import { Drawer, Toolbar, Typography, List, ListItemButton, ListItemText, Box } from "@mui/material";
import Link from "next/link";

export const SIDEPANEL_WIDTH = 240

const links = [
    { label: "Home", href: "/"},
    { label: "Knowledge Hub", href: "/knowledge-hub" },
    { label: "Events", href: "/events" },
    { label: "Groups", href: "/groups" },
    { label: "Knowledge Graph", href: "/knowledge-graph" },
    { label: "Membership", href: "/billing/membership" },
    { label: "Notifications", href: "/notifications" },
    { label: "Admin", href: "/admin"}
    
]

export default function SidePanel() {
    return (
        <Drawer variant="permanent" sx={{ 
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
        }}>
            <Toolbar>
                <Typography variant="h6" noWrap>
                    CKH
                </Typography>
            </Toolbar>
            <Box sx={{ overflow: "auto" }}>
                <List>
                {links.map((link) => (
                    <ListItemButton key={link.href} component={Link} href={link.href}>
                        <ListItemText primary={link.label} />
                    </ListItemButton>
                ))}
                </List>
            </Box>
        </Drawer>
    );
}