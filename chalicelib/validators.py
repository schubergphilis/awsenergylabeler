import os

from chalicelib.exceptions import (MissingArgument,
                                   MutuallyExclusiveArguments,
                                   UnsupportedLogLevel)


def get_required_variable(variable_name):
    variable_value = os.getenv(variable_name)
    if not variable_value:
        raise MissingArgument(variable_name)
    return variable_value


def get_mutually_exclusive(variable_name_a, variable_name_b):
    value_a = os.getenv(variable_name_a)
    value_b = os.getenv(variable_name_b)
    if value_a and value_b:
        raise MutuallyExclusiveArguments(variable_name_a, variable_name_b)
    return value_a, value_b


def get_environment_boolean(variable_name, default_value=True):
    value = os.getenv(variable_name)
    if not value:
        return default_value
    if value.lower() in ['false', '0']:
        return False
    return True


def get_log_level(log_level, default_level="INFO"):
    level = os.getenv(log_level)
    level = level.upper() if level else default_level.upper()
    if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        return level
    raise UnsupportedLogLevel(level)
