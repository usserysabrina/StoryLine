##################################################################################################
##################################################################################################
##################### Ussery, Sabrina Dissertation Research 2018 #################################

#The goal of the program is to read in user stories from a file, split them where necessary,
#analyze their structure, and prepare them for re-generation via SimpleNLG to improve their quality.

#Working Dataframes:
# df
# df2
# df_ambig
# df_ambig_sent
# df_Acronyms_all
# df_conceptual_density
# df4
# df_to_SimpleNLG

#Output (to Excel) dataframes:
# df3
# df_Acronyms_Final - list of acronyms found in input requirements
# df_ambig_to_excel - lexical ambiguity metrics
# df_conceptual_density_to_excel
# df_to_SimpleNLG_final
# df_to_SimpleNLG_final_FINAL
# df_ambig_to_excel_new
# df_conceptual_density_to_excel_new

##################################################################################################
##################################################################################################

#NLTK tokenizer and POS tagger
from nltk import word_tokenize, sent_tokenize
from nltk import pos_tag, pos_tag_sents
from nltk.corpus import wordnet
from nltk import RegexpParser
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import ChartParser
from nltk import CFG

#for writing to Excel
import openpyxl
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter

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
nlp = spacy.load('en')

from itertools import chain
from itertools import combinations

import pygame
from pygame import mixer

# file = 'Jeopardy-theme-song.mp3'
# mixer.init()
# mixer.music.load(file)
# mixer.music.play()
# pygame.mixer.music.queue('next_song.mp3')

#------------------------Creates a "README" tab for users to aid in result interpretation------------#
#Model Intro and README

print("********************************************************************************")
print("Welcome to the RoboReq! \n\nThis tool will help you write quality User Stories that meet the criteria of both the Quality User Story(QUS) and INVEST frameworks.")

print("Upon finishing, the outputs of the tool will be stored in a 'RoboReq_Outputs.xlsx' file in the working directory for your use.\n")
print("Further details of the innerworkings of the tool can be found in the README tab of the output file.\n")
print("Please be reminded to name your input file as 'Requirements_Input.xlsx' and save it in the working directory prior to running the tool. Otherwise, the tool will fail to produce results.\n")

#Get thresholds for QFD report

#ambig_threshold = input ("For reporting purposes: At what percentage of potential requirement ambiguity would you like to be notified? (e.g., 50, 75, etc.)\n")
# if ambig_threshold <= 0 or ambig_threshold > 100:
#     print("Please enter a valid number between 0 and 100")
# #semsim_threshold = input ("For reporting purposes: At what percentage of potential requirement duplication would you like to be notified? (e.g., 50, 75, etc.)\n")
# if semsim_threshold <= 0 or semsim_threshold > 100:
#     print("Please enter a valid number between 0 and 100")

print("Thanks! Your requirements are cooking. Happy writing!")
print("********************************************************************************")

#for run time metrics
import time
from datetime import timedelta

start_time = time.time()
#################################################################################
#-----------------------Processing baseline Data-----------------------#
#save in working directory to prevent errors

#this code tokenizes and applies POS to each user story.

file = 'Requirements_Input.xlsx'
df = pd.read_excel(file, encoding = 'utf-8')

#################################################################################
#-----------------------------Splitting Multi-sentence US---------------------#
#When a User story has more than one sentence, this function will split all non-primary
# sentences and store them in a new column called "Supplementary Notes" that can be used in the user story's
# description, instead of in the primary user story itself.

#-------------------------Quotations and Commas- ------------------------------#
#This code removes quotations and commas from inputs so that linguistic outputs are easier to parse.

df['US'] = df['US'].str.replace('&',' and ')
df['US'] = df['US'].str.replace('|',' or ')
df['US'] = df['US'].str.replace(' and/or ',' or ')
df['US'] = df['US'].str.replace('/',' or ')
df['US']  = df['US'].str.replace('-',' ')
df['US']  = df['US'].str.replace(',','')
df['US']  = df['US'].str.replace('  ',' ')
df['US']  = df['US'].str.replace('etc.','etcetera')
df['US']  = df['US'].str.replace('10. 04.','10v04 ')
df['US'] = (df['US'].str.split()).str.join(' ')

def sent_split(US):
    try:
        sent_tokenize_list = sent_tokenize(US)
        return sent_tokenize_list
    except Exception as e:
        print(str(e))
df['sent_list'] = df['US'].apply(sent_split)

df2=pd.DataFrame(df.sent_list.values.tolist(), df.index).add_prefix('sent_')
df2.rename(columns = {'sent_0':'Revised US'}, inplace = True)
#If US has only one sentence, replace sentences 2 - 4 with a blank space instead of default 'None'.
df2.where(pd.notnull(df2), '', inplace=True)
#concatenate non-primary sentences and include them as Supplementary Notes to the primary US
df2['Supplementary Notes'] = df2['sent_1'].astype(str) + ' ' + df2['sent_2'].astype(str) + ' '  + df2['sent_3'].astype(str) + ' '  + df2['sent_4'].astype(str)

df3 = df2[['Revised US', 'Supplementary Notes']].copy()
df3['Original US'] = df['US'].copy()
df3 = df3[['Original US','Revised US','Supplementary Notes']]

#################################################################################
# #-----------------------------Removing Parenthetical Information-------------#
#When a User story contains Parenthetical information, this function will remove them
#information from the US text and store it in a new column called "Additional Notes" that
#can be used in the user story's description, instead of in the primary user story itself.

#this code will copy parenthetical or bracketed information, along with preceeding word for context,
#into dataframe for consideration by the user. This information is then removed from the US so that it
#satisfies QUS quality rules.

#extract data from between parentheses
df2['Parenthetical Info'] = df3['Revised US'].apply(lambda x: re.findall('\((.*?)\)',x))

# #extract word before parentheses for context
df2['Paren_Prefix_working'] = df3['Revised US'].str.split('(', 1)


#When length of df2['Parenthetical Prefix'] > 1, the input contained parentheses.
#Since split on opening parenthesis above, first item in each row's list is the part of the input before the parentheses.

for index, row in df2.iterrows():
    df2.loc[index,'Paren_Prefix_working_split'] = row['Paren_Prefix_working'][0]
df2['Paren_Prefix_working_split'] = df2['Paren_Prefix_working_split'].str.split()

for index, row in df2.iterrows():
    df2.loc[index,'Paren_Prefix_last_word'] = row['Paren_Prefix_working_split'][-1]

df2['Paren_Prefix_last_word'] = df2['Paren_Prefix_last_word'].str.strip('.')

#Only fill out Parenthetical Info if sentence actually contains parenthetical Information
#for index, row in df2.iterrows():
for index, row in df2.iterrows():
     if bool(df2.loc[index, 'Parenthetical Info']):
        df2.loc[index,'Final Paren'] = "\n\nExtracted Parenthetical Information:\n\n "+ df2.loc[index,'Paren_Prefix_last_word'] + " ("+df2.loc[index, 'Parenthetical Info'][0]+")"
     else:
        df2.loc[index,'Final Paren'] = None

for index, row in df2.iterrows():
     if bool(df2.loc[index, 'Final Paren']):
        df3.loc[index,'Supplementary Notes'] = df3.loc[index, 'Supplementary Notes'] + df2.loc[index,'Final Paren']

