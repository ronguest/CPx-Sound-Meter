# The code below was originally provided by Adafruit in this project:
# https://learn.adafruit.com/3d-printed-led-microphone-flag/circuitpython-code
# and subsequently adapted by Dan Halbert, kattni, Tony DiCola and possibly others.
#
# Written by Adafruit Industries.  Distributed under the BSD license.
# This paragraph must be included in any redistribution.

import audiobusio
import board
import math
import neopixel
import time

# code to check memory usage example: https://learn.adafruit.com/adafruit-gemma-m0/handy-tips

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1, auto_write=False)
pixels.fill((0, 0, 0))
pixels.show()

mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, frequency=16000)
time.sleep(0.11)
volume_sample = bytearray(320)
mic.record(volume_sample, len(volume_sample))
print(volume_sample)
input_floor = max(volume_sample) - min(volume_sample) +1
print("Input floor: ", input_floor)

peak = 0

def pin(value, floor=None, ceiling=None):
    assert floor is not None or ceiling is not None
    assert floor is None or ceiling is None or ceiling > floor
    if floor is not None and floor > value:
        return floor
    if ceiling is not None and ceiling < value:
        return ceiling
    return value

def fscale(original_min, original_max, new_begin, new_end, input_value, curve):
    if original_min > original_max:
        return 0
    curve = pin(curve, floor=-10, ceiling=10)
    curve = math.pow(10, curve*-0.1)
    input_value = pin(input_value, floor=original_min, ceiling=original_max)
    normalized_cur_val = (input_value - original_min) / (original_max - original_min)
    return new_begin + math.pow(normalized_cur_val, curve) * (new_end - new_begin)


volume_color = (200, 100, 0)
peak_color = (100, 0, 255)

while True:
    # Sample audio for a bit.
    mic.record(volume_sample, len(volume_sample))
    #print(volume_sample)
    magnitude = max(volume_sample) - min(volume_sample)
    print(magnitude)
    c = fscale(input_floor, 120, 0, 10, magnitude, 2)
    # Light up pixels that are below the scaled and interpolated magnitude.
    pixels.fill((0, 0, 0))
    for i in range(10):
        if i < c:
            pixels[i] = volume_color
    # Light up the peak pixel and animate it slowly dropping.
    if c >= peak:
        peak = min(c, 9)
    elif peak > 0:
        peak = peak - 1
    if peak > 0:
        pixels[int(peak)] = peak_color
    pixels.show()
