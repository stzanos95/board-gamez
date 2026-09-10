import type { DescMethod } from "@bufbuild/protobuf";
import { getExtension, hasExtension } from "@bufbuild/protobuf";
import { http } from "@board-gamez/idl/google/api/annotations_pb";

const POST = "post";

/**
 * The path a method is served at, read from the method itself.
 *
 * Every operation in this system declares `google.api.http` with a `post` rule,
 * and that annotation travels in the generated descriptor. Reading it here is
 * what keeps a URL from being written down a second time.
 *
 * A method whose annotation is missing or is not a post stops the caller: the
 * contract and this client disagree, and guessing a path would send a request
 * nowhere.
 */
export function postPathOf(method: DescMethod): string {
  const options = method.proto.options;
  if (options === undefined || !hasExtension(options, http)) {
    throw new Error(`${method.parent.typeName}.${method.name} declares no google.api.http rule`);
  }
  const rule = getExtension(options, http);
  if (rule.pattern.case !== POST) {
    throw new Error(
      `${method.parent.typeName}.${method.name} is served over ${String(rule.pattern.case)}, and this client posts`,
    );
  }
  return rule.pattern.value;
}
