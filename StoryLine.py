##################################################################################################
##################################################################################################
##################### Ussery, Sabrina Dissertation Research 2018 #################################

#The goal of the StoryLine program is to improve the quality of user stories in accordance with the QUS frameworkself.
#The program is divided into three components:

#1) Data preprocessor (Python)
 #Ensures user stories are minimal by removing non-primary sentences and text within parentheses or brackets.
 #Ensures the means of user stories are uniform and follow a “I want to <some goal>” format.

#2) Linguistic parser (Python + Spacy) -
 #Ensures user stories are well-formed, including a role, means, and an end.
 #Ensures user stories are atomic, containing no coordinating conjunction and representing a single feature request.

#3) Simple NLG (Java)
 #Ensures user stories are grammatically correct and are modified in accordance with the user story template.

#Working Dataframes:
# df
# df2
# df4
# df_to_SimpleNLG

#Output (to Excel) dataframes:
# df3
# df_to_SimpleNLG_final
# df_to_SimpleNLG_final_FINAL

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

# for spell checker
from autocorrect import spell
from num2words import num2words

#StoryLine Intro and README
print("StoryLine is starting!")

###############################Inputs###############################################
import sys
file = sys.argv[1]
#file = 'Requirements_Input.xlsx'
df = pd.read_excel(file, encoding = 'utf-8')

#Global function that is used throughout this program to flatten lists.
from collections import Iterable

def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

# Standardizing inputs

df['US'] = df['US'].str.replace('&',' and ')
df['US'] = df['US'].str.replace('|',' or ')
df['US'] = df['US'].str.replace(' and/or ',' or ')
df['US'] = df['US'].str.replace('/',' or ')
df['US'] = df['US'].str.replace('%',' percent ')
df['US'] = df['US'].str.replace(', , ',', ')
df['US'] = df['US'].str.replace(', when ',' when ')
df['US'] = df['US'].str.replace('when ,', ' when ')
df['US'] = df['US'].str.replace('  ',' ')
df['US'] = df['US'].str.replace('etc.','etcetera')
df['US'] = df['US'].str.replace('10. 04.','10v04 ')
df['US'] = df['US'].str.replace('-',' ')
df['US'] = df['US'].str.replace(u'\u2013','').replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u'\u201d', '"').replace(u'\u2022','')
df['US'] = (df['US'].str.split()).str.join(' ')
df['US'] = df['US'].str.replace(" xml ",' XML ')
df['US'] = df['US'].str.replace(" api.",' API.')
df['US'] = df['US'].str.replace(" url ",' URL ')
df['US'] = df['US'].str.replace('“','')
df['US'] = df['US'].str.replace('”','')

# Identifying acronyms
#---Regex debugger - https://regex101.com/
df['Acronyms'] = df['US'].str.findall(r'\b([A-Z]{3}-[0-9]|[A-Z][a-zA-Z]*[A-Z][a-z]*)\b')

for index,row in df.iterrows():
    if df.loc[index,'Acronyms']!= None:
       df.loc[index,'Acronyms'] = set(df.loc[index,'Acronyms'])
       df.loc[index,'Acronyms'] = ", ".join(str(x) for x in df.loc[index,'Acronyms'])
#################################################################################
############################Data Preprocessor###################################
#Ensures user stories are minimal by removing non-primary sentences and text within parentheses or brackets.
#Ensures the means of user stories are uniform and follow a “I want to <some goal>” format.

# When a User story has more than one sentence, this function will split all non-primary
# sentences and store them in a new column called "Supplementary Notes" that can be used in the user story's
# description, instead of in the primary user story itself.

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
if 'sent_1' in df2.columns:
    df2['Supplementary Notes'] = df2['sent_1'].astype(str)
if 'sent_2' in df2.columns:
    df2['Supplementary Notes'] = df2['sent_1'].astype(str) + df2['sent_2'].astype(str)
if 'sent_3' in df2.columns:
    df2['Supplementary Notes'] = df2['sent_1'].astype(str) + df2['sent_2'].astype(str) + df2['sent_3'].astype(str)
if 'sent_4' in df2.columns:
    df2['Supplementary Notes'] = df2['sent_1'].astype(str) + df2['sent_2'].astype(str) + df2['sent_3'].astype(str)+ df2['sent_4'].astype(str)

df3 = df2[['Revised US', 'Supplementary Notes']].copy()
df3['Original US'] = df['US'].copy()
df3['Acronyms'] = df['Acronyms'].copy()
df3 = df3[['Original US','Revised US','Supplementary Notes', 'Acronyms']]

#When a User story contains Parenthetical information, this function will remove them
#information from the US text and store it in a new column called "Additional Notes" that
#can be used in the user story's description, instead of in the primary user story itself.

#extract data from between parentheses
df2['Parenthetical Info'] = df3['Revised US'].apply(lambda x: re.findall('\((.*?)\)',x))

#extract word before parentheses for context
df2['Paren_Prefix_working'] = df3['Revised US'].str.split('(', 1)

for index, row in df2.iterrows():
    df2.loc[index,'Paren_Prefix_working_split'] = row['Paren_Prefix_working'][0]
df2['Paren_Prefix_working_split'] = df2['Paren_Prefix_working_split'].str.split()

for index, row in df2.iterrows():
    df2.loc[index,'Paren_Prefix_last_word'] = row['Paren_Prefix_working_split'][-1]

df2['Paren_Prefix_last_word'] = df2['Paren_Prefix_last_word'].str.strip('.')

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

# This function replaces contractions with their full word equivalents so that tokenization,
# performed later, maintains the integrity of the user's inputs.

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
df3['Revised US'] = df3['Revised US'].str.replace("it's",' it is')
df3['Revised US'] = df3['Revised US'].str.replace(".",' .')

