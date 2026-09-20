"Use Client";

import { Link, Tab, TabProps, Tabs } from "@mui/material";
import { usePathname } from "next/navigation";
import { JSX } from "react";

export type LinkProps = {
  label: string;
  href: string;
} & TabProps;

export interface NavTabsProps {
  links: LinkProps[];
}

function LinkTab({ label, href, ...props }: LinkProps): JSX.Element {
  return (
    <Tab
      value={href}
      component={Link}
      label={label}
      href={href}
      aria-current={usePathname() === href && "page"}
      style={{ pointerEvents: "auto" }} // Show "title" on disabled links
      {...props}
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