def remove_text_inside_paren(US, brackets="()[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    try:
        for character in US:
            for i, b in enumerate(brackets):
                if character == b: # found bracket
                    kind, is_close = divmod(i, 2)
                    count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                    if count[kind] < 0: # unbalanced bracket
                        count[kind] = 0  # keep it
                    else:  # found bracket to remove
                        break
            else: # character is not a [balanced] bracket
                if not any(count): # outside brackets
                    saved_chars.append(character)
        return ''.join(saved_chars)
    except Exception as e:
        print(str(e))

df3['Revised US'] = df3['Revised US'].apply(remove_text_inside_paren)

##Note: Spell checker to be included after tokenization.
#-----------------------------Fixing Contractions-------------------------------#
# This function replaces contractions with their full word equivalents so that tokenization, performed later,
# maintains the integrity of the user's inputs.

def decontracted(phrase):
    # specific
    phrase = re.sub(r"won't", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    #phrase = re.sub(r"\'s", " is", phrase) #seperates possession unncessarily
    phrase = re.sub(r"\'d", " would", phrase) #could be had as well
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase

df3['Revised US'] = df3['Revised US'].apply(decontracted)

#-----------------------------Phrase Replacement for Uniformity-----------------#
#replace "so" with "so that" for benefit extraction later.
for index, row in df3.iterrows():
    if "so " in df3.loc[index,'Revised US'] and " so that" not in df3.loc[index,'Revised US'] and " so on" not in df3.loc[index,'Revised US'] :
        df3.loc[index,'Revised US'] = df3.loc[index,'Revised US'].replace("so ", "so that ")

#may not be comprehensive, which may result in issues with finding benefits (depends on Prep phrase and comma placement)
df3['Revised US'] = df3['Revised US'].str.replace('I want',', I want')
df3['Revised US'] = df3['Revised US'].str.replace('I need',', I need')
df3['Revised US'] = df3['Revised US'].str.replace('I would like',', I would like')
df3['Revised US'] = df3['Revised US'].str.replace(' she would',', she would')
df3['Revised US'] = df3['Revised US'].str.replace('I can',', I can')
df3['Revised US'] = df3['Revised US'].str.replace('I should',', I should')
df3['Revised US'] = df3['Revised US'].str.replace('I am',', I am')
df3['Revised US'] = df3['Revised US'].str.replace('I like',', I like')
df3['Revised US'] = df3['Revised US'].str.replace('so that,','so that')
# lowercasing all user stories to minimize tagging errors
df3['Revised US'] = df3['Revised US'].apply(lambda x: x.lower())

#################################################################################
#-------------------------Natural Language Analysis ------------------------------#
# This code uses SpAcy to find the part of speech of each word in the user inputs as well as
# the dependency between the words in the inputs so that these requirements can be written according
# to QUS quality rules.

def tokenize(US):
    try:
        tokenized_text = word_tokenize(US)
        return tokenized_text
    except Exception as e:
        print(str(e))
df_ambig = pd.DataFrame()
df_ambig['tokenized_text'] = df3['Revised US'].apply(tokenize)


def POS_tagz(token):
    try:
        pos = pos_tag(token)
        return pos
    except Exception as e:
        print(str(e))
df['POS'] = df_ambig['tokenized_text'].apply(POS_tagz)


#-------------------Chunking: Finding Noun, Verb and Prep Phrases--------------#
# This section of code finds the noun, verb, and prepositional phrases in the input text using
# regular expressions and the English SVO model for declarative sentences described below:
#https://pythonprogramming.net/regular-expressions-regex-tutorial-python-3/
#http://www.cs.uccs.edu/~jkalita/work/cs589/2010/12Grammars.pdf

def chunker(pos):
    chunkGram =r"""
         NP:
             {<DT>?<JJ|JJR|VBN|VBG>*<CD><JJ|JJR|VBN|VBG>*<NNS|NN>+}
             {<DT>?<JJS><NNS|NN>?}
             {<DT>?<PRP|NN|NNS><POS><NN|NNP|NNS>*}
             {<DT>?<NNP>+<POS><NN|NNP|NNS>*}
             {<DT|PRP\$>?<RB>?<JJ|JJR|VBN|VBG>*<NN|NNP|NNS>+}
             {<DT><JJ>*<CD>}
             {<\$>?<CD>+}
         VP: {<MD>?<TO>?<VB.*><JJ>?<TO>?<VB.*>?<VBN>?}
         """
    try:
        chunkParser = RegexpParser(chunkGram)
        chunked = chunkParser.parse(pos)
        return chunked
    except Exception as e:
        print(str(e))

df2['chunks_all'] = df['POS'].apply(chunker)

# This function extracts all the noun, verb and prep phrases that meet the grammar conditions above
# so they can be outputted to an Excel file for further user
def extract_np(psent):
    NPs = list(psent.subtrees(filter=lambda x: x.label()=='NP'))
    return NPs

df['Noun Phrases'] = df2['chunks_all'].apply(extract_np)

def extract_vp(psent):
    VPs = list(psent.subtrees(filter=lambda x: x.label()=='VP'))
    return VPs

df['Verb Phrases'] = df2['chunks_all'].apply(extract_vp)

df4 = df[['POS', 'Noun Phrases', 'Verb Phrases']].copy()
df4['Revised US'] = df3['Revised US'].copy()
df4 = df4[['Revised US', 'POS', 'Noun Phrases', 'Verb Phrases']]

# -----------------------SpaCy Tagging and Dependency Analysis------------------#
docs = df4['Revised US'].tolist()
docz = nlp.pipe(docs)



tokens = []
pos = []
tag = []
dep = []
head = []
headpos = []
noun_phrases = []

for doc in docz:
    if doc.is_parsed:
        tokens.append([n.text for n in doc])
        pos.append([n.pos_ for n in doc])
        tag.append([n.tag_ for n in doc])
        dep.append([n.dep_ for n in doc])
        head.append([n.head.text for n in doc])
        headpos.append([n.head.pos_ for n in doc])
        noun_phrases.append([chunk.text for chunk in doc.noun_chunks])
    else:
        # We want to make sure that the lists of parsed results have the
        # same number of entries of the original Dataframe, so add some blanks in case the parse fails
        tokens.append(None)
        pos.append(None)
        tag.append(None)
        dep.append(None)
        head.append(None)
        headpos.append(None)
        noun_phrases.append(None)

df4['tokens'] = tokens
df4['pos'] = pos
df4['tag'] = tag
df4['dep'] = dep
df4['head'] = head
df4['head_pos'] = headpos
df4['noun_phrases'] = noun_phrases

# -----------------------Finding subjects--------------------------------------#
##Corresponds to the following inputs for SimpleNLG:
#1. p.setSubject (word)
#2. nlgFactory = createNounPhrase(word)

##NOTE: in later phases of this tool, these measures can be consolidated with those for CD as they are somewhat duplicative.
#dependency tags interpreted using this list: https://github.com/explosion/spaCy/issues/233

#
# sub_subjs = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if (df4.loc[index,'dep'][i] =='nsubj' or df4.loc[index,'dep'][i] =='csubj'):
#             sub_subjs.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_subjs.append(None)
#
# # -----------------------finding verbs-----------------------------------------#
# ##Corresponds to the following inputs for SimpleNLG:
# #1. p.setVerb (word)
# #2. nlgFactory = createVerbPhrase(word)
#
# sub_verbs = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if df4.loc[index,'dep'][i] == 'ROOT':
#              sub_verbs.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_verbs.append(None)
#
# # -----------------------finding objects---------------------------------------#
# ##Corresponds to the following inputs for SimpleNLG:
# #1. p.setObject(det + word)
#
# sub_objs = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if (df4.loc[index,'dep'][i] == 'dobj' or df4.loc[index,'dep'][i] == 'iobj' or df4.loc[index,'dep'][i] =='oprd'):
#              sub_objs.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_objs.append(None)
#
# # -----------------------finding Modifiers-------------------------------------#
# ##Corresponds to the following inputs for SimpleNLG:
# #1. subject.addModifier(adjective)
# #2. verb.addModifier(adverb);
# sub_adjs = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if (df4.loc[index,'dep'][i] == 'amod' or df4.loc[index,'pos'][i] =='ADJ'):
#              sub_adjs.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_adjs.append(None)
#
# sub_adverbs = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if (df4.loc[index,'dep'][i] == 'advmod' or df4.loc[index,'dep'][i] =='advcl' or df4.loc[index,'pos'][i] =='ADV') :
#              sub_adverbs.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_adverbs.append(None)
#
# # -----------------------finding prepositions / PP-----------------------------#
# ##Corresponds to the following inputs for SimpleNLG: (Note: unlike with Noun/Verb phrases, cannot explicitly attach PP in SimpleNLG)
# #1 p.addComplement("in the park")
# #2 pp = nlgFactory.createPrepositionPhrase(prep, noun phrase); p.addcomplement(pp)
#
# sub_prep = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if (df4.loc[index,'dep'][i] == 'prep' or df4.loc[index,'dep'][i] == 'pobj'):
#              sub_prep.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_prep.append(None)
#
# #-------------------------Finding Coordinating Conjunctions---------------------#
# # these sentences need to be split and replicated.
# sub_cc = []
# for index, row in df4.iterrows():
#     #print(len(df4.loc[index,'tokens']))
#     for i in range(0,len(df4.loc[index,'tokens'])):
#         if df4.loc[index,'dep'][i] == 'cc':
#              sub_cc.append(df4.loc[index,'tokens'][i])
#         else:
#             sub_cc.append(None)
#
#
# #dividing by width of dataframe so that outputs are per user story:
#
# subjects_SNLG = []
# verbs_SNLG = []
# adjectives_SNLG = []
# adverbs_SNLG = []
# prepositions_SNLG = []
# objects_SNLG = []
# conjunctions_to_split = []
#
step = []
for index, row in df4.iterrows():
    step.append(len(df4.loc[index,'tokens']))


# splitting subjects,...., by length of DF rows
stepz = []
start = []
stepz = [sum(step[:y]) for y in range(1, len(step) + 1)]
start = [m - n for m,n in zip(stepz,step)]

# for i in range(0,len(stepz)):
#       subjects_SNLG.append(sub_subjs[start[i]:stepz[i]])
#       verbs_SNLG.append(sub_verbs[start[i]:stepz[i]])
#       adjectives_SNLG.append(sub_adjs[start[i]:stepz[i]])
#       adverbs_SNLG.append(sub_adverbs[start[i]:stepz[i]])
#       prepositions_SNLG.append(sub_prep[start[i]:stepz[i]])
#       objects_SNLG.append(sub_objs[start[i]:stepz[i]])
#       conjunctions_to_split.append(sub_cc[start[i]:stepz[i]])
#
#
# df_to_SimpleNLG_working = pd.DataFrame(
# {    'subjects_SNLG': subjects_SNLG,
#      'objects_SNLG': objects_SNLG,
#      'verbs_SNLG': verbs_SNLG,
#      'adjectives_SNLG': adjectives_SNLG,
#      'adverbs_SNLG': adverbs_SNLG,
#      'prepositions_SNLG': prepositions_SNLG,
#      'conjunctions_to_split':conjunctions_to_split
#     })
#
# df_to_SimpleNLG_working = df_to_SimpleNLG_working[['subjects_SNLG', 'objects_SNLG', 'verbs_SNLG', 'adjectives_SNLG', 'adverbs_SNLG', 'prepositions_SNLG', 'conjunctions_to_split']]
#
#
# #filtering empty values
#
# df_to_SimpleNLG_working['subjects_SNLG'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['subjects_SNLG']]
# df_to_SimpleNLG_working['adjectives_SNLG'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['adjectives_SNLG']]
# df_to_SimpleNLG_working['verbs_SNLG'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['verbs_SNLG']]
# df_to_SimpleNLG_working['adverbs_SNLG'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['adverbs_SNLG']]
# df_to_SimpleNLG_working['objects_SNLG'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['objects_SNLG']]
# df_to_SimpleNLG_working['prepositions_SNLG'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['prepositions_SNLG']]
# df_to_SimpleNLG_working['conjunctions_to_split'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_working['conjunctions_to_split']]

################################## SVO Model ####################################
# In this chunk of code, each input will be carved into the constituent parts of the US template:
# 1. role - As a ....,
# 2.  I want to...
# 3. benefit - so that....

# when the role and/or benefit do not exist, they will be replaced with a default role
#and/or default benefit so that they comply with the US templates.

# doing this slicing simplifies the list of inputs to SimpleNLG.

#------------Finiding users in "As a user.." -------------------
# Follows dep pattern: ADP DET .... PRON (As a ....I) or ADP NOUN..., etc.
# If role exists, will appear as the first entry in the prep phrases list per US
def get_pps(doc):
    "Function to get PPs from a parsed document."
    pps = []
    for token in doc:
        # Try this with other parts of speech for different subtrees.
        if token.dep_ == 'prep':
            pp = ' '.join([tok.orth_ for tok in token.subtree])
            pps.append(pp)
    return pps

def get_role(doc):
    "Function to get PPs from a parsed document."
    pps = []
    for token in doc:
        # Try this with other parts of speech for different subtrees.
        if token.pos_ == 'ADP':
            pp = ' '.join([tok.orth_ for tok in token.subtree])
            pps.append(pp)
    return pps

docs = df4['Revised US'].tolist()
df4['doc']= df4['Revised US'].apply(lambda x: nlp(x))
df4['roles_working']= df4['doc'].apply(get_role)
df4['prep_phrases']= df4['doc'].apply(get_pps)


#Note: for some reason, the function above is not working the same for all user stories when the input type is a DataFrame
#causing a lengh issue between benefits_flat and benefits
# However, the function provides the correct results when the user stories are passed in isolation.
# So, as a work around, df4['prep_phrases'] will be updated director for the 11 problem cases found as shown below:

## May be fixed by ensuring inputu data follows "As a .., I want" to format, with the comma

roles = []
for index, row in df4.iterrows():
    if df4.loc[index,'roles_working']!='' and len(df4.loc[index,'roles_working'])> 1 and "as " in df4.loc[index,'roles_working'][0] and ("as of " not in df4.loc[index,'roles_working'][0] and "as well as" not in df4.loc[index,'roles_working'][0] and "as being" not in df4.loc[index,'roles_working'][0]):
        roles.append(df4.loc[index,'roles_working'][0])
    elif df4.loc[index,'roles_working']!='' and len(df4.loc[index,'roles_working'])> 1 and "as " not in df4.loc[index,'roles_working'][0]  and "as " in df4.loc[index,'roles_working'][1] and ("as of " not in df4.loc[index,'roles_working'][1] and "as well as" not in df4.loc[index,'roles_working'][1] and "as being" not in df4.loc[index,'roles_working'][1]):
        roles.append(df4.loc[index,'roles_working'][1])
    elif df4.loc[index,'roles_working']!='' and len(df4.loc[index,'roles_working'])==1 and "as " in df4.loc[index,'roles_working'][0] and ("as of " not in df4.loc[index,'roles_working'][0] and "as well as" not in df4.loc[index,'roles_working'][0] and "as being" not in df4.loc[index,'roles_working'][0]):
        roles.append(df4.loc[index,'roles_working'][0])
    else:
        roles.append(None)

df4['role'] = roles

# count number of words in role to know where action starts
df4['role_end_index'] = df4['role'].str.split().str.len()

df4['role_end_index'] = df4['role_end_index'].fillna('')

for index,row in df4.iterrows():
    if df4.loc[index,'role_end_index']!='':
        df4.loc[index,'role_end_index'] = int(round(df4.loc[index,'role_end_index']))


# where role is empty, insert default role.
for index,row in df4.iterrows():
    if df4.loc[index,'role'] == None:
       df4.loc[index,'role'] = "As a <default user>"

#------------Finding phrase in input AFTER user phrase: "As a user.." -------------------

#returning the rest of the phrase, after the user phrase (As a ...) has been carved out
def find_after_user_phrase(x, y):
    if x!='':
        return y[x:]
    else:
        return y

df4['after_user_phrase'] = df4.apply(lambda row: find_after_user_phrase(row['role_end_index'], row['tokens']), axis=1)

#------------Finding benefit phrase in input ------------- -------------------
# Follows the following POS pattern: ADP ADP..... (so that...)
# and the following dep pattern: mark mark .... (so that....)

for index, row in df4.iterrows():
       if " so that " in df4.loc[index,'Revised US']:
            df4.loc[index, 'Has_benefit'] = "True"
       else:
            df4.loc[index, 'Has_benefit'] = "False"

# # Find indices of the start of the benefit  phrase
def find_benefit_index(US):
    return [i for i, elem in enumerate(US) if elem =='so']
df4['find_benefit_start_index'] = df4['after_user_phrase'].apply(find_benefit_index)


benefits = []
for index, row in df4.iterrows():
    if df4.loc[index,'Has_benefit'] == 'True':
        benefits.append(df4.loc[index,'find_benefit_start_index'])
    else:
        benefits.append(None)
#
# for i in range(len(benefits)):
#     if benefits[i]!=None:
#         print(i, benefits[i])


from collections import Iterable

def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

benefits_flat = list(flatten(benefits))

#print(len(benefits_flat))
#Note: for trouble shooting, this value should be the same length as benfeits. If not, check inputs for lack of commas.

df4['find_benefit_start_index'] = benefits_flat
df4['find_benefit_start_index'] = df4['find_benefit_start_index'].fillna('')

# Finding instances of "so that.."
def find_benefit(x, y):
    if x!='':
        return y[x:]

for index,row in df4.iterrows():
    if df4.loc[index,'find_benefit_start_index']!='':
        df4.loc[index,'find_benefit_start_index'] = int(round(df4.loc[index,'find_benefit_start_index']))

df4['benefit'] = df4.apply(lambda row: find_benefit(row['find_benefit_start_index'], row['after_user_phrase']), axis=1)

#flatten benefit phrase; where benefit is empty, insert default benefit.
for index,row in df4.iterrows():
    if df4.loc[index,'benefit']!= None:
       df4.loc[index,'benefit'] = " ".join(str(x) for x in df4.loc[index,'benefit'])
       df4.loc[index,'benefit'] = df4.loc[index,'benefit'].replace(' ,','')
    else:
       df4.loc[index,'benefit'] = "so that <default benefit>"

#------------Finding Action phrase in input ---------------- -------------------
def find_action(x, y):
    if x!='':
        return y[0:x]

df4['action'] = df4.apply(lambda row: find_action(row['find_benefit_start_index'], row['after_user_phrase']), axis=1)

#carving out parts of POS, Dep and Head lists that belong to Role and/or benefit phrases.
# Remainder (Action phrase) will be further dissected into SVO parts for input into SimpleNLG.

# Finding start index for benefit phrase
for index, row in df4.iterrows():
    if  df4.loc[index,'find_benefit_start_index'] != '' and df4.loc[index,'role_end_index']!='':
        df4.loc[index,'find_benefit_start_POS'] = df4.loc[index, 'find_benefit_start_index'] + df4.loc[index, 'role_end_index']
    elif df4.loc[index,'find_benefit_start_index'] == '' and df4.loc[index,'role_end_index']!='':
        df4.loc[index,'find_benefit_start_POS'] = ''
    else:
        df4.loc[index,'find_benefit_start_POS'] = df4.loc[index, 'find_benefit_start_index']

# finding end index for benefit phrase
step = []
for index, row in df4.iterrows():
    step.append(len(df4.loc[index,'tokens']))
df4['row_length'] = step

for index, row in df4.iterrows():
    if  df4.loc[index,'find_benefit_start_index'] != '':
        df4.loc[index,'find_benefit_end_POS'] = df4.loc[index,'row_length']
    else:
        df4.loc[index,'find_benefit_end_POS'] = ''


# finding start index for action
for index, row in df4.iterrows():
    if  df4.loc[index,'role_end_index']!='':
        df4.loc[index,'find_action_start_POS'] = df4.loc[index, 'role_end_index']
    else:
        df4.loc[index,'find_action_start_POS'] = 0

# finding end index for action
for index, row in df4.iterrows():
    if  df4.loc[index,'find_benefit_start_POS']!='':
        df4.loc[index,'find_action_end_POS'] = df4.loc[index, 'find_benefit_start_POS']
    else:
        df4.loc[index,'find_action_end_POS']  = df4.loc[index,'row_length']

df4['find_action_start_POS'] = df4['find_action_start_POS'].astype('int64')
df4['find_action_end_POS']= df4['find_action_end_POS'].astype('int64')


def find_action(x, y, z):
    if x!='' and y!='':
        return z[x:y]

df4['action'] = df4.apply(lambda row: find_action(row['find_action_start_POS'], row['find_action_end_POS'], row['tokens']), axis=1)

def find_action_pos(x, y, z):
    if x!='' and y!='':
        return z[x:y]

df4['action_pos'] = df4.apply(lambda row: find_action_pos(row['find_action_start_POS'], row['find_action_end_POS'], row['pos']), axis=1)


def find_action_dep(x, y, z):
    if x!='' and y!='':
        return z[x:y]

df4['action_dep'] = df4.apply(lambda row: find_action_dep(row['find_action_start_POS'], row['find_action_end_POS'], row['dep']), axis=1)


def find_action_head(x, y,z):
    if x!='' and y!='':
        return z[x:y]


df4['action_head'] = df4.apply(lambda row: find_action_head(row['find_action_start_POS'], row['find_action_end_POS'], row['head']), axis=1)

######################### Finding parts - SVO - of "Actions"####################
# Includes the identification of verbs, objects and prep phrases (to include noun phrases)
# as well as heads for modifiers (adjectives and/or adverbs)

# Auto-generated US = role + SimpleNLG Output + benefit, where SimpleNLG Output =
# "I want to" + Action(secondary verbs, objects, adjectives, adverbs, and prep phrases)

df_to_SimpleNLG_final = pd.DataFrame()
df_to_SimpleNLG_working = pd.DataFrame()

df_to_SimpleNLG_final['role_phrase'] = df4['role']
df_to_SimpleNLG_final['benefit_phrase'] = df4['benefit']
df_to_SimpleNLG_final['action'] = df4['action']
df_to_SimpleNLG_final['action subject'] = "I"
df_to_SimpleNLG_final['action verb phrase'] = "want to"


df_to_SimpleNLG_working['prep phrase working'] = df4['prep_phrases']
df_to_SimpleNLG_working['action pos'] = df4['action_pos']
df_to_SimpleNLG_working['action dep'] = df4['action_dep']
df_to_SimpleNLG_working['action head'] = df4['action_head']

#---------------------------------- action verbs--------------------------------
action_verbs = []
for index, row in df4.iterrows():
    for i in range(0,len(df4.loc[index,'action'])):
        if df_to_SimpleNLG_working.loc[index,'action pos'][i] == 'VERB' and df_to_SimpleNLG_working.loc[index,'action dep'][i] != 'compound':
             action_verbs.append(df4.loc[index,'action'][i])
        else:
            action_verbs.append(None)

# Cleanup
#A. Verbs - If verbs contain (want, should, need, shall, are, must, can, am, would), then remove from phrase

for i in range(0, len(action_verbs)):
    if action_verbs[i]!= None and action_verbs[i] in ["want", "should", "need", "shall", "are", "am", "must", "can", "am", "would"]:
        action_verbs[i] = None

#B: if first verb ends in 's', strip 's'

for i in range(0, len(action_verbs)):
    if action_verbs[i]!= None and action_verbs[i].endswith('s') :
        action_verbs[i] = action_verbs[i].strip('s')


#C. Remove 1 character verbs
for i in range(0, len(action_verbs)):
    if action_verbs[i]!= None and len(action_verbs[i])==1 :
        action_verbs[i] = None

##Note: deduplication between action verb and prep phrases done later in code.

#-------------------------------action Adverbs ---------------------------------

action_adverbs = []
for index, row in df4.iterrows():
    for i in range(0,len(df4.loc[index,'action'])):
        if df_to_SimpleNLG_working.loc[index,'action pos'][i] == 'ADV' and (df_to_SimpleNLG_working.loc[index,'action dep'][i] == 'advmod' or df_to_SimpleNLG_working.loc[index,'action dep'][i] == 'advcl'):
             action_adverbs.append(df4.loc[index,'action'][i])
        else:
            action_adverbs.append(None)

#print(action_adverbs[0:50])
#-------------------------------action Adjectives ------------------------------

# action_adjectives = []
# for index, row in df4.iterrows():
#     for i in range(0,len(df4.loc[index,'action'])):
#         if df_to_SimpleNLG_working.loc[index,'action pos'][i] == 'ADJ' or  df_to_SimpleNLG_working.loc[index,'action dep'][i] == 'amod':
#              action_adjectives.append(df4.loc[index,'action'][i])
#         else:
#             action_adjectives.append(None)

# ---------------------------------action Objects-------------------------------
# action_objects = []
# for index, row in df4.iterrows():
#     for i in range(0,len(df4.loc[index,'action'])):
#         if df_to_SimpleNLG_working.loc[index,'action dep'][i] == 'dobj' or df_to_SimpleNLG_working.loc[index,'action dep'][i] == 'iobj' or df_to_SimpleNLG_working.loc[index,'action dep'][i] == 'oprd':
#              action_objects.append(df4.loc[index,'action'][i])
#         else:
#             action_objects.append(None)

# -----------------------------action noun Phrases-------------------------------
# df_to_SimpleNLG_final['action noun phrases'] = df4['noun_phrases']
# if noun phrase NOT in action phrase, then remove from list:
for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'action']!= None:
       df_to_SimpleNLG_final.loc[index,'action'] = " ".join(str(x) for x in df_to_SimpleNLG_final.loc[index,'action'])
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' ,','')

