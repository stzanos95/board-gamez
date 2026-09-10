import type { ThemeTokens } from "./theme_tokens";

const SYSTEM_FONT_STACK =
  '"Inter", "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif';

/**
 * A light board: paper surfaces, one deep accent.
 */
export const DAYLIGHT_TOKENS: ThemeTokens = {
  mode: "light",
  palette: {
    background: "#f4f1ea",
    surface: "#ffffff",
    surfaceRaised: "#faf8f4",
    border: "#ddd6c9",
    primary: "#8a5a2b",
    onPrimary: "#fffaf2",
    accent: "#2f6b9a",
    textPrimary: "#1f2933",
    textSecondary: "#5b6773",
    success: "#2f7d4f",
    warning: "#a86a12",
    danger: "#b3413c",
  },
  seat: {
    open: "#cfc6b6",
    occupied: "#2f6b9a",
    mine: "#8a5a2b",
  },
  bodyFontFamily: SYSTEM_FONT_STACK,
  headingFontFamily: SYSTEM_FONT_STACK,
  cornerRadiusPixels: 10,
  spacingUnitPixels: 8,
};
