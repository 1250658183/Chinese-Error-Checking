# -*- coding:utf-8 -*-
#@Time  : 2019/12/31 11:26
#@Author: Cao Yongchang
#@File  : Extract_PDF.py


import glob
import os
import math
eps = 3e-2
# from pdf_extractor import extract_pdf_content

# pdf_path = r'G:\MyFiles\Courses\Chinese Essay Error Checking\2019年1-3月精选深度报告'
# pdfs = glob.glob("{}/*.pdf".format(pdf_path))

import re
import sys
import importlib
importlib.reload(sys)

from pdfminer.pdfparser import PDFParser,PDFDocument,PDFEncryptionError
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import *           #修改源码（len(boxes)
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
spe_pat = r"(\xe2\x98\x85|\xe2\x97\x86)"
spe_repat = re.compile(spe_pat)


def is_chinese(char):
    if char >= '\u4e00' and char <= '\u9fa5':
        return True
    else:
        return False

def is_alphabet(char):
    if (char >= '\u0041' and char <= '\u005a') or (char >= '\u0061' and char <= '\u007a'):
        return True
    else:
        return False

def is_number(char):
    if char >= '\u0030' and char <= '\u0039':
        return True
    else:
        return False

def is_other(uchar):
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def spe_pun_drop(seq):
    nnseq = seq.replace('\n','')     #去除多余换行符
    nseq = nnseq.replace(' ','')
    ch = nseq[0]
    if is_other(ch) and  ch not in [',','。','，','？','?',';','；','！','!','“','”','\'','\"','(','（']:     #
        return '\n'+nseq[1:]
    return nseq


def contain_zh(seq):        #匹配中文，对没有中文的句子或短语进行跳过
    chF = False
    punF = False
    for ch in seq:
        if u'\u4e00' <= ch <= u'\u9fff':
            chF = True
        elif ch in [',','。','，','？','?',';','！','!','“','”','\'','\"','(','（']:        #,'（','(','）',')' 利用中英文分隔符判断是否为标题等脏数据
            punF = True
    return chF and punF

def match_pattern(seq):
    if contain_zh(seq):
        return True
    return False


