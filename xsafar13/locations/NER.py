#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import subprocess
import sys
import os

def states():
    f2 = open("states",'r')
    states={}
    while True:
      state_code= f2.readline()
      if state_code == '':
        f2.close()
        break
      b = state_code.split('\n')
      b = b[0].split('\t')
      states[b[0]]= b[1]
    f2.close()
    return states

def dupli():
    file = open('list_of_duplicates','r')
    duplicates={}
    while True:
      a = file.readline()
      if a == '':
        file.close()
        break
      b = a.split('\n')
      c = b[0]
      duplicates[c]=1;
    file.close()
    return duplicates

def readFile():
  fileHandle=open("duplicates_static","r")
  line = fileHandle.readline()
  dictName = {}
  line=line.split('\n')
  line=line[0].split('\t')

  while line!=['']:
    if line[0] in dictName:
      dictName[line[0]].append(line)
    else:
      dictName[line[0]] = []
      dictName[line[0]].append(line)
    line = fileHandle.readline()
    line=line.split('\n')
    line=line[0].split('\t')
  return dictName

def frequency(uniq):
  cnt = {}
  word_list=[]

#  cnt=Counter()

  for line in uniq:
    word=line[-2]
    word_list.append(word)
  for word in word_list:
    cnt[word] = cnt.get(word, 0) + 1
  return cnt

#  for word in word_list:
#    cnt[word] += 1
#  return cnt

# Zjisteni kontextu
def context(uniq):
  cnt=frequency(uniq)
  context=[]
  keys=sorted(cnt.items(), key=lambda x: x[1])
  try:
    keys[-1][1]
  except:  
    return None
  try:
    keys[-2][1]
  except: 
    context=[keys[-1][0]]
    return context
  
  if keys[-1][1]!=keys[-2][1]:
    context=[keys[-1][0]]
  elif keys[-1][1]==keys[-2][1]:
    context=[keys[-1][0]]
    context.append(keys[-2][0])
  elif keys[-2][1]==keys[-3][1]:
    context=[keys[-1][0]]
    context.append(keys[-2][0])
    context.append(keys[-3][0])
  return context

# Najdu prvky odpovidajici kontextu
def findContextElement(context,list,location):
  resultKeys=[]
  if context != None:
    for element in context:
      for i in list[location[2]]:
        pom = i[:]
        if pom[-3]==element:
          pom[-1] = str(float(i[-1]) + 0.5)
        resultKeys.append(pom)
  else:
      for i in list[location[2]]:
        resultKeys.append(i)
  return resultKeys

def contextImportance(contextKeys,location):
  keys=sorted(contextKeys, key=lambda x: x[-1])
  try:
    return keys[-1]
  except:
    return None

def disambiguation(dupl,uniq,list):
  for location in dupl:  
    dataContext=context(uniq) # Zjistim kontext

    contextKeys=findContextElement(dataContext,list,location) # Vyhleedam polozky odpovidajici kontextu
    result=[]
    result=contextImportance(contextKeys,location)
    result = result[0:-1]
    resu = [location[0],location[1],result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7]]
    uniq.append(resu)
  return uniq

def repairTags(text,tags):
     '''
     position correction
     '''
     offsets = [0,len(text)]
     for t in tags:
         offsets.extend([t[0],t[1]])
     
     offsets = list(set(offsets))
     offsets.sort()
     posDict = {} # {original position : position to offsets}

     for i in range(0,len(offsets)):
         posDict[offsets[i]] = i
     
     #correct \n
     offindex = 1 # index to offsets
     prevReduc = 0 # reduces next index 
     #print offsets
     
     for i in range(0,len(text)):
         if i >= offsets[offindex]:
             offindex += 1
             if offindex >= len(offsets):
                 break
             offsets[offindex] -= prevReduc
         if text[i] == '\n':
             prevReduc += 1
             offsets[offindex] -= 1
         
         
     
     #print offsets
     
     splitedText = []
     for i in range(1,len(offsets)):   
         splitedText.append(text[offsets[i-1]:offsets[i]])
     
     
     position = 0
     offindex = 1 #index to offsets
     
     #correct UTF-8        
     for string in splitedText:
         try:
           string = string.decode('utf-8')
         except:
           string= string;
         position += len(string)
         offsets[offindex] = position
         offindex += 1
     newTags = [[offsets[posDict[t[0]]],
                 offsets[posDict[t[1]]],
                 t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9],t[10]] 
                for t in tags]
     return newTags

