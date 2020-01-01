
##################################################################################################
# The purpose of this code is to do the following:
# 1. Calculate the conceptual density of the user stories that were generated by SimpleNLG. These Metrics
# will be used to compare against the conceptual density of the original user storiesself.
# 2. To calculate the semantic similarity between the original user story inputs and their respective SimpleNLG outputs.
# 3. To create a QFD Report (in excel) that summarizes (1), (2) into a readable format for the user. The report will provide
# provide traceability between the inputs and  outputs, identify potential duplicate user stories, and group user stories by key
# elements to give insight to the user into the completeness of the user story set.
##################################################################################################

#for writing to Excel
import openpyxl
from openpyxl import Workbook
#from openpyxl.compat import range
from openpyxl.utils import get_column_letter
import xlsxwriter

#for dataframe operations
import pandas as pd
import numpy as np
import re
import itertools

# for writing / reading from Excel
from xlutils.copy import copy
import xlrd
import xlwt

from collections import Counter

import spacy
nlp = spacy.load('en_core_web_lg')

from itertools import chain
from itertools import combinations

#NLTK tokenizer and POS tagger
import nltk
#nltk.download()
from nltk import word_tokenize, sent_tokenize
from nltk import pos_tag, pos_tag_sents
from nltk.corpus import wordnet
from nltk import RegexpParser
from nltk.stem.wordnet import WordNetLemmatizer

#Get thresholds for QFD report
# import sys
# ambig_threshold = float(sys.argv[1])
# CD_threshold = float(sys.argv[2])
# dup_threshold = float(sys.argv[3])

ambig_threshold = .75
CD_threshold = .75
dup_threshold = .9

file = 'StoryLine_Outputs.xls'
df_revised_inputs = pd.read_excel(file, encoding = 'utf-8')

simpleNLG_outputs = 'SimpleNLG_Outputs.xls'
df_simpleNLG_outputs= pd.read_excel(simpleNLG_outputs, encoding = 'utf-8')

df_simpleNLG_outputs['StoryLine Revised US']  = df_simpleNLG_outputs['StoryLine Revised US'] .str.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u'\u201d', '"')

simpleNLG_inputs = 'StoryLine_to_SimpleNLG.xls'
df_simpleNLG_inputs= pd.read_excel(simpleNLG_inputs, encoding = 'utf-8')

pairwise_semsim_results = 'Pairwise_SemSim.xlsx'
df_pairwise_semsim = pd.read_excel(pairwise_semsim_results, encoding = 'utf-8')

# ###############################Output Metrics##################################

# #----------------------SemSim- Inputs and Outputs 1:1------------------------#
# for index, row in df_simpleNLG_outputs.iterrows():
    # doca = nlp(df_revised_inputs.loc[index,'Revised US'])
    # docb = nlp(df_simpleNLG_outputs.loc[index,'StoryLine Revised US'])
    # df_simpleNLG_outputs.loc[index,'Semantic Similarity'] = docb.similarity(doca)
    # #print(doca.similarity(docb))

df_simpleNLG_outputs_to_excel = pd.DataFrame()
df_simpleNLG_outputs_to_excel['Revised US'] = df_revised_inputs['Revised US'].copy()
df_simpleNLG_outputs_to_excel['StoryLine Revised US'] = df_simpleNLG_outputs['StoryLine Revised US'].copy()
# df_simpleNLG_outputs_to_excel['Semantic Similarity'] = df_simpleNLG_outputs['Semantic Similarity'].copy()

#---------------------------------SemSim- Pairwise between Outputs---------------------------#
# Note to reader - due to performance issues, the calculation of pairwise semantic similarity between US
# has been moved to RoboReq-Pairwise_SemSim.py. This script takes a while to run, so performance enhancements are
# encouraged.

# The results of this script are read into this Python script for use in the QFD Report.
#
# df_pairwise_semsim_overthresold = pd.DataFrame()
# for index, row in df_pairwise_semsim.iterrows():
    # if df_pairwise_semsim.loc[index,'Pairwise SemSim Score']>= dup_threshold:
        # df_pairwise_semsim_overthresold.loc[index,'US1'] = df_pairwise_semsim.loc[index,'Output US1']
        # df_pairwise_semsim_overthresold.loc[index,'US2'] = df_pairwise_semsim.loc[index,'Output US2']
        # df_pairwise_semsim_overthresold.loc[index,'Similarity Score'] = df_pairwise_semsim.loc[index,'Pairwise SemSim Score']

