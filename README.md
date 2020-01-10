# Chinese-Error-Checking

This is my first attempt in the direction of nlp，it is dedicated to complete a Chinese error detection!

## 01.08面谈任务简述：
&emsp;&emsp;在pdf抽取text时，由于**pdfminer库**会将原pdf中的每一行text创建一个单独的元素，此时需要面临的一个问题就是判断判断两个子句是否是属于同一个sentence。利用启发式规则，如：两行的height相同；两行的x0相同等均会产生不可预测的错误，因此设计一个自动判断两个子句是否属于一个sentence的**二分类分类器** 就显得十分主重要。<br><br>
&emsp;&emsp;同样，在抽取pdf中的text时，有些存在于表格中表头等**不是完整句子**的元素,其可能是存在**特定领域特定表征**的有用信息，可以探索是否可以设置二分类器，其能够判别抽取的数据是有用信息或者是无用表项等。

## segmented_text.tsv
&emsp;&emsp;其内容包含编号以及分好词的源数据，其内容与tot_acc_sent.tsv一一对应。


## Extract_PDF.py
&emsp;&emsp;该文件包含了将PDF抽取出TXT的基本操作，其处理结果为输入一个文件目录，其自动便利此目录下的子目录与.pdf文件，同时将抽取的.txt文件放入到与.pdf同目录下的文件夹中。<br>
&emsp;&emsp;抽取模式为利用pdfminer库，实现识别pdf文件中的TEXT信息，并添加启发式规则，合并应该属于同一条语句的TEXT，目前启发式规则仍在不断完善中。

## TXT2TSV.py
&emsp;&emsp;实现将抽取的TXT转化为id \t contence \n 格式的.tsv文件，同样输入文件目录，程序自动递归遍历，输出文件再程序同目录下，其基本处理模式为判断中英文标点作为分隔符，并过滤长度<10的句子。

## tot_acc_sent.tsv
&emsp;&emsp;包含了抽取出的可用句子。
