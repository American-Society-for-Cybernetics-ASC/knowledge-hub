"use client";

import { createTheme } from "@mui/material/styles";

declare module "@mui/material/styles" {
  interface Palette {
    icon: {
      red: { main: string; background: string };
      blue: { main: string; background: string };
      green: { main: string; background: string };
    };
    brand: { anchor_primary: string; anchor_secondary: string };
    surfaces: {
      subtleSurface: string;
      panel: string;
      panelBorder: string;
      search: string;
      searchHover: string;
    };
    borders: { default: string; strong: string };
  }
  interface PaletteOptions {
    icon?: Palette["icon"];
    brand?: Palette["brand"];
    surfaces?: Palette["surfaces"];
    borders?: Palette["borders"];
  }
  interface TypeText {
    tertiary: string;
    search: string;
  }
}

export const theme = createTheme({
  palette: {
    primary: {
      main: "#f6d548",
    },
    secondary: {
      main: "#aca29f",
    },
    background: {
      default: "#F5F4F2",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#2C2927",
      secondary: "#6B6460",
      tertiary: "#ACA29F",
      search: "#A9A9A9",
    },
    divider: "#D6D2CF",
    icon: {
      red: { main: "#963732", background: "#FAEDEB" },
      blue: { main: "#3B3484", background: "#EEEDFD" },
      green: { main: "#224F42", background: "#E5F5EF" },
    },
    brand: {
      anchor_primary: "ACA29F",
      anchor_secondary: "F6D548",
    },
    surfaces: {
      subtleSurface: "#EDEBE8",
      panel: "#2C2927",
      panelBorder: "#343331",
      search: "#EDEBE8",
      searchHover: "#E4E2DF",
    },
    borders: {
      default: "#D6D2CF",
      strong: "#ACA29F",
    },
  },
  typography: {
    fontFamily: "var(--font-geist-sans), sans-serif",
  },
});
