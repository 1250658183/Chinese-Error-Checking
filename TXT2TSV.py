# -*- coding:utf-8 -*-
#@Time  : 2020/1/7 13:57
#@Author: Cao Yongchang
#@File  : TXT2TSV.py

import os
import re
import glob

bin_stop_punc = [',','，','；',';']
stop_punc = ['。','?','？','!','！']

num_pun_pattern1 = re.compile(r'\d,\d')     #去除数字之间的逗号
num_pun_pattern2 = re.compile(r'\d，\d')
num_pattern = re.compile(r'[+-]?(\d)+(\.\d+)?(%)?')
brackets_pattern1 = re.compile(r'(\(|（).*(\)|）)')
eng_pattern = re.compile(r'[a-zA-Z]+')

selected_sent = set()

def get_tot_acc_sent(filename):
    global sent_num
    fs = open(filename,'r',encoding='utf-8')
    for line in fs.readlines():
        line = brackets_pattern1.sub("",line)
        line = eng_pattern.sub("@",line)
        line = num_pun_pattern2.sub("",line)        #去除数字之间的逗号
        line = num_pun_pattern1.sub("",line)
        line = num_pattern.sub("*",line)
        begin = 0
        end = 0
        while begin<len(line) and end < len(line):
            if begin == 0 or line[begin] in bin_stop_punc+stop_punc:
                end = begin+1
                while end < len(line):
                    if line[end] in stop_punc:
                        if(end - begin >= 10):
                            get_line = line[begin:end+1].strip('\n')
                            get_line = line[begin:end + 1].strip('\t')
                            if len(get_line) > 30:
                                pre_index = 0
                                index = pre_index + 10
                                while index < len(get_line) - 10:
                                    if get_line[index] in stop_punc+bin_stop_punc:
                                        selected_sent.add(get_line[pre_index:index+1])
                                        pre_index = index+1
                                        index = pre_index+10
                                        if len(get_line) - pre_index < 30:
                                            break
                                    else:
                                        index += 1
                                if pre_index < len(get_line):
                                    selected_sent.add(get_line[pre_index:])
                            else:
                                selected_sent.add(get_line)
                            # ft.write('{}\t{}\n'.format(sent_num,line[begin:end+1].strip('\n')))
                        begin = end +1
                    end += 1
            else: begin += 1
    fs.close()


def go_through(filepath):
    if os.path.isdir(filepath):
        for s in os.listdir(filepath):
            newdir = os.path.join(filepath, s)
            if os.path.isdir(newdir):
                go_through(newdir)
            else:
                if newdir[-4:] == '.txt':
                    print('extracting from {}'.format(newdir))
                    get_tot_acc_sent(newdir)

def write_to_file():
    ft = open('tot_acc_sent.tsv', "a+", encoding='utf-8')
    global selected_sent
    for id,text in enumerate(selected_sent):
        # text = num_pun_pattern2.sub("",text)        #去除数字之间的逗号
        # text = num_pun_pattern1.sub("",text)
        # text = num_pattern.sub("@NUM",text)
        # text = brackets_pattern1.sub("",text)
        # text = brackets_pattern2.sub("", text)
        ft.write('{}\t{}\n'.format(id+1,text))
    ft.close()


if __name__ == '__main__':

    # filefold = input('please input fold path: ')
    filefold = r'C:\Users\12506\Downloads\中文文本纠错\19【备份】医药行业报告汇总【360压缩解压】'
    f = open('tot_acc_sent.tsv', "w", encoding='utf-8')
    f.write('id\tsentence\n')
    f.close()
    go_through(filefold)
    write_to_file()