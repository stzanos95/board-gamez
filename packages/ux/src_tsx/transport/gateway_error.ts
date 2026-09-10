/**
 * Why a call to the gateway did not produce an answer.
 *
 * `status` carries the HTTP status when one was received, and is null when the
 * request never got that far.
 */
export const GatewayFailure = {
  UNREACHABLE: "unreachable",
  TIMED_OUT: "timed_out",
  REFUSED: "refused",
  UNREADABLE: "unreadable",
} as const;

export type GatewayFailure = (typeof GatewayFailure)[keyof typeof GatewayFailure];

export class GatewayError extends Error {
  readonly failure: GatewayFailure;
  readonly status: number | null;

  constructor(failure: GatewayFailure, message: string, status: number | null) {
    super(message);
    this.name = "GatewayError";
    this.failure = failure;
    this.status = status;
  }
}

/**
 * Whether asking again could answer differently.
 *
 * A status in the 4xx range says the request itself is what the gateway
 * objected to, so the same request will be refused again.
 */
export function isWorthRetrying(error: unknown): boolean {
  if (!(error instanceof GatewayError)) {
    return false;
  }
  if (error.status === null) {
    return true;
  }
  return error.status >= 500;
}
