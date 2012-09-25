#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import subprocess
import sys
import os
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
import Stemmer




def stem(str):
  ## funkce prevede text na vstupu a prevede jej na slovnik indexovany offsetem 
  stemm= Stemmer.Stemmer('german')
  split = str.split(' ')
  index = 1
  new = []
  new1  = []
  dict = {}
  new1.append(['',0,0])
  pom2 = 0
  for word in split:
    item = []
    #item bude obsahovat prevedene slovo, celkovy posun o ktery je posunut v textu
    # a index na kterem se slovo nachazi
    new.append(word)
    if word != '':
      # kazde slovo prevede pomoci stemmeru
      pom = stemm.stemWord(word)
      item.append(pom)
      item.append(pom2 + new1[-1][1])
      dict[index]= item
      item.append(index)
      new1.append(item)
      index += len(pom) + 1
      pom2 = len(word) - len(pom)
    else:
      pom2 += 1
  outp = ''
  for i in new1:
    outp += i[0] + ' '
  outp = outp[1:]
  result = []
  result.append(outp)
  result.append(dict)
  return result

def lemmat(str):

  lemm = WordNetLemmatizer()
  split = str.split(' ')
  index = 1
  new = []
  new1  = []
  dict = {}
  new1.append(['',0,0])
  pom2 = 0
  for word in split:
    item = []
    new.append(word)
    if word != '':
      pom = lemm.lemmatize(word,'n')
      item.append(pom)
      item.append(pom2 + new1[-1][1])
      dict[index]= item
      item.append(index)
      new1.append(item)
      index += len(pom) + 1
      pom2 = len(word) - len(pom)
    else:
      pom2 += 1
  outp = ''
  for i in new1:
    outp += i[0] + ' '
  outp = outp[1:]
  result = []
  result.append(outp)
  result.append(dict)
  return result

def find(input,lang):
  if lang != 'en' and  lang != 'de':
     return {}
  input = input.lower()
  input = input.replace('\n',' ')
  input = re.sub('\xe3\x9f','ss',input,re.UNICODE)
  input = re.sub('[^\xc3\xB6\xe3\x9f\xBCa-zA-Z0-9_]',' ',input,re.UNICODE)
  if lang == 'en':
    list = lemmat(input)
  if lang == 'de':
    list = stem(input)
  input = list[0]
  inputfile = open('NERvstup333','w')
  inputfile.write(input)
  inputfile.write('\n') 
  inputfile.close()
  if lang == 'en':
    subprocess.call(['./figav07 -l  allc_list  -d automaton.fsa -m mapa.map < NERvstup333  > result'],shell = True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  if lang == 'de':
    subprocess.call(['./figav07 -l  gallc_list  -d gautomaton.fsa -m gmapa.map < NERvstup333  > result'],shell = True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  f1 = open("result","r")
  dict = {}
  #print list[1]
  while True:
    line = f1.readline()
    if line == '':
      f1.close()
      break
    line = line.split('\n')
    lnsplit = line[0].split('	')
    
    beg = int(lnsplit[1]) 
    en = int(lnsplit[2])
    try:
      en += list[1][beg][1]
      beg += list[1][beg][1]
    except:
      continue
      print "continuing"
    len = en-beg+1
    print lnsplit[0]+'\t'+str(beg)+'\t'+lnsplit[2]+'\t'+lnsplit[3]+'\t'+lnsplit[4]+'\t'+lnsplit[5]
    if lnsplit[3] in dict:
      dict[lnsplit[3]].append([beg-1,len,lnsplit[3],lnsplit[5],lnsplit[8]])
    else:
      dict[lnsplit[3]] = []
      dict[lnsplit[3]].append([beg-1,len,lnsplit[3],lnsplit[5],lnsplit[8]])
  return dict	 

