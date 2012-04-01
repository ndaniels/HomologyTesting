class BetaSet
  
  attr_accessor :strand_pairs, :residue_pairs, :beta_positions
  
  def initialize(strands=nil)
    @strand_pairs = []
    @residue_pairs = Hash.new
    @beta_positions = Set.new
    strands.each{|s| self.add(s)} if strands
    
  end
  
  def display
    @strand_pairs.each do |pair|
      puts pair.display
    end
  end
  
  def add(strand)
    
    @strand_pairs << strand
    
    # add the residue-pairing info
    strand.residue_pairs.each_pair do |k,v|
      # puts "warning: already have a pairing: #{k} -> #{@residue_pairs[k].inspect}. Adding #{v}" if @residue_pairs[k]
      @residue_pairs[k] ||= Set.new
      @residue_pairs[k] << v
    end
    
    strand.positions.each do |pos|
      @beta_positions << pos
    end
    
  end
  
  def find_with_position(pos)
    strand_pairs.select{|b| b.positions.include?(pos)}
  end
  
  def beta_positions_with_min_interleave(threshold)
    # look at the beta positions
    # return the ones that are in a beta_pair with interleave >= threshold
    @beta_positions.select{|pos| ! self.find_with_position(pos).select{|b| b.interleave >= threshold}.empty? }.uniq
    
  end
  
  def find_with_max_interleave(threshold)
    @strand_pairs.select{|b| b.interleave <= threshold}
  end
  
  def find_with_min_interleave(threshold)
    @strand_pairs.select{|b| b.interleave >= threshold}
  end
  
  def compute_interleave

    @strand_pairs.each do |beta|
      # compare to every other pair
      strand_1_start = beta.s1
      strand_2_start = beta.s2

      @strand_pairs.each do |other|
        next if beta == other # rely on object equality
        # core logic: if the other's range is within this one's range, increment interleave_count[idx]
        # puts "comparing #{other.s1}-#{other.s2} to #{beta.s1}-#{beta.s2}" if DEBUG
        if (other.s1 >= beta.s1 && other.s1 <= beta.s2) ||
           (other.s1 >= beta.s1 && other.s2 <= beta.s2) then
             beta.interleave += 1
        end
      end
    end
  end
  
  def paired_residues(position)
    # return the positions of the residues paired with this one
    @residue_pairs[position]
  end
  
  def paired_residue(position)
    # randomly return one of the available positions
    possibilities = paired_residues(position).to_a
    if possibilities.length == 1
      possibilities[0]
    else
      selector = rand(possibilities.length)
      possibilities[selector]
    end
    
  end
  
  
end

class BetaPair
  require 'set'
  attr_accessor :s1, :s2, :length, :maxgap, :parallel, :conformation, :interleave, :beta_id, :positions, :exposures, :residue_pairs
  DEBUG = false
  
  def initialize(s1, s2, length, maxgap, parallel, conformation)

    
    @s1, @s2, @length, @maxgap, @parallel, @conformation = s1.to_i, s2.to_i, length.to_i, maxgap.to_i, (parallel.to_i == 1), conformation
    
        raise "Illegal conformation #{@conformation} for length #{@length}" unless @length == @conformation.length
    

    
    @interleave = 0
    
    # set the positions and exposures
    
    @positions = Set.new
    
    @exposures = Hash.new
    @residue_pairs = Hash.new
    
    # see if we need to read conformation in reverse for back strand
    if ! @parallel then
      s2_conformation = @conformation.reverse
    else
      s2_conformation = @conformation
    end
    # now set the exposures and positions
    (0...@length).to_a.each do |pos|

      @positions << @s1 + pos
      @positions << @s2 + pos
      @exposures[@s1 + pos] = (@conformation[pos].chr == 'i' ? :buried : :exposed)
      @exposures[@s2 + pos] = (s2_conformation[pos].chr == 'i' ? :buried : :exposed)
      if @parallel then
        p2 = @s2 + pos
      else
        p2 = @s2 + @length - 1 - pos
      end
      @residue_pairs[@s1 + pos] = p2
      @residue_pairs[p2] = @s1 + pos
      
      
    end
    # puts @residue_pairs.inspect
    
  end
  
  def self.new_from_string(str)
    raise "Invalid input #{str}" unless str =~ /^#=BETA/
    items = str.split(/\s+/)
    return self.new(*items[1..-1])
  end
  
  def to_s
     ["#=BETA #{@s1}", @s2, @length, @maxgap, (@parallel ? '1' : '-1'), @conformation].join("\t")
  end
  
  def display
    "BETA: #{@s1} and #{@s2}, length: #{length}, interleave: #{interleave}"
  end
  
  def exposure(idx)
    @exposures[idx]
  end

end