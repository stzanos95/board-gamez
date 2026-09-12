---
name: typescript-style
description: Coding standards for ALL TypeScript and TSX in this repository. Load before writing or editing any .ts or .tsx file — a hook, a component, a client, a theme, a config module, or a throwaway script. Covers records keyed by an enum instead of switch chains, the shape a rendering component must take, why no arrow function may be created inside a render, the ban on `any` and on barrel files, modelling domain vocabulary as types, and how SOLID applies to a module.
---

# TypeScript style

These rules address whoever writes the code, a developer or an assistant. A
step a rule leaves to "the user" — running the generator, committing — is the
developer's own when they work alone.

The Python half of this repository is governed by `python-style`. This is the
same rule set for the language on the other side of the wire, and the rules that
have a Python counterpart are deliberately worded to match it.

Non-negotiables first.

## 1. A record replaces a chain

**A closed set of values maps through a `Record`, never through `switch`, `if`
chains, or a lookup that can miss.** The enum comes from the generated contract
wherever one exists.

```ts
export const TABLE_STATUS_LABELS: Record<TableStatus, string> = {
  [TableStatus.UNSPECIFIED]: "Unknown",
  [TableStatus.WAITING]: "Waiting for players",
  [TableStatus.IN_PROGRESS]: "In progress",
  [TableStatus.FINISHED]: "Finished",
  [TableStatus.ABANDONED]: "Abandoned",
};
```

`Record<TableStatus, string>` is exhaustive. Adding a member to the enum and
regenerating turns every record that maps it into a compile error, which names
each place that has to answer for the new value. A `switch` with a `default`
answers silently and wrongly.

- **The record's name says what it maps.** `TABLE_STATUS_LABELS`, not `LABELS`.
  A name that survives being imported is rule 6.
- **One record per thing being decided.** Labels, colours and icons are three
  records, not one record of objects, unless the three are always read together.
- **A record whose values are functions is a registry**, and that is how a
  swappable collaborator is selected. See rule 5.
- **`Partial<Record<K, V>>` is a different claim** — it says some keys have no
  answer, and every read must handle `undefined`. Reach for it only when that is
  true.

Where the key set is open — a table id, a player id — the type is
`ReadonlyMap<string, T>` or `Record<string, T | undefined>`, and the read is
checked. `Record<string, T>` over an open key set lies about every miss.

## 2. No function is created during a render

**A function value written inside a component body is a new object on every
render.** Every child that receives it sees a changed prop, so `memo` on that
child does nothing and its subtree re-renders with the parent. On a slow
machine this is the difference between a list that scrolls and one that does
not.

```tsx
<Button onClick={() => onJoin(table.id)} />        // no — new function per render
<Button onClick={handleJoinClick} />               // yes
```

Three ways to have a stable handler, in order of preference:

- **Hoist it out of the component** when it closes over nothing.
- **`useCallback`** when it closes over props or state. Its dependency list is
  the values it reads, and nothing else.
- **Push the argument into the child.** A list never builds one closure per row.
  The row component takes the id and the callback, and makes its own handler:

```tsx
// The parent hands down one stable callback for the whole list.
<TableCard tableId={table.id} onJoin={handleJoin} />

// The row supplies the argument, once, for itself.
const handleClick = useCallback(() => onJoin(tableId), [onJoin, tableId]);
```

The same rule covers every value with an identity: an object or array literal in
a prop (`sx={{ mt: 2 }}`, `items={[]}`) is a new object per render. Hoist it to a
module constant, or memoise it when it depends on props.

**This is not a rule about arrow functions.** `const handle = function () {}`
inside a component is the same object churn. What is banned is creating the value
during a render.

**What the rule binds on is identity that someone compares.** A value crosses
into a child's props, into a dependency array, or into a memo. Two places
legitimately create a value per render and are not the target:

- **An options object handed to a hook that reads it fresh each render.** The
  object passed to `useQuery` or `useMutation` is never compared, so memoising
  it buys nothing. The callbacks a component keeps — the ones it passes down —
  still follow the rule.
- **An `sx` prop.** MUI resolves it by value, and hoisting every one of them
  costs more in noise than it saves. Hoist the `sx` on a memoised list row,
  where it is drawn many times, and leave a one-off on a screen inline.

If in doubt, ask whether anything downstream would notice a new object. If
nothing would, leave it.

## 3. A rendering component reads top to bottom

**The `return` of a component is a layout, not a place where logic lives.** Every
piece with its own structure or styling is bound to a `const` above the return,
named for what it is. The return then reads as the shape of the screen.