# -----------------------Compounds-------------------------------------------------#
# count_compounds = []
# count_split = []
# df_simpleNLG_inputs = df_simpleNLG_inputs.fillna('')
# for index, rows in df_simpleNLG_inputs.iterrows():
#     if df_simpleNLG_inputs.loc[index, 'Orig_US_ID']!='':
#         count_split.append(1)
# #print(len(count_split))
#
# count_compounds = df_simpleNLG_inputs.Orig_US_ID.nunique()
# #print(df_simpleNLG_inputs.Orig_US_ID.nunique(), count_compounds)

# -----------------------SpaCy NLP processing - for CD of results------------------#

docs_df_revised_inputs = df_revised_inputs['Revised US'].tolist()
doc_inputs = nlp.pipe(docs_df_revised_inputs)

tokens_inputs = []
pos_inputs = []
dep_inputs = []
tag_inputs = []

for doc in doc_inputs:
    if doc.is_parsed:
        tokens_inputs.append([n.text for n in doc])
        pos_inputs.append([n.pos_ for n in doc])
        dep_inputs.append([n.dep_ for n in doc])
        tag_inputs.append([n.tag_ for n in doc])

    else:
        tokens_inputs.append(None)
        pos_inputs.append(None)
        dep_inputs.append(None)
        tag_inputs.append(None)

df_revised_inputs['tokens_inputs'] = tokens_inputs
df_revised_inputs['pos_inputs'] = pos_inputs
df_revised_inputs['dep_inputs'] = dep_inputs
df_revised_inputs['tag_inputs'] = tag_inputs

# #--------------------------- Outputs: Conceptual Density-------------------------------#
#
# #Notes from :Robeer, M., Lucassen, G., van der Werf, J. M. E., Dalpiaz, F.,
# #& Brinkkemper, S. (2016, September). Automated extraction of conceptual models
# #from user stories via NLP. In Requirements engineering conference (RE), 2016 IEEE 24th international (pp. 196-205). IEEE.
#
# # concepts include:
# # 1. nouns,
# # 2. common nouns (disregarding Proper Nouns),
# # 3. sentence subjects,
# # 4. compound nouns (of length 2) and
# # 5. gerunds
#
# # relationships include:
# # 1. verbs,
# # 2. transitive verbs,
# # 3. linking verbs,
# # 4. compound nouns (relationship between two nouns)
#
# #Constant - num_tmpl
tmpl = "As a <type of user>, I want <some goal>, so that <some reason>"

char=0
num_tmpl=1
for i in tmpl:
      char=char+1
      if(i==' '):
            num_tmpl=num_tmpl+1

#Finding Nouns (includes class of common nouns)
nouns_CD = []
for index, row in df_revised_inputs.iterrows():
    #print(len(df_simpleNLG_outputs.loc[index,'tokens_inputs']))
    for i in range(0,len(df_revised_inputs.loc[index,'tokens_inputs'])):
        if df_revised_inputs.loc[index,'pos_inputs'][i] == 'NOUN' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'nsubj' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'csubj' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'compound' :
             nouns_CD.append('Y')
        else:
            nouns_CD.append(None)

# #Finding non-subject, proper nouns

propernouns_CD = []
for index, row in df_revised_inputs.iterrows():
    #print(len(df_simpleNLG_outputs.loc[index,'tokens_inputs']))
    for i in range(0,len(df_revised_inputs.loc[index,'tokens_inputs'])):
        if df_revised_inputs.loc[index,'pos_inputs'][i] == 'PROPN' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'nsubj' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'csubj' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'compound':
            propernouns_CD.append('Y')
        else:
            propernouns_CD.append(None)

#Finding subjects
subjects_CD = []
for index, row in df_revised_inputs.iterrows():
    #print(len(df_simpleNLG_outputs.loc[index,'tokens_inputs']))
    for i in range(0,len(df_revised_inputs.loc[index,'tokens_inputs'])):
        if df_revised_inputs.loc[index,'dep_inputs'][i] == 'nsubj' or df_revised_inputs.loc[index,'dep_inputs'][i] == 'csubj':
            subjects_CD.append('Y')
        else:
            subjects_CD.append(None)

