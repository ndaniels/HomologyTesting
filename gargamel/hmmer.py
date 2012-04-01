# hmmer.py - functions for reading from files produced by HMMER
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

"""Provides functions for reading from files produced by HMMER.

"""

from util import require_python_version
require_python_version(2, 7)

import re
from logger import logger

SCORES_REGEX = r"""(?P<result>  # the total result group
                     (?P<scores>  # the group containing the score triples
                       (-?[0-9]+      # a number...
                       (\.[0-9]+)?  # ...possibly followed by a decimal...
                       (e-?[0-9]+)? # ...possibly followed by an exponent...
                       \s+          # ...followed by spaces...
                       ){3}         # ...repeated three times
                     ){2}         # repeated two times
                     [0-9]+(.[0-9]+)? # a decimal number
                     \s+              # followed by spaces
                     [0-9]+           # followed by an integer
                     \s+              # followed by spaces
                     (?P<sequence>  # the sequence ID group
                       [0-9A-Z]{4}    # four letters or numbers (the PDBID)...
                       _[A-Z0-9]         # ...the underscore and the chain ID
                     )
                   )"""
"""A regular expression matching the score line of an output file from
`hmmsearch'.

"""

scores_regex = re.compile(SCORES_REGEX, re.IGNORECASE | re.VERBOSE)
"""The compiled regular expression, ignoring case, and allowing for extra
comments and whitespace within the regular expression string.

"""

class Score(object):
    """A score for a HMMER alignment.

    """

    def __init__(self, evalue=0.0, score=0.0, bias=0.0):
        """Instantiates this score with the specified E-value, score, and bias.

        """
        self.evalue = float(evalue)
        self.score = float(score)
        self.bias = float(bias)

    def __str__(self):
        """Returns the string representation of this score."""
        return 'Score[{}, {}, {}]'.format(self.evalue, self.score, self.bias)


class HmmerResult(object):
    """The result of a HMMER alignment, as expressed by the output from, for
    example, `hmmsearch'.

    For now, this class maintains a Score object for the full sequence and for
    the best one domain, as well as the domain exponent, domain N, and the PDB
    ID and chain ID of the sequence compared by `hmmsearch'.

    """

    def __init__(self, full_seq_score, best_domain_score, domain_exp, domain_N,
                 pdbid, chain):
        """Instantiates this class with the specified Score objects for the
        full sequence and the best one domain, respectively.

        """
        self.full_seq_score = full_seq_score
        self.best_domain_score = best_domain_score
        self.domain_exp = float(domain_exp)
        self.domain_N = int(domain_N)
        self.pdbid = pdbid
        self.chain = chain

    def __str__(self):
        """Returns the string representation of this result."""
        return 'HmmerResult[{}:{}: {}, {}, {}, {}]'.format(self.pdbid,
                                                        self.chain,
                                                        self.full_seq_score,
                                                        self.best_domain_score,
                                                        self.domain_exp,
                                                        self.domain_N)


def result_from_file(filename):
    """Reads the specified `filename' output by `hmmsearch' and returns an
    instance of HmmResult.

    """
    # read all the text from the file
    with open(filename, 'r') as f:
        all_text = f.read()

    if len(all_text) < 1:
      return None
    # search for a match in the text
    match = scores_regex.search(all_text)
    # split the match up into space-separated fields
    if match == None:
      # instead, deal with broken hmmsearch
      # return a fake HmmerResult
      logger.debug('Got no result from input. Setting negative value.')
      return HmmerResult(Score(1.0, -1000.0, 0.0), Score(1.0, -1000.0, 0.0),
                         '0.0', '0', 'unkn', 'A')
    fields = match.group('result').split()
    # create the Score objects from the fields
    full_seq_score = Score(*fields[0:3])
    best_domain_score = Score(*fields[3:6])
    # get the PDBID and chain ID from the last field
    pdbid = fields[-1].split('_')[0]
    chain = fields[-1].split('_')[1]

    # return a new instance of HmmerResult, with the created full sequence and
    # best domain scores, the domain exponent and domain N, and the PDB ID and
    # chain ID of the compared sequence
    return HmmerResult(full_seq_score, best_domain_score, fields[6], fields[7],
                       pdbid, chain)
