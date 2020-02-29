# -*- coding:utf-8 -*-
#@Time  : 2020/2/22 21:09
#@Author: Cao Yongchang
#@File  : Error_Sent_Generate.py


import random
import jieba
from pypinyin import lazy_pinyin
from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
from tqdm import tqdm
import pandas as pd
sentences = []
data_path = r'E:\Anaconda3\Lib\site-packages\pycorrector\data'
custom_dict_path = r'E:\Anaconda3\Lib\site-packages\pycorrector\data\custom_word_freq.txt'

custom_dict = open(custom_dict_path, 'r', encoding='utf-8')
for line in custom_dict:
    if line[0] == '#':
        continue
    if len(line.strip().split()) == 2:
        word, freq = line.strip().split()[0], line.strip().split()[1]
        jieba.add_word(word, freq)
    elif len(line.strip().split()) == 1:
        jieba.add_word(line.strip())

random.seed(1)

def get_same_pinyin(filepath):          #获取同音字
    pinyin = []
    with open(filepath,'r',encoding='utf-8') as f:
        for line in f:
            if line[0] == '#':
                continue
            pinyin.append(''.join(line.split()))        #去除文件中的空格
    return pinyin

def get_same_stroke(filepath):          #获取同形词
    stroke = []
    with open(filepath,'r',encoding='utf-8') as f:
        for line in f:
            if line[0] == '#':
                continue
            stroke.append(''.join(line.split()))        #去除文件中的空格
    return stroke

def genarate_pinyin_error(sents,same_pinyin):
    ans = []
    for sent in sents:
        seg_sent = list(jieba.cut(sent))
        while True:
            select_word = random.sample(seg_sent,1)[0]         #随机一个候选词
            if len(select_word) > 1:
                break

        select_char = random.choice(list(select_word))     #随机一个需要更改的字
        err_char = select_char                             #确保产生一个词
        for item in same_pinyin:
            if select_char in item:
                while True:
                    err_char = random.choice(item)
                    if err_char != select_char:
                        break
                else:
                    continue
                break
        char_index = select_word.find(select_char)          #替换词语中的单字
        err_word = select_word[:char_index] + err_char
        if char_index < len(select_word)-1:
            err_word += select_word[char_index+1:]

        word_index = sent.find(select_word)                 #替换语句中的错词
        err_sent = sent[:word_index] + err_word
        if word_index + len(select_word) < len(sent):
            err_sent += sent[word_index+len(select_word):]

        if err_sent != sent:
            ans.append((sent,err_sent))
    return ans

def genarate_stroke_error(sents,same_stroke):
    ans = []
    for sent in sents:
        seg_sent = list(jieba.cut(sent))
        while True:
            select_word = random.sample(seg_sent,1)[0]         #随机一个候选词
            if len(select_word) > 1:
                break

        select_char = random.choice(list(select_word))     #随机一个需要更改的字
        err_char = select_char                             #确保产生一个词
        for item in same_stroke:
            if select_char in item:
                while True:
                    err_char = random.choice(item)
                    if err_char != select_char:
                        break
                else:
                    continue
                break
        char_index = select_word.find(select_char)          #替换词语中的单字
        err_word = select_word[:char_index] + err_char
        if char_index < len(select_word)-1:
            err_word += select_word[char_index+1:]

        word_index = sent.find(select_word)                 #替换语句中的错词
        err_sent = sent[:word_index] + err_word
        if word_index + len(select_word) < len(sent):
            err_sent += sent[word_index+len(select_word):]

        if err_sent != sent:
            ans.append((sent,err_sent))
    return ans

def genarate_miss_error(sents):
    ans = []
    for sent in sents:
        seg_sent = list(jieba.cut(sent))
        while True:
            select_word = random.sample(seg_sent,1)[0]         #随机一个候选词
            if len(select_word) > 1:
                break

        select_char_index = random.choice(list(range(len(select_word))))     #随机一个需要更改的字
        err_word = select_word[:select_char_index]
        if select_char_index < len(select_word)-1:
            err_word += select_word[select_char_index+1:]
        err_sent = sent.replace(select_word,err_word,1)

        ans.append((sent,err_sent))
    return ans

def genarate_word_error(sents):
    ans = []
    # hmmparams = DefaultHmmParams()
    dagparams = DefaultDagParams()
    for sent in sents:
        seg_sent = list(jieba.cut(sent))
        while True:
            select_word = random.sample(seg_sent,1)[0]         #随机一个候选词
            if len(select_word) > 1:
                break

        error_word = select_word
        pinyin_list = lazy_pinyin(select_word)      #获取选定词的拼音
        # result1 = viterbi(hmm_params=hmmparams, observations=pinyin_list, path_num=5)
        try:
            result2 = dag(dagparams,pinyin_list,path_num = 5,log = True)
        except KeyError:
            continue
        while len(result2)>1:
            error_word = ''.join(random.choice(result2).path)
            if error_word != select_word:
                break

        word_index = sent.find(select_word)          #替换词语中的单字
        err_sent = sent[:word_index]+error_word
        if word_index + len(select_word) < len(sent):
            err_sent += sent[word_index + len(select_word):]
        if err_sent != sent:
            ans.append((sent,err_sent))
    return ans

source = open('data/segmented_text_v2_test.tsv','r',encoding = "utf-8")
same_pinyin = get_same_pinyin(data_path+'\same_pinyin.txt')
same_stroke = get_same_stroke(data_path+'\same_stroke.txt')

for line in source:
    sentences.append(line.strip())

same_pinyin_error_sents = genarate_pinyin_error(random.sample(sentences,100),same_pinyin)
same_stroke_error_sents = genarate_stroke_error(random.sample(sentences,100),same_stroke)
miss_char_error_sents = genarate_miss_error(random.sample(sentences,100))
change_word_error_sents = genarate_word_error(random.sample(sentences,100))

with open('data/cor_err_sents_chart.txt','w',encoding='utf-8') as f:
    f.write('type:same_pinyin\n')
    for item in same_pinyin_error_sents:
        f.write('{}\t{}\n'.format(item[0],item[1]))
    f.close()
with open('data/cor_err_sents_chart.txt','a+',encoding='utf-8') as f:
    f.write('\ntype:same_stroke\n')
    for item in same_stroke_error_sents:
        f.write('{}\t{}\n'.format(item[0],item[1]))
    f.write('\ntype:miss_char\n')
    for item in miss_char_error_sents:
        f.write('{}\t{}\n'.format(item[0], item[1]))
    f.write('\ntype:change_word\n')
    for item in change_word_error_sents:
        f.write('{}\t{}\n'.format(item[0], item[1]))

    f.close()