#Finding compound Nouns (will exclude phrases like '$1 billion dollars')

compounds_CD = []
for index, row in df_revised_inputs.iterrows():
    #print(len(df_simpleNLG_outputs.loc[index,'tokens_inputs']))
    for i in range(0,len(df_revised_inputs.loc[index,'tokens_inputs'])):
        if df_revised_inputs.loc[index,'dep_inputs'][i]=='compound' and (df_revised_inputs.loc[index,'pos_inputs'][i] == 'NOUN' or df_revised_inputs.loc[index,'pos_inputs'][i] == 'PROPN'):
            compounds_CD.append('Y')
        else:
            compounds_CD.append(None)

#Finding gerunds
# # #Note: as per Penn Treebank tag_inputs Set, gerunds can be tag_inputsged as "VBG" when used as a verb
# # #However, do not want to double count as subject or verb below, so must discount for those cases.
# #
# # #Note: noun gerunds labeled as "Noun" by Spacy, though they end in 'ing' by defintiion and are caught in  sub_noun above

gerunds_CD = []
for index, row in df_revised_inputs.iterrows():
    #print(len(df_simpleNLG_outputs.loc[index,'tokens_inputs']))
    for i in range(0,len(df_revised_inputs.loc[index,'tokens_inputs'])):
        if df_revised_inputs.loc[index,'tag_inputs'][i]=='VBG' and (df_revised_inputs.loc[index,'dep_inputs'][i] != 'nsubj' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'csubj' and df_revised_inputs.loc[index,'dep_inputs'][i] != 'compound'):
            gerunds_CD.append('Y')
        else:
            gerunds_CD.append(None)

#Finding verbs:
verbs_CD = []
for index, row in df_revised_inputs.iterrows():
    #print(len(df_simpleNLG_outputs.loc[index,'tokens_inputs']))
    for i in range(0,len(df_revised_inputs.loc[index,'tokens_inputs'])):
        if df_revised_inputs.loc[index,'pos_inputs'][i]=='VERB' and df_revised_inputs.loc[index,'tag_inputs'][i] != 'VBG':
            verbs_CD.append('Y')
        else:
            verbs_CD.append(None)

#Dividing lists by dataframe size so can calculate CD per Revised uS:

chunks_nouns = []
chunks_verbs = []
chunks_compounds = []
chunks_gerunds = []
chunks_propernouns = []
chunks_subjects = []

step = []
for index, row in df_revised_inputs.iterrows():
    step.append(len(df_revised_inputs.loc[index,'tokens_inputs']))

# splitting subjects,...., by length of DF rows
stepz = []
start = []
stepz = [sum(step[:y]) for y in range(1, len(step) + 1)]
start = [m - n for m,n in zip(stepz,step)]

for i in range(0,len(stepz)):
      chunks_nouns.append(nouns_CD[start[i]:stepz[i]])
      chunks_verbs.append(verbs_CD[start[i]:stepz[i]])
      chunks_compounds.append(compounds_CD[start[i]:stepz[i]])
      chunks_gerunds.append(gerunds_CD[start[i]:stepz[i]])
      chunks_propernouns.append(propernouns_CD[start[i]:stepz[i]])
      chunks_subjects.append(subjects_CD[start[i]:stepz[i]])

df_conceptual_density_output = pd.DataFrame(
    {'verbs_CD': chunks_verbs,
     'nouns_CD': chunks_nouns,
     'compounds_CD': chunks_compounds,
     'gerunds_CD': chunks_gerunds,
     'propernouns_CD': chunks_propernouns,
     'subjects_CD': chunks_subjects
    })

#calculating num_word and tallying results
df_conceptual_density_output['n_word'] = df_revised_inputs['Original US'].str.split().str.len()
def count_Y(s):
    return s.count('Y')

df_conceptual_density_output['noun_count'] = df_conceptual_density_output['nouns_CD'].apply(count_Y)
df_conceptual_density_output['propernoun_count'] = df_conceptual_density_output['propernouns_CD'].apply(count_Y)
df_conceptual_density_output['subject_count'] = df_conceptual_density_output['subjects_CD'].apply(count_Y)
df_conceptual_density_output['gerund_count'] = df_conceptual_density_output['gerunds_CD'].apply(count_Y)
df_conceptual_density_output['compound_count'] = df_conceptual_density_output['compounds_CD'].apply(count_Y)
df_conceptual_density_output['verb_count'] = df_conceptual_density_output['verbs_CD'].apply(count_Y)

