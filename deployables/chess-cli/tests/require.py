"""
Narrowing an optional in a test.

A test that reaches through an optional field knows it is set; the type checker
does not. Fails with a readable message when the assumption is wrong.
"""


def require[Value](value: Value | None) -> Value:
    if value is None:
        raise AssertionError("expected a value here, but it was None")
    return value