# spell checker (Note: misspells "frontend" to "fronted" and "preffered" to "proffered")
df3['US_spellcheck'] = df3['Revised US'].str.split()
for index,row in df.iterrows():
    for i in range(0, len(df3.loc[index,'US_spellcheck'])):
        #convert numbers to word format
        if df3.loc[index,'US_spellcheck'][i].isdigit() and df3.loc[index,'US_spellcheck'][i]!='19115' and df3.loc[index,'US_spellcheck'][i]!='1GB' and df3.loc[index,'US_spellcheck'][i]!='SWORD2':
             df3.loc[index,'US_spellcheck'][i]= num2words(df3.loc[index,'US_spellcheck'][i])

#Note: code uses most likely spelling, however, corrected spelling may not be correct.
misspelled = []
for index,row in df.iterrows():
    misspelled = []
    for i in range(0, len(df3.loc[index,'US_spellcheck'])):
        if spell(df3.loc[index,'US_spellcheck'][i]) != df3.loc[index,'US_spellcheck'][i] and "." not in df3.loc[index,'US_spellcheck'][i] and "-" not in df3.loc[index,'US_spellcheck'][i] and "'" not in df3.loc[index,'US_spellcheck'][i] and '"' not in df3.loc[index,'US_spellcheck'][i] and ":" not in df3.loc[index,'US_spellcheck'][i] and ";" not in df3.loc[index,'US_spellcheck'][i] and  "," not in df3.loc[index,'US_spellcheck'][i] and df3.loc[index,'US_spellcheck'][i]!='1GB' and df3.loc[index,'US_spellcheck'][i]!='SWORD2':
            misspelled.append(df3.loc[index,'US_spellcheck'][i])
            df3.loc[index,'Misspelled Words'] = misspelled
            if df3.loc[index,'US_spellcheck'][i] not in df3.loc[index,'Acronyms']:
                df3.loc[index,'US_spellcheck'][i] = spell(df3.loc[index,'US_spellcheck'][i])
            df3.loc[index,'Misspelled Words'] = ", ".join(str(x) for x in df3.loc[index,'Misspelled Words'])
    df3.loc[index,'US_spellcheck'] = " ".join(str(x) for x in df3.loc[index,'US_spellcheck'])

# if mispelled word is an acronym, remove it from the mispelled words list.
df3['Misspelled Words'] = df3['Misspelled Words'].str.replace(r'\b([A-Z]{3}-[0-9]|[A-Z][a-zA-Z]*[A-Z][a-z]*)\b','').replace(', ','')

# lowercasing all user stories to minimize tagging errors (only acronyms, proper pronouns, and acronyms capitalized)
df3['US_spellcheck'] = df3['US_spellcheck'].apply(lambda x: x.lower())
df3['US_spellcheck'] = df3['US_spellcheck'].str.capitalize()
df3['US_spellcheck'] = df3['US_spellcheck'].str.replace(' i ', ' I ')

#capitalize acronyms
df3['Split US'] = df3['US_spellcheck'].str.split()

df3['Acronyms_lower'] = df3['Acronyms'].str.lower()

for index, row in df3.iterrows():
    for i in range(0, len(df3.loc[index,'Split US'])):
         if df3.loc[index,'Split US'][i].lower() in df3.loc[index,'Acronyms_lower']:
             df3.loc[index,'Split US'][i] = df3.loc[index,'Split US'][i].upper()

for index,row in df3.iterrows():
      df3.loc[index,'Split US'] = list(flatten([x for x in df3.loc[index,'Split US'] if x is not None]))
      df3.loc[index,'Split US'] = " ".join(str(x) for x in df3.loc[index,'Split US'])
      df3.loc[index,'Split US'] = df3.loc[index,'Split US'].replace(' ,','')

df3['US_spellcheck'] = df3['Split US']
#reassign Revised US since rest of code depends on it----------------

df3['Revised US'] = df3['US_spellcheck']

for index, row in df3.iterrows():
    if " so " in df3.loc[index,'Revised US'] and " so that" not in df3.loc[index,'Revised US'] and " so on" not in df3.loc[index,'Revised US'] and " also " not in df3.loc[index,'Revised US'] :
        df3.loc[index,'Revised US'] = df3.loc[index,'Revised US'].replace(" so ", " so that ")

df3['Revised US'] = df3['Revised US'].str.replace(' I want',', I want')
df3['Revised US'] = df3['Revised US'].str.replace(' A ',' a ').replace(' AN ', ' an ')
df3['Revised US'] = df3['Revised US'].str.replace(' I need',', I need')
df3['Revised US'] = df3['Revised US'].str.replace(' I would like',', I would like')
df3['Revised US'] = df3['Revised US'].str.replace(' she would',', she would')
df3['Revised US'] = df3['Revised US'].str.replace(' I can',', I can')
df3['Revised US'] = df3['Revised US'].str.replace(' I should',', I should')
df3['Revised US'] = df3['Revised US'].str.replace(' I am',', I am')
df3['Revised US'] = df3['Revised US'].str.replace(' I like',', I like')
df3['Revised US'] = df3['Revised US'].str.replace('so that,','so that')
df3['Revised US'] = df3['Revised US'].str.replace('  ',' ')
df3['Revised US'] = df3['Revised US'].str.replace(',,', ',')

