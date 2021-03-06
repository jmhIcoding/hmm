__author__ = 'jmh081701'
import json
import os
import re
import  random
WORD=0
POS=1
exp =0.000000000001 #无穷小量 防止出现分母为0
class Text_loader(object):
    def __init__(self,file,seprate_rate=0.2):
        self.file =file
        self.seprate_rate = seprate_rate
        self.A={} #转移频次字典{'本词的词性':{'下个词的词性i':次数;···'total':总次数}···}
        self.B={} #发射频次字典{'当前词性':{'发射状态i':次数,···,'total':总次数}}
        self.PI={}#初始状态频次字典

    def load_text(self):
        with open(self.file,encoding='utf8') as fp :
            rawdata = fp.readlines()
        for i in range(len(rawdata)):
            rawdata[i] = rawdata[i].replace('\n','')
            line = rawdata[i].split(" ")
            rawdata[i]=[]
            for each in line:
                try:
                    word = each.rsplit('/',1)[WORD]
                    pos = each.rsplit('/',1)[POS]
                except:
                    print('except',each)
                rawdata[i].append((word,pos))
                #每一行,多个(词,词性)对
        #划分训练集,验证集
        len_lines = len(rawdata)
        valid_lines = int(len_lines * self.seprate_rate)
        start_pointer = random.randint(0,len_lines-valid_lines-1) #随机取出一堆来作为验证集
        self.traindata = rawdata[0:start_pointer]+rawdata[(start_pointer+valid_lines):]
        self.validdata = rawdata[start_pointer:(start_pointer+valid_lines)]

    def generator(self):
        #基于语料库,使用极大似然法得到各种参数
        len_lines = 0
        for line in self.traindata:
            len_lines += 1
            len_line= len(line)
            for i in range(len_line):
                pos =line[i][POS]
                word =line[i][WORD]
                if i==0:
                    #行开始
                    if  pos not in self.PI:
                        self.PI.setdefault(pos,1)
                    else:
                        self.PI[pos] += 1
                if i ==(len_line-1):
                    #行末尾,只统计发射状态
                    if pos not in self.B:
                        self.B.setdefault(pos,{'total':1})
                    else:
                        self.B[pos]['total'] += 1
                    if word not in self.B[pos]:
                        self.B[pos].setdefault(word,1)
                    else:
                        self.B[pos][word] += 1
                    break

                #普通字符,同时计算A和B
                #计算B
                if pos not in self.B:
                    self.B.setdefault(pos,{'total':1})
                else:
                    self.B[pos]['total'] += 1
                if word not in self.B[pos]:
                    self.B[pos].setdefault(word,1)
                else:
                    self.B[pos][word] += 1

                #计算A
                try:
                    next_pos = line[i+1][POS]
                except:
                    print(line,i,len_line,i+1)
                if pos not in self.A :
                    self.A.setdefault(pos,{'total': 1})
                else:
                    self.A[pos]['total'] += 1
                if next_pos not in self.A[pos]:
                    self.A[pos].setdefault(next_pos,1)
                else:
                    self.A[pos][next_pos] += 1


        #计算频率
        #计算B
        for pos in self.B :
            for word in self.B[pos] :
                if word=='total':
                    continue
                self.B[pos][word] /= (self.B[pos]['total'] + exp )
            self.B[pos]['total'] /= (len_lines + exp)
        #计算A

        for pos in self.A:
            for next_pos in self.A[pos]:
                if next_pos =='total':
                    continue
                self.A[pos][next_pos] /=(self.A[pos]['total'] +exp)
            self.A[pos]['total'] /=(len_lines+ exp)

        # 计算PI
        for pos in self.PI:
            self.PI[pos] /=(len_lines + exp)
        return self.A,  self.B, self.PI

    def save(self,model_path="hmm.model"):
        with open(model_path,"w") as fp:
            json.dump({'A':self.A,'B':self.B,'PI':self.PI},fp)
        with open(model_path+".valid","w") as fp:
            json.dump({'valid_data':self.validdata},fp)

    def load(self,model_path="hmm.model"):
        with open(model_path) as fp:
            _ = json.load(fp)
            self.A = _['A']
            self.B = _['B']
            self.PI = _['PI']
        with open(model_path+".valid") as fp:
            _ = json.load(fp)
            self.validdata = _['valid_data']
        return self.A,self.B,self.PI,self.validdata

if __name__ == '__main__':
    loader = Text_loader(file="data/raw_data.txt")
    #loader.load_text()
    #loader.generator()
    #loader.save()
    loader.load()
    for each in loader.A :
        print(each)