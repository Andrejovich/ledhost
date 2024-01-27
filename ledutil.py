#!/usr/bin/python
import ledconfig

# Posible reactions to when a `:led &stack ...` or `:led &plan ...` message would
# cause a stack or plan to grow beyond its maximum size..
ON_EXCEED_BYE   = 0xB00F    # Disconnect the 'offending' client.
ON_EXCEED_CLEAR = 0xC00F    # Clear stack or plan before appending frame.
ON_EXCEED_DENY  = 0xD00F    # Don't append the 'offending' frame.

def gradient(from_rgb, to_rgb, steps):
    if steps < 2:
        return [to_rgb]
    delta = tuple( (j-i)/steps for i,j in zip(from_rgb, to_rgb) )
    result = [from_rgb]
    frame = from_rgb
    for i in range(int(steps)):
        frame = tuple( i+d for i,d in zip(frame, delta) )
        result.append( tuple(map(round, frame)) )
    return result

def greenhack(rgb, apply=None):
    apply = ledconfig.GREENHACK if apply is None else apply
    r, g, b = rgb
    if apply:
        if 0 < r < 255: r += 1
        if 0 < g:       g  = round(g/2) + 1
        if 0 < b < 255: b += 1
    return (r, g, b)

def oxford_comma(items, empty='nothing', and_=" and ", sep=", ", penum=","):
    if len(items) == 0:
        return empty
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return and_.join(map(str, items))
    result = [str(i) for i in items]
    return f"{sep.join(result[0:-1])}{penum}{and_}{items[-1]}"