# removing "point zero" from num to word translation
df3['Revised US'] = df3['Revised US'].str.replace(" point zero ",' ')
df3['Revised US'] = df3['Revised US'].str.replace(" UTF eight ",' UTF 8 ')
df3['Revised US'] = df3['Revised US'].str.replace(" TO ",' to ')
df3['Revised US'] = df3['Revised US'].str.replace(" accel ",' Accela ').replace(" acoela ", " Accela ")
df3['Revised US'] = df3['Revised US'].str.replace(" icel ",' iCal ')
df3['Revised US'] = df3['Revised US'].str.replace(" lashups ",' mashups ')
df3['Revised US'] = df3['Revised US'].str.replace(" sealpoints ",' mealpoints ')
df3['Revised US'] = df3['Revised US'].str.replace(" fronted ",' frontend ')
df3['Revised US'] = df3['Revised US'].str.replace("Fronted ",'Frontend ')
df3['Revised US'] = df3['Revised US'].str.replace(" proffered ",' preferred ')
df3['Revised US'] = df3['Revised US'].str.replace(" ivy ",' IPv6 ')
df3['Revised US'] = df3['Revised US'].str.replace(" enuf ",' enum ')
df3['Revised US'] = df3['Revised US'].str.replace("Backed ",'Backend ')
df3['Revised US'] = df3['Revised US'].str.replace("Fronted ",'Fronted ')
df3['Revised US'] = df3['Revised US'].str.replace(" sword2 ",' SWORD2 ')
df3['Revised US'] = df3['Revised US'].str.replace(" wanted add ",' wanted ad ')
df3['Revised US'] = df3['Revised US'].str.replace(" AN ",' an ')
df3['Revised US'] = df3['Revised US'].str.replace(" E mail ",' e-mail ').replace('email', 'e-mail')
df3['Revised US'] = df3['Revised US'].str.replace("AS ",'As ')
df3['Revised US'] = df3['Revised US'].str.replace(" VIEW ",' view ')
df3['Revised US'] = df3['Revised US'].str.replace(" re enter ",' re-enter ')
df3['Revised US'] = df3['Revised US'].str.replace('trident ','Trident ')
df3['Revised US'] = df3['Revised US'].str.replace(" scrum alliance ",' Scrum Alliance ')
df3['Revised US'] = df3['Revised US'].str.replace(" SCRUM alliance ",' Scrum Alliance ')
df3['Revised US'] = df3['Revised US'].str.replace(" urns",' URNs')
df3['Revised US'] = df3['Revised US'].str.replace(" urn ",' URN ')
df3['Revised US'] = df3['Revised US'].str.replace(" DOIS ",' DOIs ')
df3['Revised US'] = df3['Revised US'].str.replace(" duke ",' Duke ')
df3['Revised US'] = df3['Revised US'].str.replace(" acoela ",' Acoela ')
df3['Revised US'] = df3['Revised US'].str.replace(" URLS ",' URLs ')
df3['Revised US'] = df3['Revised US'].str.replace(" refferals ",' referrals ')
df3['Revised US'] = df3['Revised US'].str.replace(" ids ",' IDs ')
df3['Revised US'] = df3['Revised US'].str.replace(" 's", "'s")
df3['Revised US'] = df3['Revised US'].str.replace(" i ", " I ")
df3['Revised US'] = df3['Revised US'].str.replace("want do not ", "do not ")
df3['Revised US'] = df3['Revised US'].str.replace(" emailed ", " e-mailed ")
df3['Revised US'] = df3['Revised US'].str.replace(" meta data ", " metadata ")
df3['Revised US'] = df3['Revised US'].str.replace(" houghton ", " Houghton ")
df3['Revised US'] = df3['Revised US'].str.replace(" IS ", " is ")
df3['Revised US'] = df3['Revised US'].str.replace("' ", " ")
df3['Revised US'] = df3['Revised US'].str.replace("'", " ")
df3['Revised US'] = df3['Revised US'].str.replace(" re user ", " reuser ")
df3['Revised US'] = df3['Revised US'].str.replace(" neurohub ", " Neurohub ")
df3['Revised US'] = df3['Revised US'].str.replace(" neurohub", " Neurohub")
df3['Revised US'] = df3['Revised US'].str.replace(" southampton ", " Southampton ")
df3['Revised US'] = df3['Revised US'].str.replace(" IT MANAGER", " IT Manager")
df3['Revised US'] = df3['Revised US'].str.replace(" SCRUMMASTER ", " ScrumMaster ")
df3['Revised US'] = df3['Revised US'].str.replace(" PLANTHISTORIAN ", " PlantHistorian ")
df3['Revised US'] = df3['Revised US'].str.replace(" PLANTVIEWER ", " PlantViewer ")
df3['Revised US'] = df3['Revised US'].str.replace(" mendeley ", " Mendeley ")
df3['Revised US'] = df3['Revised US'].str.replace(" CITEMANAGER ", " Citemanager ")

#################################################################################
############################Linguistic Parser#####################################
#Ensures user stories are well-formed, including a role, means, and an end.
#Ensures user stories are atomic, containing no coordinating conjunction and representing a single feature request.
#Extracts key pieces of user stories - subject, action phrases, prep phrases, adverb phrases, etc. - for passing to df_to_SimpleNLG

# SpaCy Tagging and Dependency Analysis
df4 = pd.DataFrame()
df4['Revised US'] = df3['Revised US'].copy()
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
#df4['noun_phrases'] = noun_phrases

#------------------------Finding incomplete inputs-----------------------------#
# Inputs must have at least a verb and a noun. Else, the resulting improvements
# from StoryLine will result in sentence fragments.

for index, row in df4.iterrows():
    if 'VERB' in df4.loc[index,'pos'] and 'NOUN' in df4.loc[index,'pos']:
        df3.loc[index,"Completeness"] = "Yes"
    else:
        df3.loc[index,"Completeness"] = "No"