# #------A: Entity Density (rho_entity) [see Lucassen reference above]
# # rho_ent = num_ent / (num_word - num_tmpl)
# # where num_ent = sum (#entities above) / (# words in sentence - num words in user story template)
# num_ent = noun_count + propernoun_count + subject_count + compound_count + gerund_count
# rho_ent = num_ent / (num_word - num_tmpl)

df_conceptual_density_output['n_word - num_tmpl'] = df_conceptual_density_output['n_word'] - num_tmpl
df_conceptual_density_output['num_ent'] = df_conceptual_density_output['noun_count'] + df_conceptual_density_output['compound_count'] + df_conceptual_density_output['propernoun_count'] + df_conceptual_density_output['gerund_count'] + df_conceptual_density_output['subject_count']
df_conceptual_density_output['rho_ent'] = df_conceptual_density_output['num_ent'] / df_conceptual_density_output['n_word - num_tmpl']

# #------B: Relationship Density (rho_rel) [see Lucassen reference above]
# #rho_rel = num_rel / (num_word - num_tmpl)
# # where num_rel = sum (#relationships above) / (# words in sentence - num words in user story template)
#
# num_rel = sub_verb_count + sub_compound_count
# rho_rel =  num_rel / (num_word - num_tmpl)
#
df_conceptual_density_output['num_rel'] = df_conceptual_density_output['verb_count'] + df_conceptual_density_output['compound_count']
df_conceptual_density_output['rho_rel'] = df_conceptual_density_output['num_rel'] / df_conceptual_density_output['n_word - num_tmpl']

# #------C: Concept Density (rho_conc) [see Lucassen reference above]
# #rho_conc = rho_ent + rho_rel

#if n_word = num_tmpl or if rho_conc < 0, set rho_conc = 0
df_conceptual_density_output['rho_conc'] = df_conceptual_density_output['rho_ent'] + df_conceptual_density_output['rho_rel']
#

for index, row in df_conceptual_density_output.iterrows():
    if df_conceptual_density_output.loc[index, 'rho_conc'] < 0:
       df_conceptual_density_output.loc[index, 'rho_conc'] = 0
    elif df_conceptual_density_output.loc[index,'n_word - num_tmpl'] == 0:
        df_conceptual_density_output.loc[index, 'rho_conc'] = 0

#normalizing CD
max_CD = max(df_conceptual_density_output['rho_conc'])
min_CD = min(df_conceptual_density_output['rho_conc'])
diff = 0
diff = max_CD - min_CD
for index, row in df_conceptual_density_output.iterrows():
    df_conceptual_density_output.loc[index, 'rho_conc_norm'] = ((df_conceptual_density_output.loc[index, 'rho_conc']) - min_CD) /diff


#Preparing for printed outputs
df_conceptual_density_output_to_excel = pd.DataFrame()
df_conceptual_density_output['Original US'] = df_revised_inputs['Original US'].copy()
df_conceptual_density_output_to_excel['n_word'] = df_conceptual_density_output['n_word'].copy()
df_conceptual_density_output_to_excel = df_conceptual_density_output[['Original US', 'n_word', 'rho_conc_norm']]
#
midCD_threshold = CD_threshold-CD_threshold*0.5
for index, row in df_conceptual_density_output_to_excel.iterrows():
    if df_conceptual_density_output_to_excel.loc[index, 'rho_conc_norm'] >= CD_threshold:
        df_conceptual_density_output_to_excel.loc[index, 'CD Level'] = '3'
    elif df_conceptual_density_output_to_excel.loc[index, 'rho_conc_norm'] < CD_threshold and df_conceptual_density_output_to_excel.loc[index, 'rho_conc_norm'] >= midCD_threshold:
        df_conceptual_density_output_to_excel.loc[index, 'CD Level'] = '2'
    else:
        df_conceptual_density_output_to_excel.loc[index, 'CD Level'] = '1'

#
high_CD = []
med_CD = []
low_CD = []
for index, row in df_conceptual_density_output_to_excel.iterrows():
    if df_conceptual_density_output_to_excel.loc[index, 'CD Level'] == '3':
        high_CD.append(1)
    elif df_conceptual_density_output_to_excel.loc[index, 'CD Level'] == '2':
        med_CD.append(1)
    else:
        low_CD.append(1)

