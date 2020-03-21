from pynput import keyboard

class Input:
    def add_key_listener(self, key, action):
        def handle_keypress(keypress):
            pressed_key = getattr(keypress, 'char', keypress)

            if(pressed_key == key):
                action()

        listener = keyboard.Listener(
            on_press = handle_keypress)
        listener.start()

