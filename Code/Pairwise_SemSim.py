
#for writing to Excel
import openpyxl
from openpyxl import Workbook
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
from xlwt import Workbook


from collections import Counter

import spacy
nlp = spacy.load('en_core_web_lg')

from itertools import chain
from itertools import combinations

storyLine_inputs = 'StoryLine_Outputs.xls'
df_storyline_inputs = pd.read_excel(storyLine_inputs,  encoding = 'utf-8')
simpleNLG_outputs = 'SimpleNLG_Outputs.xls'
df_simpleNLG_outputs= pd.read_excel(simpleNLG_outputs, encoding = 'utf-8')
df_simpleNLG_outputs['StoryLine Revised US']  = df_simpleNLG_outputs['StoryLine Revised US'] .str.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u'\u201d', '"')

df_storyline_inputs_ref = df_storyline_inputs['Revised US'].copy()

#---------------------------------SemSim- Pairwise between Outputs---------------------------#
df_simpleNLG_outputs_copy = pd.DataFrame()
df_simpleNLG_outputs_copy['StoryLine Revised US'] = df_simpleNLG_outputs['StoryLine Revised US'].copy()

docs_simpleNlG_outputs_copy = df_simpleNLG_outputs_copy['StoryLine Revised US'].tolist()
docs_storyline_inputs = df_storyline_inputs['Revised US'].tolist()

doc_inputs_copy = nlp.pipe(docs_storyline_inputs)
doc_outputs_copy = nlp.pipe(docs_simpleNlG_outputs_copy)

#comb=combinations(docs_simpleNlG_outputs_copy, 2)
#comb_list = list(comb)

pairwise_score=[]
pairwise_combo = []
pairwise_combo2=[]
for i in range(len(docs_storyline_inputs)):
    #doca = nlp(comb_list[i][0])
    doca = nlp(docs_storyline_inputs[i])
    docb = nlp(docs_simpleNlG_outputs_copy[i])
    #docb = nlp(comb_list[i][1])
    pairwise_score.append(docb.similarity(doca))
    pairwise_combo.append(docs_storyline_inputs[i])
    pairwise_combo2.append(docs_simpleNlG_outputs_copy[i])
# Process test_pairwise so that it can fit into df for writing to excel
df_pairwise_semsim = pd.DataFrame()

df_pairwise_semsim['Output US1'] = pairwise_combo
df_pairwise_semsim['Output US2'] = pairwise_combo2

# for index, row in df_pairwise_semsim.iterrows():
#     df_pairwise_semsim.loc[index,'Output US1'] = df_pairwise_semsim.loc[index,'Output US Combinations'][0]
#     df_pairwise_semsim.loc[index,'Output US2'] = df_pairwise_semsim.loc[index,'Output US Combinations'][1]

df_pairwise_semsim['Pairwise SemSim Score'] = pairwise_score

# ############################### outputs to Excel for QFD#########################
writer = pd.ExcelWriter('Pairwise_SemSim_analysis.xls', engine='xlwt')
df_pairwise_semsim.to_excel(writer, 'Pairwise Semantic Similarity')

writer.save()
writer.close()
