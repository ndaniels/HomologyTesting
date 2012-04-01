class BetaMutation
  require './stockholm'
  require './beta_pair'
  
  LETTERS = 'ACDEFGHIKLMNPQRSTVWY'

  # take an alignment as input. output a mutated alignment.
  def self.mutate_alignment(ssi_in, ssi_out, frequency, num_each, threshold=nil)
    
    raise "invalid frequency: #{frequency} must be between 0.0 and 1.0" unless 0 <= frequency && 1 >= frequency
    
    threshold ||= 0 # if no threshold, set to 0 so we mutate all betas
    
    # read ssi file
    
    training_data = Stockholm.new(ssi_in)
    
    # now, for each beta that's got an interleave > threshold
    mutable_positions = training_data.beta_set.beta_positions_with_min_interleave(threshold)
    if ! mutable_positions.empty?
      # for each sequence in the alignment
      training_data.sequences.each do |sequence|
        # create num_each new sequences for this sequence
        orig_name = sequence.name
        num_each.times do |i|
          new_name = "m_#{i}_" + orig_name
          mutation_positions = self.mutation_positions(mutable_positions, frequency)
          # puts "mutating: #{mutation_positions.inspect}"
          new_sequence = sequence.mutate(mutation_positions)
          new_sequence.name = new_name
          training_data.append(new_sequence)
        end
      
      end
    
    end
    
    training_data.output(ssi_out)

  end
  
  def self.load_tables(exposed_path, buried_path)
    # seed rand
    srand(1)
    
    # already normalized
    
    # these are row,col, where row indicates the existing AA and col indicates the AA to mutate to.
    @@probabilities = {}
    paths = {:buried => buried_path, :exposed => exposed_path}
    paths.each do |kind, path|
      line_num = 0
      File.foreach(path) do |line|
        from_aa = LETTERS[line_num].chr
        entries = line.chomp.split(',')
        entries.each_with_index do |ent, col_num|
          next if (!ent || ent.length == 0 || ent == ' ')
          to_aa = LETTERS[col_num].chr
          @@probabilities[kind] ||= {}
          @@probabilities[kind][from_aa] ||= {}
          @@probabilities[kind][from_aa][to_aa] = ent.to_f
        end
        line_num += 1
      end
    end 
  end
  
  def self.mutation(exposure, from)
    # returns the aa to mutate the residue paired with 'from', given the exposure
    raise "bad exposure #{exposure}" unless exposure == :buried || exposure == :exposed
    raise "bad 'from' #{from}" unless from && LETTERS.include?(from)
    probs = @@probabilities[exposure][from]

    r = rand(0)
    # puts "r: #{r}"
    last_aa = from # default to no change
    LETTERS.each_char do |aa|
      if r - probs[aa] < 0.0
        # puts "done. last_aa now: #{last_aa}"
        return last_aa
      else
        last_aa = aa
        # puts "last_aa now: #{last_aa}"
        r -= probs[aa]
      end
    end
    # puts "last_aa now: #{last_aa}"
    # default to the last one
    return last_aa
    
  end
  
  def self.mutation_positions(mutation_positions, freq)
    # mutation_positions should be the result of either BetaPair.beta_positions or 
    # BetaPair.beta_positions_with_min_interleave
    # return the beta-strand positions (vs. sum of lengths) that will be mutated.
    bpos = mutation_positions.to_a
    num_to_mutate = (freq*bpos.length).to_i
    
    result = []
    num_to_mutate.times do |t|
      result << bpos[rand(bpos.length)]
    end
    result
    
  end
  
end