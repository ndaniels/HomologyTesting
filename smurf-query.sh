#!/usr/bin/env tcsh
#
# smurf-query.sh - creates an alignment given a HMM and a FASTA file as a query
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

set STATUS_ARGS=4

if ($# != 3) then
    echo "Usage: $0 <HMMfile> <FASTAfiletotest> <outputfile>"
    exit $STATUS_ARGS
endif

# get file names from command line arguments
set HMMFILE=$1
set FASTAFILE=$2
set OUTPUTFILE=$3

# run smurf
smurf $HMMFILE $FASTAFILE $OUTPUTFILE

exit $status
