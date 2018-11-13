# -*- coding: utf-8 -*-


from fontTools.ttLib import TTFont     # 导包

font = TTFont('base_font.woff')   # 打开文件
gly_list = font.getGlyphOrder()     # 获取 GlyphOrder 字段的值
for gly in gly_list:    # 前两个值不是我们要的，切片去掉
    print(gly)

font.saveXML('./1.xml')

