import numpy
from numpy import *

class ScoreSearch:

  def __init__(self):
    return
    
  def scoreStrings(self, string1, string2):
    """Takes to strings and returns their Levenshtein Distance. Limited to max. 15 chars per string"""
    if len(string1) and len(string2) <= 15:
      table = resize(array((0)), (len(string1),len(string2)))
    else:
      return -1
      
    #init gap penalties
    table[:,0] = arange(len(string1))
    table[0,:] = arange(len(string2))
  
    for i in range(1, len(string1)):
      for j in range(1, len(string2)):
        #current chars match - no penalty added
        if string1[i] == string2[j]:
          table[i,j] = table[i-1,j-1]
        #gap or substitution
        else:
          table[i,j] = min([table[i-1,j], table[i,j-1], table[i-1,j-1]]) + 1
    return table[len(string1)-1,len(string2)-1]  

  #compares string 1 with all strings in strings[] and returns strings[] in descending order,
  #with the lowest distance string first.
  def findMatches(self, string, strings):
    """Takes a string and a list of strings. Returns strings sorted, in descending order of Levenshtein Distance"""
    result = []
    for currStr in strings:
      result.append([self.scoreStrings(string, currStr), currStr])
    result.sort()
    return map(lambda currEl:currEl[1], result)
