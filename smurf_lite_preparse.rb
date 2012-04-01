#!/usr/bin/env ruby

# this takes the same arguments that smurf-preparse would plus an 'interleave'

# usage: smurf-preparse <structure pdb> <alignment fasta> <output ssi>

usage = "usage: #{$0} <structure pdb> <alignment fasta> <output ssi> <interleave> <mutation_rate> <num_seq> <mutation_interleave_threshold> <blast_augment?>"

structure = ARGV[0]

alignment = ARGV[1]

output = ARGV[2]

threshold = ARGV[3]

mutation_rate = ARGV[4]

num_seq = ARGV[5]

mutation_interleave_threshold = ARGV[6]

blast_augmentation = ( ARGV[7] && ARGV[7].downcase == 'true' )

temp_output = output.gsub('smurf-lite', 'smurf-lite_temp')

cmd = "smurf-preparse #{structure} #{alignment} #{temp_output}"

puts "running #{cmd}"

system(cmd)

if num_seq && mutation_rate
  mutation_output = temp_output.gsub('_temp', '_temp_m')
  puts "mutating, output: #{mutation_output}"
  cmd = "./sim_ev.rb #{temp_output} #{mutation_output} #{mutation_rate} #{num_seq} #{mutation_interleave_threshold}"
  temp_output = mutation_output
  puts "running #{cmd}"
  system(cmd)
end

# insert here optional blast-augmentation
if blast_augmentation
  # this is now orthogonal to mutation
  augmentation_output = temp_output.gsub('.ssi', '_blast.ssi')
  puts "blast augment: output: #{augmentation_output}"
  cmd = "./blast_augment_training.rb #{temp_output} #{augmentation_output}"
  temp_output = augmentation_output
  puts "running #{cmd}"
  system(cmd)
end
#

cmd = "./smurf_lite_simplify.rb #{temp_output} #{output} #{threshold}"

puts "running #{cmd}"

system(cmd)