# TODO refactor this into separate files for distinct classes

class AlignedSequence
  
  require './beta_pair'
  attr_accessor :name, :sequence, :alignment
  
  def initialize(name, sequence, alignment)
    @name, @sequence, @alignment = name, (sequence && sequence.upcase), alignment
  end
  
  def [](idx)
    @sequence[idx].chr
  end
  
  def mutate(indices)
    
    new_sequence = AlignedSequence.new(name, sequence, alignment)
    # puts self.sequence

    indices.each do |idx|
      # get the residue
      res = @sequence[idx].chr

      partner_index = alignment.beta_set.paired_residue(idx)
      # don't mutate gaps
      # puts alignment.beta_set.inspect
      # puts self.inspect
      # puts "#{idx},#{partner_index}"
      # puts "considering #{idx} (#{self[idx].chr}),#{partner_index}(#{self[partner_index].chr})"
      next if self.gap?(idx) || self.gap?(partner_index)
      # puts "continuing... "
      # get the conformation
      bp = alignment.beta_set.find_with_position(idx).first
      conformation = bp.exposure(idx)
      # puts @sequence.inspect
      # mutate that index's partner
      
      new_residue = BetaMutation.mutation(conformation, res)
      # puts "mutating: #{conformation}, #{res} at #{idx}. p: #{partner_index} from #{new_sequence[partner_index]} to #{new_residue}"
      new_sequence[partner_index] = new_residue
      # puts @sequence[partner_index].chr
      # puts self[partner_index]
      # puts new_sequence[partner_index]
    end
    
    new_sequence
    
  end
  
  def []=(idx, mutation)
    @sequence[idx] = mutation
  end
  
  def to_s
    @name + ' '*5 + @sequence
  end
  
  def gap?(position)
    @sequence[position].chr == '-' || @sequence[position].chr == '.' || @sequence[position].chr == 'X'
  end
  
  def ungapped
    @sequence.gsub(/[\-\.X]/, '')
  end
  
end

class Stockholm
  
  attr_accessor :header, :sequences, :tail, :beta_set
  
  def initialize(infile)
    
    @header = []
    @sequences = []
    @new_sequences = []
    @beta_set = BetaSet.new
    @tail = nil
    File.foreach(infile) do |line|
      line.chomp!
      if line =~ /^#=BETA/
        @beta_set.add(BetaPair.new_from_string(line))
      elsif line.empty? || line[0].chr == '#'
        @header << line
      elsif line == '//' # end of file
        @tail = [line]
      else
        name, seq = line.split(/\s+/)
        @sequences << AlignedSequence.new(name,seq,self)
      end
    end  
    
    @beta_set.compute_interleave
    
  end
  
  def display_betas
    @beta_set.display
  end
  
  def simplify_betas(threshold)
    # modifies betas to include only those with an interleave <= threshold
    new_betas = @beta_set.find_with_max_interleave(threshold)
    @beta_set = BetaSet.new(new_betas)
    
  end
  
  def append(seq)
    @new_sequences << seq
  end
  
  def sequence_strings
    (@sequences + @new_sequences).collect{|s| s.to_s}
  end
  
  def beta_strings
    @beta_set.strand_pairs.collect{|b| b.to_s}
  end
  
  def to_s
    (self.header + self.beta_strings + [''] + self.sequence_strings + self.tail).join("\n")
  end
  
  def output(filename)
    File.open(filename, 'w') do |f|
      f.puts self.to_s
    end
  end
  
end