```tsx
export const TableCard = memo(function TableCard(props: TableCardProps): ReactElement {
  const { tableId, gameType, status, occupiedSeats, totalSeats, onJoin } = props;
  const handleJoinClick = useCallback(() => onJoin(tableId), [onJoin, tableId]);

  const statusChip = <StatusChip status={status} />;

  const seatCount = (
    <Typography variant="body2" color="text.secondary">
      {occupiedSeats} of {totalSeats} seated
    </Typography>
  );

  const joinButton = (
    <Button variant="contained" onClick={handleJoinClick}>
      Take a seat
    </Button>
  );

  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between">
          {gameTypeLabel}
          {statusChip}
        </Stack>
        {seatCount}
      </CardContent>
      <CardActions>{joinButton}</CardActions>
    </Card>
  );
});
```

- **Layout containers may be written inline in the return.** `Stack`, `Box`,
  `Grid` and a `<div>` are the arrangement, and that is what the return is for.
- **Anything with its own props, styling or condition is bound above it.** A
  button, a chip, a field, a list, a dialog.
- **A conditional is resolved above the return**, into a `const` that holds an
  element or `null`. A ternary nested in JSX is what this rule exists to stop.
- **No `.map` in the return.** Bind the mapped list to a `const`, and give the
  row its own component.
- **No hook is called conditionally**, so every hook sits at the top of the body,
  above the first `const` that renders anything.

A component whose bound sections no longer fit on a screen is two components.

## 4. Types

- **Never `any`.** Not in a cast, not in a generic argument, not in a catch. A
  value whose type is genuinely unknown is `unknown`, and it is narrowed at the
  boundary that received it. `any` disables checking for everything downstream of
  it, silently.
- **Annotate every exported function's parameters and return.** Inference is
  fine for a local; an exported signature is a contract and is written down.
- **`interface` for an object another module implements or extends. `type` for
  everything else** — unions, records, function types, aliases.
- **`readonly` on anything a caller must not change**, including array props:
  `readonly Seat[]`, not `Seat[]`. A component's props are all read-only.
- **A discriminated union replaces a boolean pair.** Two booleans describe four
  states when only three exist. Name the states.
- **No enum of your own where the contract declares one.** `TableStatus` comes
  from `@board-gamez/idl`. A second declaration drifts.
- **A `const` object with `as const` is preferred to a hand-written enum** for
  values this repository owns, because it erases at compile time and carries no
  runtime object. A generated enum is used as generated.

### Domain vocabulary becomes a type

Anything passed between modules is a named type, never a bare object literal
whose keys carry the meaning, and never a positional tuple.

```ts
export type SeatView = {              // yes
  readonly number: number;
  readonly status: SeatStatus;
  readonly occupantLabel: string;
  readonly isMine: boolean;
};

function seatInfo(): [number, string, boolean];   // no — positions carry meaning
```

The test is the one from `python-style`: if a comment is needed to say what a
position or a key means, it is a record and wants a type. A container holding
many of one already-named type stays a plain array.

## 5. Modules

- **No barrel files.** No `index.ts` that re-exports a directory. A consumer
  imports the full path — `import { useTable } from "../lobby/use_table"`. This
  is the `__init__.py` rule, and it holds for the same reasons: a barrel makes
  every import reach the whole directory, defeats tree-shaking, and turns two
  modules that reference each other into a cycle through the barrel.
- **One concern per file, and the filename says which.** `use_join_seat.ts`,
  `table_intents.ts`, `midnight_tokens.ts`.
- **Files are `snake_case`, except a file whose default export is a component,
  which is `PascalCase` and matches the component's name.**
- **Imports at the top.** No dynamic `import()` for a module that is always
  needed. Lazy loading is a deliberate split, not an import style.
- **A cycle between modules is a design signal.** Move the shared thing down into
  the layer both depend on.

### A swappable collaborator is four files

The shape is the one `python-style` rule 5 defines, in this language:

```
theme/
├── theme_name.ts        the enum that selects
├── theme_tokens.ts      the contract every option satisfies
├── midnight_tokens.ts   one option per file
└── theme_registry.ts    the record, and the function that selects by name
```

The registry is a `Record` keyed by the enum (rule 1), so adding an option is a
member and an entry. Consumers are typed against the contract and never name a
concrete option. Selection happens once, at bringup, from configuration.

## 6. Names survive being imported

Read every name as the file that imports it will see it, not as the file that
declares it. Inside `midnight_tokens.ts`, `TOKENS` is obvious; imported anywhere
it is nothing.

