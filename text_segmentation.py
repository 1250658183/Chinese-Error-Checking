# -*- coding:utf-8 -*-
#@Time  : 2020/1/10 18:02
#@Author: Cao Yongchang
#@File  : text_segmentation.py

import jieba
import pandas as pd
from tqdm import tqdm

stop = [line.strip() for line in open('哈工大停用词表.txt',encoding = "utf-8").readlines() ]

def text_segment():
    source = pd.read_csv('tot_acc_sent.tsv',sep='\t',encoding = "utf-8")
    targetf = open('segmented_text.tsv','w+',encoding = "utf-8")
    targetf.write('id\tsegmented_text\n')
    targetf.close()

    targetf1 = open('no_id_seg_text.tsv', 'w+', encoding="utf-8")
    targetf1.write('segmented_text\n')
    targetf1.close()

    targetf = open('segmented_text.tsv', 'a+', encoding="utf-8")
    targetf1 = open('no_id_seg_text.tsv', 'a+', encoding="utf-8")
    for id,text in tqdm(zip(source['id'],source['sentence'])):
        ans = ""
        seg_list = jieba.cut(text)
        for seg in seg_list:
            if seg not in stop:
                ans += ' '+seg
        targetf.write('{}\t{}\n'.format(id,ans.strip(' ')))
        targetf1.write('{}\n'.format(ans.strip(' ')))
    targetf.close()
    targetf1.close()

if __name__ == '__main__':
    text_segment()