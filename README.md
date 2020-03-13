# Chinese-Error-Checking

This is my first attempt in the direction of nlp，it is dedicated to complete a Chinese error detection!

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

| 更新文件                      | 算法简介                                                     | 简易对比                                                     | 简易分析                                                     |
| ----------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| origin0228.txt ours0228.txt   | 在当前版本中，已经划分出测试集、整合抽取出的领域专有名词、使用贪心策略在每个纠错步进行最优词的纠错，检错Threshold=1（越小发现的可能错词越多）、限定词语的候选词为相同简拼。 | 原始模型:<br>same_pinyin: 59/98;<br>same_stroke: 30/52;<br>miss_char: 0/100;<br>change_word: 32/100;<br>我们的模型：<br>same_pinyin: 40/98;<br>same_stroke: 20/52;<br>miss_char: 16/100;<br>change_word: 19/100; | 原始模型在添加候选词时存在与原始词拼音相同的限制，我们尝试因此加入简拼相同的限制，用以较少候选词的发散性，实验效果有较刚划分测试集时有部分提升，但仍弱于原始模型结果。认为原因是语料模型过小导致。 |
| origin0301t.txt ours0301t.txt | 在当前版本中，将错误发生处向专有名词倾斜，同时在为解决检错时我们的小语料模型准确率较低的问题，我们暂时将源模型的人民日报大规模语料用于我们的检错模块，此时检错的准确率较高，但是纠错模块准确率较低。 | 原始模型:<br/>64/100<br/>58/100<br/>0/100<br/>15/100<br/>我们的模型：<br/>49/100<br/>52/100<br/>21/100<br/>14/100 | 在纠错模块中，目前我们的模型的常见错误是将原本正确的词误以为是缺词而加字，如将正确的“性价比”改为了“性价比高”，而在原大规模语料中不存在这样修改的原因是原模型不具备为产生加字候选词的能力。此外，也看到了之前预想的Bug,如“执业医师”生成错误“执业仪师”，由于抽取预料中“执业药师”出现次数更多，我们的模型倾向于将其改为“执业药师”，从而引发改错错误。 |





```
数据解释：每个错误下有5行数据，分别代表检错精确率，检错召回率，纠错精确度，纠错召回率，纠正比例
eg:在origin0309.txt行、同音字列下的5行数据分别表示：
91/212：共检测出212处错误，其中91处真正包含错误；
91/100：原始句子中共有100处错误，模型检测出91处；
77/125：共纠正了125处错误，其中77处纠正地正确；
77/100：原始句子中共有100处错误，模型纠正出77处；
64/100：测试错误语句100个句子，完全改出64个。
```