df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace('  ',' ')
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(" '","'")
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace('.', '')
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(', ','')

# for index, row in df_to_SimpleNLG_final.iterrows():
#     for i in range(0, len(df_to_SimpleNLG_final.loc[index,'action noun phrases'])):
#         if df_to_SimpleNLG_final.loc[index, 'action noun phrases'][i] not in df_to_SimpleNLG_final.loc[index,'action'] or df_to_SimpleNLG_final.loc[index, 'action noun phrases'][i]=='i':
#             df_to_SimpleNLG_final.loc[index, 'action noun phrases'][i] = None

# action prep phrases-----------------------------------------------------------
# Note: if a US has a role, then the first entry in prep_phrases os the role
# all others should be extracted as true prep phrases


action_prep_phrases = []
action_prep_phrase_length = []

for index, row in df_to_SimpleNLG_final.iterrows():
    for i in range(len(df4.loc[index, 'prep_phrases'])):
        if  df4.loc[index,'prep_phrases'][i] in df_to_SimpleNLG_final.loc[index,'action']:
            action_prep_phrases.append(df4.loc[index, 'prep_phrases'][i])
    action_prep_phrase_length.append(len(action_prep_phrases))

action_prep_phrase_length_new = [j-i for i, j in zip(action_prep_phrase_length[:-1], action_prep_phrase_length[1:])]
action_prep_phrase_length_new.insert(0, action_prep_phrase_length[0])

