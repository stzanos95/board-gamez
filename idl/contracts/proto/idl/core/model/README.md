# core/model

Empty on purpose.

Vocabulary shared by every domain and owned by none of them — identifiers,
pagination, the shape of an error a caller can branch on.

Nothing has needed to be here yet, and that is worth defending. Anything that
belongs to one domain belongs in that domain, and a message put here to avoid
choosing is how a shared layer turns into a layer everything depends on.
