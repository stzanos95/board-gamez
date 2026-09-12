import { createRegistry, fromBinary, isMessage } from "@bufbuild/protobuf";
import { anyUnpack } from "@bufbuild/protobuf/wkt";
import { WebsocketMessageEnvelopeSchema } from "@board-gamez/idl/core/dto/websocket_pb";
import { SessionChangedSchema, type SessionChanged } from "@board-gamez/idl/game/model/event_pb";
import { TableChangedSchema, type TableChanged } from "@board-gamez/idl/lobby/model/event_pb";

import type { SocketSettings } from "../config/ux_config";

const LOBBY_PATH = "/lobby";
const TABLES_PATH = "/tables/";
const BINARY_TYPE = "arraybuffer";
const SECURE_HTTP = "https:";
const SECURE_SOCKET = "wss:";
const PLAIN_SOCKET = "ws:";
const BACKOFF_FACTOR = 2;
const NORMAL_CLOSURE = 1000;

/**
 * What a socket is opened on: one table, or the lobby's list of tables.
 */
export type SocketTarget =
  | { readonly kind: "lobby" }
  | { readonly kind: "table"; readonly tableId: string };

export const LOBBY_TARGET: SocketTarget = { kind: "lobby" };

export function tableTarget(tableId: string): SocketTarget {
  return { kind: "table", tableId };
}

/**
 * What the server announces: a table has a new version, or the game at one
 * does. A change carries no state; a listener holding an older version reads
 * again, and one holding this version or a later one does nothing.
 */
export type Change =
  | { readonly kind: "table"; readonly change: TableChanged }
  | { readonly kind: "session"; readonly change: SessionChanged };

/**
 * What a subscriber is told.
 *
 * `onReconnect` fires when a socket that had dropped is open again. Whatever
 * was announced in between was not delivered, so a subscriber reads
 * everything it watches once more.
 */
export type ChangeHandlers = {
  readonly onChange: (change: Change) => void;
  readonly onReconnect: () => void;
};

type StatusListener = () => void;

/**
 * One socket, and everyone subscribed to it.
 *
 * Mutable: this is the connection's live state, written by the socket's own
 * events and read by the status hooks.
 */
type Connection = {
  readonly path: string;
  readonly handlers: Set<ChangeHandlers>;
  socket: WebSocket | null;
  isOpen: boolean;
  hasOpenedBefore: boolean;
  failures: number;
  reconnectTimer: ReturnType<typeof setTimeout> | null;
};

const CHANGE_REGISTRY = createRegistry(TableChangedSchema, SessionChangedSchema);

/**
 * The one thing in this application that knows a socket URL exists.
 *
 * A subscriber names a target and is handed every change announced on it.
 * One socket is held per target however many subscribe, and it is closed
 * when the last one leaves. A socket that drops while it is still wanted is
 * reopened with a growing delay; the timer that does so is the only timer
 * here, and it runs only between a drop and the next attempt.
 *
 * Frames are binary. The payload is opened by its type name against the two
 * change schemas, and a frame of a type this build does not know is dropped.
 */
export class SocketClient {
  private readonly settings: SocketSettings;
  private readonly connections = new Map<string, Connection>();
  private readonly statusListeners = new Map<string, Set<StatusListener>>();

  constructor(settings: SocketSettings) {
    this.settings = settings;
  }

  /**
   * Start receiving what is announced on this target. The function answered
   * stops it.
   */
  connect(target: SocketTarget, handlers: ChangeHandlers): () => void {
    const path = socketPathOf(target);
    let connection = this.connections.get(path);
    if (connection === undefined) {
      connection = {
        path,
        handlers: new Set(),
        socket: null,
        isOpen: false,
        hasOpenedBefore: false,
        failures: 0,
        reconnectTimer: null,
      };
      this.connections.set(path, connection);
      this.open(connection);
    }
    connection.handlers.add(handlers);
    return () => this.disconnect(path, handlers);
  }

  isOpen(target: SocketTarget): boolean {
    return this.connections.get(socketPathOf(target))?.isOpen ?? false;
  }