step_prep = [sum(action_prep_phrase_length_new[:y]) for y in range(1, len(action_prep_phrase_length_new) + 1)]
start_prep = [m - n for m,n in zip(step_prep,action_prep_phrase_length_new)]

# #split by # of action prep_phrases per US
split_action_prep_phrases = []
for i in range(len(action_prep_phrase_length)):
     split_action_prep_phrases.append(action_prep_phrases[start_prep[i]:step_prep[i]])

df_to_SimpleNLG_working['action_prep_phrases'] = split_action_prep_phrases

#finding unique prep phrases per sublist
def unique_prep(string_list):
    return list(set(i for i in string_list
               if not any(i in s for s in string_list if i != s)))

df_to_SimpleNLG_final['action_prep_phrases'] = df_to_SimpleNLG_working['action_prep_phrases'].apply(unique_prep)

#splitting prep phrases across multiple columns
action_pps_split = df_to_SimpleNLG_final['action_prep_phrases'].apply(pd.Series)
action_pps_split = action_pps_split.rename(columns = lambda x : 'action_pp' + str(x))
df_to_SimpleNLG_final = pd.concat([df_to_SimpleNLG_final[:], action_pps_split[:]], axis=1)

#removing single word prep phrases "for", "to", "before", etc

# if word count ==1, then turn to blank.

df_to_SimpleNLG_final['lengthaction_pp1']= df_to_SimpleNLG_final['action_pp0'].str.split().str.len()
df_to_SimpleNLG_final['lengthaction_pp2']= df_to_SimpleNLG_final['action_pp1'].str.split().str.len()
df_to_SimpleNLG_final['lengthaction_pp3']= df_to_SimpleNLG_final['action_pp2'].str.split().str.len()
df_to_SimpleNLG_final['lengthaction_pp4']= df_to_SimpleNLG_final['action_pp3'].str.split().str.len()

for i in range(len(df_to_SimpleNLG_final['action_pp0'])):
        for index, rows in df_to_SimpleNLG_final.iterrows():
            if df_to_SimpleNLG_final.loc[index,'lengthaction_pp1'] ==1:
                df_to_SimpleNLG_final.loc[index,'action_pp0'] = ''

for index, rows in df_to_SimpleNLG_final.iterrows():
        for i in range(0,len(df_to_SimpleNLG_final['action_pp1'])):
            if df_to_SimpleNLG_final.loc[index,'lengthaction_pp2'] ==1:
                df_to_SimpleNLG_final.loc[index,'action_pp1'] = ''

for index, rows in df_to_SimpleNLG_final.iterrows():
        for i in range(0,len(df_to_SimpleNLG_final['action_pp2'])):
            if df_to_SimpleNLG_final.loc[index,'lengthaction_pp3'] ==1:
                df_to_SimpleNLG_final.loc[index,'action_pp2'] = ''

for index, rows in df_to_SimpleNLG_final.iterrows():
        for i in range(0,len(df_to_SimpleNLG_final['action_pp3'])):
            if df_to_SimpleNLG_final.loc[index,'lengthaction_pp4'] ==1:
                df_to_SimpleNLG_final.loc[index,'action_pp3'] = ''

#----------------------------Preparing SVO for insertion into DF---------------#

verbs_to_SNLG = []
# adjectives_to_SNLG = []
# adverbs_to_SNLG = []
# objects_to_SNLG = []

step_simpleNLG = []
for index, row in df4.iterrows():
    step_simpleNLG.append(len(df4.loc[index,'action']))
df4['action_length'] = step_simpleNLG

# splitting subjects,...., by length of DF rows
stepz_simpleNLG = []
start_simpleNLG = []
stepz_simpleNLG = [sum(step_simpleNLG[:y]) for y in range(1, len(step_simpleNLG) + 1)]
start_simpleNLG = [m - n for m,n in zip(stepz_simpleNLG,step_simpleNLG)]