# -----------------------Finding user story roles----------------------------------#
# Follows dep pattern: ADP DET .... PRON (As a ....I) or ADP NOUN..., etc.
# If role exists, will appear as the first entry in the prep phrases list per US

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

roles = []
for index, row in df4.iterrows():
    if df4.loc[index,'roles_working']!='' and len(df4.loc[index,'roles_working'])> 1 and ("As a" in df4.loc[index,'roles_working'][0] or "As " in df4.loc[index,'roles_working'][0]) and ("As of " not in df4.loc[index,'roles_working'][0] and "As well as" not in df4.loc[index,'roles_working'][0] and "As being" not in df4.loc[index,'roles_working'][0]):
        roles.append(df4.loc[index,'roles_working'][0])
    elif df4.loc[index,'roles_working']!='' and len(df4.loc[index,'roles_working'])> 1 and "As a" not in df4.loc[index,'roles_working'][0]  and ("As a" in df4.loc[index,'roles_working'][1] or "As " in df4.loc[index,'roles_working'][0]) and ("As of " not in df4.loc[index,'roles_working'][1] and "As well as" not in df4.loc[index,'roles_working'][1] and "As being" not in df4.loc[index,'roles_working'][1]):
        roles.append(df4.loc[index,'roles_working'][1])
    elif df4.loc[index,'roles_working']!='' and len(df4.loc[index,'roles_working'])==1 and ("As a" in df4.loc[index,'roles_working'][0] or "As " in df4.loc[index,'roles_working'][0]) and ("As of " not in df4.loc[index,'roles_working'][0] and "As well as" not in df4.loc[index,'roles_working'][0] and "As being" not in df4.loc[index,'roles_working'][0]):
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
       df4.loc[index,'role'] = "As a default role"

df4['role'] = df4['role'].str.replace(',', '')

#find role pos for adverb phrase identification
def find_role_pos(x, y):
    if x!='':
        return y[0:x]
    else:
        return y

df4['role pos'] = df4.apply(lambda row: find_role_pos(row['role_end_index'], row['pos']), axis=1)

#returning the rest of the user story, after the role
def find_after_user_phrase(x, y):
    if x!='':
        return y[x:]
    else:
        return y

df4['after_user_phrase'] = df4.apply(lambda row: find_after_user_phrase(row['role_end_index'], row['tokens']), axis=1)
#-----------------Finding user story ends---------------------------------------
# Follows the following POS pattern: ADP ADP..... (so that...)
# and the following dep pattern: mark mark .... (so that....)

for index, row in df4.iterrows():
       if " so that " in df4.loc[index,'Revised US'] and " so that ." not in df4.loc[index,'Revised US'] :
            df4.loc[index, 'Has_benefit'] = "True"
       else:
            df4.loc[index, 'Has_benefit'] = "False"

def find_benefit_index(US):
    return [i for i, elem in enumerate(US) if elem =='so']
df4['find_benefit_start_index'] = df4['after_user_phrase'].apply(find_benefit_index)

benefits = []
for index, row in df4.iterrows():
    if df4.loc[index,'Has_benefit'] == 'True':
        benefits.append(df4.loc[index,'find_benefit_start_index'])
    else:
        benefits.append(None)

benefits_flat = list(flatten(benefits))

df4['find_benefit_start_index'] = benefits_flat
df4['find_benefit_start_index'] = df4['find_benefit_start_index'].fillna('')

# Finding instances of "so that.."
def find_benefit(x, y):
    if x!='':
        return y[x:]

# find start index for ends
for index,row in df4.iterrows():
    if df4.loc[index,'find_benefit_start_index']!='':
        df4.loc[index,'find_benefit_start_index'] = int(round(df4.loc[index,'find_benefit_start_index']))

df4['benefit'] = df4.apply(lambda row: find_benefit(row['find_benefit_start_index'], row['after_user_phrase']), axis=1)
df4['benefit pos'] = df4.apply(lambda row: find_benefit(row['find_benefit_start_index'], row['pos']), axis=1)

# flatten ends phrase; where ends does not exist, insert default ends.
for index, row in df4.iterrows():
    if df4.loc[index,'benefit']!= None:
       df4.loc[index,'benefit'] = " ".join(str(x) for x in df4.loc[index,'benefit'])
       df4.loc[index,'benefit'] =  df4.loc[index,'benefit'].replace(".", " ")
    else:
       df4.loc[index,'benefit'] = "so that default end"

#----------------Finding user story actions---------------------------------------
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

# finding start index for means
for index, row in df4.iterrows():
    if  df4.loc[index,'role_end_index']!='':
        df4.loc[index,'find_action_start_POS'] = df4.loc[index, 'role_end_index']
    else:
        df4.loc[index,'find_action_start_POS'] = 0

# finding end index for means
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
    else:
        return z

df4['action'] = df4.apply(lambda row: find_action(row['find_action_start_POS'], row['find_action_end_POS'], row['tokens']), axis=1)

def find_action_pos(x, y, z):
    if x!='' and y!='':
        return z[x:y]

df4['action_pos'] = df4.apply(lambda row: find_action_pos(row['find_action_start_POS'], row['find_action_end_POS'], row['pos']), axis=1)
df4['action tokens'] = df4.apply(lambda row: find_action_pos(row['find_action_start_POS'], row['find_action_end_POS'], row['tokens']), axis=1)

def find_action_dep(x, y, z):
    if x!='' and y!='':
        return z[x:y]

df4['action_dep'] = df4.apply(lambda row: find_action_dep(row['find_action_start_POS'], row['find_action_end_POS'], row['dep']), axis=1)

def find_action_head(x, y,z):
    if x!='' and y!='':
        return z[x:y]

