# logger.py - a custom logger for this package and modules which use it
# Copyright 2010 Jeffrey Finkelstein
#
# This file is part of smurf.
#
# smurf is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# smurf is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# smurf.  If not, see <http://www.gnu.org/licenses/>.

"""Provides a logger which modules using this package can use.

"""

import logging

# the format string for logging messages; see documentation for logging module
LOG_FORMAT = ('[%(levelname)s] (%(asctime)s) %(filename)s:%(lineno)s: '
              '%(message)s')
formatter = logging.Formatter(LOG_FORMAT)

# the name of the logger; this doesn't really matter, just use the same name in
# every place where we want to use the same logger
LOGGER_NAME = 'gargamel'

# the file to which to log
LOG_FILE = './gargamel.log'

# create the logger
logger = logging.getLogger(LOGGER_NAME)

# create a console appender, which logs to stderr
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# create a file appender, which appends to a logfile
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# enable the logger for all messages DEBUG and higher (that is, all messages)
logger.setLevel(logging.DEBUG)

# log that we are creating a new logger
logger.debug('')
logger.debug('CREATED NEW INSTANCE OF LOGGER (probably means this is a new')
logger.debug('  run of the alignment scripts)')
logger.debug('')
