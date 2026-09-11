import type {
  DescMessage,
  DescMethodUnary,
  JsonValue,
  MessageInitShape,
  MessageShape,
  Registry,
} from "@bufbuild/protobuf";
import { create, fromJson, toJson } from "@bufbuild/protobuf";

import type { GatewaySettings } from "../config/ux_config";
import { GatewayError, GatewayFailure } from "./gateway_error";
import { postPathOf } from "./service_paths";

const JSON_CONTENT_TYPE = "application/json";
const ABORT_ERROR_NAME = "TimeoutError";

/**
 * The one thing in this application that knows a URL exists.
 *
 * A caller names a method from a generated service and hands it a request. The
 * body and the answer are proto3 canonical JSON, produced and read by the
 * schema itself, so no field name is written down here.
 *
 * Unknown fields are ignored when reading. A gateway redeployed against a newer
 * schema sends fields a running browser has never heard of, and a tab that has
 * been open since before the deploy has to keep working.
 *
 * The registry names every type a payload may carry packed. JSON writes a
 * packed message by its type name and reads it back by the same name, so a
 * type the registry does not hold cannot be sent or received inside one, in
 * any message. Nothing here opens a payload; the registry only lets it cross.
 */
export class GatewayClient {
  private readonly settings: GatewaySettings;
  private readonly registry: Registry;

  constructor(settings: GatewaySettings, registry: Registry) {
    this.settings = settings;
    this.registry = registry;
  }

  async unary<Input extends DescMessage, Output extends DescMessage>(
    method: DescMethodUnary<Input, Output>,
    request: MessageInitShape<Input>,
  ): Promise<MessageShape<Output>> {
    const url = `${this.settings.baseUrl}${postPathOf(method)}`;
    const body = toJson(method.input, create(method.input, request), {
      registry: this.registry,
    });
    const answer = await this.post(url, body);
    return this.decode(method.output, answer, url);
  }

  private async post(url: string, body: JsonValue): Promise<unknown> {
    const response = await this.send(url, body);
    if (!response.ok) {
      throw new GatewayError(
        GatewayFailure.REFUSED,
        `${url} answered ${response.status}`,
        response.status,
      );
    }
    return this.readJson(response, url);
  }

  private async send(url: string, body: JsonValue): Promise<Response> {
    try {
      return await fetch(url, {
        method: "POST",
        headers: { "content-type": JSON_CONTENT_TYPE },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.settings.requestTimeoutMs),
      });
    } catch (cause: unknown) {
      throw this.asGatewayError(cause, url);
    }
  }

  private async readJson(response: Response, url: string): Promise<unknown> {
    try {
      return await response.json();
    } catch {
      throw new GatewayError(
        GatewayFailure.UNREADABLE,
        `${url} answered something that is not JSON`,
        response.status,
      );
    }
  }

  private decode<Output extends DescMessage>(
    schema: Output,
    answer: unknown,
    url: string,
  ): MessageShape<Output> {
    try {
      return fromJson(schema, answer as JsonValue, {
        ignoreUnknownFields: true,
        registry: this.registry,
      });
    } catch (cause: unknown) {
      const detail = cause instanceof Error ? cause.message : String(cause);
      throw new GatewayError(
        GatewayFailure.UNREADABLE,
        `${url} answered a ${schema.typeName} this build cannot read: ${detail}`,
        null,
      );
    }
  }

  private asGatewayError(cause: unknown, url: string): GatewayError {
    if (cause instanceof Error && cause.name === ABORT_ERROR_NAME) {
      return new GatewayError(
        GatewayFailure.TIMED_OUT,
        `${url} did not answer within ${this.settings.requestTimeoutMs}ms`,
        null,
      );
    }
    const detail = cause instanceof Error ? cause.message : String(cause);
    return new GatewayError(GatewayFailure.UNREACHABLE, `${url} is not reachable: ${detail}`, null);
  }
}