def parse(pdf_path):
    global eps
    # 保存文本内容
    key = pdf_path.split('/')[-1]
    print('extracting from ', key)
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
    try:
        doc.initialize()
    except PDFEncryptionError:
        return

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        return
        # raise PDFTextExtractionNotAllowed
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
            pre_sent = {'text':'','height':0,'left':0,'width':0}
            post_sent = {'text':'','height':0,'left':0,'width':0}
            pre_flag = False
            post_flag = False
            try:
                interpreter.process_page(page)
            except KeyError:
                continue
            except AssertionError:
                continue
            except OSError:
                continue
            f = open(key[:-4] + '.txt', 'a', encoding='utf-8')
            f.write('\n\n')
            f.close()
            # 接受该页面的LTPage对象
            layout = device.get_result()

            text_dic_list = []       #建立空字典链表，其值为宽度相同的字符串的拼接
            for x in layout:
                if isinstance(x,LTImage):  # 图片对象
                    num_image += 1
                if isinstance(x,LTCurve):  # 曲线对象
                    num_curve += 1
                if isinstance(x,LTFigure):  # figure对象
                    num_figure += 11
                if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                    num_TextBoxHorizontal += 1  # 水平文本框对象增一
                    # results = x.get_text()
                    results = ""
                    for i in x._objs:
                        for j in i._objs:
                            temch = j._text[0]
                            for w in range(1,len(j._text)):
                                if is_chinese(j._text[w]):
                                    ch = j._text[w]
                                    break
                            results += temch
                    height = x._avg_lineheight
                    for gethei in range(len(x._objs[0]._objs)):
                        if is_chinese(x._objs[0]._objs[gethei]._text[0]):
                            height = x._objs[0]._objs[gethei].height

                    if match_pattern(results):      #检测是否符合启发式规则
                        nresults = spe_pun_drop(results)
                        inserted = False
                        for item in text_dic_list:      #主要清洗方式，为联合在pdf分行的同一个语句，将同一页中所有宽度相同的句子联合，并用空格分隔
                            if(abs(item['hide'] - (height)) < eps) and abs(item['left']-x.x0) < 5*height:
                                if pre_flag and abs(pre_sent['height']-height) < eps and pre_sent['width'] >= x.width-height*5:
                                    nresults = pre_sent['text'] + nresults
                                if (item['y0']-x.y0) > 4*height and nresults[0] != '\n':            #平行段落之间添加换行符
                                    nresults = '\n'+nresults
                                item['text']+=(nresults)
                                if x.x0 > item['left']:
                                    item['left'] = x.x0
                                if x.y0 < item["y0"]:
                                    item["y0"] = x.y0
                                inserted = True
                                break
                        if not inserted:
                            if pre_flag and abs(pre_sent['height'] - height) < eps and pre_sent['width'] >= x.width - height*5:
                                nresults = pre_sent['text'] + nresults
                            text_dic_list.append({'hide':height,'left':x.x0,'width':x.width,'text':nresults,"y0":x.y0})
                        pre_flag = False
                        post_flag = True
                    else:
                        fun_flag = False                #处理pdf文段最后一句话不被添加至句子中
                        if post_flag == True:
                            nresults = spe_pun_drop(results)
                            for item in text_dic_list:
                                if (abs(item['hide'] - (height)) < eps and abs(item['left'] - x.x0) < height*5):
                                    item['text'] += (nresults)
                                    fun_flag = True
                                    break
                            if fun_flag == False:       #处理连续的末尾没有标点
                                post_flag = False
                        if not fun_flag:
                            if pre_flag and abs(pre_sent['height']-height) < eps and abs(pre_sent['left'] - x.x0) < height*5:     #处理有多行之间没有标点等情况
                                pre_sent['text'] += spe_pun_drop(results)
                            else:
                                pre_sent['text'] = spe_pun_drop(results)
                                pre_sent['height'] = height
                                pre_sent['left'] = x.x0
                                pre_sent['width'] = x.width
                            pre_flag = True
            for item in text_dic_list:
                f = open(key[:-4] + '.txt', 'a', encoding='utf-8')
                f.write(item['text']+'\n')
                f.close()

        print('对象数量：\n','页面数：%s\n'%num_page,'图片数：%s\n'%num_image,'曲线数：%s\n'%num_curve,'水平文本框：%s\n'
              %num_TextBoxHorizontal)


def go_through(filepath):
    if os.path.isdir(filepath):
        pdfs = glob.glob("{}/*.pdf".format(filepath))
        for pdf_file in pdfs:
            ansname = pdf_file.split('/')[-1][:-4] + '.txt'
            if not os.path.exists(ansname):
                parse(pdf_file)
        for s in os.listdir(filepath):
            newdir = os.path.join(filepath,s)
            if os.path.isdir(newdir):
                go_through(newdir)

def get_txt(filepath):
    if os.path.isdir(filepath):
        for s in os.listdir(filepath):
            newdir = os.path.join(filepath, s)
            if os.path.isdir(newdir):
                get_txt(newdir)
            else:
                if newdir[-4:] != '.txt':
                    os.remove(newdir)

def del_txt(filepath):
    if os.path.isdir(filepath):
        for s in os.listdir(filepath):
            newdir = os.path.join(filepath, s)
            if os.path.isdir(newdir):
                del_txt(newdir)
            else:
                if newdir[-4:] == '.txt':
                    os.remove(newdir)

if __name__ == '__main__':

    # filefold = input('please input fold path: ')
    filefold = r'C:\Users\12506\Downloads\中文文本纠错\19【备份】医药行业报告汇总【360压缩解压】'
    # del_txt(filefold)
    go_through(filefold)
    # get_txt(filefold)

