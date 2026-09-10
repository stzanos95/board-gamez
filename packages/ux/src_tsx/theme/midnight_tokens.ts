import type { ThemeTokens } from "./theme_tokens";

const SYSTEM_FONT_STACK =
  '"Inter", "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif';

/**
 * A dark table felt: low-luminance surfaces, one warm accent.
 */
export const MIDNIGHT_TOKENS: ThemeTokens = {
  mode: "dark",
  palette: {
    background: "#0e1116",
    surface: "#161b22",
    surfaceRaised: "#1d242e",
    border: "#2b3440",
    primary: "#e0b070",
    onPrimary: "#1a1206",
    accent: "#6fa8dc",
    textPrimary: "#e8edf4",
    textSecondary: "#9aa7b8",
    success: "#5fbf7f",
    warning: "#d9a441",
    danger: "#e06c75",
  },
  seat: {
    open: "#3d4956",
    occupied: "#6fa8dc",
    mine: "#e0b070",
  },
  bodyFontFamily: SYSTEM_FONT_STACK,
  headingFontFamily: SYSTEM_FONT_STACK,
  cornerRadiusPixels: 10,
  spacingUnitPixels: 8,
};
