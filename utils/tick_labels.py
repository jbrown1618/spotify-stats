import math

def get_ticks(max: int, min: int):
    diff = max - min
    exponent = math.floor(math.log10(diff))
    interval = 10 ** exponent
    
    if diff < interval * 3:
        interval = int(interval / 2)

    middle_ticks = [i * interval for i in range(-10, 10) if i * interval > min and i * interval < max]

    return [min] + middle_ticks + [max]