df_conceptual_density_output_to_excel['CD Level'] = df_conceptual_density_output_to_excel['CD Level'].str.replace('3', "HIGH")
df_conceptual_density_output_to_excel['CD Level'] = df_conceptual_density_output_to_excel['CD Level'].str.replace('2', "MED")
df_conceptual_density_output_to_excel['CD Level'] = df_conceptual_density_output_to_excel['CD Level'].str.replace('1', "LOW")


#------------------ Ambiguity Measurements -------------------------------------------------
# The following code measures the lexical and syntactic (semantic) ambiguity of user inputs disgusting
# four metrics, labelled A1, A2, B1, and B2 below.
# Source for equations:
    # Kiyavitskaya, N., Zeni, N., Mich, L., & Berry, D. M. (2008). Requirements for tools for ambiguity identification and
    # measurement in natural language requirements specifications. Requirements engineering, 13(3), 207-239.

#A. Lexical Ambiguity of Inputs----------------------------------------------------------#
df_ambig = pd.DataFrame()
#df_revised_inputs['tokens_inputs'] = df_revised_inputs['tokens_inputs'].str.lower()
df_ambig['tokenized_text'] = df_revised_inputs['tokens_inputs'].copy()

for index, row in df_ambig.iterrows():
    for i in range(0, len(df_ambig.loc[index,'tokenized_text'])):
        df_ambig.loc[index,'tokenized_text'][0] = df_ambig.loc[index,'tokenized_text'][0].lower()

#removing stop words
df_ambig['filtered_tokens'] = df_ambig['tokenized_text'].copy()

#finding # of meanings per word per sentence
def first(wordlist):
    # wordlist is a list of words, i.e. ['sun', 'shine', 'spotless']
    return [wordnet.synsets(word) for word in wordlist]

df_ambig['syn'] = df_ambig['filtered_tokens'].apply(first)

df_ambig_sent = pd.DataFrame(list(map(lambda d: list(chain.from_iterable(d)), df_ambig['syn'])))

#A1. lexical ambiguity per word per sentence
def lexwordambig(wordlist):
    lengths = []
    for x in wordlist:
        lengths.append(len(x))
    return lengths
df_ambig['Lexical Ambiguity per Word'] = df_ambig['syn'].apply(lexwordambig)

print(df_ambig['Lexical Ambiguity per Word'][700:715])

print(df_ambig['filtered_tokens'][700:715])


def round_robin(first, second):
    return[item for items in zip(first, second) for item in items]

df_ambig['Lexical Ambiguity per Word'] = df_ambig.apply(lambda x: round_robin(x['filtered_tokens'], x['Lexical Ambiguity per Word']), axis=1)

#A2. lexical ambiguity per sentence

def foo(l1):
    return sum(filter(lambda i: isinstance(i, int), l1))
    

df_ambig_sent['Sentence Lexical Ambiguity']= df_ambig['Lexical Ambiguity per Word'].apply(foo)

# syns = wordnet.synsets("complaint")
# print(syns[3].name())
# print(syns[3].definition())
# print(syns[4].name())
# print(syns[4].definition())

#combining results of A1 and A2 above to print to excel
df_ambig_to_excel = pd.DataFrame()
df_ambig_to_excel = df_ambig[['syn','Lexical Ambiguity per Word']].copy()
df_ambig_to_excel['Original US'] = df_revised_inputs['Original US'].copy()
df_ambig_to_excel['Sentence Lexical Ambiguity'] = df_ambig_sent['Sentence Lexical Ambiguity'].copy()
df_ambig_to_excel = df_ambig_to_excel[['syn', 'Lexical Ambiguity per Word', 'Sentence Lexical Ambiguity']]

#normalizing LexAmbigSent
max_lex = max(df_ambig_to_excel['Sentence Lexical Ambiguity'])
min_lex = min(df_ambig_to_excel['Sentence Lexical Ambiguity'])
diff = 0
diff = max_lex - min_lex
for index, row in df_ambig_to_excel.iterrows():
    df_ambig_to_excel.loc[index, 'LexAmbigSentNorm'] = ((df_ambig_to_excel.loc[index, 'Sentence Lexical Ambiguity']) - min_lex) /diff