for i in range(0,len(stepz_simpleNLG)):
      verbs_to_SNLG.append(action_verbs[start_simpleNLG[i]:stepz_simpleNLG[i]])
      # adjectives_to_SNLG.append(action_adjectives[start_simpleNLG[i]:stepz_simpleNLG[i]])
      # adverbs_to_SNLG.append(action_adverbs[start_simpleNLG[i]:stepz_simpleNLG[i]])
      # objects_to_SNLG.append(action_objects[start_simpleNLG[i]:stepz_simpleNLG[i]])

# df_to_SimpleNLG_final['action objects'] =  objects_to_SNLG
df_to_SimpleNLG_final['action verbs'] = verbs_to_SNLG
# df_to_SimpleNLG_final['action adjectives'] = adjectives_to_SNLG
# df_to_SimpleNLG_final['action adverbs'] =  adverbs_to_SNLG

#filtering empty /None values
# df_to_SimpleNLG_final['action objects'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['action objects']]
df_to_SimpleNLG_final['action verbs'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['action verbs']]
# df_to_SimpleNLG_final['action adjectives'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['action adjectives']]
# df_to_SimpleNLG_final['action adverbs'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['action adverbs']]
# df_to_SimpleNLG_final['action noun phrases'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['action noun phrases']]
#
# action_objects_split = df_to_SimpleNLG_final['action objects'].apply(pd.Series)
# action_objects_split = action_objects_split.rename(columns = lambda x : 'action_object' + str(x))
# df_to_SimpleNLG_final = pd.concat([df_to_SimpleNLG_final[:], action_objects_split[:]], axis=1)

action_verbs_split = df_to_SimpleNLG_final['action verbs'].apply(pd.Series)
action_verbs_split = action_verbs_split.rename(columns = lambda x : 'action_verb' + str(x))
df_to_SimpleNLG_final = pd.concat([df_to_SimpleNLG_final[:], action_verbs_split[:]], axis=1)

# action_adjs_split = df_to_SimpleNLG_final['action adjectives'].apply(pd.Series)
# action_adjs_split = action_adjs_split.rename(columns = lambda x : 'action_adj' + str(x))
# df_to_SimpleNLG_final = pd.concat([df_to_SimpleNLG_final[:], action_adjs_split[:]], axis=1)
#
# action_advs_split = df_to_SimpleNLG_final['action adverbs'].apply(pd.Series)
# action_advs_split = action_advs_split.rename(columns = lambda x : 'action_adv' + str(x))
# df_to_SimpleNLG_final = pd.concat([df_to_SimpleNLG_final[:], action_advs_split[:]], axis=1)

# action_nouns_split = df_to_SimpleNLG_final['action noun phrases'].apply(pd.Series)
# action_nouns_split = action_nouns_split.rename(columns = lambda x : 'action_np' + str(x))
# df_to_SimpleNLG_final = pd.concat([df_to_SimpleNLG_final[:], action_nouns_split[:]], axis=1)

df_to_SimpleNLG_final=df_to_SimpleNLG_final.fillna('<blank>')
df_to_SimpleNLG_final = df_to_SimpleNLG_final.replace('<blank>', '')

# Deduplicating verbs / nouns with prep phrases:

# #A: Verb in prep phrase
# df['verb0 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb0'] in x['action_pp0'] , axis=1).astype(int)
# df['verb0 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb0'] in x['action_pp1'] , axis=1).astype(int)
# df['verb0 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb0'] in x['action_pp2'] , axis=1).astype(int)
# df['verb0 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb0'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb0 in prep0'] ==1 or df.loc[index,'verb0 in prep1']==1 or df.loc[index,'verb0 in prep2']==1 or df.loc[index,'verb0 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb0'] = ''
#
# df['verb1 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb1'] in x['action_pp0'] , axis=1).astype(int)
# df['verb1 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb1'] in x['action_pp1'] , axis=1).astype(int)
# df['verb1 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb1'] in x['action_pp2'] , axis=1).astype(int)
# df['verb1 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb1'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb1 in prep0'] ==1 or df.loc[index,'verb1 in prep1']==1 or df.loc[index,'verb1 in prep2']==1 or df.loc[index,'verb1 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb1'] = ''
#
# df['verb2 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb2'] in x['action_pp0'] , axis=1).astype(int)
# df['verb2 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb2'] in x['action_pp1'] , axis=1).astype(int)
# df['verb2 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb2'] in x['action_pp2'] , axis=1).astype(int)
# df['verb2 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb2'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb2 in prep0'] ==1 or df.loc[index,'verb2 in prep1']==1 or df.loc[index,'verb2 in prep2']==1 or df.loc[index,'verb2 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb2'] = ''
#
# df['verb3 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb3'] in x['action_pp0'] , axis=1).astype(int)
# df['verb3 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb3'] in x['action_pp1'] , axis=1).astype(int)
# df['verb3 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb3'] in x['action_pp2'] , axis=1).astype(int)
# df['verb3 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb3'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb3 in prep0'] ==1 or df.loc[index,'verb3 in prep1']==1 or df.loc[index,'verb3 in prep2']==1 or df.loc[index,'verb3 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb3'] = ''
#
# df['verb4 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb4'] in x['action_pp0'] , axis=1).astype(int)
# df['verb4 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb4'] in x['action_pp1'] , axis=1).astype(int)
# df['verb4 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb4'] in x['action_pp2'] , axis=1).astype(int)
# df['verb4 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb4'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb4 in prep0'] ==1 or df.loc[index,'verb4 in prep1']==1 or df.loc[index,'verb4 in prep2']==1 or df.loc[index,'verb4 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb4'] = ''
#
# df['verb5 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb5'] in x['action_pp0'] , axis=1).astype(int)
# df['verb5 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb5'] in x['action_pp1'] , axis=1).astype(int)
# df['verb5 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb5'] in x['action_pp2'] , axis=1).astype(int)
# df['verb5 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb5'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb5 in prep0'] ==1 or df.loc[index,'verb5 in prep1']==1 or df.loc[index,'verb5 in prep2']==1 or df.loc[index,'verb5 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb5'] = ''
#
# df['verb6 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb6'] in x['action_pp0'] , axis=1).astype(int)
# df['verb6 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb6'] in x['action_pp1'] , axis=1).astype(int)
# df['verb6 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb6'] in x['action_pp2'] , axis=1).astype(int)
# df['verb6 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb6'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb6 in prep0'] ==1 or df.loc[index,'verb6 in prep1']==1 or df.loc[index,'verb6 in prep2']==1 or df.loc[index,'verb6 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb6'] = ''
#
# df['verb7 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb7'] in x['action_pp0'] , axis=1).astype(int)
# df['verb7 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb7'] in x['action_pp1'] , axis=1).astype(int)
# df['verb7 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb7'] in x['action_pp2'] , axis=1).astype(int)
# df['verb7 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_verb7'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'verb7 in prep0'] ==1 or df.loc[index,'verb7 in prep1']==1 or df.loc[index,'verb7 in prep2']==1 or df.loc[index,'verb7 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_verb7'] = ''
#
# #B: Nouns in prep phrase (returns true if there is overlap)
# df['noun0 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np0'] in x['action_pp0'] , axis=1).astype(int)
# df['noun0 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np0'] in x['action_pp1'] , axis=1).astype(int)
# df['noun0 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np0'] in x['action_pp2'] , axis=1).astype(int)
# df['noun0 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np0'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun0 in prep0'] ==1 or df.loc[index,'noun0 in prep1']==1 or df.loc[index,'noun0 in prep2']==1 or df.loc[index,'noun0 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np0'] = ''
#
# df['noun1 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np1'] in x['action_pp0'] , axis=1).astype(int)
# df['noun1 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np1'] in x['action_pp1'] , axis=1).astype(int)
# df['noun1 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np1'] in x['action_pp2'] , axis=1).astype(int)
# df['noun1 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np1'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun1 in prep0'] ==1 or df.loc[index,'noun1 in prep1']==1 or df.loc[index,'noun1 in prep2']==1 or df.loc[index,'noun1 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np1'] = ''
#
# df['noun2 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np2'] in x['action_pp0'] , axis=1).astype(int)
# df['noun2 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np2'] in x['action_pp1'] , axis=1).astype(int)
# df['noun2 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np2'] in x['action_pp2'] , axis=1).astype(int)
# df['noun2 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np2'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun2 in prep0'] ==1 or df.loc[index,'noun2 in prep1']==1 or df.loc[index,'noun2 in prep2']==1 or df.loc[index,'noun2 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np2'] = ''
#
# df['noun3 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np3'] in x['action_pp0'] , axis=1).astype(int)
# df['noun3 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np3'] in x['action_pp1'] , axis=1).astype(int)
# df['noun3 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np3'] in x['action_pp2'] , axis=1).astype(int)
# df['noun3 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np3'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun3 in prep0'] ==1 or df.loc[index,'noun3 in prep1']==1 or df.loc[index,'noun3 in prep2']==1 or df.loc[index,'noun3 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np3'] = ''
#
# df['noun4 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np4'] in x['action_pp0'] , axis=1).astype(int)
# df['noun4 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np4'] in x['action_pp1'] , axis=1).astype(int)
# df['noun4 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np4'] in x['action_pp2'] , axis=1).astype(int)
# df['noun4 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np4'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun4 in prep0'] ==1 or df.loc[index,'noun4 in prep1']==1 or df.loc[index,'noun4 in prep2']==1 or df.loc[index,'noun4 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np4'] = ''
#
# df['noun5 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np5'] in x['action_pp0'] , axis=1).astype(int)
# df['noun5 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np5'] in x['action_pp1'] , axis=1).astype(int)
# df['noun5 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np5'] in x['action_pp2'] , axis=1).astype(int)
# df['noun5 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np5'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun5 in prep0'] ==1 or df.loc[index,'noun5 in prep1']==1 or df.loc[index,'noun5 in prep2']==1 or df.loc[index,'noun5 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np5'] = ''
#
# df['noun6 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np6'] in x['action_pp0'] , axis=1).astype(int)
# df['noun6 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np6'] in x['action_pp1'] , axis=1).astype(int)
# df['noun6 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np6'] in x['action_pp2'] , axis=1).astype(int)
# df['noun6 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np6'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun6 in prep0'] ==1 or df.loc[index,'noun6 in prep1']==1 or df.loc[index,'noun6 in prep2']==1 or df.loc[index,'noun6 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np6'] = ''
#
# df['noun7 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np7'] in x['action_pp0'] , axis=1).astype(int)
# df['noun7 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np7'] in x['action_pp1'] , axis=1).astype(int)
# df['noun7 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np7'] in x['action_pp2'] , axis=1).astype(int)
# df['noun7 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np7'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun7 in prep0'] ==1 or df.loc[index,'noun7 in prep1']==1 or df.loc[index,'noun7 in prep2']==1 or df.loc[index,'noun7 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np7'] = ''
#
# df['noun8 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np8'] in x['action_pp0'] , axis=1).astype(int)
# df['noun8 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np8'] in x['action_pp1'] , axis=1).astype(int)
# df['noun8 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np8'] in x['action_pp2'] , axis=1).astype(int)
# df['noun8 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np8'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun8 in prep0'] ==1 or df.loc[index,'noun8 in prep1']==1 or df.loc[index,'noun8 in prep2']==1 or df.loc[index,'noun8 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np8'] = ''
#
# df['noun9 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np9'] in x['action_pp0'] , axis=1).astype(int)
# df['noun9 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np9'] in x['action_pp1'] , axis=1).astype(int)
# df['noun9 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np9'] in x['action_pp2'] , axis=1).astype(int)
# df['noun9 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np9'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun9 in prep0'] ==1 or df.loc[index,'noun9 in prep1']==1 or df.loc[index,'noun9 in prep2']==1 or df.loc[index,'noun9 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np9'] = ''
#
# df['noun10 in prep0'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np10'] in x['action_pp0'] , axis=1).astype(int)
# df['noun10 in prep1'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np10'] in x['action_pp1'] , axis=1).astype(int)
# df['noun10 in prep2'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np10'] in x['action_pp2'] , axis=1).astype(int)
# df['noun10 in prep3'] = df_to_SimpleNLG_final.apply(lambda x: x['action_np10'] in x['action_pp3'] , axis=1).astype(int)
#
# for index, row in df.iterrows():
#     if df.loc[index,'noun10 in prep0'] ==1 or df.loc[index,'noun10 in prep1']==1 or df.loc[index,'noun10 in prep2']==1 or df.loc[index,'noun10 in prep3']==1:
#         df_to_SimpleNLG_final.loc[index,'action_np10'] = ''
#

