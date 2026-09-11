const UUID_BYTE_COUNT = 16;
const VERSION_BYTE_INDEX = 6;
const VARIANT_BYTE_INDEX = 8;
const VERSION_4 = 0x40;
const VERSION_MASK = 0x0f;
const VARIANT_RFC_4122 = 0x80;
const VARIANT_MASK = 0x3f;
const HEX_RADIX = 16;
const HEX_WIDTH = 2;
const HEX_PAD = "0";
const HYPHEN = "-";
const GROUP_ENDS: readonly number[] = [4, 6, 8, 10];

/**
 * A new random identifier, in the form of a version 4 UUID.
 *
 * Built from `crypto.getRandomValues`, which every browser exposes on any
 * origin. `crypto.randomUUID` exists only on a secure origin, and this
 * application is served over plain HTTP on a LAN.
 */
export function mintIdentifier(): string {
  const bytes = new Uint8Array(UUID_BYTE_COUNT);
  window.crypto.getRandomValues(bytes);
  bytes[VERSION_BYTE_INDEX] = ((bytes[VERSION_BYTE_INDEX] ?? 0) & VERSION_MASK) | VERSION_4;
  bytes[VARIANT_BYTE_INDEX] = ((bytes[VARIANT_BYTE_INDEX] ?? 0) & VARIANT_MASK) | VARIANT_RFC_4122;

  let text = "";
  bytes.forEach((byte: number, index: number) => {
    if (GROUP_ENDS.includes(index)) {
      text += HYPHEN;
    }
    text += byte.toString(HEX_RADIX).padStart(HEX_WIDTH, HEX_PAD);
  });
  return text;
}
