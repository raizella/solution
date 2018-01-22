from BTrees.OOBTree import OOBTree

t = OOBTree()
t['a'] = True
t['apple'] = True
t['avocado'] = True
t['b'] = True
t['banana'] = True
t['c'] = True
t['carrot'] = True
t['cabbage'] = True
t['cz'] = True
t['d'] = True
t['orange'] = True
t['zucchini'] = 4

if 'zucchini' in t:
	print t['zucchini']

# Examples of range queries.
str = ''
therange = t.keys(min='c', max='d', excludemin=False, excludemax=True)
for i in therange:
  str = str + i + ' '
print 'c*: ', str

str = ''
therange = t.keys(min='ca', max='cb', excludemin=False, excludemax=True)
for i in therange:
  str = str + i + ' '
print 'ca*: ', str

str = ''
therange = t.keys(excludemin=False, excludemax=False)
for i in therange:
  str = str + i + ' '
print '*: ', str
