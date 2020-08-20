########################################################################
#   Author: Nolan Y. / bbomb64 / Christopher D.                        #
#   Description: Player class/functions                                #
########################################################################

from level import *
from cmap import *
from raylibpy import *

WIDTH = 256
HEIGHT = 192

wrap_around = True

# Define some in game constants (used for the Physics "engine")
FRICTION = 0.2
GRAVITY = 0.149

# Create player sound effects
#jump = makeSound("Sounds/jump.wav")

class Player(object):
    def __init__(self, playerSprites = None, controls = [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE, KEY_RIGHT_SHIFT]\
                 , player_number = 0, x = 50, y = 100, width = 10, height = 20, draw_width = -4, draw_height = -13):
        # Keep track of the player number
        self.player_number = player_number

        # Used to determine what sprites to load for the player
        self.playerSprite = None
        self.playerSprites = playerSprites
        self.spriteSheet = None

        # Player Positioning variables
        self.temp_position = Vector2(10,0)
        self.position = Vector2(10, 0)
        self.velocity = Vector2(0, 0)
        self.gravity = Vector2(0, GRAVITY)

        # Number is from height/width of the player sprite in pixles
        self.width = width
        self.height = height

        # Number is how far from (x,y) coordinates to draw sprite because dumb
        self.draw_width = draw_width
        self.draw_height = draw_height

        # Define player texture bounding box
        self.frame_rec = None

        # Define some physics related variables
        self.weight = 0.2
        self.SPEED_CAP = 2
        self.MAX_SPEED_CAP = 8
        self.VSPEED_CAP = 7.5
        self.DSPEED_CAP = -7.5
        self.ACCELERATION = 0.05
        self.FRICTION = 0.2

        # Define player controls
        self.controls = controls
        self.up = controls[0]
        self.down = controls[1]
        self.left = controls[2]
        self.right = controls[3]
        self.jump = controls[4]
        self.sprint = controls[5]

        # Define misc. Player variables
        self.last_held_direction = "right"
        self.idle = False
        self.skidding = False
        self.initalized = False
        self.jumping = False

        # Powerup state for the player
        self.powerupState = 0
        self.released_up = True
        self.sprinting = False

    def approach(self, current, goal, dt):
        # Why are we subtracting the position from the velocity and comparing that to dt? And why does that result in
        # the new velocity?
        difference = goal - current

        if (self.skidding):
            if (difference > dt):
                return current + dt * 2
            elif (difference < -dt):
                return current - dt * 2
        else:
            # Unless friction automatically sets the velocity to 0, this will cause the velocity to go way above the
            # cap.
            if (difference > dt):
                return current + dt
            elif (difference < -dt):
                return current - dt
        return goal

    def calculatePosition(self, dt, cmap):
        tempX, tempY = self.position
        # Make it so the player wraps around on the left and right (if enabled)
        if (wrap_around):
            x, y = self.position
            if ((x >= WIDTH) and (tempX >= 0)):
                self.x = 1
            elif ((x <= 0) and (tempX <= 0)):
                self.x = WIDTH
        
        # Calculate x & y velocity using fancy Vector math
        tempPX, tempPY = self.position
        tempVX, tempVY = self.velocity
        # I don't know why dt exists, it doesn't seem to be implemented correctly. I have to set the value dt is being
        # multiplied by to a value above or equal to the width of the stage divided by 10 to prevent dumbness.
        x = self.approach(tempPX, tempVX, dt * 1000)
        y = self.approach(tempPY, tempVY, dt * 1000)
        self.velocity = (x, y)

        # Update the player's position and velocity
        pX, pY = self.position
        vX, vY = self.velocity
        gX, gY = self.gravity

        # Cap the player's speed
        if vX >= (self.SPEED_CAP):
            vX = self.SPEED_CAP
        elif vX <= (-self.SPEED_CAP):
            vX = -self.SPEED_CAP

        if vY >= (self.VSPEED_CAP):
            vY = self.VSPEED_CAP
        elif vY <= (-self.VSPEED_CAP):
            vY = -self.VSPEED_CAP

        # Add the player's X/Y position, and the appropriate velocity
        pX += vX
        pY += vY

        # If the player is not on the ground, account for gravity too
        if (self.check_jump(cmap) == False):
            vX += gX
            vY += gY

            if vX >= (self.SPEED_CAP):
                vX = self.SPEED_CAP
            elif vX <= (-self.SPEED_CAP):
                vX = -self.SPEED_CAP

            if vY >= (self.VSPEED_CAP):
                vY = self.VSPEED_CAP
            elif vY <= (-self.VSPEED_CAP):
                vY = -self.VSPEED_CAP
        self.position = (pX, pY)
        self.velocity = (vX, vY)

    # Calculate the players vertical velocity
    def VerticalVelocity(self):
        pass
    
    # Used to determine what sprite to use for each animation
    # (Not all spritesheets will be layed out the same!)
    def animationController(self, action, last_held_direction, frame = 0, superFrame = 0):
        # Animations for powerup state 0
        if (self.powerupState == 0):
            if (action == "idle"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(0, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(0)

            elif (action == "jump"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(4, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(4)
            
            elif (action == "fall"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(5, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(5)

            elif (action == "walk"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(0 + frame, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(0 + frame)

            elif (action == "run"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(2 + frame, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(2 + frame)

            elif (action == "skidding"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(7, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(7)
            
            elif (action == "duck"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(8, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(8)

            elif (action == "looking_up"):
                if (last_held_direction == "right"):
                    self.spriteSheetHandler(9, 0, True)
                elif (last_held_direction == "left"):
                    self.spriteSheetHandler(9)

        elif (self.powerupState  == 1):
            if (action == "idle"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 17)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 0)
                    pass
            
            elif (action == "jump"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 11)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 6)
                    pass
            
            elif (action == "fall"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 10)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 7)
                    pass

            elif (action == "walk"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 17 - superFrame)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 0 + superFrame)
                    pass
            
            elif (action == "run"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 14 - superFrame)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 3 + superFrame)
                    pass
            
            elif (action == "skidding"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 18)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 19)
                    pass
            
            elif (action == "duck"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 21)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 20)
                    pass

            elif (action == "looking_up"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 22)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 23)
                    pass
        
        elif (self.powerupState  == 2):
            if (action == "idle"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 17)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 0)
                    pass
            
            elif (action == "jump"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 11)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 6)
                    pass
            
            elif (action == "fall"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 10)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 7)
                    pass

            elif (action == "walk"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 17 - superFrame)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 0 + superFrame)
                    pass
            
            elif (action == "run"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 14 - superFrame)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 3 + superFrame)
                    pass
            
            elif (action == "skidding"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 18)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 19)
                    pass
            
            elif (action == "duck"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 21)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 20)
                    pass

            elif (action == "looking_up"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 23)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 22)
                    pass
            
            elif (action == "fire"):
                if (last_held_direction == "right"):
                    #changeSpriteImage(self.playerSprite, 25)
                    pass
                elif (last_held_direction == "left"):
                    #changeSpriteImage(self.playerSprite, 24)
                    pass
        
    def spriteSheetHandler(self, x_offset = 0, y_offset = 0, flipX = False, flipY = False):
        playerSprite = load_image(self.spriteSheet)

        if flipX == True:
            image_flip_horizontal(playerSprite)
            x_offset = (9 - x_offset)
        
        if flipY == True:
            image_flip_vertical(playerSprite)

        xPos = x_offset * self.playerSprite.width/10
        yPos = y_offset * self.playerSprite.height/10

        self.playerSprite = load_texture_from_image(playerSprite)

        self.frame_rec = Rectangle(xPos, yPos, self.playerSprite.width/10, self.playerSprite.height)

    def spriteChanger(self, newSprite):
        if (self.playerSprite != None):
            unload_texture(self.playerSprite)
        self.playerSprite = load_texture(newSprite)
    
    def powerupHandler(self, powerupID):
        # 0 - Small
        # 1 - Super
        # 2 - Fire Flower
        # 3 - Blue Shell
        # 4 - Mini Mushroom
        # 5 - Mega Mushroom
        # 6 - Hammer Suit
        # 7 - Frog Suit
        # 8 - Raccoon Leaf
        # 9 - Cape Feather
        # 10 - Propeller Suit
        # 11 - Mari0 (Portal Gun + Mario)

        # Change the player's powerup state to the correct powerup ID
        self.powerupState = powerupID

        # Load the correct spritesheet depending on the powerup
        if (powerupID == 0):
            self.powerupState = 0

            if (self.player_number == 0):
                self.draw_height  = -22
                self.height = 15
            elif (self.player_number == 1):
                self.draw_height  = -22
                self.height = 15
            
            spriteSheet = self.playerSprites + "small.png"
            self.spriteChanger(spriteSheet)
            self.spriteSheet = spriteSheet
            return spriteSheet

        elif (powerupID == 1):
            self.powerupState = 1

            if (self.player_number == 0):
                self.draw_height  = -30
                self.height = 27
            elif (self.player_number == 1):
                self.draw_height  = -30
                self.height = 20

            spriteSheet = self.playerSprites + "super.png"
            self.spriteChanger(spriteSheet)
            return spriteSheet

        elif (powerupID == 2):
            self.powerupState = 2

            if (self.player_number == 0):
                self.draw_height  = -30
                self.height = 27
            elif (self.player_number == 1):
                self.draw_height  = -30
                self.height = 20

            spriteSheet = self.playerSprites + "fire.png"
            self.spriteChanger(spriteSheet)
            return spriteSheet
    
    # If the player gets hurt, make them shrink one powerup, otherwise kill the player
    def hurt(self):
        if (self.powerupState > 1):
            self.draw_height = -18
            self.height = 20
            self.powerupState = 1
            self.powerupHandler(1)

        elif (self.powerupState == 1):
            self.powerupState = 0
            self.draw_height  = -13
            self.height = 26
            self.powerupHandler(0)

        elif (self.powerupState == 0):
            self.respawn()

    # "Kill" the player when their y value >= 4000
    def death(self):
        x, y = self.position
        if y >= HEIGHT:
            self.respawn()
        

    # Really basic respawn function (set the players x & y pos. to 100)
    def respawn(self):
        self.position = [100, 100]
        self.velocity = [0, 0]

    # Check to see if the player can jump
    def check_jump(self,cmap):
        if cmap.on_tile(self.position[0], self.position[1], self.width, self.height) != False:
            return True
        return False

    # Check to see if the player should have gravity applied
    def check_fall(self,cmap):
        if cmap.on_tile(self.position, self.width,self.height) != False:
            return cmap.on_tile(self.position, self.width, self.height)
        return False

    # Check if a player touches part of a tile
    def check_collision(self, cmap):
        # Define temporary variables to make things look neat
        pX, pY = self.position
        vX, vY = self.velocity
        if pY >= HEIGHT:
            return pX, pY, vX, vY, False
        return cmap.in_tile(pX, pY, vX, vY, self.width, self.height)

    # Allow the user to control the player
    def RefineInput(self, cmap, playerSprite, last_held_direction, frame, superFrame, level):
        # Moved all "x, y = self.velocity" to here because we only need it once
        x = self.velocity[0]
        y = self.velocity[1]

        # Update the player's sprite when idling
        if (self.check_jump(cmap) == True):
            if (self.idle == False):
                self.animationController("idle", last_held_direction, frame, superFrame)

        # Set the last held direction to right, and update the player's walk animation if they're on the ground

        #---DEBUG---#
        if is_key_down(KEY_Z):
            print(y)
        #-----------#

        if is_key_down(self.up):
            if (self.check_jump(cmap) == True):
                self.animationController("looking_up", last_held_direction, frame, superFrame)

        if is_key_down(self.right):
            self.last_held_direction = "right"

            # Check to see if the player is on the ground before walking
            if (self.check_jump(cmap) == True):
                # Check to see if ducking
                if is_key_down(self.down):
                    self.animationController("duck", last_held_direction, frame, superFrame)
                    # Add friction to the player
                    self.velocity = (self.Friction(x),y)

                else:
                    # Update the player's velocity
                    if (x <= 2):
                        self.animationController("walk", last_held_direction, frame, superFrame)
                    # Update the player's sprite when running
                    else:
                        self.animationController("run", last_held_direction, frame, superFrame)
                    self.velocity = (x+self.ACCELERATION, y)
            else:
                self.velocity = (x+self.ACCELERATION, y)

            # Change Sprite to ducking sprite if down is held
            if is_key_down(self.down):
                self.animationController("duck", last_held_direction, frame, superFrame)

        # Set the last held direction to left, and update the player's walk animation if they're on the ground           
        elif is_key_down(self.left):
            self.last_held_direction = "left"

            # Check to see if the player is on the ground before applying the sprite change
            if (self.check_jump(cmap) == True):
                # Check to see if ducking
                if is_key_down(self.down):
                    self.animationController("duck", last_held_direction, frame, superFrame)
                    # Add friction to the player
                    self.velocity = (self.Friction(x),y)

                else:
                    # Update the player's sprite when walking
                    if (x >= -2):
                        self.animationController("walk", last_held_direction, frame, superFrame)
                    # Update the player's sprite when running
                    else:
                        self.animationController("run", last_held_direction, frame, superFrame)
                    # Add acceleration to the velocity
                    self.velocity = (x-self.ACCELERATION, y)
            else:
                # Add acceleration to the velocity
                self.velocity = (x-self.ACCELERATION, y)
            # Change Sprite to ducking sprite if down is held
            if is_key_down(self.down):
                self.animationController("duck", last_held_direction, frame, superFrame)

        elif is_key_down(self.down):
            # If the player is on the ground, make them duck
            if self.check_jump(cmap) == True:
                self.animationController("duck", last_held_direction, frame, superFrame)
            # Apply friction to the player
            self.velocity = (self.Friction(x),y)
        # Apply friction to the player if they are not holding a button or ducking
        # (slow them to a hault)
        else:
            self.velocity = (self.Friction(x),y)

        # Check to see if the player can jump
        if is_key_down(self.jump):
            if self.check_jump(cmap) == True and self.released_up == True:
                # Update the player's sprite, then apply vertical velocity
                self.animationController("jump", last_held_direction, frame, superFrame)

                self.velocity = (x, self.DSPEED_CAP)

                #playSound(jump)
                self.released_up = False
                if is_key_down(self.down):
                    self.animationController("duck", last_held_direction, frame, superFrame)

            else:
                # Update the player's sprite if the peak of the jump has been passed, then apply gravity
                if (y > 0):
                    self.animationController("fall", last_held_direction, frame, superFrame)
                if is_key_down(self.down):
                    self.animationController("duck", last_held_direction, frame, superFrame)

        # Apply gravity to the player
        elif (self.check_jump(cmap) == False):
            # Update the player's sprite if the peak of the jump has been passed, then apply gravity
            if (y > 0):
                self.animationController("fall", last_held_direction, frame, superFrame)
            self.released_up = True
            if is_key_down(self.down):
                self.animationController("duck", last_held_direction, frame, superFrame)

        else:
            if is_key_down(self.down):
                self.animationController("down", last_held_direction, frame, superFrame)
            self.released_up = True

        if is_key_down(self.sprint):
            # If the player is powerups 2 (Fire), shoot a fireball
            if (self.powerupState == 2):
                self.animationController("fire", last_held_direction, frame, superFrame)

            self.SPEED_CAP = 4
            self.ACCELERATION = 0.17

        else:
            self.SPEED_CAP = 2
            self.ACCELERATION = .17

    # Make the player have friction against the ground
    def Friction(self,x):
        if ((x <= self.MAX_SPEED_CAP) and (x > 0)):
            x -= FRICTION
            if x < 0:
                x = 0.0
        elif ((x >= -self.MAX_SPEED_CAP) and (x < 0)):
            x += FRICTION
            if x > 0:
                x = 0.0
        return x

    # Print stats of the player when called
    def __str__(self):
        return "Player X Velocity: {}\nPlayer Y Velocity: {}\nPlayer X: {}\nPlayer Y: {}"\
            .format(self.velocity[0], self.velocity[1], self.position[0], self.position[1])


