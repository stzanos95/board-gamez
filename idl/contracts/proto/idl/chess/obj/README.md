# chess/obj

Empty on purpose.

What a repository reads and writes: rows, documents, stored aggregates, and the
keys they are found by. Built from `chess/model`, shaped by what the store needs.

Separate from `chess/model` because storage changes for reasons the domain does
not share — an index, a partition key, a denormalised copy, a schema migration
that has to be readable by both the old code and the new. A model that doubles
as a row cannot be changed without a migration, and a row that doubles as a model
drags storage concerns into the rules.

Filled in when there is something to store.
