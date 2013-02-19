# argumentparsers.py - custom parsers for command-line arguments
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

"""Provides custom parsers for command-line arguments based on the argparse
module.

"""

from util import require_python_version
require_python_version(2, 7)

from argparse import Action
from argparse import ArgumentParser

from constants import VERSION_NUMBER
from constants import HMMER, SMURF, PROFILE_SMURF, SMURF_LITE, DEFAULT_SMURF_LITE_THRESHOLD, DEFAULT_SIMEV_FREQUENCY, DEFAULT_SIMEV_COUNT, DEFAULT_SIMEV_THRESHOLD, MRFY
from nrpdb import RepresentativeFields
from scop import Keys

# the default argument for which field in a NRPDB record to examine to
# determine whether a chain is a representative of a set of redundant chains
DEFAULT_REP_ARG = RepresentativeFields.BLAST80

# the default directory containing PDB files in a hierarchy
DEFAULT_PDB_DIR = '/r/bcb/protein_structure/pdb'

# text to display after the help message
DEFAULT_EPILOG = ('For bugs or comments, contact Jeffrey Finkelstein '
                 '<jeffrey.finkelstein@gmail.com>')

# help messages for options and arguments
ALIGNER_HELP = 'the program to use to align chains'
LEVEL_HELP = ('the SCOP hierarchy identifier and sunid of the top hierarchy '
             'level to test, specified in the form "key=sunid", where "key" '
             'is one of "cl", "cf", "sf", "fa", "dm", "sp", or "px" and '
             '"sunid" is the sunid of the hierarchy element to test')
OUTPUT_DIR_HELP = 'the directory in which to place output alignment files'
PDBDIR_HELP = 'the directory containing all PDB files in a hierarchy'
REPFIELD_HELP = ('identifier of field in NRPDB file containing the flag for '
                'whether a chain is a representative of a set of chains')
SUPERFAMILY_HELP = ('the SCOP "sunid" of the superfamily whose families will '
                   'be aligned')
THRESHOLD_HELP = ('the maximum interleave count allowed in a beta strand pair')                   
VERBOSE_HELP = 'print debug messages'

class LevelParser(Action):
    """The argparse.Action class which is called when a -l or --level hierarchy
    level specification argument is provided.

    The argument must be of the form '`key'=`sunid'' where `key' is one of
    scop.Keys (that is, 'cf', 'fa', 'sf', etc.) and `sunid' is the sunid of the
    desired SCOP hierarchy element.

    When called, this class will store the `key' in `namespace.target_level'
    and the `sunid' in `namespace.target_sunid'.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        """Parses the `values' provided as the command-line argument by
        splitting the string on '=' and taking the first element of the tuple
        (as a string) to be the key for the SCOP hierarchy level and the second
        element of the tuple (as an integer) to be the sunid of the hierarchy
        element.

        """
        namespace.target_level, namespace.target_sunid = values.split('=')
        # force the target sunid to be an integer
        namespace.target_sunid = int(namespace.target_sunid)

class BaseArgumentParser(object):
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(BaseArgumentParser, self).__init__()
        self.argparser = ArgumentParser(description=description, epilog=epilog)
        # options
        self.argparser.add_argument('--version', action='version',
                                    version='%(prog)s ' + str(VERSION_NUMBER))
        self.argparser.add_argument('-v', '--verbose', action='store_true',
                                    default=False, help=VERBOSE_HELP)

        # positional arguments
        self.argparser.add_argument('outputdir', type=str,
                                    help=OUTPUT_DIR_HELP)

    def parse_args(self):
        """Parse the command-line arguments provided in sys.argv."""
        return self.argparser.parse_args()

class SmurfArgumentParser(BaseArgumentParser):
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(SmurfArgumentParser, self).__init__(description, epilog)
        self.argparser.add_argument('aligner', type=str,
                                    choices=[HMMER, SMURF, PROFILE_SMURF, SMURF_LITE], help=ALIGNER_HELP)
        self.argparser.add_argument('query_file', type=str)
                                    

class SuperfamilyArgumentParser(BaseArgumentParser):
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(SuperfamilyArgumentParser, self).__init__(description, epilog)
        # positional arguments
        self.argparser.add_argument('level', action=LevelParser, type=str,
                                    help=LEVEL_HELP)
        # options
        self.argparser.add_argument('-r', '--repfield',
                                    default=DEFAULT_REP_ARG, type=str,
                                    choices=RepresentativeFields.ALL_REPS,
                                    help=REPFIELD_HELP)

class AlignmentArgumentParser(BaseArgumentParser):
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(AlignmentArgumentParser, self).__init__(description, epilog)
        self.argparser.add_argument('aligner', type=str,
                                    choices=[HMMER, SMURF, PROFILE_SMURF, SMURF_LITE, MRFY], help=ALIGNER_HELP)
        self.argparser.add_argument('-s', '--smurf_lite_threshold', default=DEFAULT_SMURF_LITE_THRESHOLD, type=str, help=THRESHOLD_HELP)
        self.argparser.add_argument('-f', '--simev_frequency', default=DEFAULT_SIMEV_FREQUENCY, type=str, help=THRESHOLD_HELP)
        self.argparser.add_argument('-c', '--simev_count', default=DEFAULT_SIMEV_COUNT, type=str, help=THRESHOLD_HELP)
        self.argparser.add_argument('-t', '--simev_threshold', default=DEFAULT_SIMEV_THRESHOLD, type=str, help=THRESHOLD_HELP)
        
class MrfArgumentParser(BaseArgumentParser):
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(MrfArgumentParser, self).__init__(description, epilog)
        self.argparser.add_argument('aligner', type=str,
                                    choices=[MRFY], help=ALIGNER_HELP)
        self.argparser.add_argument('-f', '--simev_frequency', default=DEFAULT_SIMEV_FREQUENCY, type=str, help=THRESHOLD_HELP)
        self.argparser.add_argument('-c', '--simev_count', default=DEFAULT_SIMEV_COUNT, type=str, help=THRESHOLD_HELP)
        self.argparser.add_argument('-t', '--simev_threshold', default=DEFAULT_SIMEV_THRESHOLD, type=str, help=THRESHOLD_HELP)

class MultipleAlignmentArgumentParser(SuperfamilyArgumentParser):
    """Argument parser for generating multiple alignments (for example, in the
    generate-matt-alignments.py script.

    """
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(MultipleAlignmentArgumentParser, self).__init__(description,
                                                              epilog)
        # options
        self.argparser.add_argument('-p', '--pdbdir', default=DEFAULT_PDB_DIR,
                                    type=str, help=PDBDIR_HELP)

class StructuralAlignmentArgumentParser(SuperfamilyArgumentParser,
                                        AlignmentArgumentParser):
    def __init__(self, description, epilog=DEFAULT_EPILOG):
        super(StructuralAlignmentArgumentParser, self).__init__(description,
                                                                epilog)
