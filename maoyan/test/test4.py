# -*- coding: utf-8 -*-


from PIL import Image

img = Image.open('./3.png')
rangle = (791, 497, 882, 536)

png = img.crop(rangle)

png.save('4.png')
