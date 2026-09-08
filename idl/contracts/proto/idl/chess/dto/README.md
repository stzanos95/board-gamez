# chess/dto

Empty on purpose.

What an API hands out and takes in: request and response bodies, and the
aggregates a client wants in one round trip. Built from `chess/model`, shaped by
what a caller needs rather than by what the domain is.

A DTO exists when the API's shape and the domain's shape genuinely differ — a
game plus the id it was stored under, a paginated list, a projection that leaves
out what a caller must not see. When the two are the same shape, the API sends
the model and this directory stays empty.

Filled in when the API exists. See `chess/service`.
