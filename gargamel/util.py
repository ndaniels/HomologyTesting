# util.py - common utility functions
# Copyright 2010 Jeffrey Finkelstein
#
# This file is part of smurf.
#
# smurf is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# smurf is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# smurf.  If not, see <http://www.gnu.org/licenses/>.

"""Provides common utility functions.

"""

def require_python_version(*version):
    """Exits with status 1 if the current version of Python as determined by
    sys.version_info is less than the specified version.

    Positional arguments must used to specify the required version number. For
    example:

    >>> require_python_version(1, 0) # does not exit
    >>> require_python_version(4, 0) # will exit the interpreter
    CRITICAL:root:This script requires Python version 4.0 or later.
    CRITICAL:root:Your interpreter version: 2.6.5.final.0.
    [exits with status 1]

    """
    import sys
    if sys.version_info < version:
        import logging
        logging.critical('This script requires Python version '
                         + '.'.join(str(n) for n in version) + ' or later.')
        logging.critical('Your interpreter version: '
                         + '.'.join(str(n) for n in sys.version_info) + '.')
        sys.exit(1)
