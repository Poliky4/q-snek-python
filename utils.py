from pynput import keyboard

def add_key_listener(key, action):
    def handle_keypress(keypress):
        pressed_key = getattr(keypress, 'char', keypress)

        if(pressed_key == key):
            action()

    listener = keyboard.Listener(
        on_press = handle_keypress)
    listener.start()

def check_collision2(
    x1=0,
    y1=0,
    x2=0,
    y2=0,
    distance=0
):
    x_distance = abs(x1 - x2)
    y_distance = abs(y1 - y2)

    return x_distance < distance and y_distance < distance

