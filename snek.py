from time import sleep
import os

def clear_screen():
  os.system("clear")

width = 20
height = 10

padding_left = 0 # 13

legend = {
  "border": "+",
  "empty": " ",
  "player": "o",
}

def pad(pads, string):
  return str(string).rjust(pads, " ")

def pad_index(i):
  return pad(padding_left, "")
  # return pad(padding_left, i)

def make_solid_line_with_borders(c):
  return list(
    legend["border"] + str(c) * (width) + legend["border"]
  )

def make_horizontal_border():
  return make_solid_line_with_borders(legend["border"])
def print_horizontal_border():
  print(pad(padding_left, "") + "".join(make_horizontal_border()))

def print_empty_lines(count = 1):
  for i in range(count):
    print()

def make_map():
  _map = []
  for y in range(height):
    _map.append(
      make_solid_line_with_borders(legend["empty"])
    )
  return _map

def render_header():
  print_empty_lines()
  # print(" " * 30, "snek")
  print_empty_lines()

def render_game_map(thing):
  print_horizontal_border()
  for i, line in enumerate(thing):
    print(
      pad_index(i),
      "".join(line)
    )
  print_horizontal_border()

def render(thing):
  clear_screen()
  # render_header()
  render_game_map(thing)
  # print_empty_lines(5)

def update():
  game_map = make_map()

  player["x"] += player["vx"]
  player["y"] += player["vy"]
  x = player["x"]
  y = player["y"]
  game_map[y][x] = legend["player"]

  if player["x"] >= width - 1:
    player["vx"] = -1
  elif player["x"] == 0:
    player["vx"] = 1

  if player["y"] >= height - 1:
    player["vy"] = -1
  elif player["y"] == 0:
    player["vy"] = 1

  return game_map

player = {
  "x": round(width / 2),
  "y": round(height / 2),
  "vx": 1,
  "vy": 1,
}
# fps = 1000/60
count = 0
# while(count < 50):
while(True):
  game_state = update()
  render(game_state)

  count += 1
  # print(f"Render count: { count }")
  # print(f"Target FPS: { fps }")

  sleep(0.15)

