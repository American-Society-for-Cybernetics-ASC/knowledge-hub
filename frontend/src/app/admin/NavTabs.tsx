"use client";

import { Tab } from "@mui/material";
import Link from "next/link";
import { JSX } from "react";
import { Tabs } from "@mui/material";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

export interface LinkTabProps {
        label: string,
        href: string,
}
export interface NavTabsProps {
    tabs: LinkTabProps[],
}

function LinkTab(props: LinkTabProps): JSX.Element {
    return <Tab value={props.href} component={Link} label={props.label} href={props.href} aria-current={(usePathname() === props.href) && 'page'} />
}

export function NavTabs(props: NavTabsProps & { children?: ReactNode }) {
    const tabs = props.tabs.map(p => LinkTab(p));
    
    return <Tabs value={usePathname()} role="navigation">
        {tabs}
    </Tabs>
}