```ts
import { TOKENS } from "../theme/midnight_tokens";           // no
import { MIDNIGHT_TOKENS } from "../theme/midnight_tokens";  // yes
```

- **A hook says what it gives you.** `useTableSeats`, not `useTableData`.
- **A boolean reads as a predicate.** `isMine`, `hasOpenSeat`, `canJoin`.
- **A handler prop is `onSomething`; the function bound to it is
  `handleSomething`.** The prop names the event and the local names the reaction.
- **A converter is `<source>To<target>`**, matching the Python adapters.

## 7. Clean code

- **A hook returns one named object**, not a positional tuple, once it has more
  than two values. `const { tables, isLoading, error } = useTables()`.
- **No dead code, no commented-out code.** Git remembers.
- **Comments follow `CLAUDE.md`**: what the thing is, and the constraint a reader
  would otherwise get wrong. Never the conversation that produced it, never a
  comparison against code that is not there.
- **Explicit beats DRY**, as in Python. Two similar components stay two
  components. What overrides that is a subtle, correctness-critical routine,
  which belongs in one place.
- **Errors are values at a boundary.** A caught `unknown` is narrowed where it is
  caught and converted into a named type before it travels.

## Checklist before finishing a file

- [ ] No function, object literal or array literal is created during a render
- [ ] Every closed set maps through a `Record` keyed by its enum
- [ ] The `return` holds layout and bound `const`s, with no `.map` and no nested ternary
- [ ] Every hook is called unconditionally, at the top of the body
- [ ] No `any`; every exported signature is annotated
- [ ] Props are `readonly`, and arrays in props are `readonly T[]`
- [ ] No `index.ts` barrel, and no import reaches a directory rather than a file
- [ ] Every name still reads correctly in the file that imports it
- [ ] A swappable choice is enum, contract, one file per option, and a registry
- [ ] Nothing declares a type the generated contract already declares

## 8. More rules worth having

- **`unknown` at every boundary, narrowed once.** JSON off a socket, a caught
  error, a value out of `sessionStorage`. Narrow it in the module that received
  it and hand a named type onwards. Nothing downstream re-checks.
- **Never assert with `as` to make an error go away.** `as` says you know
  something the checker cannot see, and it is only honest right after a check
  that established it. `as const` and `as unknown as T` at a genuine boundary are
  different things and stay rare.
- **No non-null `!` except where the line above it proves the value.** A `!`
  three lines from its check is a crash waiting for a refactor.
- **Exhaustiveness is checked, not assumed.** Where a union is consumed by
  branching, the fallback branch takes `never`, so adding a member is a compile
  error.
- **Optional and nullable are different claims.** `field?: T` means the key may
  be absent. `field: T | null` means it is always present and may hold nothing.
  Generated messages use the first. Do not add the second on top.
- **`??` and `?.` over `||` and `&&` for absence.** `0`, `""` and `false` are
  values, and `||` throws them away.
- **Nothing is exported that is not imported elsewhere.** An export is a promise
  to other modules. A helper used once stays local.
- **A function takes at most two positional parameters.** Beyond that it takes one
  named object, so a call site cannot transpose two arguments of the same type.
- **A default parameter is a decision.** Prefer requiring the value, so every
  call site says what it wants. A default that varies by deployment is
  configuration, not a default.
- **`Promise` rejection is handled where it is awaited.** No floating promise, no
  `void somePromise()` to quiet a linter.
- **Time, money and identity get named types.** `type TableId = string` reads as
  a domain fact where `string` reads as storage. It costs nothing and it makes a
  transposed argument visible.
- **Dates are carried as the contract carries them** and formatted once, at the
  edge, by one function.

## 9. A review comment becomes a rule

When the author of this repository reviews TypeScript or TSX and leaves a
comment, decide whether it is about the line or about the codebase.

- **About the line** — a wrong name, a missed case, a typo. Fix it and move on.
- **About the codebase** — a comment that would apply the same way to the next
  file, and the one after that. Fix the line, then write the rule into this
  skill, in the section it belongs to, with a short example in the same
  `# yes` / `# no` shape the rest of the file uses.

The test is whether the reviewer would have to say it again. If they would, the
skill is missing a rule, and leaving it unwritten means the next change makes the
same mistake and costs the same review.

Applying a comment to one file and not to the rule is the failure this section
exists to prevent. `frontend-development`, `backend-development` and
`python-style` carry the same instruction for their own subjects.
