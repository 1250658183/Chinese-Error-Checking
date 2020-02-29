# -*- coding:utf-8 -*-
#@Time  : 2020/1/10 18:02
#@Author: Cao Yongchang
#@File  : text_segmentation.py

import jieba
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
stop_word_file = r'data/哈工大停用词表保留特殊符号版.txt'
stop = [line.strip() for line in open(stop_word_file,encoding = "utf-8").readlines() ]
custom_dict_path = r'E:\Anaconda3\Lib\site-packages\pycorrector1\data\custom_word_freq.txt'


def text_segment():
    source = pd.read_csv('data/tot_acc_sent.tsv',sep='\t',encoding = "utf-8")
    targetf1 = open('data/segmented_text_v2_train.tsv','w+',encoding = "utf-8")
    targetf1.close()
    targetf2 = open('data/segmented_text_v2_test.tsv', 'w+', encoding="utf-8")
    targetf2.close()
    train_data,test_data = train_test_split(source,test_size=0.1,random_state=0)
    print(len(source),len(train_data),len(test_data))

    targetf1 = open('data/segmented_text_v2_train.tsv','a+',encoding = "utf-8")
    targetf2 = open('data/segmented_text_v2_test.tsv', 'a+', encoding="utf-8")

    custom_dict = open(custom_dict_path,'r',encoding='utf-8')
    for line in custom_dict:
        if line[0] == '#':
            continue
        if len(line.strip().split()) == 2:
            word,freq = line.strip().split()[0],line.strip().split()[1]
            jieba.add_word(word,freq)
        elif len(line.strip().split()) == 1:
            jieba.add_word(line.strip())

    for id,text in tqdm(zip(train_data['id'],train_data['sentence'])):
        ans = ""
        seg_list = jieba.cut(text)
        for seg in seg_list:
            if seg not in stop:
                ans += ' '+seg
        # targetf.write('{}\t{}\n'.format(id,ans.strip(' ')))
        targetf1.write('{}\n'.format(ans.strip(' ')))
    # targetf.close()
    targetf1.close()
    for id,text in tqdm(zip(test_data['id'],test_data['sentence'])):
        targetf2.write('{}\n'.format(text.strip()))
    # targetf.close()
    targetf2.close()

if __name__ == '__main__':
    text_segment()