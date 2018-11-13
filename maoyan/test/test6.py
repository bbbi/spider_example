# -*- coding: utf-8 -*-
from fontTools.ttLib import TTFont

baseFont = TTFont('base_font.woff')
testFont = TTFont('47b01555f36a1243ea7aecbbb28dd81e2076.woff')
uniList = testFont['cmap'].tables[0].ttFont.getGlyphOrder()
numList = []
baseNumList = ['.', '6', '5', '3', '7', '1', '4', '2', '8', '9', '0', ]
baseUniCode = ["x", "unif097", "unif3e3", "unif74c", "unif315", "unif523", "unieaa7", "unie62a", "unif39d", "uniec75",
               "unie40e", ]

for i in range(1, 12):
    maoyanGlyph = testFont['glyphs'][uniList[i]]
    for j in range(11):
        baseGlyph = baseFont['glyphs'][baseUniCode[j]]
        if maoyanGlyph == baseGlyph:
            numList.append(baseNumList[j])
            break

print(numList)