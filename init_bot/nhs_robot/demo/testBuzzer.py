#################################
#    Buzzer Class Test Script   #
#################################

# This program tests the simplified Buzzer class
# that you added to the nhs_robotics.py file.

# It will:
# 1. Create a Buzzer object.
# 2. Play a short, high-pitched tone.
# 3. Play a longer, low-pitched tone.
# 4. Play a defined musical note.
# 5. Play pre-programmed sound effects.

from nhs_robotics import Buzzer
from time import sleep_ms

print("Buzzer Test Program")

# 1. Instantiate a control object
# This creates our Buzzer object. If the buzzer is connected
# correctly, you should see "Buzzer attached successfully."
my_buzzer = Buzzer()

try:
    # --- Test 1: Short, high beep ---
    print("\nPlaying a short, high-pitched beep (1000 Hz for 200ms)")
    my_buzzer.set_frequency(1000)
    my_buzzer.set_duration(200)
    my_buzzer.on()
    sleep_ms(1000)

    # --- Test 2: Longer, low beep ---
    print("Playing a longer, low-pitched beep (500 Hz for 500ms)")
    my_buzzer.set_frequency(500)
    my_buzzer.set_duration(500)
    my_buzzer.on()
    sleep_ms(1000)

    # --- Test 3: Playing a defined note ---
    print("Playing a C4 note.")
    my_buzzer.set_frequency(my_buzzer.NOTE_C4)
    my_buzzer.set_duration(300)
    my_buzzer.on()
    sleep_ms(1000)
    
    # --- Test 4: Continuous sound and off() method ---
    print("Playing a continuous sound for 1 second...")
    my_buzzer.set_frequency(800)
    my_buzzer.set_duration(0) # Duration of 0 means it stays on
    my_buzzer.on()
    sleep_ms(1000)
    print("...stopping the continuous sound.")
    my_buzzer.off() # Manually turn it off
    sleep_ms(1000)

    # --- Test 5: Sound Effects ---
    print("\nTesting Sound Effects...")

    print("Playing SIREN effect...")
    my_buzzer.play_effect(my_buzzer.EFFECT_SIREN)
    sleep_ms(2000) # Wait for the effect to finish

    print("Playing YES effect...")
    my_buzzer.play_effect(my_buzzer.EFFECT_YES)
    sleep_ms(2000)

    print("Playing NO effect...")
    my_buzzer.play_effect(my_buzzer.EFFECT_NO)
    sleep_ms(2000)
    
    print("Test complete.")

finally:
    # It's good practice to ensure the buzzer is off when the program ends.
    my_buzzer.off()
    print("Program finished.")
