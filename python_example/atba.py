class Agent: # do not change class name, team index name or get get_output_vector
    def __init__(self, name, team, index): # constructor
        self.index = index

    def get_output_vector(self, values): # values is to get access to all availiable data
        return [1, 0, 0, 0, 0, False, False, False]
        
        # First Element - Throttle (1 = Max Acceleration) (-1 = Max Deceleration )
        # Second Element - X-Axis/Steering (1 = Max Right) (-1 = Max Left)
        # Third Element - Pitch (1 = Nose Up) (-1 = Nose down)
        # Forth Element - Yaw (Like a pole through roof) (1 = full right) (-1 = full left)
        # Fifth Element - Roll (1 = roll right) (-1 = roll left)
        # Sixth Element - Jump
        # Seventh Element - Boost
        # Eigth Element - Handbrake