import os

import papier


def path(*level):
    return os.path.abspath(
        os.path.join(
            os.path.dirname(papier.__file__),
            *level
        )
    )