midambig_threshold = ambig_threshold-ambig_threshold*0.5
for index, row in df_ambig_to_excel.iterrows():
    if df_ambig_to_excel.loc[index, 'LexAmbigSentNorm'] >= ambig_threshold:
        df_ambig_to_excel.loc[index, 'Sentence LexAmbig Level'] = '3'
    elif df_ambig_to_excel.loc[index, 'LexAmbigSentNorm'] < ambig_threshold and df_ambig_to_excel.loc[index, 'LexAmbigSentNorm'] >= midambig_threshold:
        df_ambig_to_excel.loc[index, 'Sentence LexAmbig Level'] = '2'
    else:
        df_ambig_to_excel.loc[index, 'Sentence LexAmbig Level'] = '1'
#
high_lexambig = []
med_lexambig = []
low_lexambig = []
for index, row in df_ambig_to_excel.iterrows():
    if df_ambig_to_excel.loc[index, 'Sentence LexAmbig Level'] == '3':
        high_lexambig.append(1)
    elif df_ambig_to_excel.loc[index, 'Sentence LexAmbig Level'] == '2':
        med_lexambig.append(1)
    else:
        low_lexambig.append(1)

# df_ambig_to_excel['Sentence LexAmbig Level'] = df_ambig_to_excel['Sentence LexAmbig Level'].str.replace('3', "HIGH")
# df_ambig_to_excel['Sentence LexAmbig Level'] = df_ambig_to_excel['Sentence LexAmbig Level'].str.replace('2', "MED")
# df_ambig_to_excel['Sentence LexAmbig Level'] = df_ambig_to_excel['Sentence LexAmbig Level'].str.replace('1', "LOW")
# #
#B. Syntactic Ambiguity of Inputs----------------------------------------------------------#

#B1. syntactic ambiguity of a word (# of POS per word)

def count_by_syntype(wordlist): #runs counts of synsets by POS type (7 noun, 2 verb synsets)
    counts=[]
    for word in wordlist:
        counts.append(Counter([ss.pos() for ss in wordnet.synsets(word)]))
    return counts

df_ambig['syn_set'] = df_ambig['filtered_tokens'].apply(count_by_syntype)

def count_pos(synsetcount): #returns counts of distinct POS (7 noun, 2 verb synsets = 2 POS)
    count_POS=[]
    for syn in synsetcount:
        count_POS.append(len(syn))
    return count_POS
df_ambig['Syntactic Ambiguity per Word'] = df_ambig['syn_set'].apply(count_pos)
df_ambig['Syntactic Ambiguity per Word'] = df_ambig.apply(lambda x: round_robin(x['filtered_tokens'], x['Syntactic Ambiguity per Word']), axis=1)

#combining results of B1 to results of A above to print to excel
df_ambig_to_excel['Syntactic Ambiguity per Word'] = df_ambig['Syntactic Ambiguity per Word'].copy()

#B2. syntactic ambiguity of a sentence (delta(S)) - count of sentence parse trees
# computed using: https://www.link.cs.cmu.edu/cgi-bin/link/construct-page-4.cgi#submit

# number of  US per distinct role-------------------------------------------------------------------------
role_phrase_count = df_simpleNLG_inputs['role_phrase'].value_counts().sort_values(ascending=[False])

missing_role_count =  df_simpleNLG_inputs[df_simpleNLG_inputs['role_phrase'] == 'As a default role'].count()
missing_benefit_count =  df_simpleNLG_inputs[df_simpleNLG_inputs['benefit_phrase'] == 'so that default end'].count()

missing_role_count = missing_role_count[1]
missing_benefit_count = missing_benefit_count[2]

grouped = df_simpleNLG_inputs.groupby('role_phrase')
rolecount = grouped.agg(np.size)

#
# for name,group in grouped:
#    print (name)
#    print (group)
# ############################### outputs + QFD to Excel#########################

writer = pd.ExcelWriter('StoryLine QFD Report.xlsx', engine='xlsxwriter')
workbook  = writer.book
worksheet = workbook.add_worksheet('QFD Report Summary')
bold = workbook.add_format({'bold': True})
italics = workbook.add_format({'italic': True})

