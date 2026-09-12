import { create } from "@bufbuild/protobuf";
import {
  CardDrawSchema,
  CardPlaySchema,
  TurnPassSchema,
  UnoActionSchema,
  type UnoAction,
} from "@board-gamez/idl/uno/model/action_pb";
import type { Card, CardColor } from "@board-gamez/idl/uno/model/card_pb";
import type { ActionResult } from "@board-gamez/idl/uno/model/session_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { mintIdentifier } from "../format/mint_identifier";
import { usePlayer } from "../identity/player_context";
import { useUnoGateway } from "../runtime/app_services";
import { COMMAND_OUTCOME_MESSAGES } from "./uno_labels";
import { unoQueryKeys } from "./uno_queries";
import type { UnoCommand } from "./uno_gateway";

const NO_GAME_MESSAGE = "There is no game at this table.";

/**
 * A card as the player committed to it. `chosenColor` is UNSPECIFIED for
 * every card that is not a wild.
 */
export type PlayCardIntent = {
  readonly tableId: string;
  readonly card: Card;
  readonly chosenColor: CardColor;
  readonly expectedVersion: bigint;
};

export type TurnIntent = {
  readonly tableId: string;
  readonly expectedVersion: bigint;
};

export type PlayActionHandle = {
  readonly playCard: (intent: PlayCardIntent) => void;
  readonly drawCard: (intent: TurnIntent) => void;
  readonly passTurn: (intent: TurnIntent) => void;
  readonly isPending: boolean;
  readonly problem: string | null;
  readonly dismissProblem: () => void;
};

/**
 * Send one action to the game.
 *
 * A command identifier is minted when the player commits, so a repeat of the
 * same intent is recognised as the same command. Whatever the outcome, the
 * session that comes back is current and replaces the one showing.
 */
export function usePlayAction(): PlayActionHandle {
  const gateway = useUnoGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const play = useCallback((command: UnoCommand) => gateway.play(command), [gateway]);

  const onAnswered = useCallback(
    (result: ActionResult | null) => {
      if (result?.session === undefined) {
        return;
      }
      queryClient.setQueryData(unoQueryKeys.session(result.session.id), result.session);
    },
    [queryClient],
  );

  const mutation = useMutation({ mutationFn: play, onSuccess: onAnswered });
  const { mutate } = mutation;

  const send = useCallback(
    (tableId: string, action: UnoAction, expectedVersion: bigint) => {
      mutate({
        tableId,
        playerId: player.id,
        commandId: mintIdentifier(),
        action,
        expectedVersion,
      });
    },
    [mutate, player.id],
  );

  const playCard = useCallback(
    (intent: PlayCardIntent) => {
      const play = create(CardPlaySchema, { card: intent.card, chosenColor: intent.chosenColor });
      const action = create(UnoActionSchema, { kind: { case: "play", value: play } });
      send(intent.tableId, action, intent.expectedVersion);
    },
    [send],
  );

  const drawCard = useCallback(
    (intent: TurnIntent) => {
      const action = create(UnoActionSchema, {
        kind: { case: "draw", value: create(CardDrawSchema) },
      });
      send(intent.tableId, action, intent.expectedVersion);
    },
    [send],
  );

  const passTurn = useCallback(
    (intent: TurnIntent) => {
      const action = create(UnoActionSchema, {
        kind: { case: "pass", value: create(TurnPassSchema) },
      });
      send(intent.tableId, action, intent.expectedVersion);
    },
    [send],
  );

  const problem = useMemo(() => {
    if (mutation.error !== null) {
      return mutation.error.message;
    }
    if (mutation.data === undefined) {
      return null;
    }
    if (mutation.data === null) {
      return NO_GAME_MESSAGE;
    }
    return COMMAND_OUTCOME_MESSAGES[mutation.data.outcome];
  }, [mutation.error, mutation.data]);

  return {
    playCard,
    drawCard,
    passTurn,
    isPending: mutation.isPending,
    problem,
    dismissProblem: mutation.reset,
  };
}
