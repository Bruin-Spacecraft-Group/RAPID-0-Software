"""
Wrapper around code which is not accessible to all due to internal non-disclosure agreements.

Allows for runtime checks for whether or not this build was deployed in a context with access
to undisclosable code. Also provides helpd functions to conditionally execute code based on
the results of those checks.
"""

try:
    import nda_libraries.src as NDA_LIB
except ModuleNotFoundError as ex:
    NDA_LIB = None


def nda_libraries_available():
    """
    Locates undisclosable code and determines whether or not it is available. Returns a bool.
    """
    return NDA_LIB is not None


def safe_import_nda_libraries():
    """
    Import the undisclosable code if and only if it exists.

    Returns a module that provides access to the undisclosable code as though it was imported,
    if possible; otherwise returns None.
    """
    return NDA_LIB


def run_if_nda_libraries_available(helper_function):
    """
    Run some code if and only if undisclosable code is available to the current runtime.

    The provided helper function must take a single parameter, to which a module providing
    access to the undisclosable code will be passed.

    Thie function returns nothing.
    """
    nda_lib = safe_import_nda_libraries()
    if nda_lib is not None:
        helper_function(nda_lib)
