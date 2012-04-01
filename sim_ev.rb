#!/usr/bin/env ruby

require './beta_mutation'

EXPOSED = 'ExposedProbability.csv'
BURIED = 'BuriedProbability.csv'

# arguments: input file, output file, mutation_frequency, multiplication_factor, interleave_threshold
usage = "Usage: #{$0} <infile> <outfile> <mutation_frequency> <multiplication_factor> <interleave_threshold>"

raise usage unless ARGV.length >= 4

infile, outfile, mutation_frequency, multiplication_factor, interleave_threshold = *ARGV
mutation_frequency = mutation_frequency.to_f

multiplication_factor = multiplication_factor.to_i
if interleave_threshold
  interleave_threshold = interleave_threshold.to_i
end
puts "mutation frequency: #{mutation_frequency}, multiplication_factor: #{multiplication_factor}"
BetaMutation.load_tables(EXPOSED, BURIED)

BetaMutation.mutate_alignment(infile, outfile, mutation_frequency, multiplication_factor, interleave_threshold)