import math

def get_ticks(max: int, min: int):
    diff = max - min
    exponent = math.floor(math.log10(diff))
    interval = 10 ** exponent
    ticks = [min] + [i * interval for i in range(-10, 10) if i * interval > min and i * interval < max] + [max]
    return ticks