df4['action_head'] = df4.apply(lambda row: find_action_head(row['find_action_start_POS'], row['find_action_end_POS'], row['head']), axis=1)

def find_action_tokens(x, y,z):
    if x!='' and y!='':
        return z[x:y]

df4['action_tokens'] = df4.apply(lambda row: find_action_tokens(row['find_action_start_POS'], row['find_action_end_POS'], row['tokens']), axis=1)

#-----------------Trimming adverb phrases from user story roles/actions--------------------------

# adverb phrases in roles ------------------------
#Adverb phrases contain "when" start with POS ADV
def find_role_phrase_pos(x, y):
    if x!='':
        return y[0:x]
    else:
        return y

df4['role_phrase pos'] = df4.apply(lambda row: find_role_phrase_pos(row['role_end_index'],row['pos']), axis=1)

for index,row in df4.iterrows():
    if df4.loc[index,'role'] == "As a default role":
        df4.loc[index,'role_phrase pos'] = ''

#extract adverb phrase from roles
df4['role_split'] = df4['role'].str.split()

adverbphrase = []
for index, row in df4.iterrows():
    for i in range(0, len(df4.loc[index,'role_phrase pos'])):
        if df4.loc[index,'role_phrase pos'][i]=='ADV' and df4.loc[index,'tag'][i]=='WRB':
            #WRB POS Tag = Wh-adverb
            adverbphrase.append(df4.loc[index,'role_split'][i:])
        else:
            adverbphrase.append(None)

adverbphrase_flat = list(flatten(adverbphrase))

# splitting adverbphrase list by length of role_phrase pos so can insert adverb phrases into df4
step_adverb = []
for index, row in df4.iterrows():
    step_adverb.append(len(df4.loc[index,'role_phrase pos']))

stepz_adverb = []
start_adverb = []
stepz_adverb = [sum(step_adverb[:y]) for y in range(1, len(step_adverb) + 1)]
start_adverb = [m - n for m,n in zip(stepz_adverb,step_adverb)]

adverbphrase_div = []
for i in range(0,len(stepz_adverb)):
       adverbphrase_div.append(adverbphrase[start_adverb[i]:stepz_adverb[i]])

# filting out none values
df_adverbphrases= pd.DataFrame()

df_adverbphrases['adverbphrase'] = adverbphrase_div

# role based adverb phrases at beginning of actions/means ("<adverb phrase>, I want/need/am")
for index, row in df4.iterrows():
    if df4.loc[index,'action_pos'][0]=='ADV' and df4.loc[index,'action'][0] =='when' and 'I' in df4.loc[index,'action']:
        comma_index = df4.loc[index,'action'].index(",")
        df_adverbphrases.loc[index, 'adverbphrase'] = df4.loc[index,'action'][0:comma_index]

for index,row in df_adverbphrases.iterrows():
      df_adverbphrases.loc[index,'adverbphrase'] = list(flatten([x for x in df_adverbphrases.loc[index,'adverbphrase'] if x is not None]))
      df_adverbphrases.loc[index,'adverbphrase'] = " ".join(str(x) for x in df_adverbphrases.loc[index,'adverbphrase'])
      df_adverbphrases.loc[index,'adverbphrase'] = df_adverbphrases.loc[index,'adverbphrase'].replace(' ,','')

df4['adverb phrase'] = df_adverbphrases['adverbphrase'].copy()

# adverb phrases from actions (if, when)

################### Prepping inputs for SimpleNLG###################
# Includes the identification of subjects, verb phrases, and modifier phrases (prep and adverb phrases)
# user story roles and ends along with means (SVO / SVOO) serve as input to SimpleNLG
# Means = Subject ("I") + verb phrase ("want" / "want to" + action phrase[VO/VOO]), where
# VO is verb + (Noun + object phrase) and VOO is the same with an optional Prepositional phrase or adverb phrase, if either exists

df_to_SimpleNLG_final = pd.DataFrame()

df_to_SimpleNLG_final['role_phrase'] = df4['role']
df_to_SimpleNLG_final['benefit_phrase'] = df4['benefit']
df_to_SimpleNLG_final['action'] = df4['action']
df_to_SimpleNLG_final['action subject'] = "I"
df_to_SimpleNLG_final['adverb phrase'] = df4['adverb phrase']
df_to_SimpleNLG_final['action pos'] = df4['action_pos']
df_to_SimpleNLG_final['action dep'] = df4['action_dep']
df_to_SimpleNLG_final['action head'] = df4['action_head']
df_to_SimpleNLG_final['action tokens'] = df4['action_tokens']

#--finding action prepositional phrases-----------------------------------
# to find VO/VOO phrases in trimmed actions, need to know where the first pos = ADP starts,
# as this starts the segment of prepositional phrases. For simplicity, v0.1 of StoryLine
# assumes a single action prep phrase(s), starting with the first 'ADP' and ending with the action phrase.

length_trimmed_pos = []
index_first_ADP = []

for index, row in df_to_SimpleNLG_final.iterrows():
    length_trimmed_pos.append(len(df_to_SimpleNLG_final.loc[index,'action pos']))
    for i in range(0,len(df_to_SimpleNLG_final.loc[index,'action pos'])):
        if df_to_SimpleNLG_final.loc[index,'action pos'][i] == "ADP" and df_to_SimpleNLG_final.loc[index,'action dep'][i] =='prep':
            index_first_ADP.append(i)
        else:
            index_first_ADP.append(None)

step_trimmedadp = [sum(length_trimmed_pos[:y]) for y in range(1, len(length_trimmed_pos) + 1)]
start_trimmedadp = [m - n for m,n in zip(step_trimmedadp,length_trimmed_pos)]