df_revised_inputs['Original US'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol= 0, startrow = 10)
df_revised_inputs['Supplementary Notes'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol= 2, startrow = 10,index=False)
df_revised_inputs['Acronyms'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol= 3, startrow = 10,index=False)
df_revised_inputs['Misspelled Words'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol= 4, startrow = 10,index=False)

df_revised_inputs['Input Completeness Indicator'] = df_revised_inputs['Completeness']
df_revised_inputs['Input Completeness Indicator'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol= 5, startrow = 10,index=False)
df_simpleNLG_outputs_to_excel['StoryLine Revised US'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol= 6, startrow = 10,index=False)

df_conceptual_density_output['US Length'] = df_conceptual_density_output['n_word']

df_conceptual_density_output['US Length'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol = 7, startrow = 10,index=False)

#df_conceptual_density_output_to_excel['CD Level'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol = 8, startrow = 10,index=False)
df_conceptual_density_output['CD Score'] = df_conceptual_density_output['rho_conc_norm']
df_conceptual_density_output['CD Score'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol = 9, startrow = 10,index=False)

#df_ambig_to_excel['Sentence Lexical Ambiguity Level'] = df_ambig_to_excel['Sentence LexAmbig Level']
#df_ambig_to_excel['Sentence Lexical Ambiguity  Level'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol = 10, startrow = 10,index=False)
df_ambig_to_excel['Lexical Ambiguity Score'] = df_ambig_to_excel['LexAmbigSentNorm']
df_ambig_to_excel['Lexical Ambiguity Score'].to_excel(writer, sheet_name='Inputs, Outputs, and Metrics', startcol = 11, startrow = 10,index=False)

worksheet_summary = writer.sheets['Inputs, Outputs, and Metrics']

text_intro1 = 'This table below provides traceability between user stories input into StoryLine (Original US) and the resulting user stories with QUS defects removed (StoryLine Revised US).'
worksheet_summary.write(1, 0, text_intro1, bold)
b1 = 'The table also provides the following key metrics to aid with further requirements analysis and validation: '
worksheet_summary.write(2, 0, b1, bold)
b2 = "1. Input Completeness Indicator - 'Yes' if user story contains both a noun and verb, representing a complete sentence. 'No' otherwise."
worksheet_summary.write(3, 0, b2, bold)
b3 = "2. US Length - Number of words in the StoryLine Revised US."
worksheet_summary.write(4, 0, b3, bold)
b4 = "3. Conceptual Density (CD) Level - 'HIGH' if normalized CD is greater or equal to the user provided threshold: " + str(CD_threshold) + "'MED' if normalized CD is between the user provided threshold and half of the same threshold; LOW otherwise."
worksheet_summary.write(5, 0, b4, bold)
b5 = "4. Conceptual Density Score - The normalized CD score for each 'Original US'."
worksheet_summary.write(6, 0, b5, bold)
b6 = "5. Sentence Lexical Ambiguity Level -'HIGH' if normalized ambiguity is greater or equal to the user provided threshold: " + str(ambig_threshold) + "'MED' if normalized CD is between the user provided threshold and half of the same threshold; 'LOW' otherwise."
worksheet_summary.write(7, 0, b6, bold)
b7 = "6. Sentence Lexical Ambiguity Score - The normalized lexical ambiguity score for each 'Original US'."
worksheet_summary.write(8, 0, b7, bold)


### Add Summary / Description for QFD report

text = 'Congratulations! Your RoboReq Quality Function Deployment (QFD) Report is ready for your review.'
worksheet.write(0, 0, text, bold)

#insert summary text and QFD diagram:
worksheet.insert_image('A4', 'qfd.png',{'x_scale': 0.55, 'y_scale': 0.55})
text_intro = 'This is a summary of how to use this workbook.'
worksheet.write(1, 0, text_intro, bold)

