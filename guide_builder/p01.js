const {build, SAVE, PARTA, GRADING} = require('./build');

build("P01_Gamepad_Lights_Guide.docx", "V01", [
["title", "Project 01: Gamepad Lights"],
["lead", "In this project you build a robot whose headlights change color when you press buttons on a PS5 controller."],
["note", SAVE("01", "p01_gamepad_lights.py")],

["h1", "Part 1: How It Works"],
["p", "Read this part when you get stuck. It has the answer to almost every question you will have."],

["h2", "1. The Main Loop"],
["p", "Real robots do not run once and stop. They loop. They check their sensors over and over, hundreds of times a second."],
["p", "Your code has a loop like this:"],
["code", "while not (alvik.get_touch_cancel() or gamepad.buttons['options']):"],
["p", "Everything indented under that line runs again and again."],
["p", "That line is also your stop button. Touch Cancel (X) on the robot, or press Options on the gamepad, and the loop ends on its own. You do not need Thonny's Stop button."],

["h2", "2. Ask the Gamepad for Fresh Data"],
["p", "The first line inside the loop is this:"],
["code", "gamepad.update()"],
["p", "Think of it like checking your phone. If you never refresh, you never see the new text. `gamepad.update()` asks the controller which buttons are down right now. Leave it out and your robot is flying blind."],

["h2", "3. Making Choices"],
["p", "Now the robot has the button data. It has to decide what to do. You write rules."],
["b", ["`if` is the first rule. Python checks it first.",
       "`elif` is the next rule. Python only checks it if the rule above was false.",
       "`else` is the catch-all. It runs when nothing else matched."]],
["p", "Checking a button looks like this:"],
["code", "if gamepad.buttons['cross']:\n    # do something while X is held"],
["p", "Only ONE branch runs each time through the loop. That is the point of a chain. If you used three separate `if` statements instead, two of them could run at once and the lights would fight each other."],

["h2", "4. Mixing Colors"],
["p", "Your robot has two headlights: `alvik.left_led` and `alvik.right_led`."],
["p", "Each one mixes red, green, and blue. You pass a 1 to turn a color on and a 0 to turn it off. These examples all use the left LED. The right one works exactly the same way."],
["code", "alvik.left_led.set_color(1, 0, 0)   # red\nalvik.left_led.set_color(0, 1, 0)   # green\nalvik.left_led.set_color(0, 0, 1)   # blue\nalvik.left_led.set_color(1, 1, 1)   # white, all three at once\nalvik.left_led.set_color(0, 0, 0)   # off"],
["p", "Two colors at once make a new one. Red plus blue is magenta. Green plus blue is cyan. You will want those for the flex."],

["h2", "5. The finally Block"],
["p", "At the bottom of your file is a `finally:` block."],
["p", "Code inside `finally` always runs. It runs when the program ends normally. It runs when you hit Stop. It runs even if your code crashes."],
["p", "That matters. Without it the robot freezes in whatever state it was in. Lights stuck on. In later projects, with motors, wheels stuck spinning."],
["p", "So every program in this class cleans up in `finally`."],
["p", "One line is already written for you: `alvik.stop()`. Always call it, in every project. It shuts down the robot software and frees the WiFi network. Skip it and the robot can hang, and then you have to restart it to get going again."],

["h1", "Part 2: Do the Work"],

["h2", "Step 1: Set Up"],
["n", ["Turn on your Alvik robot.",
       "Open `p01_gamepad_lights.py` in Thonny and save your own copy to the robot, as described at the top of this guide.",
       "Run the program. Thonny prints your robot's WiFi name in the Shell.",
       "Connect your Mac to that WiFi network. The password is `password`.",
       "Open `http://192.168.4.1` in Chrome. Keep that Chrome window in front for the whole project. Chrome blocks gamepad input to any window that is not focused, so clicking over to Thonny makes your buttons stop working.",
       "Pair your PS5 controller to the Mac over Bluetooth. The robot's LEDs turn green when it connects."]],

["h2", "Step 2: Write Your Code"],
["p", "Look for the `# WORK` comments in your Python file. Do them in order."],
["p", "WORK 1 has two halves, and they sit at the top and bottom of the same chain."],
["b", ["In the `if gamepad.buttons['cross']:` block, turn both LEDs blue.",
       "In the `else:` block at the bottom, turn both LEDs white."]],
["p", "White means \"running, waiting for a button.\" Now you can tell the difference between a robot that is waiting and a robot that is frozen. Get this working before you start WORK 2."],
["p", "WORK 2 adds two `elif` branches, between the `if` and the `else`."],
["b", ["Hold CIRCLE, both LEDs turn red.",
       "Hold TRIANGLE, both LEDs turn green."]],
["p", "WORK 3 fills in the `finally:` block. Three things, in this order."],
["b", ["Turn both LEDs red.",
       "Sleep for half a second.",
       "Turn both LEDs off."]],
["p", "Your code goes above the `alvik.stop()` line that is already there. Leave that line alone."],
["p", "The red flash proves the shutdown ran. A silent stop looks exactly like a crash, and you want to be able to tell them apart."],

["h2", "Step 3: Worksheet and Check Off"],
["p", "When you run the finished file, all of this happens in one go. Hold X for blue, CIRCLE for red, TRIANGLE for green, let go for white, then stop and watch the red flash."],
["p", PARTA],
["p", GRADING],

["h2", "FLEX: The A+"],
["p", "Make the SQUARE button run a light show. Add it as one more `elif`."],
["p", "You could set the left LED to magenta and the right one to cyan. Or use `time.sleep_ms()` to flip between two colors while you hold the button. Your call."],
]);
