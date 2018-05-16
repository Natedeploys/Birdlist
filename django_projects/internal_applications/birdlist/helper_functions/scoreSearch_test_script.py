#!/usr/bin/python

from scoreSearch import ScoreSearch

strings = ['hansi','hans','markus','manu','e10r19','birdy','numnum','honsi']

sc = ScoreSearch()

print('compare hansi and hanso')
print(sc.scoreStrings('hansi', 'hanso'))

print('comparing strings')
print(sc.findMatches('hans', strings))