### Summary Statistics
worksheet.write(18, 0, "Summary Statistics", bold)
worksheet.write(19, 0, "Total User Story Count", italics)
worksheet.write(19, 1, len(df_simpleNLG_outputs_to_excel['Revised US']), italics)
worksheet.write(20, 0, "Count of Missing Roles", italics)
worksheet.write(20, 1, missing_role_count, italics)
worksheet.write(21, 0, "Count of Missing Benefits", italics)
worksheet.write(21, 1, missing_benefit_count, italics)
worksheet.write(22, 0, "Count of Compound User Stories(and/or)", italics)
#worksheet.write(22, 1, count_compounds, italics)
#worksheet.write(23, 0, "Count of Split User Stories(and/or)", italics)
#worksheet.write(23, 1, len(count_split), italics)
#
worksheet.write(25, 0, "Distribution of Conceptual Density (CD) Scores", bold)
worksheet.write(26, 0, "HIGH" , italics)
worksheet.write(26, 1,  str(len(high_CD)), italics)
worksheet.write(27, 0, "MED", italics)
worksheet.write(27, 1, str(len(med_CD)), italics)
worksheet.write(28, 0, "LOW", italics)
worksheet.write(28, 1,  str(len(low_CD)), italics)

worksheet.write(30, 0, "Distribution of Sentence Lexical Ambiguity Scores", bold)
worksheet.write(31, 0, "HIGH" , italics)
worksheet.write(31, 1,  str(len(high_lexambig)), italics)
worksheet.write(32, 0, "MED", italics)
worksheet.write(32, 1, str(len(med_lexambig)), italics)
worksheet.write(33, 0, "LOW", italics)
worksheet.write(33, 1,  str(len(low_lexambig)), italics)


### Conditional Formatting for CD and ambiguity-------------------------

# Add a format. Light red fill with dark red text.
format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#006100'})

# Add a format. Green fill with dark green text.
format2 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})

format3 = workbook.add_format({'bg_color': '#FFFF00',
                               'font_color': '#006100'})

# # color formatting of CD level and LexAmbig Level
worksheet_summary.conditional_format('I3:I846', {'type':     'cell',
                                        'criteria': '==',
                                        'value': "HIGH",
                                        'format':   format1})

worksheet_summary.conditional_format('I3:I846', {'type':     'cell',
                                        'criteria': '==',
                                        'value': "MED",
                                        'format':   format2})

worksheet_summary.conditional_format('I3:I846', {'type':     'cell',
                                        'criteria': '==',
                                        'value': "LOW",
                                        'format':   format3})

worksheet_summary.conditional_format('K3:K846', {'type':     'cell',
                                        'criteria': '==',
                                        'value': "HIGH",
                                        'format':   format1})

worksheet_summary.conditional_format('K3:K846', {'type':     'cell',
                                        'criteria': '==',
                                        'value': "MED",
                                        'format':   format2})

worksheet_summary.conditional_format('K3:K846', {'type':     'cell',
                                        'criteria': '==',
                                        'value': "LOW",
                                        'format':   format3})
# format CD and Ambiguity as %
percent_fmt = workbook.add_format({'num_format': '0%'})
worksheet_summary.set_column('E3:E846', None, percent_fmt)
worksheet_summary.set_column('F3:F836', None, percent_fmt)

#-----Role Coverage Report--------------------------------------
# number of US by distinct role
worksheet_coverage = workbook.add_worksheet('Role Coverage Matrix')
worksheet_coverage.write(0, 0, "Summary", bold)
text_roleintro = 'The following table provides a matrix of user story roles to means. Please review this matrix to ensure a). all user role types are presented and b). all required functions per user role is adequately presented.'
worksheet_coverage.write(1, 0, text_roleintro, bold)

#worksheet.write(3, 1, rolecount, italics)

# full Coverage matrix


#----Duplication Report--------------------------------------------

# df_pairwise_semsim_overthresold['US1'].to_excel(writer, sheet_name='Similarity Report', startcol= 0, startrow = 2)
# df_pairwise_semsim_overthresold['US2'].to_excel(writer, sheet_name='Similarity Report', startcol= 1, startrow = 2,index=False)
# df_pairwise_semsim_overthresold['Similarity Score'].to_excel(writer, sheet_name='Similarity Report', startcol= 2, startrow = 2,index=False)
# worksheet_sim = writer.sheets['Similarity Report']
# text_dupintro = 'User story pairs with similarity scores ' + str(dup_threshold) + ' over are presented below. Please review this list for potential dependencies or duplication between user stories.'
# worksheet_sim.write(1, 0, text_dupintro, bold)

#CD, Sim and Lex as %
percent_fmt = workbook.add_format({'num_format': '0%'})
worksheet_summary.set_column('J3:J846', None, percent_fmt)
worksheet_summary.set_column('L3:L836', None, percent_fmt)