df_to_SimpleNLG_final_FINAL = pd.DataFrame()

df_to_SimpleNLG_final_FINAL = df_to_SimpleNLG_final[[
'role_phrase',
'benefit_phrase',
'action subject',
'action',
'action verb phrase',
'action_verb0',
'action_verb1',
'action_pp0',
'action_pp1',
'action_pp2',
'action_pp3'
#'action_nounobjectphrase',

#'action_advphrase',
]].copy()


# ################################# Metrics #########################################
#------------------------------Input Variability Metrics -----------------------#
# includes things like count of missing roles, count of missing benefits, count of US with more than one sentence,
# count of parentheticals, # of acronyms, and variation in action phrasing (I want, I need, I can, etc.)

#Count instances of non conformant actions for statistical analysis:
#"need to"
#"would like"
#"like to"
#"I am"/  "am able"
#"should be able"
#"I have" / "Should have" / "can have"
#"I can"
#"I want to be able to"

I_need = []
I_would_like = []
I_like = []
I_want = []
I_am = []
I_should = []
shall = []
I_have = []
I_can = []
to_be_able_to = []
other = []

for index, row in df3.iterrows():
    if " i need " in df3.loc[index,'Revised US']:
        I_need.append(df3.loc[index,'Revised US'])
    elif " i want " in df3.loc[index,'Revised US']:
        I_want.append(df3.loc[index,'Revised US'])
    elif " i would like " in df3.loc[index,'Revised US']:
        I_would_like.append(df3.loc[index,'Revised US'])
    elif " i like " in df3.loc[index,'Revised US']:
        I_like.append(df3.loc[index,'Revised US'])
    elif " i am " in df3.loc[index,'Revised US']:
        I_am.append(df3.loc[index,'Revised US'])
    elif " i should " in df3.loc[index,'Revised US']:
        I_should.append(df3.loc[index,'Revised US'])
    elif " shall " in df3.loc[index,'Revised US']:
        shall.append(df3.loc[index,'Revised US'])
    elif " i have " in df3.loc[index,'Revised US']:
        I_have.append(df3.loc[index,'Revised US'])
    elif " i can " in df3.loc[index,'Revised US']:
        I_can.append(df3.loc[index,'Revised US'])
    elif " to be able to " in df3.loc[index,'Revised US']:
        to_be_able_to.append(df3.loc[index,'Revised US'])
    else:
        other.append(df3.loc[index,'Revised US'])

action_variation_names = ["To be able to Count", "Shall count", "I need count", "I want count", "I would like count", "I like count", "I am count", "I should count", "I have count", "I can count", "Other count", "Total count"]
action_variation_metrics = [len(to_be_able_to), len(shall), len(I_need), len(I_want), len(I_would_like), len(I_like), len(I_am), len(I_should), len(I_have), len(I_can), len(other), len(df4['Revised US'])]


# role metrics
default_role = []
non_default_role = []
for index, row in df4.iterrows():
    if df4.loc[index, 'role'] == "As a <default user>":
        default_role.append(df4.loc[index, 'role'])
    else:
        non_default_role.append(df4.loc[index, 'role'])

role_metric_names = ["default role count", "has role count"]
role_metrics = [len(default_role), len(non_default_role)]

# benefit metrics
default_benefit = []
non_default_benefit = []
for index, row in df4.iterrows():
    if df4.loc[index, 'benefit'] ==  "so that <default benefit>":
        default_benefit.append(df4.loc[index, 'benefit'])
    else:
        non_default_benefit.append(df4.loc[index, 'benefit'])

benefit_metric_names = ["default benefit count", "has benefit count"]
benefit_metrics = [len(default_benefit), len(non_default_benefit)]

# of compound statements - and, or, /,  & (limited to actions)

compound_role = []
compound_action = []
compound_benefit = []
non_compound_role=[]
non_compound_action=[]
non_compound_benefit=[]
# A. Compound roles

for index, row in df4.iterrows():
    if " and " in df4.loc[index, 'role'] or " or " in df4.loc[index, 'role']:
        compound_role.append(df4.loc[index, 'role'])
    else:
        non_compound_role.append(df4.loc[index, 'role'])

# B. Compound actions
for index, row in df_to_SimpleNLG_final.iterrows():
    if " and " in  df_to_SimpleNLG_final.loc[index,'action'] or " or " in  df_to_SimpleNLG_final.loc[index,'action']:
        compound_action.append(df_to_SimpleNLG_final.loc[index,'action'])
    else:
        non_compound_action.append(df_to_SimpleNLG_final.loc[index,'action'])

# C. Compound Benefits
for index, row in df4.iterrows():
    if " and " in df4.loc[index, 'benefit'] or " or " in df4.loc[index, 'benefit']:
        compound_benefit.append(df4.loc[index, 'benefit'])
    else:
        non_compound_benefit.append(df4.loc[index, 'benefit'])


compound_metric_names = ["compound role count", "non compound role", "compound action count", "non compound action count", "compound benefit count", "non compound benefit count"]
compound_metrics = [len(compound_role), len(non_compound_role), len(compound_action), len(non_compound_action), len(compound_benefit), len(non_compound_benefit)]


# number of US with count sent > 1
multi_sentence=[]
for index, row in df.iterrows():
    if len(df.loc[index, 'sent_list'])>1:
        multi_sentence.append(df.loc[index, 'sent_list'])


# parentheticals
paren = []
for index, row in df2.iterrows():
     if bool(df2.loc[index, 'Final Paren']):
         paren.append(df2.loc[index, 'Final Paren'])


other_metric_names = ["multi sentence count", "parenthetical count"]
other_metrics = [len(multi_sentence), len(paren)]


# undefined acronyms
acronyms = []
df_Acronyms_all = pd.DataFrame()
df_Acronyms_all['Acronym List'] = df4['Revised US'].str.findall(r'\b[A-Z\.]{2,}s?\b')
for index, row in df_Acronyms_all.iterrows():
    if len(df_Acronyms_all.loc[index, 'Acronym List'])>=1:
        acronyms.append(df_Acronyms_all.loc[index, 'Acronym List'])

# -----------------------Input Ambiguity Metrics-------------------------------------#
# The following code measures the lexical and syntactic (semantic) ambiguity of user inputs disgusting
# four metrics, labelled A1, A2, B1, and B2 below.
# Source for equations:
    # Kiyavitskaya, N., Zeni, N., Mich, L., & Berry, D. M. (2008). Requirements for tools for ambiguity identification and
    # measurement in natural language requirements specifications. Requirements engineering, 13(3), 207-239.


#A. Lexical Ambiguity of Inputs----------------------------------------------------------#
#finding # of meanings per word per sentence
def first(wordlist):
    # wordlist is a list of words, i.e. ['sun', 'shine', 'spotless']
    return [wordnet.synsets(word) for word in wordlist]

df_ambig['syn'] = df_ambig['tokenized_text'].apply(first)

