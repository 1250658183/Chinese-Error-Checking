# -*- coding:utf-8 -*-
#@Time  : 2020/2/27 12:21
#@Author: Cao Yongchang
#@File  : Add_custom_dict.py
import sys
logfile = 'loginfo.txt'
f = open(logfile,'w')
f.close()
class Logger(object):
    def __init__(self, filename='loginfo.txt', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a',encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

sys.stdout = Logger(logfile, sys.stdout)
sys.stderr = Logger(logfile, sys.stderr)		# redirect std err, if necessary

import os
source_dict = r'G:\MyFiles\Courses\Chinese Essay Error Checking\Chinese_segment_augment-master\Got_New_Word.txt'
target_dict = r'E:\Anaconda3\Lib\site-packages\pycorrector1\data\custom_word_freq.txt'
commom_char_path = r'E:\Anaconda3\Lib\site-packages\pycorrector1\data\common_char_set.txt'
THU_path = r'G:\MyFiles\Courses\Chinese Essay Error Checking\THUsegment'

common_char_list = []
common_char_list = [line.strip() for line in open(commom_char_path,encoding = "utf-8").readlines() ]

def Add_custom_dict():
    new_word_dict = {}
    with open(source_dict,'r',encoding='utf-8') as f:
        for line in f:
            new_word = line.split()[0]
            for zifu in new_word:
                if zifu not in common_char_list:
                    break
            else:
                new_word_dict[new_word] = new_word_dict.get(new_word,0) + float(line.split()[1])
            continue
    new_word_list = sorted(new_word_dict.items(),key=lambda x:x[1],reverse=True)

    with open(target_dict,"a",encoding='utf-8') as tf:
        for (word,frec) in new_word_list:
            tf.write('\n{}\t{}'.format(word,min(10000,int(frec*1000+50))))
        tf.close()

def Add_THU_dict():
    new_word_dict = {}
    for filename in os.listdir(THU_path):
        filepath = os.path.join(THU_path,filename)
        print(filename)
        with open(filepath,'r',encoding='utf-8') as f:
            for line in f:
                if len(line.split()) > 1:
                    new_word = line.split()[0]
                    new_word_dict[new_word] = new_word_dict.get(new_word, 0) + float(line.split()[1])
        f.close()
    new_word_list = sorted(new_word_dict.items(), key=lambda x: x[1], reverse=True)
    with open(target_dict,"a",encoding='utf-8') as tf:
        for (word,frec) in new_word_list:
            tf.write('\n{}\t{}'.format(word,min(10000,int(frec*1000+50))))
        tf.close()





# Add_custom_dict()
Add_THU_dict()