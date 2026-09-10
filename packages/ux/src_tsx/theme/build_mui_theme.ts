import { createTheme, type Theme } from "@mui/material/styles";

import type { SeatPaletteTokens, ThemeTokens } from "./theme_tokens";

/**
 * `theme.palette.seat` is available wherever a theme is, so a seat's colour is
 * read the same way as any other.
 */
declare module "@mui/material/styles" {
  interface Palette {
    seat: SeatPaletteTokens;
  }

  interface PaletteOptions {
    seat: SeatPaletteTokens;
  }
}

/**
 * The MUI theme a set of tokens describes.
 *
 * Component defaults are set here, so every button, card and chip in the
 * application is shaped by one file.
 */
export function buildMuiTheme(tokens: ThemeTokens): Theme {
  return createTheme({
    palette: {
      mode: tokens.mode,
      background: {
        default: tokens.palette.background,
        paper: tokens.palette.surface,
      },
      primary: {
        main: tokens.palette.primary,
        contrastText: tokens.palette.onPrimary,
      },
      secondary: { main: tokens.palette.accent },
      success: { main: tokens.palette.success },
      warning: { main: tokens.palette.warning },
      error: { main: tokens.palette.danger },
      divider: tokens.palette.border,
      text: {
        primary: tokens.palette.textPrimary,
        secondary: tokens.palette.textSecondary,
      },
      seat: tokens.seat,
    },
    shape: { borderRadius: tokens.cornerRadiusPixels },
    spacing: tokens.spacingUnitPixels,
    typography: {
      fontFamily: tokens.bodyFontFamily,
      h1: { fontFamily: tokens.headingFontFamily, fontSize: "1.9rem", fontWeight: 600 },
      h2: { fontFamily: tokens.headingFontFamily, fontSize: "1.45rem", fontWeight: 600 },
      h3: { fontFamily: tokens.headingFontFamily, fontSize: "1.15rem", fontWeight: 600 },
      button: { textTransform: "none", fontWeight: 600 },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: { backgroundColor: tokens.palette.background },
        },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
      },
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            backgroundColor: tokens.palette.surfaceRaised,
            border: `1px solid ${tokens.palette.border}`,
          },
        },
      },
      MuiPaper: {
        defaultProps: { elevation: 0 },
      },
      MuiChip: {
        defaultProps: { size: "small" },
      },
      MuiTextField: {
        defaultProps: { size: "small", fullWidth: true },
      },
    },
  });
}
