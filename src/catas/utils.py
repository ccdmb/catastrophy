""" Utility functions to make programming easier. """

import logging

import functools
import inspect


def log(logger, level=logging.DEBUG):
    """ A decorator function to automatically log function calls.

    This function allows us to track down errors really quickly, as long
    as our functions are reasonably small.

    To use:

    >>> logger = logging.getLogger(__name__)
    >>> @log(logger, logging.DEBUG)
    ... def my_function(one, two):
    ...     return one + two
    >>> my_function(1, 2)
    3

    This would also log to the screen something like...
    DEBUG utils Called my_function(1, 2)
    DEBUG utils Return my_function -> 3

    You can control the level that you want to log these functions at using the
    level parameter, but usually it will just be debug level.
    """

    # Note the extra function is so we can pass arguments to the log decorator.
    def decorator(function):
        # The functools decorator makes it so that the decorator doesn't
        # interfere with the docstrings (or tab autocomplete).
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            # We get some information about the functions parameters.
            sig = inspect.signature(function).bind(*args, **kwargs)
            sig.apply_defaults()

            # Log the arguments that the function was called with
            logger.log(level, "Called %s%s", function.__name__, sig.args)
            # Call the actual function
            result = function(*args, **kwargs)
            # Log the result of the function
            logger.log(level, "Return %s -> %s", function.__name__, result)
            # Return the result.
            return result
        return wrapper
    return decorator
