# Chinese-Error-Checking

This is my first attempt in the direction of nlp，it is dedicated to complete a Chinese error detection!

# 01.08面谈任务简述：

&emsp;&emsp;在pdf抽取text时，由于**pdfminer库**会将原pdf中的每一行text创建一个单独的元素，此时需要面临的一个问题就是判断判断两个子句是否是属于同一个sentence。利用启发式规则，如：两行的height相同；两行的x0相同等均会产生不可预测的错误，因此设计一个自动判断两个子句是否属于一个sentence的**二分类分类器** 就显得十分主重要。<br><br>
&emsp;&emsp;同样，在抽取pdf中的text时，有些存在于表格中表头等**不是完整句子**的元素,其可能是存在**特定领域特定表征**的有用信息，可以探索是否可以设置二分类器，其能够判别抽取的数据是有用信息或者是无用表项等。

------
# 解决方案
- 中文纠错分为两步走，第一步是错误检测，第二步是错误纠正；
- 错误检测部分先通过中文分词器切词，由于句子中含有错别字，所以切词结果往往会有切分错误的情况，这样从字粒度和词粒度两方面检测错误，整合这两种粒度的疑似错误结果，形成疑似错误位置候选集；
- 错误纠正部分，是遍历所有的疑似错误位置，并使用音似、形似词典替换错误位置的词，然后通过语言模型计算句子困惑度，对所有候选集结果比较并排序，得到最优纠正词；

# 模型
- 通用语言模型(使用人民日报2014版熟语料)
- 领域特定语言模型（医学领域预料）

## 错误检测
- 字粒度：语言模型困惑度（ppl）检测某字的似然概率值低于句子文本平均值，则判定该字是疑似错别字的概率大。
- 词粒度：切词后不在词典中的词是疑似错词的概率大(新词发现)。

## 错误纠正
- 通过错误检测定位所有疑似错误后，取所有疑似错字的音似、形似候选词;
- 使用候选词替换，基于语言模型得到类似翻译模型的候选排序结果，得到最优纠正词;

# 实验部分
## 1. Data Process

| 文件             | 含义                                                         |
| :--------------- | :----------------------------------------------------------- |
| Extract_PDF.py   | 该文件包含了将PDF抽取出TXT的基本操作，其处理结果为输入一个文件目录，其自动便利此目录下的子目录与.pdf文件，同时将抽取的.txt文件放入到与.pdf同目录下的文件夹中. 抽取模式为利用pdfminer库，实现识别pdf文件中的TEXT信息，并添加启发式规则，合并应该属于同一条语句的TEXT，目前启发式规则仍在不断完善中 |
| TXT2TSV.py       | 实现将抽取的TXT转化为id \t contence \n 格式的.tsv文件，同样输入文件目录，程序自动递归遍历，输出文件再程序同目录下，其基本处理模式为判断中英文标点作为分隔符，并过滤长度<10的句子 |
| tot_acc_sent.tsv | 存放数据相关，包括抽取语料，分词后训练集，未分词测试集等     |
| Model\           | 存放计算出的ngrams模型                                       |
| result\          | c                                                            |

------

## 2. Language Model

### 2.1 kenlm统计语言模型使用(已完成测试)
#### 2.1.1 下载
```bash
https://github.com/kpu/kenlm
```
#### 2.1.2 安装Boost(kenlm需要的依赖)
```bash
下载boost_1_67_0.tar.bz2(https://www.boost.org/users/history/version_1_67_0.html)
tar --bzip2 -xf boost_1_67_0.tar.bz2
cd boost_1_67/
./bootstrap.sh --prefix=/usr/local
sudo ./b2 install --with=all
sudo apt install libbz2-dev
sudo apt install liblzma-dev
```
#### 2.1.3 编译并安装kenlm
```bash
cd kenlm
mkdir -p build
cd build
cmake ..
make -j 4
```
### 2.2 训练领域特定语言模型
#### 2.2.1 数据准备(分词的文件)
```bash
no_id_seg_text.tsv
```
#### 2.2.2 训练模型(在build目录下操作)
```bash
bin/lmplz -o 3 --verbose_header --text no_id_seg_text.tsv --arpa MyModel/log.arpa

-o n:最高采用n-gram语法
-verbose_header:在生成的文件头位置加上统计信息
--text text_file:指定存放预料的txt文件
--arpa:指定输出的arpa文件
```

![test](test.png)

### 2.3 使用训练的模型纠错
#### 2.3.1 安装kenlm的python包

```bash
pip3 install https://github.com/kpu/kenlm/archive/master.zip
```
#### 2.3.2 将arpa文件转换为binary文件(在build目录下操作)
```bash
bin/build_binary -s MyModel/log.arpa MyModel/log.bin
```

#### 2.3.3 使用训练的模型预测句子的概率
```bash
#encoding:utf8
import kenlm
model = kenlm.Model('MyModel/log.bin')
print(model.score('我 是 中国人 .',bos = True,eos = True))
```



# 算法更新及结果显示

更新文件放入result文件夹下。

| 更新文件                    | 算法简介                                                     | 简易对比                                                     | 简易分析                                                     |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| origin0228.txt ours0228.txt | 在当前版本中，已经划分出测试集、整合抽取出的领域专有名词、使用贪心策略在每个纠错步进行最优词的纠错，检错Threshold=1（越小发现的可能错词越多）、限定词语的候选词为相同简拼。 | 原始模型:<br>same_pinyin: 59/98;<br>same_stroke: 30/52;<br>miss_char: 0/100;<br>change_word: 32/100;<br>我们的模型：<br>same_pinyin: 40/98;<br>same_stroke: 20/52;<br>miss_char: 16/100;<br>change_word: 19/100; | 原始模型在添加候选词时存在与原始词拼音相同的限制，我们尝试因此加入简拼相同的限制，用以较少候选词的发散性，实验效果有较刚划分测试集时有部分提升，但仍弱于原始模型结果。认为原因是语料模型过小导致。 |
|                             |                                                              |                                                              |                                                              |

