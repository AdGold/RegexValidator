import re
from copy import deepcopy

def freePipes(s):
    c = 0
    for e in s:
        if e == '(': c+=1
        elif e == ')': c-=1
        elif e == '|' and c == 0: return True
    return False
        
def containPipes(s):
    if freePipes(s):
        return '(%s)'%s
    else:
        return s

class eq(object):
	def __init__(self, eqNum, terms):
		self.eqNum = eqNum
		self.terms = terms[::]
	def isolateRHS(self):
		if self.terms[self.eqNum]:
			#apply rule A=xA+y is equivelent to A=x*y
			if len(self.terms[self.eqNum]) > 1:toadd = '(%s)*'%self.terms[self.eqNum]
			else: toadd = self.terms[self.eqNum]+'*'
			self.terms[self.eqNum] = ''
			for i in xrange(len(self.terms)):
				if self.terms[i]:
					self.terms[i] = toadd+containPipes(self.terms[i])
	def subIn(self, eq2):
		if self.terms[eq2.eqNum]:
			prefix = self.terms[eq2.eqNum]
			self.terms[eq2.eqNum] = ''
			for i,t in enumerate(eq2.terms):
				if not t: continue
				tmp = containPipes(prefix) + containPipes(t)
				if self.terms[i]:
					#tmp = '%s|%s'%(containPipes(self.terms[i]),containPipes(tmp))
					tmp = self.terms[i]+'|'+tmp
				self.terms[i] = tmp

def convertEquations(equations):
        eqs = [None]*len(equations)
        baseTerms = ['']*len(equations)
        for i in xrange(len(equations)):
                terms = list(baseTerms)
                for k,v in equations[i].items():
                        terms[k] = v
                eqs[i] = eq(i,terms)
        return eqs

def compress(eqs, cmpto):
        for i in xrange(len(eqs)-1,-1,-1):
                if i == cmpto: continue
                eqs[i].isolateRHS()
                for j in xrange(i):
                        eqs[j].subIn(eqs[i])
                eqs[cmpto].subIn(eqs[i])
        if len(eqs[cmpto].terms[cmpto]) == 1: return eqs[cmpto].terms[cmpto]+'*'
        return ('('+eqs[cmpto].terms[cmpto]+')*') if eqs[cmpto].terms[cmpto] else ''

def getRegexFromEqs(equations):
        eqs = convertEquations(equations)
        return '|'.join(filter(None,(compress(deepcopy(eqs),i)for i in xrange(len(eqs)))))
                




class graph(object):
        

        def __init__(self,maxheight, balls):
                self.edgeList = {}
                self.ids = {}
                self.idCount = 0
                s = (1,)*balls + (0,)*(maxheight-balls)
                self.makeGraph(s)
        
        def makeGraph(self, state):
                if state in self.ids: return
                throws = {}
                self.ids[state] = self.idCount
                self.idCount+=1
                for th in self.possThrows(state):
                        st = self.doThrow(state,th)
                        self.makeGraph(st)
                        throws[self.ids[st]] = str(th)
                self.edgeList[self.ids[state]] = throws

        def possThrows(self, state):
                if state[0] == 0: yield 0
                else:
                        for th in xrange(1,len(state)):
                                if not state[th]: yield th
                        yield len(state)

        def doThrow(self, state, th):
                if th == 0: return state[1:]+(0,)
                elif th == len(state): return state[1:]+(1,)
                return state[1:th]+(1,)+state[th+1:]+(0,)


def getFullRegex(maxheight):
        res = []
        for i in xrange(maxheight+1):
                g = graph(maxheight,i)
                res.append(getRegexFromEqs(g.edgeList))
                del g
        return '^('+'|'.join(res)+')$'
