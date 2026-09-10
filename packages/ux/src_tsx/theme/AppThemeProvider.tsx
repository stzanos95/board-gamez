import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { useMemo, type ReactElement, type ReactNode } from "react";

import { buildMuiTheme } from "./build_mui_theme";
import type { ThemeName } from "./theme_name";
import { THEME_TOKENS_BY_NAME } from "./theme_registry";

export type AppThemeProviderProps = {
  readonly themeName: ThemeName;
  readonly children: ReactNode;
};

/**
 * Puts the selected theme in reach of every component below it.
 *
 * The theme object is rebuilt only when the name changes, so a re-render costs
 * nothing.
 */
export function AppThemeProvider(props: AppThemeProviderProps): ReactElement {
  const { themeName, children } = props;
  const theme = useMemo(() => buildMuiTheme(THEME_TOKENS_BY_NAME[themeName]), [themeName]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