df_ambig_sent = pd.DataFrame(list(map(lambda d: list(chain.from_iterable(d)), df_ambig['syn'])))

#A1. lexical ambiguity per sentence
df_ambig_sent['Sentence Lexical Ambiguity']= 376 - df_ambig_sent.apply(lambda x: x.isnull().sum(), axis='columns')
#normalizing sentence lex. ambiguity
max_CD = max(df_ambig_sent['Sentence Lexical Ambiguity'])
min_CD = min(df_ambig_sent['Sentence Lexical Ambiguity'])
diff = 0
diff = max_CD - min_CD
for index, row in df_ambig_sent.iterrows():
    df_ambig_sent.loc[index, 'Sentence Lex_ambig_norm'] = (df_ambig_sent.loc[index, 'Sentence Lexical Ambiguity']- min_CD) /diff


#A2. lexical ambiguity per word per sentence
def lexwordambig(wordlist):
    lengths = []
    for x in wordlist:
        lengths.append(len(x))
    return lengths
df_ambig['Lexical Ambiguity per Word'] = df_ambig['syn'].apply(lexwordambig)

def round_robin(first, second):
    return[item for items in zip(first, second) for item in items]

df_ambig['Lexical Ambiguity per Word'] = df_ambig.apply(lambda x: round_robin(x['tokenized_text'], x['Lexical Ambiguity per Word']), axis=1)

#combining results of A1 and A2 above to print to excel

df_ambig_to_excel = df_ambig[['syn','Lexical Ambiguity per Word']].copy()
df_ambig_to_excel['Revised US'] = df3['Revised US'].copy()
df_ambig_to_excel['Sentence Lexical Ambiguity'] = df_ambig_sent['Sentence Lexical Ambiguity'].copy()
df_ambig_to_excel = df_ambig_to_excel[['Revised US', 'syn', 'Lexical Ambiguity per Word', 'Sentence Lexical Ambiguity']]

#converting to strings so can write to Excel
df_ambig_sent= df_ambig_sent.astype(str)

#B. Syntactic Ambiguity of Inputs----------------------------------------------------------#

#B1. syntactic ambiguity of a word (# of POS per word)

def count_by_syntype(wordlist): #runs counts of synsets by POS type (7 noun, 2 verb synsets)
    counts=[]
    for word in wordlist:
        counts.append(Counter([ss.pos() for ss in wordnet.synsets(word)]))
    return counts

df_ambig['syn_set'] = df_ambig['tokenized_text'].apply(count_by_syntype)

def count_pos(synsetcount): #returns counts of distinct POS (7 noun, 2 verb synsets = 2 POS)
    count_POS=[]
    for syn in synsetcount:
        count_POS.append(len(syn))
    return count_POS
df_ambig['Syntactic Ambiguity per Word'] = df_ambig['syn_set'].apply(count_pos)

df_ambig['Syntactic Ambiguity per Word'] = df_ambig.apply(lambda x: round_robin(x['tokenized_text'], x['Syntactic Ambiguity per Word']), axis=1)

#combining results of B1 to results of A above to print to excel
df_ambig_to_excel['Syntactic Ambiguity per Word'] = df_ambig['Syntactic Ambiguity per Word'].copy()


#B2. syntactic ambiguity of a sentence (delta(S)) - count of sentence parse trees
#note that grammar mirrors chunking pattern

# from nltk import CFG
# from nltk import ChartParser
# from nltk import Nonterminal
# from nltk import data
#
# grammar1 = data.load('file:outfile.cfg')
# print(grammar1)
# sent = "As a Archivist I want bi-directional linking between items in the digital collections and EAD finding aids".split()
# parser = ChartParser(grammar1)
# trees = parser.parse(sent)
# for tree in trees:
#      print (tree)

#From NLTK book Chapter 9: Calling the parser's nbest_parse() method will return a list trees of parse trees; trees will be empty if the grammar
#fails to parse the input and will contain one or more parse trees, depending on whether the input is syntactically ambiguous or not.

# >>> tokens = 'Kim likes children'.split()
# >>> from nltk import load_parser [1]
# >>> cp = load_parser('grammars/book_grammars/feat0.fcfg', trace=2)  [2]
# >>> trees = cp.nbest_parse(tokens)


#B3. lexical ambiguity of word W according to parse tree of S: (accounts for POS role of W in S, unlike A1)

#combining results of A1 and A2 above to print to excel

# df_ambig_to_excel = df_ambig[['syn','Lexical Ambiguity per Word']].copy()
# df_ambig_to_excel['Revised US'] = df3['Revised US'].copy()
# df_ambig_to_excel['Sentence Lexical Ambiguity'] = df_ambig_sent['Sentence Lexical Ambiguity'].copy()
# df_ambig_to_excel = df_ambig_to_excel[['Revised US', 'syn', 'Lexical Ambiguity per Word', 'Sentence Lexical Ambiguity']]

#converting to strings so can write to Excel
df_ambig_sent= df_ambig_sent.astype(str)

#---------------------------Inputs: Conceptual Density-------------------------------#

#Notes from :Robeer, M., Lucassen, G., van der Werf, J. M. E., Dalpiaz, F.,
#& Brinkkemper, S. (2016, September). Automated extraction of conceptual models
#from user stories via NLP. In Requirements engineering conference (RE), 2016 IEEE 24th international (pp. 196-205). IEEE.

# concepts include:
# 1. nouns,
# 2. common nouns (disregarding Proper Nouns),
# 3. sentence subjects,
# 4. compound nouns (of length 2) and
# 5. gerunds

# relationships include:
# 1. verbs,
# 2. transitive verbs,
# 3. linking verbs,
# 4. compound nouns (relationship between two nouns)

#Constant - num_tmpl
tmpl = "As a <role>, I want to <action>, so that <benefit>"

char=0
num_tmpl=1
for i in tmpl:
      char=char+1
      if(i==' '):
            num_tmpl=num_tmpl+1

#Finding Nouns (includes class of common nouns)
nouns_CD = []
for index, row in df4.iterrows():
    #print(len(df4.loc[index,'tokens']))
    for i in range(0,len(df4.loc[index,'tokens'])):
        if df4.loc[index,'pos'][i] == 'NOUN' and df4.loc[index,'dep'][i] != 'nsubj' and df4.loc[index,'dep'][i] != 'compound' :
             nouns_CD.append('Y')
        else:
            nouns_CD.append(None)

# #Finding non-subject, proper nouns

propernouns_CD = []
for index, row in df4.iterrows():
    #print(len(df4.loc[index,'tokens']))
    for i in range(0,len(df4.loc[index,'tokens'])):
        if df4.loc[index,'pos'][i] == 'PROPN' and df4.loc[index,'dep'][i] != 'nsubj' and df4.loc[index,'dep'][i] != 'compound':
            propernouns_CD.append('Y')
        else:
            propernouns_CD.append(None)

#Finding subjects
subjects_CD = []
for index, row in df4.iterrows():
    #print(len(df4.loc[index,'tokens']))
    for i in range(0,len(df4.loc[index,'tokens'])):
        if df4.loc[index,'dep'][i] == 'nsubj' or df4.loc[index,'dep'][i] == 'csubj':
            subjects_CD.append('Y')
        else:
            subjects_CD.append(None)

#Finding compound Nouns (will exclude phrases like '$1 billion dollars')

compounds_CD = []
for index, row in df4.iterrows():
    #print(len(df4.loc[index,'tokens']))
    for i in range(0,len(df4.loc[index,'tokens'])):
        if df4.loc[index,'dep'][i]=='compound' and (df4.loc[index,'pos'][i] == 'NOUN' and df4.loc[index,'pos'][i] == 'PROPN'):
            compounds_CD.append('Y')
        else:
            compounds_CD.append(None)

#Finding gerunds
# # #Note: as per Penn Treebank Tag Set, gerunds can be tagged as "VBG" when used as a verb
# # #However, do not want to double count as subject or verb below, so must discount for those cases.
# #
# # #Note: noun gerunds labeled as "Noun" by Spacy, though they end in 'ing' by defintiion and are caught in  sub_noun above

gerunds_CD = []
for index, row in df4.iterrows():
    #print(len(df4.loc[index,'tokens']))
    for i in range(0,len(df4.loc[index,'tokens'])):
        if df4.loc[index,'tag'][i]=='VBG' and (df4.loc[index,'dep'][i] != 'nsubj' and df4.loc[index,'dep'][i] != 'csubj'):
            gerunds_CD.append('Y')
        else:
            gerunds_CD.append(None)

#Finding verbs:
# Find and replace instances of "wanted", "need" or "needed" and replace with "want"
verbs_CD = []
for index, row in df4.iterrows():
    #print(len(df4.loc[index,'tokens']))
    for i in range(0,len(df4.loc[index,'tokens'])):
        if df4.loc[index,'pos'][i]=='VERB' and df4.loc[index,'tag'][i] != 'VBG':
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

for i in range(0,len(stepz)):
      chunks_nouns.append(nouns_CD[start[i]:stepz[i]])
      chunks_verbs.append(verbs_CD[start[i]:stepz[i]])
      chunks_compounds.append(compounds_CD[start[i]:stepz[i]])
      chunks_gerunds.append(gerunds_CD[start[i]:stepz[i]])
      chunks_propernouns.append(propernouns_CD[start[i]:stepz[i]])
      chunks_subjects.append(subjects_CD[start[i]:stepz[i]])

df_conceptual_density = pd.DataFrame(
    {'verbs_CD': chunks_verbs,
     'nouns_CD': chunks_nouns,
     'compounds_CD': chunks_compounds,
     'gerunds_CD': chunks_gerunds,
     'propernouns_CD': chunks_propernouns,
     'subjects_CD': chunks_subjects
    })

