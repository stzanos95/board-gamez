# chess/service

Empty, and likely to stay that way.

Chess does not define a service of its own. It implements
`idl.table.service.GameService`, the one contract every game implements, packing
its position and its moves into `google.protobuf.Any` so the session layer can
carry them without knowing what they are.

A service belongs here only if chess grows an API that is chess-shaped and not a
game of chess — an opening explorer, an analysis endpoint, a PGN import. Playing
is not that.