# #split by # of mean prep_phrases per US
split_trimmed_action_ADP = []
for i in range(len(length_trimmed_pos)):
     split_trimmed_action_ADP.append(index_first_ADP[start_trimmedadp[i]:step_trimmedadp[i]])

df_to_SimpleNLG_final['index_action ADPs'] = split_trimmed_action_ADP

#finding first instance of ADP if more than one exists.
df_to_SimpleNLG_final['index_action ADPs'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['index_action ADPs']]

for index, row in df_to_SimpleNLG_final.iterrows():
    if len(df_to_SimpleNLG_final.loc[index,'index_action ADPs']) > 0:
        df_to_SimpleNLG_final.loc[index,'index_prep start'] = (min(df_to_SimpleNLG_final.loc[index,'index_action ADPs']))
    else:
        df_to_SimpleNLG_final.loc[index,'index_prep start'] = None

df_to_SimpleNLG_final['index_prep start'] = df_to_SimpleNLG_final['index_prep start'].fillna('')

for index,row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'index_prep start']!='':
        df_to_SimpleNLG_final.loc[index,'index_prep start'] = int(round(df_to_SimpleNLG_final.loc[index,'index_prep start']))

def action_pps(x,y):
    if y!='':
        return x[y:]

df_to_SimpleNLG_final['action prep phrases']= df_to_SimpleNLG_final.apply(lambda row: action_pps(row['action tokens'], row['index_prep start']), axis=1)

# Removing periods from prep phrases since will be added by SimpleNLG
for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'action prep phrases']!= None and df_to_SimpleNLG_final.loc[index,'action prep phrases'][-1] =='.':
       df_to_SimpleNLG_final.loc[index,'action prep phrases'] = df_to_SimpleNLG_final.loc[index,'action prep phrases'][0:-1]

for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'action prep phrases']!= None:
       df_to_SimpleNLG_final.loc[index,'action prep phrases'] = " ".join(str(x) for x in df_to_SimpleNLG_final.loc[index,'action prep phrases'])
       df_to_SimpleNLG_final.loc[index,'action prep phrases'] = df_to_SimpleNLG_final.loc[index,'action prep phrases'].replace(' ,','')
    else:
       df_to_SimpleNLG_final.loc[index,'action prep phrases'] = ''

for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'action']!= None:
       df_to_SimpleNLG_final.loc[index,'action'] = " ".join(str(x) for x in df_to_SimpleNLG_final.loc[index,'action'])
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' ,','')

#trimming out the rest of the action phrase, without the prep phrase
for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'action prep phrases']!='':
        df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(df_to_SimpleNLG_final.loc[index,'action prep phrases'], '')

#####################################User Story Part Cleanup - for SimpleNLG###############################################################################

#-----cleanup user story ends---------------------------------------------------
df_to_SimpleNLG_final['benefit_phrase'] = df_to_SimpleNLG_final['benefit_phrase'].str.replace(" i ", " I ")
df_to_SimpleNLG_final['benefit_phrase'] = df_to_SimpleNLG_final['benefit_phrase'].str.replace(" '", "'")
df_to_SimpleNLG_final['benefit_phrase'] = df_to_SimpleNLG_final['benefit_phrase'].str.replace(', I ', 'I ')

for index, row in df_to_SimpleNLG_final.iterrows():
 if "  " in df_to_SimpleNLG_final.loc[index,'benefit_phrase']:
    df_to_SimpleNLG_final.loc[index,'benefit_phrase'] = df_to_SimpleNLG_final.loc[index,'benefit_phrase'].replace('  ',' ')

for index, row in df_to_SimpleNLG_final.iterrows():
 if " ." in df_to_SimpleNLG_final.loc[index,'benefit_phrase']:
    df_to_SimpleNLG_final.loc[index,'benefit_phrase'] = df_to_SimpleNLG_final.loc[index,'benefit_phrase'].replace(' .',' ')

for index, row in df_to_SimpleNLG_final.iterrows():
 if "." in df_to_SimpleNLG_final.loc[index,'benefit_phrase']:
    df_to_SimpleNLG_final.loc[index,'benefit_phrase'] = df_to_SimpleNLG_final.loc[index,'benefit_phrase'].replace('.',' ')

#-----cleanup user story roles--------------------------------------------------
df_to_SimpleNLG_final['role_phrase'] = df_to_SimpleNLG_final['role_phrase'].str.replace(" '", "'")

for index, row in df_to_SimpleNLG_final.iterrows():
 if "  " in df_to_SimpleNLG_final.loc[index,'role_phrase']:
    df_to_SimpleNLG_final.loc[index,'role_phrase'] = df_to_SimpleNLG_final.loc[index,'role_phrase'].replace('  ',' ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "as a" in  df_to_SimpleNLG_final.loc[index,'role_phrase']:
      df_to_SimpleNLG_final.loc[index,'role_phrase']= df_to_SimpleNLG_final.loc[index,'role_phrase'].replace("as a ", "As a ")

for index, row in df_to_SimpleNLG_final.iterrows():
    if " , " in  df_to_SimpleNLG_final.loc[index,'role_phrase']:
      df_to_SimpleNLG_final.loc[index,'role_phrase']= df_to_SimpleNLG_final.loc[index,'role_phrase'].replace(" , ", " ")

df_to_SimpleNLG_final['role_phrase'] = df_to_SimpleNLG_final['role_phrase'].str.replace(" i ", " I ")

# remove adverb phrases from roles
for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'adverb phrase'] in  df_to_SimpleNLG_final.loc[index,'role_phrase']:
      df_to_SimpleNLG_final.loc[index,'role_phrase']= df_to_SimpleNLG_final.loc[index,'role_phrase'].replace(df_to_SimpleNLG_final.loc[index,'adverb phrase'], "")

