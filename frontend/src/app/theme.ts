"use client";

import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
    palette: {
        primary: {
            main: "#f6d548"
        },
        secondary: {
            main: "#aca29f"
        }
    },
    typography: {
        fontFamily: "var(--font-geist-sans), sans-serif"
    }
})