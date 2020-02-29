#encoding:utf-8
import sys
import kenlm
import jieba
import numpy as np
import pandas as pd
#漏字例句： 患者大脑中感知痛觉的神经网络会被异常激活 患者大脑中感知痛觉的神经络会被异常激活
#错字例句： 延禧攻略电视剧剧情介绍  延禧工略电视剧剧情介绍
#错词例句： 地方各级人民政府设置医疗机构  地方各级人民政府设置医疗机会
# logname = 'with_add_func.txt'
logname = 'with_add_func.txt'
f = open(logname,'w')
f.close()
class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a',encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

sys.stdout = Logger(logname, sys.stdout)
sys.stderr = Logger(logname, sys.stderr)		# redirect std err, if necessary
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
my_stop_word_file = r'G:\MyFiles\Courses\Chinese Essay Error Checking\data\哈工大停用词表保留特殊符号版.txt'
my_stop = [line.strip() for line in open(my_stop_word_file,encoding = "utf-8").readlines() ]

cor_sents = ['地方各级人民政府设置医疗机构',
            '延禧攻略电视剧剧情介绍',
            '规范市场行为，确保患者用药安全',     #规范市场行为，确保患者用药安全。
             '类似于我国的医辽保险基金' ,    #类似于我国的医疗保险基金
             '抑制剂方案治疗失败的基因型',    #抑制剂方案治疗失败的基因型
             '自然就会牵涉商誉减值问题',     #自然就会牵涉商誉减值问题
             '溶瘤病毒通过携带外源基因增加抗肿瘤效果',
             '在考虑开始或者停止荷尔蒙替代疗法时',
             '由于多肽链的折叠和糖基化修饰',
            '药政改革逐步走向制高点',
            '康柏西普销售不达预期',
            '在如此庞大的基因组中',
]

err_sents = ['地方各级人民政府设置医疗机会',
            '延禧工略电视剧剧情介绍',
            '规费市场行为，确保患者用药安全',     #规范市场行为，确保患者用药安全。
             '类似于我国的益辽保险基金' ,    #类似于我国的医疗保险基金
             '抑治剂方案治疗失败的基因型',    #抑制剂方案治疗失败的基因型
             '自然就会牵涉熵誉减值问题',     #自然就会牵涉商誉减值问题
             '溶留病毒通过携带外源基因增加抗肿瘤效果',
             '在考虑开始或者停止荷耳蒙替代疗法时',
             '由于多肽链的折叠和唐基化修饰',
             '药政改革逐步走向致高点',
             '康柏茜普销售不达预期',
             '在如此庞大的基因阻中',
             ]

model = kenlm.Model('MyModel/log_v3.bin')
# print('cor:',model.perplexity(' '.join(jieba.cut(cor_sent)), bos=True, eos=True))

#修改了 corrector.py 148 ;    212 min(maybe_right_items ;    227 ma ybe_errors = self.detect(sentence)
import pycorrector
cor = '国家卫生健康委员会副主任王贺胜医政医管局局长张宗久接绍加强三级公立医院绩效考核工作有关情况。'
err = '例乳在中亚的乌兹别克斯坦哈萨克斯坦还有非洲的埃塞俄比亚和纳米比亚的投资。'
print(' '.join(jieba.cut(cor)))
print('cor:', model.perplexity(' '.join([word for word in list(jieba.cut(cor)) if word not in my_stop])))
print('err:', model.perplexity(' '.join([word for word in list(jieba.cut(err)) if word not in my_stop])))
test = pycorrector.correct(err)
print('err:', model.perplexity(' '.join([word for word in list(jieba.cut(test[0])) if word not in my_stop])))
print(test)
sent_chart = {}
with open('data\cor_err_sents_chart.txt','r',encoding='utf-8') as f:
    for line in f:
        if line[:4] == 'type':
            now_type = line[5:]
            sent_chart[now_type] = []
        elif len(line.strip()) > 0:
            sent_chart[now_type].append((line.split('\t')[0],line.split('\t')[1].strip()))      #前为正确的句子，后为错误的句子
fixed_num = {}
for error_type in sent_chart.keys():
    # if error_type == 'miss_char\n':
        fixed_num[error_type] = [0,0]
        print('\nerr type:',error_type,'\n')
        for (cor_sent,err_sent) in sent_chart[error_type]:
            print('cor:', model.perplexity(' '.join([word for word in jieba.cut(cor_sent) if word not in my_stop])))
            print('err:', model.perplexity(' '.join([word for word in jieba.cut(err_sent) if word not in my_stop])))
            corrected_sent, detail = pycorrector.correct(err_sent)
            print('fixed:', model.perplexity(' '.join([word for word in jieba.cut(corrected_sent) if word not in my_stop])))
            print('cor_sent:',cor_sent)
            print('err_sent:', err_sent)
            print('fix_sent:', corrected_sent)
            if corrected_sent == cor_sent:
                fixed_num[error_type][0] += 1
            fixed_num[error_type][1] += 1
            print('detail:', detail)
            print('\n')

for type in fixed_num.keys():
    print('{} : {}\t{}\n'.format(type,fixed_num[type][0],fixed_num[type][1]))