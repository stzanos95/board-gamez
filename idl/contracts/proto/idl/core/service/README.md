# core/service

Empty on purpose.

A service belongs here only if it is genuinely domain-agnostic — health, schema
registry, anything the platform offers rather than the product.

Contracts that every domain *implements* are a different thing and also belong
here when they arrive; a contract implemented once per game is core's, even
though no game is.
