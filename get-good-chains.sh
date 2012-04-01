#!/usr/bin/env bash
#
# get-good-chains.sh - parses useable PDBID chains from Matt output
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

STATUS_ARGS=4

if [ $# != 1 ]; then
    echo "Usage: $0 <Matt-output-file>"
    exit $STATUS_ARGS
fi

# the first argument must be a file containing the output of Matt
MATT_OUTPUT=$1

grep -Fe "Chain" $MATT_OUTPUT \
    | grep -ve "([01234] residues)" \
    | grep -vFe "**" \
    | cut -d" " -f5 \
    | sed -e "s/pdb//" -e "s/.ent.gz//"

exit 0