# cleanup user story actions -------------------------------
    # Cleanup actions by uncapitalizing non acronym first words and
    # adding "want" or "want to" to each user story action.
    # providing uniformity to action phrasing

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I should have " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I should have','to have')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I am " in df_to_SimpleNLG_final.loc[index,'action'] and " I am " not in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I am ','to be ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if ", I am " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(', I am ','to be ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I have " in df_to_SimpleNLG_final.loc[index,'action'] and  " I have " not in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I have ','to have ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " wants " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' wants ',' ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " should " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' should ',' to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " should have " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' should have ',' to have ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " must be " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' must be ',' to be ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " to be able to " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' to be able to ',' to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "to be able to " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('to be able to ','to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " to be able " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' to be able ',' to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "to be able " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('to be able ','to ')

for index, row in df_to_SimpleNLG_final.iterrows():
   if " inthe " in df_to_SimpleNLG_final.loc[index,'action']:
      df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' inthe ',' in the ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I want " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I want ','')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I do not want to " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I do not want to ','do not want to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I would like " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I would like ','')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I like " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I like ','')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I should be able " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I should be able ','')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I can have " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I can have ','to have ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I can " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I can ','to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "she would like " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('she would like ', '')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I need " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I need ', '')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " as well as " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' as well as ', ' and ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " shall be able to " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' shall be able to ',' to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " shall " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' shall ',' to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if "I to " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('I to ','to ')

for index, row in df_to_SimpleNLG_final.iterrows():
    if " to to " in df_to_SimpleNLG_final.loc[index,'action']:
       df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' to to ',' to ')

for index, row in df_to_SimpleNLG_final.iterrows():
 if "  " in df_to_SimpleNLG_final.loc[index,'action']:
    df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace('  ',' ')

for index, row in df_to_SimpleNLG_final.iterrows():
 if " needs " in df_to_SimpleNLG_final.loc[index,'action']:
    df_to_SimpleNLG_final.loc[index,'action'] = df_to_SimpleNLG_final.loc[index,'action'].replace(' needs ',' ')

df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(" i ", " I ")
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(" 's", "'s")
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(" '", "'")
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace("that to have ", "")
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace('  ',' ')
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(" '","'")
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace('.', '')
df_to_SimpleNLG_final['action'] = df_to_SimpleNLG_final['action'].str.replace(', ','')

df4['action_split'] = df_to_SimpleNLG_final['action'].str.split()

for index,row in df4.iterrows():
    if len(df4.loc[index,'action_split'])!= 0 and df4.loc[index,'action_split'][0].islower()==False and df4.loc[index,'action_split'][0] not in df3.loc[index,'Acronyms']:
        df4.loc[index,'action_split'][0] = df4.loc[index,'action_split'][0].lower()

# change "are" + verb in action to be "to be" + verb (ex. "are displayed" -> "to be displayed"), when verb is last word in action
for index, row in df4.iterrows():
     for i in range(0, len(df4.loc[index,'action_split'])):
         if len(df4.loc[index,'action_split'])!= 0 and df4.loc[index,'action_split'][i].endswith('ed')==True and df4.loc[index,'action_split'][i-1] =='are' and df4.loc[index,'action_split'][i] == df4.loc[index,'action_split'][-1]:
             df4.loc[index,'action_split'][i-1] = 'to be'

for index, row in df4.iterrows():
    if len(df4.loc[index,'action_split'])!= None:
       df4.loc[index,'action_split'] = " ".join(str(x) for x in df4.loc[index,'action_split'])
       df4.loc[index,'action_split'] = df4.loc[index,'action_split'].replace(' ,','')

df_to_SimpleNLG_final['action'] = df4['action_split']

# determine if prefix of "want" or "want to" is appropriate given the rest of each action phrase.

for index, row in df4.iterrows():
    for i in range(0, len(df4.loc[index,'action_pos'])):
         if df4.loc[index,'action_pos'][0] =='VERB':
             df4.loc[index,'action_prefix']= "want to "
         elif df4.loc[index,'action_pos'][0] =='NOUN':
             df4.loc[index,'action_prefix']= "want the "
         else:
             df4.loc[index,'action_prefix']= "want "

df_to_SimpleNLG_final['full action phrase'] =  df4['action_prefix'] + df_to_SimpleNLG_final['action']

for index, row in df_to_SimpleNLG_final.iterrows():
     if " are to be " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" are to be ", " to be ")

for index, row in df_to_SimpleNLG_final.iterrows():
     if "we would like " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace("we would like ", "")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " I d " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" I d ", " ID ")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " I d" in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" I d", " ID")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " it to '" in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" it to '", " it's")

for index, row in df_to_SimpleNLG_final.iterrows():
     if "I to " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace("i to ", "to")

for index, row in df_to_SimpleNLG_final.iterrows():
    if " is " in df_to_SimpleNLG_final.loc[index, 'full action phrase'] and " that is" not in df_to_SimpleNLG_final.loc[index, 'full action phrase'] :
      df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" is ", " to be ")

for index, row in df_to_SimpleNLG_final.iterrows():
    if " system will " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
      df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" system will ", " system to ")

for index, row in df_to_SimpleNLG_final.iterrows():
    if " should be " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
      df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" should be ", " to be ")

for index, row in df_to_SimpleNLG_final.iterrows():
    if " should" in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
      df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" should", " to")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " to be to be " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" to be to be ", " to be ")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " to to " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" to to ", " to ")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " would like " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" would like ", " ")

for index, row in df_to_SimpleNLG_final.iterrows():
     if " to need " in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(" to need ", " ")