#calculating num_word and tallying results
df_conceptual_density['n_word'] = df3['Revised US'].str.split().str.len()
def count_Y(s):
    return s.count('Y')

df_conceptual_density['noun_count'] = df_conceptual_density['nouns_CD'].apply(count_Y)
df_conceptual_density['propernoun_count'] = df_conceptual_density['propernouns_CD'].apply(count_Y)
df_conceptual_density['subject_count'] = df_conceptual_density['subjects_CD'].apply(count_Y)
df_conceptual_density['gerund_count'] = df_conceptual_density['gerunds_CD'].apply(count_Y)
df_conceptual_density['compound_count'] = df_conceptual_density['compounds_CD'].apply(count_Y)
df_conceptual_density['verb_count'] = df_conceptual_density['verbs_CD'].apply(count_Y)

#Preparing for printed outputs
df_conceptual_density_to_excel = pd.DataFrame()
df_conceptual_density_to_excel['Revised US'] = df3['Revised US'].copy()

# df_conceptual_density = df_conceptual_density_to_excel[['Revised US', 'n_word', 'Lexical Ambiguity per Word', 'Sentence Lexical Ambiguity']]


# #------A: Entity Density (rho_entity) [see Lucassen reference above]
# #rho_ent = num_ent / (num_word - num_tmpl)
# # where num_ent = sum (#entities above) / (# words in sentence - num words in user story template)
#
# num_ent = noun_count + propernoun_count + subject_count + compound_count + gerund_count
# rho_ent = num_ent / (num_word - num_tmpl)
df_conceptual_density_to_excel['n_word'] = df_conceptual_density['n_word']
df_conceptual_density_to_excel['n_word - num_tmpl'] = df_conceptual_density['n_word'] - num_tmpl
df_conceptual_density_to_excel['num_ent'] = df_conceptual_density['noun_count'] + df_conceptual_density['compound_count'] + df_conceptual_density['propernoun_count'] + df_conceptual_density['gerund_count'] + df_conceptual_density['subject_count']

df_conceptual_density_to_excel['rho_ent'] = df_conceptual_density_to_excel['num_ent'] / df_conceptual_density_to_excel['n_word - num_tmpl']

# #------B: Relationship Density (rho_rel) [see Lucassen reference above]
# #rho_rel = num_rel / (num_word - num_tmpl)
# # where num_rel = sum (#relationships above) / (# words in sentence - num words in user story template)
#
# num_rel = sub_verb_count + sub_compound_count
# rho_rel =  num_rel / (num_word - num_tmpl)
#
df_conceptual_density_to_excel['num_rel'] = df_conceptual_density['verb_count'] + df_conceptual_density['compound_count']

df_conceptual_density_to_excel['rho_rel'] = df_conceptual_density_to_excel['num_rel'] / df_conceptual_density_to_excel['n_word - num_tmpl']

# #------C: Concept Density (rho_conc) [see Lucassen reference above]
# #rho_conc = rho_ent + rho_rel

#if n_word = num_tmpl or if rho_conc < 0, set rho_conc = 0
df_conceptual_density_to_excel['rho_conc'] = df_conceptual_density_to_excel['rho_ent'] + df_conceptual_density_to_excel['rho_rel']

for index, row in df_conceptual_density_to_excel.iterrows():
    if df_conceptual_density_to_excel.loc[index, 'rho_conc'] < 0:
       df_conceptual_density_to_excel.loc[index, 'rho_conc'] = 0
    elif df_conceptual_density_to_excel.loc[index,'n_word - num_tmpl'] == 0:
        df_conceptual_density_to_excel.loc[index, 'rho_conc'] = 0

#normalizing CD
max_CD = max(df_conceptual_density_to_excel['rho_conc'])
min_CD = min(df_conceptual_density_to_excel['rho_conc'])
diff = 0
diff = max_CD - min_CD
for index, row in df_conceptual_density_to_excel.iterrows():
    df_conceptual_density_to_excel.loc[index, 'rho_conc_norm'] = ((df_conceptual_density_to_excel.loc[index, 'rho_conc']) - min_CD) /diff

#---------------------------Semantic Similarity-------------------------------#
#uses Cosine similarity based out of SpaCy module.
#
# doc1 = nlp(u"my fries were super gross")
# doc2 = nlp(u"such disgusting fries")
# similarity = doc1.similarity(doc2)
# print(doc1.text, doc2.text, similarity)


################################# Supplementary Info #########################################
# This section of code builds a glossary of acronyms and ambiguous words for the user's benefit.

#---------------------------Building an Acronym Glossary-------------------#
#extracts acronyms and adds to a glossary for a user to define
# df_Acronyms_all = pd.DataFrame()
# df_Acronyms_Final = pd.DataFrame()
# #finds all acronyms per US
# df_Acronyms_all['Acronym List'] = df4['Revised US'].str.findall(r'\b[A-Z\.]{2,}s?\b')
#
# df_Acronyms_Final['Acronym List'] = df_Acronyms_all['Acronym List'].astype(str)

#remove duplicates within as ingle row and take out of parentheses
# removing duplicate acronyms
# df_Acronyms_all['Working'] = df_Acronyms_all['Acronym List'].apply(lambda x : tuple(x) if type(x) is list else x)
# df_Acronyms_all.drop_duplicates('Working', inplace = True)
#df_Acronyms_Final['Acronym List'] = df_Acronyms_Final['Acronym List'].str.extract(r'.*?([A-Za-z]+).*?', expand=True)

#----------------------------Ambiguous Term Details-----------------------------#
#if ambiguity > user defined threshold, then return.

#Lexical ambiguity details (synonyms, definitions, etc.)
#trunk_synsets = wn.synsets("trunks")
# for sense in trunk_synsets:
#     lemmas = [l.name() for l in sense.lemmas()]
#     print("Lemmas for sense : " + sense.name() + (" +sense.definition() +
#           " - " + str(lemmas))

#synset.name().split('.')[0]

# synonyms = []
# for syn in wordnet.synsets("good"):
# #     for l in syn.lemmas():
# #         synonyms.append(l.name())
# #
# # print(set(synonyms))
#

################################# Outputs #########################################
#----------------------------Writing data to Excel-----------------------------#

#---outputs for the user--------------------------------------------------------
writer = pd.ExcelWriter('RoboReq_Outputs.xlsx', engine='xlsxwriter')
writer_metrics = pd.ExcelWriter('RoboReq_Input_Metrics.xlsx', engine='xlsxwriter')
writer_simpleNLG = pd.ExcelWriter('RoboReq_to_SimpleNLG2.xlsx', engine='xlsxwriter')
df3.to_excel(writer, '"Scrubbed" Inputs')
#df4.to_excel(writer,'"Analyzed" Inputs')
#df_Acronyms_Final.to_excel(writer,'Acronym List')
df_to_SimpleNLG_final_FINAL.to_excel(writer_simpleNLG, 'SimpleNLG Final')

#--outputs for my analysis-----------------------------------------------------
df_ambig_to_excel.to_excel(writer_metrics, 'Ambiguity Metrics_baseline')
df_conceptual_density_to_excel.to_excel(writer_metrics, 'Conceptual Density_baseline')

writer.save()
writer_metrics.save()
writer_simpleNLG.save()
writer.close()
writer_metrics.close()
writer_simpleNLG.close()

#Writing input variations to excel
import xlsxwriter

xbook = xlsxwriter.Workbook('Test.xlsx')
xsheet = xbook.add_worksheet('Input Metrics')
xsheet2 = xbook.add_worksheet('Input Arrays')

for idx, item in enumerate(action_variation_names):
    xsheet.write(idx,0,action_variation_names[idx])
    xsheet.write(idx,1,action_variation_metrics[idx])

for idx, item in enumerate(role_metric_names):
    xsheet.write(idx,2,role_metric_names[idx])
    xsheet.write(idx,3,role_metrics[idx])

for idx, item in enumerate(benefit_metric_names):
    xsheet.write(idx,4,benefit_metric_names[idx])
    xsheet.write(idx,5,benefit_metrics[idx])

for idx, item in enumerate(compound_metric_names):
    xsheet.write(idx,6,compound_metric_names[idx])
    xsheet.write(idx,7,compound_metrics[idx])

for idx, item in enumerate(other_metric_names):
    xsheet.write(idx,8,other_metric_names[idx])
    xsheet.write(idx,9,other_metrics[idx])

for idx, item in enumerate(I_need):
    xsheet2.write(idx,0,I_need[idx])

for idx, item in enumerate(I_would_like):
    xsheet2.write(idx,1,I_would_like[idx])

for idx, item in enumerate(I_like):
    xsheet2.write(idx,2,I_like[idx])

for idx, item in enumerate(I_want):
    xsheet2.write(idx,3,I_want[idx])

for idx, item in enumerate(I_am):
    xsheet2.write(idx,4,I_am[idx])

for idx, item in enumerate(I_should):
    xsheet2.write(idx,5,I_should[idx])

for idx, item in enumerate(shall):
    xsheet2.write(idx,6,shall[idx])

for idx, item in enumerate(I_have):
    xsheet2.write(idx,7,I_have[idx])

for idx, item in enumerate(I_can):
    xsheet2.write(idx,8,I_can[idx])

for idx, item in enumerate(to_be_able_to):
    xsheet2.write(idx,9,to_be_able_to[idx])

for idx, item in enumerate(other):
    xsheet2.write(idx,10,other[idx])

xbook.close()


# pygame.mixer.music.stop()
print("Congratulations! Your results are ready.")

#------------------------Print Program Run Time Metrics-------------------------#
elapsed_time_secs = time.time() - start_time

msg = "Execution took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))

print(msg)
