# -*- coding:utf-8 -*-
#@Time  : 2020/1/10 18:02
#@Author: Cao Yongchang
#@File  : text_segmentation.py

import jieba
import pandas as pd
from tqdm import tqdm

def text_segment():
    source = pd.read_csv('tot_acc_sent.tsv',sep='\t',encoding = "utf-8")
    targetf = open('segmented_text.tsv','w+',encoding = "utf-8")
    targetf.write('id\tsegmented_text\n')
    targetf.close()

    targetf = open('segmented_text.tsv', 'a+', encoding="utf-8")
    for id,text in tqdm(zip(source['id'],source['sentence'])):
        seg_list = jieba.cut(text)
        ans = ', '.join(seg_list)
        targetf.write('{}\t{}\n'.format(id,ans.strip(' ')))
    targetf.close()

if __name__ == '__main__':
    text_segment()