#encoding:utf-8
import sys
import kenlm
import jieba
import numpy as np
import pandas as pd
#漏字例句： 患者大脑中感知痛觉的神经网络会被异常激活 患者大脑中感知痛觉的神经络会被异常激活
#错字例句： 延禧攻略电视剧剧情介绍  延禧工略电视剧剧情介绍
#错词例句： 地方各级人民政府设置医疗机构  地方各级人民政府设置医疗机会
f = open('originlog.txt','w')
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

sys.stdout = Logger('originlog.txt', sys.stdout)
sys.stderr = Logger('originlog.txt', sys.stderr)		# redirect std err, if necessary


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

model = kenlm.Model('MyModel/log_v2.bin')
# print('cor:',model.perplexity(' '.join(jieba.cut(cor_sent)), bos=True, eos=True))

#修改了 corrector.py 148 ;    212 min(maybe_right_items ;    227 ma ybe_errors = self.detect(sentence)
import pycorrector
# fixed_pycorrector.correct('主品种白蛋白提升速度为全行业第一')
sent_chart = {}
with open('cor_err_sents_chart.txt','r',encoding='utf-8') as f:
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
            print('cor:', model.perplexity(' '.join(jieba.cut(cor_sent))))
            print('err:', model.perplexity(' '.join(jieba.cut(err_sent))))
            corrected_sent, detail = pycorrector.correct(err_sent)
            print('fixed:', model.perplexity(' '.join(jieba.cut(corrected_sent))))
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