import os
import papier

_base_path = os.path.dirname(papier.__file__)


def path(*level):
    global _base_path

    primary   = os.path.abspath(os.path.join(_base_path, *level))
    secondary = os.path.abspath(os.path.join(_base_path, '..', *level))
    local     = os.path.abspath(os.path.join(*level))

    return local  if os.path.exists(local)     else (
        secondary if os.path.exists(secondary) else primary
    )
