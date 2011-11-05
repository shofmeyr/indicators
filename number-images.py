#!/usr/bin/python -u

import Image, ImageDraw

def draw_number(fname, text):
    im = Image.open(fname + ".png")
    draw = ImageDraw.Draw(im)
    draw.text([5, 5], text)
    im.save(fname + "-" + text + ".png")

max_range = 21

for i in range(1, max_range + 1):
    text = "%d" % i
    if i == max_range: text = "%d+" % (i - 1) 
    draw_number("indicator-messages-new", text)
    draw_number("new-messages-red", text)



