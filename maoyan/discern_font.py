# -*- coding: utf-8 -*-
import re

from fontTools.ttLib import TTFont

base_font = TTFont('base_font.woff')  # 解析字体库font文件
# 使用 "FontCreator字体查看软件" 查看字体的对应关系，然后设置对应关系
base_num_list = ['.', '6', '5', '3', '7', '1', '4', '2', '8', '9', '0', ]
base_unicode_list = [
    "x",
    "uniF097",
    "uniF3E3",
    "uniF74C",
    "uniF315",
    "uniF523",
    "uniEAA7",
    "uniE62A",
    "uniF39D",
    "uniEC75",
    "uniE40E",

]


def get_num_mapping(font_path):
    regexer = re.compile(r'uni')
    mao_yan_font = TTFont(font_path)
    mao_yan_unicode_list = mao_yan_font['cmap'].tables[0].ttFont.getGlyphOrder()
    mao_yan_num_list = []
    for i in range(1, 12):
        mao_yan_glyph = mao_yan_font['glyf'][mao_yan_unicode_list[i]]
        for j in range(11):
            base_glyph = base_font['glyf'][base_unicode_list[j]]
            if mao_yan_glyph == base_glyph:
                mao_yan_num_list.append(base_num_list[j])
                break

    mao_yan_unicode_list = [regexer.sub('&#x', i).lower() for i in mao_yan_unicode_list[1:]]
    item = dict(map(lambda x, y: [x, y], mao_yan_unicode_list[1:], mao_yan_num_list))

    return item


if __name__ == '__main__':
    a = get_num_mapping("E:\\spider\\A\\maoyan\\fonts\\47b01555f36a1243ea7aecbbb28dd81e2076.woff")
    print(a)