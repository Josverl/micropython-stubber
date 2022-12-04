# below is valid micropython, but not OK for static type checking
# # ref https://github.dev/microsoft/pyright/blob/3cc4e6ccdde06315f5682d9cf61c51ce6fac2753/docs/builtins.md#L7

# OK:  pyright 1.1.218 should be able to handle this
# PYRIGHT: - const withoputh import - Pylance should be able to handle this
FOO = const(11)  # type: ignore
