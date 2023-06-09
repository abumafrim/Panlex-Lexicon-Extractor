#author: Di Lu ## Adapted from the original code by Idris Abdulmumin
# -*- coding: utf-8 -*-                                                                                                  
import argparse
import sqlite3 as lite
import sys
from lxml import etree
import xml.etree.ElementTree as ET
import os
import json

def langid_extract(source_language, target_language, panlex_dir):
  source_langid = None
  target_langid = None
  wiktionary_file= os.path.join(panlex_dir, 'langvar.json')
  with open(wiktionary_file) as f:
    lines = f.read()
  json_lines = json.loads(lines)
  for line in json_lines:
    if line['lang_code'] == source_language and line['var_code'] == 0:
      source_langid = str(line['id'])
    if line['lang_code'] == target_language and line['var_code'] == 0:
      target_langid = str(line['id'])
  return source_langid, target_langid


def extract_bilingual_lexicon(source_language, target_language, output_directory, sql_database):

  con = lite.connect(sql_database)

  with con:
    print('loading expression file')

    n=0
    ll={}
    hl={}
    llm={}
    hlm={}
    mention_dic={}
    nsmap = {}
    expr_dic={}

    cur = con.cursor()

    # get source and target language ids
    cur.execute(f"SELECT * FROM langvar WHERE lang_code='{source_language}'")
    source_langid = cur.fetchone()[0]

    cur.execute(f"SELECT * FROM langvar WHERE lang_code='{target_language}'")
    target_langid = cur.fetchone()[0]

    if source_langid == None:
      print("Error: incorret source language code")
    if target_langid == None:
      print("Error: incorret target language code")
    else:
      assert source_langid != None and target_langid != None

    print("Step 1\nExtracting %s_%s -- %s_%s lexicon"%(source_language, source_langid, target_language, target_langid))

    cur.execute("SELECT * FROM expr")

    while True:
      row = cur.fetchone()
      if row == None:
        break
      expr_dic[row[0]] = row[1]
      if row[1] == source_langid:
        ll[row[0]] = row[2]
      elif row[1] == target_langid:
        hl[row[0]] = row[2]

    print('Step2')
    cur.execute("SELECT * FROM denotationx")

    while True:
      row = cur.fetchone()
      if row == None:
        break
      meaning_id = row[0]
      ex_id = row[4]
      if expr_dic[ex_id] == source_langid:
        if meaning_id in mention_dic:
          mention_dic[meaning_id][0].append(ex_id)
        else:
          mention_dic[meaning_id] = [[ex_id],[]]
      elif expr_dic[ex_id] == target_langid:
        if meaning_id in mention_dic:
          mention_dic[meaning_id][1].append(ex_id)
        else:
          mention_dic[meaning_id] = [[],[ex_id]]

    with open(os.path.join(output_directory,'%s_%s_lexicon.txt'%(source_language,target_language)),'w') as f_out:
      
      mm=0

      print('Step3')
      for key, onepair in mention_dic.items():
        t1=[]
        t2=[]
        for one_1 in onepair[0]:
          t1.append(ll[one_1])
        for one_1 in onepair[1]:
          t2.append(hl[one_1])
        if t1 != [] and t2 != []:
          mm+=1
          for ile in t1:
            for hle in t2:
              f_out.write('%s\t%s\n'%(ile,hle))

  print(mm)

if __name__=="__main__":
  parser = argparse.ArgumentParser(description='Extracting bi-lingual lexicion from Panlex')
  parser.add_argument('--source_language', default='', help='3-digit language code for source language')
  parser.add_argument('--target_language', default='eng', help='3-digit language code for target language')
  parser.add_argument('--output_directory', default='data/lexicons/', help='path of the folder to save the extracted lexicon')
  parser.add_argument('--sql_database', default='data/panlex.db', help='path of processed sqlite database of panlex')
  args = parser.parse_args()

  if not os.path.exists(args.output_directory):
    os.mkdir(args.output_directory)

  extract_bilingual_lexicon(args.source_language, args.target_language, args.output_directory, args.sql_database)

  print("Extraction complated")