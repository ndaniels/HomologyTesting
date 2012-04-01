#!/usr/bin/env python
#
# add-good-chains-to-whitelist.py - adds good chains to the whitelist
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

import os.path

# The goodchains file format is as follows: each line consists of one PDB ID,
# which is an alphanumeric string of length 4, followed by a colon, followed by
# a single chain letter (like A, B, C, etc.). Repeat PDB IDs are allowed in the
# goodchains file. Lines starting with hashes are ignored.

# the file containing a list of PDB IDs with chains to include
GOODCHAINS_FILENAME = './goodchains'

if os.path.exists(GOODCHAINS_FILENAME) and os.path.isdir(GOODCHAINS_FILENAME):
    raise ValueError('Specified good chains file is a directory ('
                     + GOODCHAINS_FILENAME + ')')

# The whitelist file format is as follows: each line consists of one PDB ID,
# which is an alhanumeric string of length 4, followed by a colon, followed by
# one or more chain letters (like A, B, C, etc.). Repeat PDB IDs are NOT
# allowed in the whitelist file; behavior when repeat PDB IDs are encountered
# is undefined. Lines starting with hashes are ignored.

# the file containing the whitelist
WHITELIST_FILENAME = './whitelist'

if os.path.exists(WHITELIST_FILENAME) and os.path.isdir(WHITELIST_FILENAME):
    raise ValueError('Specified whitelist file is a directory ('
                     + WHITELIST_FILENAME + ')')

# open the good chains file only if it exists
good_chains = {}
if os.path.exists(GOODCHAINS_FILENAME):
    with open(GOODCHAINS_FILENAME, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            try:
                pdbid, chain = line.split(':')
                
                if pdbid in good_chains:
                    if chain not in good_chains[pdbid]:
                        good_chains[pdbid] += chain
                else:
                    good_chains[pdbid] = chain
            except ValueError:
                print 'Incorrectly formatted line in good chains file:', line

# open the whitelist only if it exists
whitelist = {}
if os.path.exists(WHITELIST_FILENAME):
    with open(WHITELIST_FILENAME, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            try:
                pdbid, chains = line.split(':')
                whitelist[pdbid] = chains
            except ValueError:
                print 'Incorrectly formatted line in whitelist file:', line

# add the good chains to the whitelist
for pdbid, chain in good_chains.iteritems():
    if pdbid in whitelist:
        if chain not in whitelist[pdbid]:
            whitelist[pdbid] += chain
    else:
        whitelist[pdbid] = chain

# write the whitelist back to the file
with open(WHITELIST_FILENAME, 'w') as f:
    for pdbid, chains in whitelist.iteritems():
        f.write(pdbid + ':' + chains + '\n')
