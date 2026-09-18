"Use Client";

import { Link, Tab, Tabs } from "@mui/material";
import { usePathname } from "next/navigation";
import { JSX } from "react";

export interface NavTabsProps {
    links: {
        label: string;
        href: string;
    }[];
}

function LinkTab(props: { label: string; href: string }): JSX.Element {
    return (
        <Tab
            value={props.href}
            component={Link}
            label={props.label}
            href={props.href}
            aria-current={usePathname() === props.href && "page"}
        />
    );
}

export function NavTabs({ links }: NavTabsProps) {
    //Prerendering the children is necessary: if the <Tabs> component renders first, it will get confused because its value doesn't match any of its children yet.
    const tabs = links.map((link) => LinkTab(link));

    return (
        <Tabs value={usePathname()} role="navigation">
            {tabs}
        </Tabs>
    );
}