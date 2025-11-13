import time
from arduino_alvik import ArduinoAlvik
# We also import the NanoLED for our "hungry" warning light
from nhs_robotics import NanoLED

# ---=======================================================---
# --- PART 1: YOUR "PET" CLASS (THE BLUEPRINT) ---
# --- This is the part you will build! ---
# ---=======================================================---

class Pet:
    """
    Manages the data (state) and actions (behavior) for our virtual pet.
    """
    
    def __init__(self):
        # --- WORK: ---
        # Set up the starting attributes for hunger and happiness.
        self.hunger = 50
        self.happiness = 50
        self.max_happiness = 100
        
    def feed(self):
        # --- WORK: ---
        # This method is called when the pet is fed.
        # It should DECREASE self.hunger by 10.
        self.hunger -= 10
        
        # Add a check: self.hunger should not go below 0!
        if self.hunger < 0:
            self.hunger = 0

    def play(self):
        # --- WORK: ---
        # This method is called when you play with the pet.
        # It should INCREASE self.happiness by 10.
        self.happiness += 10
        
        # Add a check: self.happiness should not go above self.max_happiness!
        if self.happiness > self.max_happiness:
            self.happiness = self.max_happiness

    def update(self):
        # --- WORK: ---
        # This is the "life tick" called once per second.
        # This has been sped up to make the game more playable!
        self.hunger += 10
        self.happiness -= 10
        
        # Add bounds checking to make sure stats don't go
        # to invalid numbers.
        if self.hunger > 100:
            self.hunger = 100
        
        if self.happiness < 0:
            self.happiness = 0

    def get_status(self):
        # --- WORK: ---
        # This is the pet's "brain."
        # Check the attributes and return a "mood" as a string.
        # This controls the LED colors in the main loop.
        
        # Priority is important:
        # 1. Is it hungry? A hungry pet can't be happy.
        # 2. Is it happy?
        # 3. Is it sad?
        # 4. Otherwise, it's content.
        
        if self.hunger > 75:
            return "HUNGRY"
        elif self.happiness > 75:
            return "HAPPY"
        elif self.happiness < 40:
            return "SAD"
        else:
            return "CONTENT"

# ---=======================================================---
# --- PART 2: THE MAIN GAME LOOP (This part is done for you!) ---
# --- Read through it to see how your class is used. ---
# ---=======================================================---

try:
    # --- Setup ---
    alvik = ArduinoAlvik()
    alvik.begin()
    nano_led = NanoLED()
    nano_led.set_brightness(50) # Dim the NanoLED a bit

    # This is where we "build" our pet from the "blueprint"
    my_pet = Pet() 

    print("Alvi-Pet is alive! Press 'X' to exit.")
    print("Feed me (UP) and play with me (DOWN)!")

    # --- Main Game Loop ---
    while not alvik.get_touch_cancel():
        
        # --- 1. SENSE (Your Choice!) ---
        # Decide how you want to feed and play with your pet.
        # We've uncommented the simple button choices for this solution.
        
        # --- How do you FEED your pet? ---
        # Choice A: Press the UP button
        is_being_fed = alvik.get_touch_up()
        
        # Choice B: "Show" food (hand < 5cm from center sensor)
        # is_being_fed = (alvik.get_distance()[2] < 50) 
        
        
        # --- How do you PLAY with your pet? ---
        # Choice A: Press the DOWN button
        is_being_played_with = alvik.get_touch_down()
        
        # Choice B: "Pick up" the pet (detect motion)
        # x, y, z = alvik.get_accelerations()
        # total_motion = abs(x) + abs(y) + abs(z)
        # is_being_played_with = (total_motion > 2.0)
        
        
        # --- 2. THINK / ACT ---
        # We call the methods on our "my_pet" object
        if is_being_fed:
            my_pet.feed()
            print(f"YUM! Happiness: {my_pet.happiness}, Hunger: {my_pet.hunger}")

        if is_being_played_with:
            my_pet.play()
            print(f"WEE! Happiness: {my_pet.happiness}, Hunger: {my_pet.hunger}")
        
        # --- 3. UPDATE ---
        # The pet's "life" ticks forward once per loop
        my_pet.update()
        
        # --- 4. OUTPUT ---
        # Show the pet's mood on the LEDs
        mood = my_pet.get_status() # Get status from the class
        
        if mood == "HAPPY":
            alvik.set_leds_color(0, 1, 0) # Green
            nano_led.off()
        elif mood == "CONTENT":
            alvik.set_leds_color(0, 0, 1) # Blue
            nano_led.off()
        elif mood == "SAD":
            alvik.set_leds_color(1, 0, 1) # Purple
            nano_led.off()
        elif mood == "HUNGRY":
            alvik.set_leds_color(1, 1, 0) # Yellow
            nano_led.off()
        
        # Special "Hungry" warning overrides the NanoLED
        if my_pet.hunger > 75:
            # We check this *after* setting moods, so this
            # warning can appear at the same time as "SAD" or "CONTENT"
            nano_led.set_color(1, 0, 0) # Red
            
        # --- 5. SLOW DOWN ---
        # This is the most important part!
        # We only run the loop ONCE per second.
        # This makes it a "turn-based" game and avoids
        # the button flicker bug completely!
        time.sleep(1.0) 

finally:
    # --- Cleanup ---
    alvik.stop()
    nano_led.off()
    print("Alvi-Pet has gone to sleep.")