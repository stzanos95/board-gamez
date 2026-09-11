/**
 * What every game's screen is told about the table it is played at.
 *
 * `canStart` is true when every seat is taken and the viewer is in one of
 * them. Whether a start is accepted is the game's to say.
 */
export type GameScreenProps = {
  readonly tableId: string;
  readonly canStart: boolean;
  readonly isSeated: boolean;
};
