const SHORT_LENGTH = 4;

/**
 * The leading characters of an identifier, for showing one on screen.
 *
 * Long enough to tell two tabs or two tables apart at a glance, and never used
 * to look anything up.
 */
export function shortIdentifier(identifier: string): string {
  return identifier.slice(0, SHORT_LENGTH);
}
