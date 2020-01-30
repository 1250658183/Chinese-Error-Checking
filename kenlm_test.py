#encoding:utf-8
import kenlm
model = kenlm.Model('/home/cyc/下载/MyModel/log_v2.bin')
print(model.score('医药 领域 快速 发展', bos=True, eos=True))
