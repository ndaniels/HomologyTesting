#!/usr/bin/env ruby
$: << File.dirname(__FILE__)
require 'stockholm'
require 'tempfile'
DEBUG = false
SKIP_MUTATED = true
GAP = '-'

# returns a modified version of subject, with leading and trailing gaps, as well as inserted gaps.
def match_to_alignment(original, query, subject, qstart)
  
  ######
  # we have original query sequence (with gaps), hit[:qseq] (with gaps in blast alignment) and
  # hit[:sseq] (with gaps in blast alignment).
  # invariants:
  # every gap in the original query sequence will exist in the output subject sequence
  # every gap in the BLAST query sequence will simply be elided from the subject
  # every gap in the BLAST subject sequence will carry through to the output subject sequence
  ######
  
  orig_query = original.sequence.split('')
  aligned_query = query.split('')
  aligned_subject = subject.split('')
  
  output = '' 
  gap_re = /^[\-\.X]+/
  orig_initial_gaps = 0
  orig_initial_gaps = original.sequence.match(gap_re)[0].length if original.sequence.match(gap_re)
  leading_blast_query_gaps = qstart.to_i - 1
  # output += (GAP * orig_initial_gaps)
  
  # now get rid of aligned_query gaps first
  gap_positions = []
  aligned_query.each_with_index do |letter, idx|
    if letter =~ gap_re
      gap_positions << idx 
    end
  end
  # cut them out from the end so we don't break indexing
  gap_positions.reverse.each do |pos|
    # aligned_query.slice!(pos) # we never use this
    aligned_subject.slice!(pos)
  end
  
  # now our aligned_query has NO gaps!
  
  # the original query (with gaps) DEFINES the length of the output string.
  offset = 0
  orig_query.each_with_index do |letter, idx|

    # offset exists to realign the query and subject with the original query
    # offset is how many characters to SUBTRACT from idx to get the current letter in
    # the query and subject sequences
    
    # this is before leading_blast_query_gaps
    # or this is a gap in the original
    ## thus, increment offset and append a gap

    if idx < leading_blast_query_gaps || letter =~ gap_re
      # puts "A: idx: #{idx}, offset: #{offset}, len: #{aligned_subject.length}, #{qstart}"
      offset += 1
      output += GAP
    elsif (idx - offset) > aligned_subject.length - 1
      # puts "B: idx: #{idx}, offset: #{offset}, len: #{aligned_subject.length}"
    # this is after the end of the aligned subject
    # thus, just append a gap
      output += GAP
    else
    # this is a non-gap in the original
    ## thus, output the aligned_subject's character
      # puts "C: idx: #{idx}, offset: #{offset}, len: #{aligned_subject.length}, char: #{aligned_subject[idx - offset]}"
      # puts aligned_subject.inspect
      output_letter = aligned_subject[idx - offset]
      if output_letter =~ gap_re
        output_letter = GAP
      end
      output += output_letter
    end
  end
  
  output
  
end

def run_blast(query)
  # runs a blast query, currently with hardcoded parameters, based on the input query string
  blast_keys = [:qseqid, :sseqid, :qseq, :sseq, :pident, :qstart, :qend, :sstart, :send]
  blast_key_string = blast_keys.map(&:to_s).join(' ')
  temp = Tempfile.new('blast')
  temp.write(query)
  temp.close
  blast_cmd = "blastp -num_threads 12 -db /data/databases/nr -evalue 1e-150 -outfmt \"10 #{blast_key_string}\" -max_target_seqs 100 -query #{temp.path}"
  # ensure that the temp file is removed even if something bad happens with the query
  begin
    result = `#{blast_cmd}`
  ensure
    temp.unlink
  end
  if DEBUG
    puts "query:"
    puts query
    puts "results:"
    puts result
  end
  # create an array of hashes, each keyed on the keys below (mirrors those requested in the blast string)
  result.split("\n").map{|line| Hash[blast_keys.zip(line.split(','))]}
end


input_file = ARGV[0]
output_file = ARGV[1]
alignment = Stockholm.new(input_file)

# we'll actually be reading a fasta (or ssi?) file, so read each entry....
# process pipeline is: matt, smurf-preparse, augment-or-simev, smurf-hmmbuild
# 
# blastp -num_threads 12 -db /data/databases/nr -evalue 1e-150 -outfmt "10 qseqid sseqid qseq sseq pident qstart qend" -max_target_seqs 100 -query ~/test_blast.fasta
# 
# we'll drop 100% identical hits.

alignment.sequences.each do |seq|
  ungapped_seq = seq.ungapped
  next if SKIP_MUTATED && seq.name =~ /^m_\d+/
  results = run_blast(ungapped_seq)
  if DEBUG
    puts "query name: #{seq.name}"
  end
  results.each do |hit|
    printable_hit_name = (hit[:sseqid] + "|matched to #{seq.name}").gsub(/\s+/, '_')
    if hit[:pident].to_f == 100.0 || hit[:pident].to_f < 50.0 # skip identical and bad hits
      if DEBUG
        puts "skipping #{printable_hit_name}, pident #{hit[:pident]}"
      end
      next
    end
    aligned_hit = match_to_alignment(seq, hit[:qseq], hit[:sseq], hit[:qstart])
    alignment.append(AlignedSequence.new(printable_hit_name, aligned_hit, alignment))
  end
end

# now output

alignment.output(output_file)
  

