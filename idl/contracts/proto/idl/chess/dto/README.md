# chess/dto

Empty, and it earns being empty.

What a client sends to play a move is `chess/model/ParsedCoordinateMove`, packed
into the generic `SubmitAction` frame. What it gets back is `ChessGame`, packed
into a generic snapshot. The transport is `idl/table/dto`, which is game-agnostic.

A DTO belongs here when chess needs a shape the domain does not have — a
projection that hides something, or an aggregate assembled for one screen. Until
then, sending the model is the right amount of machinery.
