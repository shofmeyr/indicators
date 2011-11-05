#!/usr/bin/python -u

import Image, ImageDraw, sys

def draw_number(fname, text):
    im = Image.open(fname + ".png")
    draw = ImageDraw.Draw(im)
    draw.text([5, 5], text)
    im.save(fname + "-" + text + ".png")

def number_messages():
    max_range = 21
    for i in range(1, max_range + 1):
        text = "%d" % i
        if i == max_range: text = "%d+" % (i - 1) 
        draw_number("indicator-messages-new", text)
        draw_number("new-messages-red", text)

def color_thermometer():
    for i in range(1, 6):
        if i == 1: color = "darkblue"
        elif i == 2: color = "blue"
        elif i == 3: color = "yellow"
        elif i == 4: color = "orange"
        else: color = "red"
        im = Image.open("temperature-%d-icon.png" % i)
        im_copy = im.copy()
        draw = ImageDraw.Draw(im)
        draw.rectangle([0, 0, 24, 24], outline=color, fill=color)
        im_blend = Image.blend(im, im_copy, 0.5)
        im_blend.save("temp-%d.png" % i)

def write_temp():
    for i in range(0, 1):
        im = Image.new("RGBA", (24, 24))
        draw = ImageDraw.Draw(im)
#        text = "%d %c" % (i, u"\u2103")
        draw.text([2, 5], "%dC" % 100)
        im.save("temp-num-%d.png" % i)



if __name__ == "__main__":
#    number_messages()
#    color_thermometer()
    write_temp()
