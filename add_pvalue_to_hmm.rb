#!/usr/bin/env ruby

require 'tempfile'

# takes 2 mandatory arguments: an hmm+ file to read (and modify), and a fasta file to run on
# computes mean and stddev of the distrbution, writes these to the hmm file.
# also takes 3 option arguments: smurflite threshold, simev-freq, simev-count
# and populates HMM with those if present.

# use /r/bcb/protein_structure/smurf_calibration/calibration.fasta
# just pull raw score out of everything

#  Add methods to Enumerable, which makes them available to Array
module Enumerable
 
  #  sum of an array of numbers
  def sum
    return self.inject(0){|acc,i|acc +i}
  end
 
  #  average of an array of numbers
  def mean
    return self.sum/self.length.to_f
  end
 
  #  variance of an array of numbers
  def sample_variance
    avg=self.mean
    sum=self.inject(0){|acc,i|acc +(i-avg)**2}
    return(1/self.length.to_f*sum)
  end
 
  #  standard deviation of an array of numbers
  def standard_deviation
    return Math.sqrt(self.sample_variance)
  end
 
end  #  module Enumerable

def parse_scores(filehandle)
  results = []
  filehandle.each_line do |line|
    if line =~ /^Raw score: (-?\d+\.?\d+)/
      results << Regexp.last_match[1].to_f
    end
  end
  results
end

BINARY = 'smurf-lite'
hmm_path = ARGV[0]
fasta_file = ARGV[1]

threshold, simev_freq, simev_count = ARGV[2], ARGV[3], ARGV[4]

usage = "usage: #{$0} hmm_path fasta_file <threshold> <simev_freq> <simev_count>"

if ! File.readable?(hmm_path)
  puts "hmm file #{hmm_path} not readable!"
  puts usage
  exit 1
end

if ! File.readable?(fasta_file)
  puts "query fasta file #{fasta_file} not readable!"
  puts usage
  exit 1
end

temp = Tempfile.new('smurf')
temp.close
cmd = "#{BINARY} #{hmm_path} #{fasta_file} #{temp.path}"
puts "#{$0}: running #{cmd}"
scores = []
begin
  system(cmd)
  temp.open
  scores += parse_scores(temp)
ensure
  temp.close
  temp.unlink
end
puts scores.inspect

mean = scores.mean
stddev = scores.standard_deviation

# now, modify the hmm file

# add these lines:

hmm_addition = "MEAN  #{mean}\nRMSD  #{stddev}"


hmm_addition += "\nSMURFLITE #{threshold}" if threshold
hmm_addition += "\nSIMEVFREQ #{simev_freq}" if simev_freq
hmm_addition += "\nSIMEVCOUNT #{simev_count}" if simev_count  
hmm_addition += "\n"
  
hmm_lines = File.readlines(hmm_path)

index_to_add = hmm_lines.find_index{|line| line =~ /^ALPH/} + 1

hmm_lines.insert(index_to_add, hmm_addition)

File.open(hmm_path, 'w') do |f|
  f.print hmm_lines.join('')
end




