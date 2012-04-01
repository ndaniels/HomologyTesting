#!/usr/bin/env tcsh
#
# blastp-to-muscle.sh - generate multiple alignment from BLAST similar proteins
# Copyright 2010 Noah M. Daniels
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

# set the default value for the prefix for the blastp database
set DATABASE="/r/bcb/databases/nr"

# set the default expectation value threshold for saving hits
set EVALUE=0.001

# set the max number of aligned sequences to keep
set MAX_TARGET_SEQS=20

set CACHE="/data/profile_smurf/cache"

# define the print_usage "function" (c shell doesn't have functions)
alias print_usage ./run_profile_smurf_usage.sh

# use getopt to parse the command line arguments
set args=`getopt d:e:x: $*`

# iterate over the command-line arguments, popping them off (with the shift
# command) one at a time (or two at a time in the case of options which accept
# parameters)
# the code for this is adapted from
# http://www.decf.berkeley.edu/help/unix/csh/flowcontrol.html
while ($#args > 0)
    switch ($args[1])
    case -d # database prefix
        set DATABASE=$args[2]
        shift args
        breaksw
    case -e # expectation value threshold
        set EVALUE=$args[2]
        shift args
        breaksw
    case -x # maximum target sequences
        set MAX_TARGET_SEQS=$args[2]
        shift args
        breaksw
    case -- # no more options
        # if the query file has not been defined, print usage and exit
        if ($#args < 4) then
            echo "run_profile_smurf.sh: no query file declared"
            print_usage
            exit $STATUS_ARGS
        endif

        # otherwise get the query file
        set HMM_FILE=$args[2]
        set QUERY=$args[3]
        set OUTPUT=$args[4]
        set TEMP_PROFILE= `basename $QUERY.$EVALUE.$MAX_TARGET_SEQS.profile`
        set PROFILE="$CACHE/$TEMP_PROFILE"
        breaksw
    endsw
    shift args
end



echo "./blastp-to-muscle.sh -d $DATABASE -e $EVALUE -x $MAX_TARGET_SEQS -o $PROFILE $QUERY"
  
./blastp-to-muscle.sh -d $DATABASE -e $EVALUE -x $MAX_TARGET_SEQS -o $PROFILE $QUERY
echo "profile-smurf $HMM_FILE $PROFILE $OUTPUT"

profile-smurf $HMM_FILE $PROFILE $OUTPUT

exit $status