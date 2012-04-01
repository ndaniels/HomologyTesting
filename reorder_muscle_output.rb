#!/usr/bin/env ruby
require 'rubygems'
require 'bio'

# reorder_muscle_output.rb
# this program attempts to overcome the current limitation in muscle whereby
# the '-stable' option is currently unavailable. We want the original
# query sequence to appear first.
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

class String
  
  def all_indices(char)
    # return an array of all indices in the string that match the passed character 'char'
    result = []
    self.split('').each_with_index{|e, idx| result << idx if e == char }
    result
  end
  
  def drop_indices(indices)
    result = ''
    self.split('').each_with_index{|e,idx| result += e unless indices.include?(idx)}
    result
  end
  
end

unless ARGV.length == 1
  puts "Usage: #{$0} query_file"
end

# get the query line from the query file; this is used to identify the original query to move it to the top
query_id = ''
Bio::FlatFile.new(Bio::FastaFormat, ARGF).each do |f|
  query_id = f.definition
end

input = Bio::FlatFile.new(Bio::FastaFormat, STDIN)

output = ''

container = {:first => nil, :rest => []}

input.each do |entry|
  # entry is a single fasta entry
  if entry.definition == query_id
    container[:first] = entry
  else
    container[:rest] << entry
  end
end

# next, perform surgery to remove gaps
  
gap_indices = container[:first].seq.all_indices('-')

# for each sequence, remove those chars.

container[:first].data = container[:first].seq.drop_indices(gap_indices)

container[:rest].each do |entry|
  entry.data = entry.seq.drop_indices(gap_indices)
end

# now output to a fasta file

puts Bio::Sequence::NA.new(container[:first].data).to_fasta(container[:first].definition)

container[:rest].each do |entry|
  puts Bio::Sequence::NA.new(entry.data).to_fasta(entry.definition)
end

