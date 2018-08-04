import math
import time

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

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


def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class RocketBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.DISTANCE_TO_DODGE = 500
        #Contants
        self.DODGE_TIME = 0.25

        #Game Data
        self.bot_pos = None
        self.bot_rot = None

        #Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0

    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                  target_x - self.bot_pos.x)

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -math.pi:   
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi

        if angle_front_to_target < math.radians(-10) and angle_front_to_target > math.radians(-5):
            # If the target is more than 10 degrees right from the center steer left
            self.controller.steer = -1
            self.controller.handbrake = 0

        elif angle_front_to_target < math.radians(-5):
            self.controller.steer = -0.5

        elif angle_front_to_target > math.radians(10) and angle_front_to_target < math.radians(5):  
            # If the target is more than 10 degrees left from the center steer right
            self.controller.steer = 1
            self.controller.handbrake = 0

        elif angle_front_to_target > math.radians(5):
            self.controller.steer = 0.5

        elif angle_front_to_target > math.radians(90):
            self.controller.handbrake = 1

        elif angle_front_to_target < math.radians(89):
            self.controller.handbrake = 0

        elif angle_front_to_target > math.radians(-90):
            self.controller.handbrake = 1

        elif angle_front_to_target < math.radians(-89):
            self.controller.handbrake = 0
            
        else:
            self.controller.steer = 0
            self.controller.handbrake = 0

    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1

            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME  

  

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        ball_pos = packet.game_ball.physics.location

         # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
        # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
        # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
        
        self.controller.throttle = 0.8

        if (self.index == 0 and self.bot_pos.y < ball_pos.y) or (self.index == 1 and self.bot_pos.y > ball_pos.y):
            self.aim(ball_pos.x, ball_pos.y)
            if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
                self.should_dodge = True
        else:
            if self.team == 0:
                # Blue team's goal is located at (0, -5000)
                self.aim(0, -5000)
            else:
            # Orange team's goal is located at (0, 5000)
                self.aim(0, 5000)

        self.aim(ball_pos.x, ball_pos.y)

        self.controller.jump = 0
        self.check_for_dodge()
        

        return self.controller

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)

    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)

    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction


def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)
