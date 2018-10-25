__author__ = 'jmh081701'
import  numpy as np
import  os
import  json
import  data_parse
exp =0.000000000001
class HMM_model(object):
    def __init__(self,A,B,PI):
        self.A = A #概率转移矩阵
        self.B = B #概率发射矩阵
        self.PI = PI #初始状态矩阵
    def decode(self,Observe_state):
        #使用维特比算法计算一个给定的观察序列,概率最大的状态序列
        state_length = len(Observe_state)
        alpha=[]
        _ ={}
        for each_pos in self.PI:
            _[each_pos]=self.PI.get(each_pos,exp)
            _['___prev___']= each_pos
        alpha.append(_)
        for i in range(1,state_length):
            _max=0
            _pos=None
            _ ={}
            for this_pos in self.A:
                for prev_pos in self.A:
                    p = float(alpha[i-1].get(prev_pos,exp)) * float(self.A[prev_pos].get(this_pos,exp)) * float(self.B[this_pos].get(Observe_state[i][data_parse.WORD],exp))
                    if p > _max:
                        _max = p
                        _pos = prev_pos
                _[this_pos] = _max
                _['___prev___'] = _pos
            alpha.append(_)

        #找到最后一列最大的那个
        _max = 0
        last_pos = None

        for pos in alpha[state_length-1]:
            if pos=='___prev___':
                continue
            if alpha[state_length-1][pos] > _max:
                _max = alpha[state_length-1][pos]
                last_pos = pos
        #依次找到状态序列
        rst =[]
        index = state_length -1
        while index >= 0 :
            rst.append(last_pos)
            last_pos=alpha[index]['___prev___']
            index -=1
        rst.reverse()
        return rst
    def check(self,real_pos,predict_pos):
        right_cnt = 0
        for i in range(len(real_pos)):
            if real_pos[i][data_parse.POS] ==predict_pos[i] :
                right_cnt +=1
        return right_cnt/(len(real_pos) + exp)

loader = data_parse.Text_loader(file="")
A,B,PI,validdata=loader.load()
hmm_predictor = HMM_model(A,B,PI)
print(validdata[1])
rst=hmm_predictor.decode(validdata[1])
print(rst)

print(hmm_predictor.check(validdata[1],rst))
#valid::::
right_rate =0
total_cnt =0
for line in validdata:
    pre_pos = hmm_predictor.decode(line)
    right_rate  += hmm_predictor.check(line,pre_pos)
    total_cnt += 1
    print({'right_rate':right_rate/(total_cnt+exp)})

print({'right_rate':right_rate/(len(validdata)+exp)})