def find(input,lang,args):
  if lang != 'en' and  lang != 'de':
     return {}
  inputfile = open('NERvstup333','w')
  inputline = input.replace('\n',' ')
  #inputline = input
  inputfile.write(inputline)
  inputfile.write('\n') 
  inputfile.close()
  subprocess.call(['./figav07 -l  allc_list  -d automaton.fsa -m map.map < NERvstup333  > result'],shell = True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
  f1 = open("result","r")
  uniq = []
  dupl = []
  dict = {}
  while True:
    line = f1.readline()
    if line == '':
      f1.close()
      break
    lnsplit = line.split('	')
    beg = int(lnsplit[1]) - 1
    en = int(lnsplit[2]) -1
    len = en-beg+1
    pom=lnsplit[11].split('\n')
    lnsplit[11]=pom[0]
    if lnsplit[3] in args[1]:
      dupl.append([beg,len,lnsplit[3],lnsplit[5],lnsplit[6],lnsplit[7],lnsplit[8],lnsplit[9],lnsplit[10],lnsplit[11]])
    else: 
      uniq.append([beg,len,lnsplit[3],lnsplit[5],lnsplit[6],lnsplit[7],lnsplit[8],lnsplit[9],lnsplit[10],lnsplit[11]])
  final=disambiguation(dupl,uniq,args[2])
  #print input
  pom = {}
  
  for i in final:
    if i[-2] in pom:
      pom[i[-2]] += 1
    else:
      pom[i[-2]] = 1
  print pom  
  for i in final:
    i.append(str(get_static(i[2],i[-3],int(i[-1]),i[-2],args[1],pom[i[-2]])))
  newFinal = repairTags(input,final)
  print newFinal
  for i in newFinal:
    if i[3] in dict:
      dict[i[3]].append(i)
    else:
      dict[i[3]] = []
      dict[i[3]].append(i)
  #os.remove('./NERvstup333')
  return dict	 

  
def get_static(name,fcode,popul,state,lod,count):
  if fcode == 'PPLC' or fcode == 'PCLI' or fcode == 'RGN' or fcode == 'ADM1' or fcode == 'PPLA':
    return 100  
  
  context = 0
  if state == 'DE' or state == 'GB' or state == 'CH' or state == 'AT' or state == 'BE' or state == 'LU' or state == 'CZ' or state == 'PL':
    context += 20
 
  if popul < 50000:
     context += 2
  elif popul < 100000:
     context += 4
  elif popul < 200000:
    context += 6
  elif popul < 400000:
     context += 8
  elif popul < 600000:
    context += 10
  elif popul < 800000:
    context += 12
  elif popul < 1000000:
    context += 14
  elif popul < 2000000:
     context += 16
  elif popul < 3000000:
     context += 18
  elif popul < 5000000:
    context += 20
  elif popul < 10000000:
     context += 22
  elif popul > 10000000:
     context += 24

  if name not in lod.keys():
    context += 10

  if count == 2:
    context += 5
  if count > 3:
    context += 10
 
  if fcode == 'ADMD' or fcode == 'ADM2' or fcode == 'PPLA2':
    context += 30
  elif fcode == 'ADM3' or fcode == 'PPLA3':
    context += 20
  elif fcode == 'ADM4' or fcode == 'PPLA4':
    context += 10
  
  return context
