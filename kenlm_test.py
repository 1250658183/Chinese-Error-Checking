#encoding:utf-8
import kenlm
model = kenlm.Model('/home/cyc/下载/MyModel/log.bin')
print(model.score('基层', bos=True, eos=True))
