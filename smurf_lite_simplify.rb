#!/usr/bin/env ruby

require './beta_pair'
require './stockholm'

# this removes beta-strand pairs with greater than 'threshold' interleaving
# to produce simple enough profiles for smurf to handle

DEBUG = false
usage = "Usage: #{$0} <infile> <outfile> <interleave_threshold>"
unless ARGV.length == 3
  puts usage
  exit(1)
end
# args to take: infile, outfile, interleave_threshold
infile = ARGV[0]
outfile = ARGV[1]
threshold = ARGV[2].to_i

alignment = Stockholm.new(infile)

alignment.simplify_betas(threshold)

alignment.output(outfile)