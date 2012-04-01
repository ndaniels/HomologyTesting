#!/usr/bin/env tcsh
#
# blastp-to-muscle.sh - generate multiple alignment from BLAST similar proteins
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

# exit status code for bad arguments
set STATUS_ARGS=4

# the format with which to output files (wrap this in literal quotes when using
# this string in a command)
#set OUTPUT_FORMAT="10 sseq"

# the sed expression which adds in FASTA format header lines to protein
# sequence strings (wrap this in literal quotes when using this string in a
# command)
#set SED_EXPR="s/[A-Z-]*/>some sequence.\n&/g"

# set the default value for the prefix for the blastp database
set DATABASE="/data/databases/nr" # will only work on sunfire60

# set the default expectation value threshold for saving hits
set EVALUE=1

# set the max number of aligned sequences to keep
set MAX_TARGET_SEQS=20

# define the print_usage "function" (c shell doesn't have functions)
alias print_usage ./blastp-to-muscle-usage.sh

# use getopt to parse the command line arguments
set args=`getopt d:e:x:o: $*`

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
    case -o # output file
        set OUTPUT_FILE=$args[2]
        shift args
        breaksw
    case -- # no more options
        # if the query file has not been defined, print usage and exit
        if ($#args < 2) then
            echo "blastp-to-muscle.sh: no query file declared"
            print_usage
            exit $STATUS_ARGS
        endif

        # otherwise get the query file
        set QUERY=$args[2]
        breaksw
    endsw
    shift args
end

# check if the proper cached file is there already
if (-f $OUTPUT_FILE) then
  echo "found cached copy of $PROFILE"
else

  # run blastp with the specified options, add a fasta header to each sequence,
  # and run them through muscle to align them
  blastp -num_threads 12 -db $DATABASE -evalue $EVALUE -outfmt "10 sseqid sseq" -max_target_seqs $MAX_TARGET_SEQS -query $QUERY | head -n $MAX_TARGET_SEQS | sed "s/^\(.*\),/>\1\n/g" | cat $QUERY - | muscle | ./reorder_muscle_output.rb $QUERY > $OUTPUT_FILE
endif

exit $status