  /**
   * Be told whenever the socket for this target opens or closes. The function
   * answered stops that.
   */
  subscribeToStatus(target: SocketTarget, listener: StatusListener): () => void {
    const path = socketPathOf(target);
    let listeners = this.statusListeners.get(path);
    if (listeners === undefined) {
      listeners = new Set();
      this.statusListeners.set(path, listeners);
    }
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }

  private disconnect(path: string, handlers: ChangeHandlers): void {
    const connection = this.connections.get(path);
    if (connection === undefined) {
      return;
    }
    connection.handlers.delete(handlers);
    if (connection.handlers.size > 0) {
      return;
    }
    this.connections.delete(path);
    if (connection.reconnectTimer !== null) {
      clearTimeout(connection.reconnectTimer);
      connection.reconnectTimer = null;
    }
    const socket = connection.socket;
    connection.socket = null;
    if (socket !== null) {
      socket.close(NORMAL_CLOSURE);
    }
    if (connection.isOpen) {
      connection.isOpen = false;
      this.notifyStatus(path);
    }
  }

  private open(connection: Connection): void {
    const socket = new WebSocket(socketUrlOf(this.settings.baseUrl, connection.path));
    socket.binaryType = BINARY_TYPE;
    socket.addEventListener("open", () => this.handleOpen(connection, socket));
    socket.addEventListener("message", (event: MessageEvent<unknown>) =>
      this.handleMessage(connection, socket, event.data),
    );
    socket.addEventListener("close", () => this.handleClose(connection, socket));
    connection.socket = socket;
  }

  private handleOpen(connection: Connection, socket: WebSocket): void {
    if (connection.socket !== socket) {
      return;
    }
    connection.isOpen = true;
    connection.failures = 0;
    const isReconnect = connection.hasOpenedBefore;
    connection.hasOpenedBefore = true;
    this.notifyStatus(connection.path);
    if (isReconnect) {
      connection.handlers.forEach((handlers: ChangeHandlers) => handlers.onReconnect());
    }
  }

  private handleMessage(connection: Connection, socket: WebSocket, data: unknown): void {
    if (connection.socket !== socket || !(data instanceof ArrayBuffer)) {
      return;
    }
    const change = changeOf(new Uint8Array(data));
    if (change === null) {
      return;
    }
    connection.handlers.forEach((handlers: ChangeHandlers) => handlers.onChange(change));
  }

  private handleClose(connection: Connection, socket: WebSocket): void {
    if (connection.socket !== socket) {
      return;
    }
    connection.socket = null;
    if (connection.isOpen) {
      connection.isOpen = false;
      this.notifyStatus(connection.path);
    }
    const delay = Math.min(
      this.settings.reconnectDelayMs * BACKOFF_FACTOR ** connection.failures,
      this.settings.maxReconnectDelayMs,
    );
    connection.failures += 1;
    connection.reconnectTimer = setTimeout(() => {
      connection.reconnectTimer = null;
      if (this.connections.get(connection.path) === connection) {
        this.open(connection);
      }
    }, delay);
  }

  private notifyStatus(path: string): void {
    this.statusListeners.get(path)?.forEach((listener: StatusListener) => listener());
  }
}

function socketPathOf(target: SocketTarget): string {
  return target.kind === "lobby" ? LOBBY_PATH : `${TABLES_PATH}${encodeURIComponent(target.tableId)}`;
}

/**
 * The socket's URL, on the origin the page came from and the socket scheme
 * that matches the page's.
 */
function socketUrlOf(baseUrl: string, path: string): string {
  const url = new URL(`${baseUrl}${path}`, window.location.href);
  url.protocol = url.protocol === SECURE_HTTP ? SECURE_SOCKET : PLAIN_SOCKET;
  return url.toString();
}

function changeOf(bytes: Uint8Array): Change | null {
  const envelope = fromBinary(WebsocketMessageEnvelopeSchema, bytes);
  if (envelope.payload === undefined) {
    return null;
  }
  const message = anyUnpack(envelope.payload, CHANGE_REGISTRY);
  if (isMessage(message, TableChangedSchema)) {
    return { kind: "table", change: message };
  }
  if (isMessage(message, SessionChangedSchema)) {
    return { kind: "session", change: message };
  }
  return null;
}