<table border="1">
	<tbody>
		<tr>
			<td>
				<p>
					更新文件
				</p>
			</td>
			<td>
				<p>
					算法介绍
				</p>
			</td>
			<td>
				<p>
					同音字
				</p>
			</td>
			<td>
				<p>
					同形字
				</p>
			</td>
			<td>
				<p>
					漏字
				</p>
			</td>
			<td>
				<p>
					同音词
				</p>
			</td>
			<td>
				<p>
					简易分析
				</p>
			</td>
		</tr>
		<tr>
			<td rowspan="5">
				<p>
					Origin
				</p>
				<p>
					0309.txt
				</p>
			</td>
			<td rowspan="5">
				<p>
					原始模型；不存在加字的处理；不能处理漏字；且改错时强制限制完全同音。
				</p>
			</td>
			<td>
				<p>
					91/212
				</p>
			</td>
			<td>
				<p>
					89/187
				</p>
			</td>
			<td>
				<p>
					12/138
				</p>
			</td>
			<td>
				<p>
					68/152
				</p>
			</td>
			<td rowspan="5">
				<p>
					<br />
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					91/100
				</p>
			</td>
			<td>
				<p>
					89/100
				</p>
			</td>
			<td>
				<p>
					12/100
				</p>
			</td>
			<td>
				<p>
					37/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					77/125
				</p>
			</td>
			<td>
				<p>
					79/127
				</p>
			</td>
			<td>
				<p>
					0/69
				</p>
			</td>
			<td>
				<p>
					16/83
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					77/100
				</p>
			</td>
			<td>
				<p>
					79/100
				</p>
			</td>
			<td>
				<p>
					0/100
				</p>
			</td>
			<td>
				<p>
					16/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					64/100
				</p>
			</td>
			<td>
				<p>
					58/100
				</p>
			</td>
			<td>
				<p>
					0/100
				</p>
			</td>
			<td>
				<p>
					15/100
				</p>
			</td>
		</tr>
		<tr>
			<td rowspan="5">
				<p>
					Ours
				</p>
				<p>
					0309.txt
				</p>
			</td>
			<td rowspan="5">
				<p>
					领域小语料模型；threshold=1.0；关闭漏字纠错；改错时强制限制完全同音；
				</p>
			</td>
			<td>
				<p>
					93/223
				</p>
			</td>
			<td>
				<p>
					85/220
				</p>
			</td>
			<td>
				<p>
					28/223
				</p>
			</td>
			<td>
				<p>
					85/222
				</p>
			</td>
			<td rowspan="5">
				<p>
					利用小语料模型，在使用跟原始模型相似的框架时，我们的小语料模型较优于原始模型，但是这种纠错使用了强限制，与实际生活的语句错误存在偏差。
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					93/100
				</p>
			</td>
			<td>
				<p>
					85/100
				</p>
			</td>
			<td>
				<p>
					28/100
				</p>
			</td>
			<td>
				<p>
					61/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					80/108
				</p>
			</td>
			<td>
				<p>
					71/97
				</p>
			</td>
			<td>
				<p>
					0/64
				</p>
			</td>
			<td>
				<p>
					28/83
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					80/100
				</p>
			</td>
			<td>
				<p>
					71/100
				</p>
			</td>
			<td>
				<p>
					0/100
				</p>
			</td>
			<td>
				<p>
					28/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					69/100
				</p>
			</td>
			<td>
				<p>
					65/100
				</p>
			</td>
			<td>
				<p>
					0/100
				</p>
			</td>
			<td>
				<p>
					26/100
				</p>
			</td>
		</tr>
		<tr>
			<td rowspan="5">
				<p>
					Correction
				</p>
				<p>
					_word
				</p>
				<p>
					_0312.txt
				</p>
			</td>
			<td rowspan="5">
				<p>
					当前框架使用字粒度的语言模型进行检错，语言模型n_grams中n为2、3、4，对其打分进行平均处理。使用MAD算法检错，threshold=1.2
				</p>
			</td>
			<td>
				<p>
					90/312
				</p>
			</td>
			<td>
				<p>
					82/262
				</p>
			</td>
			<td>
				<p>
					41/269
				</p>
			</td>
			<td>
				<p>
					93/270
				</p>
			</td>
			<td rowspan="5">
				<p>
					由于当前框架的纠错模型尚未优化，目前可能正确词为编辑距离为1的词，关闭漏字修改模块，不能与之前模块进行完全横向对比。可以看到，其检错召回率与之前框架相当，但是其准确率较低，此外，在漏字上的召回率高于原始框架。
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					90/100
				</p>
			</td>
			<td>
				<p>
					82/100
				</p>
			</td>
			<td>
				<p>
					41/100
				</p>
			</td>
			<td>
				<p>
					74/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					58/99
				</p>
			</td>
			<td>
				<p>
					38/81
				</p>
			</td>
			<td>
				<p>
					0/39
				</p>
			</td>
			<td>
				<p>
					21/50
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					58/100
				</p>
			</td>
			<td>
				<p>
					38/100
				</p>
			</td>
			<td>
				<p>
					0/100
				</p>
			</td>
			<td>
				<p>
					21/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					51/100
				</p>
			</td>
			<td>
				<p>
					36/100
				</p>
			</td>
			<td>
				<p>
					0/100
				</p>
			</td>
			<td>
				<p>
					19/100
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p>
					<br />
				</p>
			</td>
			<td>
				<p>
					<br />
				</p>
			</td>
			<td>
				<p>
					<br />
				</p>
			</td>
			<td>
				<p>
					<br />
				</p>
			</td>
			<td>
				<p>
					<br />
				</p>
			</td>
			<td>
				<p>
					<br />
				</p>
			</td>
			<td>
				<p>
					<br />
				</p>
			</td>
		</tr>
	</tbody>
</table>
<p>
	<br />
</p>


