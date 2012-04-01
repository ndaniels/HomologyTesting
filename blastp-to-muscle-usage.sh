#!/usr/bin/env tcsh
#
# blastp-to-muscle-usage.sh - print usage information for blastp-to-muscle.sh
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

echo "Usage: blastp-to-muscle.sh [options] fasta_file"
echo "Options:"
echo "  -d <prefix>                The prefix of the blast database to use"
echo "                             (default: /r/bcb/databases/nr)"
echo "  -e <number>                The expectation value threshold for saving hits"
echo "                             (default: 10)"
echo "  -x <number>                The maximum number of aligned sequences to keep"
echo "                             (must be greater than 0, default: 100)"
echo
echo "For bugs or comments, contact Jeffrey Finkelstein"
echo "  <jeffrey.finkelstein@gmail.com>"

exit 0
