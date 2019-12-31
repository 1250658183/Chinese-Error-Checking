# -*- coding:utf-8 -*-
#@Time  : 2019/12/31 11:26
#@Author: Cao Yongchang
#@File  : Extract_PDF.py


import glob
import os
import math
eps = 3e-2
# from pdf_extractor import extract_pdf_content

pdf_path = r'C:\Users\12506\Downloads\中文文本纠错\2019最新精选行研报告资料包\2019年1-3月精选深度报告'
pdfs = glob.glob("{}/*.pdf".format(pdf_path))

import re
import sys
import importlib
importlib.reload(sys)

from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import *
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
def contain_zh(seq):        #匹配中文，对没有中文的句子或短语进行跳过
    for ch in seq:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def parse(pdf_path):
    global eps
    # 保存文本内容
    key = pdf_path.split('/')[-1]
    f =  open(key[:-4]+'.txt', 'w', encoding='utf-8')
    fp = open(pdf_path, 'rb')  # 以二进制读模式打开
    # 用文件对象来创建一个pdf文档分析器
    parser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    parser.set_document(doc)
    doc.set_parser(parser)

    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # 用来计数页面，图片，曲线，figure，水平文本框等对象的数量
        num_page, num_image, num_curve, num_figure, num_TextBoxHorizontal = 0, 0, 0, 0, 0

        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages(): # doc.get_pages() 获取page列表
            num_page += 1  # 页面增一
            interpreter.process_page(page)
            f.write('\n\n\n')
            # 接受该页面的LTPage对象
            layout = device.get_result()

            text_dic_list = []       #建立空字典链表，其值为宽度相同的字符串的拼接
            for x in layout:
                if isinstance(x,LTImage):  # 图片对象
                    num_image += 1
                if isinstance(x,LTCurve):  # 曲线对象
                    num_curve += 1
                if isinstance(x,LTFigure):  # figure对象
                    num_figure += 1
                if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                    num_TextBoxHorizontal += 1  # 水平文本框对象增一
                    results = x.get_text()
                    if contain_zh(results):

                        inserted = False
                        for item in text_dic_list:
                            if(abs(item['hide'] - (x.y1-x.y0)) < eps):
                                item['text']+=(results[:-1]+' ')
                                inserted = True
                        if not inserted:
                            text_dic_list.append({'hide':(x.y1-x.y0),'text':results[:-1]+' '})
            for item in text_dic_list:
                f.write(item['text']+'\n')

        print('对象数量：\n','页面数：%s\n'%num_page,'图片数：%s\n'%num_image,'曲线数：%s\n'%num_curve,'水平文本框：%s\n'
              %num_TextBoxHorizontal)
    f.close()


if __name__ == '__main__':
    for pdf_file in pdfs:
        parse(pdf_file)