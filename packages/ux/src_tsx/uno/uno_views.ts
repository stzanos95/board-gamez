import { create } from "@bufbuild/protobuf";
import { CardColor, CardKind, CardSchema, type Card } from "@board-gamez/idl/uno/model/card_pb";
import { PlayDirection, type UnoResult } from "@board-gamez/idl/uno/model/game_pb";
import type { UnoSession } from "@board-gamez/idl/uno/model/session_pb";
import type { HandCard, UnoPlayerSummary, UnoView } from "@board-gamez/idl/uno/model/view_pb";

import {
  CARD_COLOR_LABELS,
  CARD_KIND_GLYPHS,
  CARD_KIND_IS_WILD,
  CARD_KIND_LABELS,
  PLAY_DIRECTION_GLYPHS,
  RESULT_REASON_LABELS,
} from "./uno_labels";

/**
 * A UNO game, in the shape a screen draws it.
 *
 * These are derivations over data already in hand: a label, a glyph, a
 * comparison against who is looking. Which cards may be played, whose turn
 * it is and whether the game is over all come from the view the game
 * answered; nothing here decides any of them.
 */

const NOT_PLAYING = 0;
const WATCHING_LABEL = "You are watching";
const NO_CARD_LABEL = "no card";

/**
 * One card as it is drawn: its colour, what is printed on it, and a label a
 * screen reader hears.
 */
export type CardView = {
  readonly color: CardColor;
  readonly kind: CardKind;
  readonly glyph: string;
  readonly label: string;
  readonly isWild: boolean;
};

/**
 * One card in the viewer's hand. `index` is its place in the hand, and is
 * what a click reports.
 */
export type HandCardView = {
  readonly index: number;
  readonly card: Card;
  readonly view: CardView;
  readonly isPlayable: boolean;
};

export type PlayerView = {
  readonly participant: number;
  readonly label: string;
  readonly cardCount: number;
  readonly isYou: boolean;
  readonly isToAct: boolean;
  readonly hasWithdrawn: boolean;
};

/**
 * Whose turn it is and how the game stands.
 *
 * `canAct` is true only for the participant whose turn it is in a game that
 * has no result.
 */
export type GameStatusView = {
  readonly isSpectator: boolean;
  readonly isOver: boolean;
  readonly canAct: boolean;
  readonly mayDraw: boolean;
  readonly mayPass: boolean;
  readonly viewerLabel: string;
  readonly headline: string;
  readonly detail: string | null;
};

export type UnoGameView = {
  readonly version: bigint;
  readonly participant: number;
  readonly players: readonly PlayerView[];
  readonly hand: readonly HandCardView[];
  readonly topCard: CardView | null;
  readonly activeColor: CardColor;
  readonly activeColorLabel: string;
  readonly directionGlyph: string;
  readonly drawPileCount: number;
  readonly status: GameStatusView;
};

export function toCardView(card: Card): CardView {
  const isWild = CARD_KIND_IS_WILD[card.kind];
  const glyph = card.kind === CardKind.NUMBER ? String(card.number) : CARD_KIND_GLYPHS[card.kind];
  return {
    color: card.color,
    kind: card.kind,
    glyph,
    label: labelOf(card),
    isWild,
  };
}

export function toUnoGameView(session: UnoSession): UnoGameView {
  const view = session.view;
  const participant = session.participant;
  const participantToAct = view?.participantToAct ?? NOT_PLAYING;
  const players = (view?.players ?? []).map((player: UnoPlayerSummary) =>
    toPlayerView(player, participant, participantToAct),
  );
  const hand = (view?.hand ?? []).map((shown: HandCard, index: number) => toHandCardView(shown, index));
  const topCard = view?.topCard === undefined ? null : toCardView(view.topCard);
  const activeColor = view?.activeColor ?? CardColor.UNSPECIFIED;

  return {
    version: session.version,
    participant,
    players,
    hand,
    topCard,
    activeColor,
    activeColorLabel: CARD_COLOR_LABELS[activeColor],
    directionGlyph: PLAY_DIRECTION_GLYPHS[view?.direction ?? PlayDirection.UNSPECIFIED],
    drawPileCount: view?.drawPileCount ?? 0,
    status: toGameStatusView(view, participant, players),
  };
}

function toPlayerView(
  player: UnoPlayerSummary,
  viewer: number,
  participantToAct: number,
): PlayerView {
  const isYou = player.participant === viewer;
  return {
    participant: player.participant,
    label: isYou ? `Seat ${player.participant} (you)` : `Seat ${player.participant}`,
    cardCount: player.cardCount,
    isYou,
    isToAct: player.participant === participantToAct,
    hasWithdrawn: player.hasWithdrawn,
  };
}

function toHandCardView(shown: HandCard, index: number): HandCardView {
  const card = shown.card ?? emptyCard();
  return {
    index,
    card,
    view: toCardView(card),
    isPlayable: shown.isPlayable,
  };
}

function emptyCard(): Card {
  return create(CardSchema);
}

function toGameStatusView(
  view: UnoView | undefined,
  participant: number,
  players: readonly PlayerView[],
): GameStatusView {
  const isSpectator = participant === NOT_PLAYING;
  const result = view?.result;
  const isOver = result !== undefined;
  const participantToAct = view?.participantToAct ?? NOT_PLAYING;
  const canAct = !isOver && !isSpectator && participant === participantToAct;
  const toAct = players.find((player: PlayerView) => player.participant === participantToAct);

  return {
    isSpectator,
    isOver,
    canAct,
    mayDraw: canAct && (view?.mayDraw ?? false),
    mayPass: canAct && (view?.mayPass ?? false),
    viewerLabel: isSpectator ? WATCHING_LABEL : `You are in seat ${participant}`,
    headline: result === undefined ? turnHeadline(canAct, toAct) : resultHeadline(result, participant),
    detail: detailOf(view, canAct),
  };
}

function turnHeadline(canAct: boolean, toAct: PlayerView | undefined): string {
  if (canAct) {
    return "Your turn";
  }
  if (toAct === undefined) {
    return "Nobody to act";
  }
  return `Waiting for seat ${toAct.participant}`;
}

function resultHeadline(result: UnoResult, participant: number): string {
  const reason = RESULT_REASON_LABELS[result.reason];
  const winner = result.winner === participant ? "You win" : `Seat ${result.winner} wins`;
  return reason.length === 0 ? winner : `${winner} ${reason}`;
}

function detailOf(view: UnoView | undefined, canAct: boolean): string | null {
  if (!canAct || view === undefined) {
    return null;
  }
  if (view.mayPass) {
    return "Play the card you drew, or pass";
  }
  return "Play a card, or draw one";
}

function labelOf(card: Card): string {
  if (card.kind === CardKind.UNSPECIFIED) {
    return NO_CARD_LABEL;
  }
  if (CARD_KIND_IS_WILD[card.kind]) {
    return CARD_KIND_LABELS[card.kind];
  }
  const color = CARD_COLOR_LABELS[card.color].toLowerCase();
  if (card.kind === CardKind.NUMBER) {
    return `${color} ${card.number}`;
  }
  return `${color} ${CARD_KIND_LABELS[card.kind]}`;
}
