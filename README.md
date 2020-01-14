# Chinese-Error-Checking

This is my first attempt in the direction of nlp，it is dedicated to complete a Chinese error detection!

## 01.08面谈任务简述：

&emsp;&emsp;在pdf抽取text时，由于**pdfminer库**会将原pdf中的每一行text创建一个单独的元素，此时需要面临的一个问题就是判断判断两个子句是否是属于同一个sentence。利用启发式规则，如：两行的height相同；两行的x0相同等均会产生不可预测的错误，因此设计一个自动判断两个子句是否属于一个sentence的**二分类分类器** 就显得十分主重要。<br><br>
&emsp;&emsp;同样，在抽取pdf中的text时，有些存在于表格中表头等**不是完整句子**的元素,其可能是存在**特定领域特定表征**的有用信息，可以探索是否可以设置二分类器，其能够判别抽取的数据是有用信息或者是无用表项等。

------

## 1. Data Process

| 文件               | 含义                                                         |
| :----------------- | :----------------------------------------------------------- |
| segmented_text.tsv | 其内容包含编号以及分好词的源数据，其内容与tot_acc_sent.tsv一一对应 |
| Extract_PDF.py     | 该文件包含了将PDF抽取出TXT的基本操作，其处理结果为输入一个文件目录，其自动便利此目录下的子目录与.pdf文件，同时将抽取的.txt文件放入到与.pdf同目录下的文件夹中. 抽取模式为利用pdfminer库，实现识别pdf文件中的TEXT信息，并添加启发式规则，合并应该属于同一条语句的TEXT，目前启发式规则仍在不断完善中 |
| TXT2TSV.py         | 实现将抽取的TXT转化为id \t contence \n 格式的.tsv文件，同样输入文件目录，程序自动递归遍历，输出文件再程序同目录下，其基本处理模式为判断中英文标点作为分隔符，并过滤长度<10的句子 |
| tot_acc_sent.tsv   | 包含了抽取出的可用句子                                       |

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
#### 2.1.4 训练中文语言模型
#### 数据准备(分词的文件)
```bash
no_id_seg_text.tsv
```
#### 训练模型(在build目录下操作)
```bash
bin/lmplz -o 3 --verbose_header --text no_id_seg_text.tsv --arpa MyModel/log.arpa

-o n:最高采用n-gram语法
-verbose_header:在生成的文件头位置加上统计信息
--text text_file:指定存放预料的txt文件
--arpa:指定输出的arpa文件
```

![2020-01-14 17-07-41屏幕截图](/home/zhaofei/图片/2020-01-14 17-07-41屏幕截图.png)

#### 安装kenlm的python包

```bash
pip3 install https://github.com/kpu/kenlm/archive/master.zip
```
#### 将arpa文件转换为binary文件(在build目录下操作)
```bash
bin/build_binary -s MyModel/log.arpa MyModel/log.bin
```

#### 使用训练的模型预测句子的概率
```bash
#encoding:utf8
import kenlm
model = kenlm.Model('MyModel/log.bin')
print(model.score('我 是 中国人 .',bos = True,eos = True))
```



