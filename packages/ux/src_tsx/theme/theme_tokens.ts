/**
 * The design decisions a theme makes, and the only source of a colour, a
 * radius or a spacing step in this application.
 *
 * A component never names a colour. It names a role the theme fills, so
 * changing the whole product's appearance is changing which token file the
 * configuration selects.
 */
export type ThemeMode = "light" | "dark";

export type PaletteTokens = {
  readonly background: string;
  readonly surface: string;
  readonly surfaceRaised: string;
  readonly border: string;
  readonly primary: string;
  readonly onPrimary: string;
  readonly accent: string;
  readonly textPrimary: string;
  readonly textSecondary: string;
  readonly success: string;
  readonly warning: string;
  readonly danger: string;
};

/**
 * The three states a seat is drawn in.
 *
 * `mine` is the seat the player at this browser tab occupies. It is a display
 * distinction and never a permission.
 */
export type SeatPaletteTokens = {
  readonly open: string;
  readonly occupied: string;
  readonly mine: string;
};

export type ThemeTokens = {
  readonly mode: ThemeMode;
  readonly palette: PaletteTokens;
  readonly seat: SeatPaletteTokens;
  readonly bodyFontFamily: string;
  readonly headingFontFamily: string;
  readonly cornerRadiusPixels: number;
  readonly spacingUnitPixels: number;
};
