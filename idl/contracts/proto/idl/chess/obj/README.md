# chess/obj

Empty on purpose.

Live games are held in Redis as the opaque `Any` the session layer stores, so
nothing chess-shaped is written down while a game is being played.

This fills in when finished games are archived somewhere durable and queried —
a stored game, its moves, the keys it is found by. That is a different shape from
the live state: it is read by ratings and history, not by the rules.
