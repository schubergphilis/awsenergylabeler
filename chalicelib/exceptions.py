class MissingArgument(Exception):
    """A required argument is missing."""


class MutuallyExclusiveArguments(Exception):
    """Mutually exclusive variables are set."""


class UnsupportedLogLevel(Exception):
    """Unsupported log level set."""


class InvalidDestinationPath(Exception):
    """Invalid destination path given."""
