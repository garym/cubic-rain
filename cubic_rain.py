from microbit import *
import neopixel
import random

SIZE = 5


class Settings:
    size = SIZE
    timestep = 5
    max_raindrops = 10
    max_brightness = 32

    # 'Probabilities' to be interpreted as 1 in <value>
    blank_probability = 10
    raindrop_probability = 10

    colors = [
        (0, 0, 255),
        (63, 63, 127),
        (91, 31, 127),
        (31, 91, 127),
        (0, 127, 127),
        (0, 63, 190),
        (31, 31, 190),
    ]
    black = (0, 0, 0)

    plane_size = SIZE * SIZE
    total_pixels = SIZE ** 3


NP = neopixel.NeoPixel(pin0, Settings.total_pixels)
NP.show()


def xyz_to_position(x, y, z):
    size = Settings.size
    if x >= size or y >= size or z >= size or x < 0 or y < 0 or z < 0:
        raise IndexError

    plane_size = Settings.plane_size
    offset = 0

    if z % 2:
        mod_y = y if size % 2 else size - y - 1
        if x % 2:
            offset = size * (size - 1 - x) + mod_y
        else:
            offset = size * (size - x) - 1 - mod_y
    else:
        mod_x = size - 1 - x if y % 2 else x
        offset = y * size + mod_x

    return plane_size * z + offset


def scale_brightness(color):
    return tuple((comp * Settings.max_brightness) // 255 for comp in color)


def set_point(x, y, z, color):
    p = xyz_to_position(x, y, z)
    NP[p] = scale_brightness(color)


def coord_generator():
    max_index = Settings.size - 1
    while True:
        yield (
            random.randint(0, max_index),
            random.randint(0, max_index),
        )


def color_selector():
    colors = Settings.colors

    while True:
        choice = random.randint(0, len(colors) - 1)
        yield (colors[choice], choice)


def raindrop(x, y, color):
    size = Settings.size
    for i in range(size, 0, -1):
        if i < size:
            set_point(x, y, i, Settings.black)

        h = i - 1
        for j in range(i * i):
            set_point(x, y, h, color)
            yield i


def main():
    NP.clear()
    display.clear()

    coords = coord_generator()
    colorsel = color_selector()

    x, y = next(coords)
    rain, colorchoice = next(colorsel)
    raindrops = [raindrop(x, y, rain)]
    display.set_pixel(x, y, min(9, colorchoice + 1))

    while True:
        if random.randint(0, Settings.blank_probability) == 0:
            x, y = next(coords)
            set_point(x, y, 0, Settings.black)
            display.set_pixel(x, y, 0)

        if (
            len(raindrops) < Settings.max_raindrops
            and random.randint(0, Settings.raindrop_probability) == 0
        ):
            x, y = next(coords)
            rain, colorchoice = next(colorsel)
            raindrops.append(raindrop(x, y, rain))
            display.set_pixel(x, y, min(9, colorchoice + 1))

        for raingen in raindrops:
            try:
                next(raingen)
            except StopIteration:
                raindrops.remove(raingen)
        NP.show()
        sleep(Settings.timestep)


main()
