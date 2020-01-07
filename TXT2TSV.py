# -*- coding:utf-8 -*-
#@Time  : 2020/1/7 13:57
#@Author: Cao Yongchang
#@File  : TXT2TSV.py

import os
import glob

bin_stop_punc = [',','，','；',';']
stop_punc = ['。','?','？','!','！']

sent_num = 1

def get_tot_acc_sent(filename):
    global sent_num
    ft = open('tot_acc_sent.tsv', "a+",encoding='utf-8')
    fs = open(filename,'r',encoding='utf-8')
    for line in fs.readlines():
        begin = 0
        end = 0
        while begin<len(line) and end < len(line):
            if begin == 0 or line[begin] in bin_stop_punc+stop_punc:
                end = begin+1
                while end < len(line):
                    if line[end] in stop_punc:
                        if(end - begin >= 10):
                            ft.write('{}\t{}\n'.format(sent_num,line[begin:end+1].strip('\n')))
                        sent_num += 1
                        begin = end +1
                    end += 1
            else: begin += 1
    fs.close()
    ft.close()


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

if __name__ == '__main__':

    # filefold = input('please input fold path: ')
    filefold = r'C:\Users\12506\Downloads\中文文本纠错\19【备份】医药行业报告汇总【360压缩解压】'
    f = open('tot_acc_sent.tsv', "w", encoding='utf-8')
    f.write('id\tsentence\n')
    f.close()
    go_through(filefold)