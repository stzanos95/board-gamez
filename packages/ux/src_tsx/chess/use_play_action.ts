import { create } from "@bufbuild/protobuf";
import {
  ChessActionSchema,
  ResignationSchema,
  type ChessAction,
} from "@board-gamez/idl/chess/model/action_pb";
import { CoordinateMoveSchema } from "@board-gamez/idl/chess/model/move_pb";
import type { PieceType } from "@board-gamez/idl/chess/model/piece_pb";
import type { ActionResult } from "@board-gamez/idl/chess/model/session_pb";
import type { Square } from "@board-gamez/idl/chess/model/square_pb";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";

import { mintIdentifier } from "../format/mint_identifier";
import { usePlayer } from "../identity/player_context";
import { useChessGateway } from "../runtime/app_services";
import { COMMAND_OUTCOME_MESSAGES } from "./chess_labels";
import { chessQueryKeys } from "./chess_queries";
import type { ChessCommand } from "./chess_gateway";

const NO_GAME_MESSAGE = "There is no game at this table.";

/**
 * A move as the player committed to it. `promotionType` is UNSPECIFIED for
 * every move that is not a pawn reaching the last rank.
 */
export type MoveIntent = {
  readonly tableId: string;
  readonly origin: Square;
  readonly destination: Square;
  readonly promotionType: PieceType;
  readonly expectedVersion: bigint;
};

export type ResignIntent = {
  readonly tableId: string;
  readonly expectedVersion: bigint;
};

export type PlayActionHandle = {
  readonly playMove: (intent: MoveIntent) => void;
  readonly resign: (intent: ResignIntent) => void;
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
  const gateway = useChessGateway();
  const queryClient = useQueryClient();
  const { player } = usePlayer();

  const play = useCallback((command: ChessCommand) => gateway.play(command), [gateway]);

  const onAnswered = useCallback(
    (result: ActionResult | null) => {
      if (result?.session === undefined) {
        return;
      }
      queryClient.setQueryData(chessQueryKeys.session(result.session.id), result.session);
    },
    [queryClient],
  );

  const mutation = useMutation({ mutationFn: play, onSuccess: onAnswered });
  const { mutate } = mutation;

  const send = useCallback(
    (tableId: string, action: ChessAction, expectedVersion: bigint) => {
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

  const playMove = useCallback(
    (intent: MoveIntent) => {
      const move = create(CoordinateMoveSchema, {
        origin: intent.origin,
        destination: intent.destination,
        promotionType: intent.promotionType,
      });
      const action = create(ChessActionSchema, { kind: { case: "move", value: move } });
      send(intent.tableId, action, intent.expectedVersion);
    },
    [send],
  );

  const resign = useCallback(
    (intent: ResignIntent) => {
      const action = create(ChessActionSchema, {
        kind: { case: "resignation", value: create(ResignationSchema) },
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
    playMove,
    resign,
    isPending: mutation.isPending,
    problem,
    dismissProblem: mutation.reset,
  };
}