#remove adverb phrases from actions
for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'adverb phrase'] in df_to_SimpleNLG_final.loc[index,'full action phrase']:
      df_to_SimpleNLG_final.loc[index,'full action phrase']= df_to_SimpleNLG_final.loc[index,'full action phrase'].replace(df_to_SimpleNLG_final.loc[index,'adverb phrase'], "")

for index, row in df_to_SimpleNLG_final.iterrows():
     if "want  I am" in df_to_SimpleNLG_final.loc[index, 'full action phrase']:
       df_to_SimpleNLG_final.loc[index,'full action phrase'] = df_to_SimpleNLG_final.loc[index,'full action phrase'].replace("want  I am", "want to be")

# changing to a new DF for printing to Excel
df_to_SimpleNLG_final_FINAL = pd.DataFrame()

df_to_SimpleNLG_final_FINAL = df_to_SimpleNLG_final[[
 'role_phrase',
 'benefit_phrase',
 'action subject',
 'full action phrase',
 'action prep phrases',
 'adverb phrase'
 ]].copy()

#######################################De-coupling Compound (and/or) SVO/SVOO components#################

index_first_verb = []
for index, row in df_to_SimpleNLG_final.iterrows():
    for i in range(0,len(df_to_SimpleNLG_final.loc[index,'action pos'])):
        if df_to_SimpleNLG_final.loc[index,'action pos'][i] == "VERB":
            index_first_verb.append(i)
        else:
            index_first_verb.append(None)

step_trimmed_vp = [sum(length_trimmed_pos[:y]) for y in range(1, len(length_trimmed_pos) + 1)]
start_trimmed_vp = [m - n for m,n in zip(step_trimmed_vp, length_trimmed_pos)]

# split by # of means prep_phrases per US
trimmed_action_vp = []
for i in range(len(length_trimmed_pos)):
    trimmed_action_vp.append(index_first_verb[start_trimmed_vp[i]:step_trimmed_vp[i]])

df_to_SimpleNLG_final['index_first_verb'] = trimmed_action_vp
df_to_SimpleNLG_final['index_first_verb'] = [[x for x in inner_list if x is not None] for inner_list in df_to_SimpleNLG_final['index_first_verb']]

for index, row in df_to_SimpleNLG_final.iterrows():
    if len(df_to_SimpleNLG_final.loc[index,'index_first_verb']) > 0:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = (min(df_to_SimpleNLG_final.loc[index,'index_first_verb'])) + 1
    else:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = None

# capturing compound verb phrases (VERB CONJ VERB patterns, e.g. to create and update)
# supports up to 4 verbs

for index, row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'index_vp end'] + 5 in df_to_SimpleNLG_final.loc[index,'index_first_verb']:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = df_to_SimpleNLG_final.loc[index,'index_vp end'] + 6
    elif df_to_SimpleNLG_final.loc[index,'index_vp end'] + 4 in df_to_SimpleNLG_final.loc[index,'index_first_verb']:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = df_to_SimpleNLG_final.loc[index,'index_vp end'] + 5
    elif df_to_SimpleNLG_final.loc[index,'index_vp end'] + 3 in df_to_SimpleNLG_final.loc[index,'index_first_verb']:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = df_to_SimpleNLG_final.loc[index,'index_vp end'] + 4
    elif df_to_SimpleNLG_final.loc[index,'index_vp end'] + 2 in df_to_SimpleNLG_final.loc[index,'index_first_verb']:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = df_to_SimpleNLG_final.loc[index,'index_vp end'] + 3
    elif df_to_SimpleNLG_final.loc[index,'index_vp end'] + 1 in df_to_SimpleNLG_final.loc[index,'index_first_verb']:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = df_to_SimpleNLG_final.loc[index,'index_vp end'] + 2
    elif df_to_SimpleNLG_final.loc[index,'index_vp end'] in df_to_SimpleNLG_final.loc[index,'index_first_verb']:
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = df_to_SimpleNLG_final.loc[index,'index_vp end'] + 1

df_to_SimpleNLG_final['index_vp end'] = df_to_SimpleNLG_final['index_vp end'].fillna('')

for index,row in df_to_SimpleNLG_final.iterrows():
    if df_to_SimpleNLG_final.loc[index,'index_vp end']!='':
        df_to_SimpleNLG_final.loc[index,'index_vp end'] = int(round(df_to_SimpleNLG_final.loc[index,'index_vp end']))


#######################################De-coupled Compound Cleanup####################################


# Attach to df_to_SimpleNLG_final_FINAL for input to df_to_SimpleNLG

################################# Outputs #########################################
df3_trimmed = pd.DataFrame()
df3_trimmed = df3[['Original US', 'Revised US', 'Supplementary Notes', 'Acronyms', 'Misspelled Words', 'Completeness']].copy()

import xlwt
from xlwt import Workbook

# Workbook is created
wb = Workbook()

# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Sheet 1')
writer = pd.ExcelWriter('StoryLine_Outputs.xls', engine='xlwt')
#writer_metrics = pd.ExcelWriter('RoboReq_Input_Metrics.xls', engine='xlwt')
writer_simpleNLG = pd.ExcelWriter('StoryLine_to_SimpleNLG.xls', engine='xlwt')
df3_trimmed.to_excel(writer, '"Scrubbed" Inputs')
df4.to_excel(writer, "POS")
df_to_SimpleNLG_final_FINAL.to_excel(writer_simpleNLG, 'SimpleNLG Inputs')

writer.save()
writer_simpleNLG.save()
writer.close()
writer_simpleNLG.close()

print("Happy writing!")

# import subprocess
# subprocess.call("javac SimpleNLG.java", shell = True)
# subprocess.call("java SimpleNLG", shell = True)
