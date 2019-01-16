
#for writing to Excel
import openpyxl
from openpyxl import Workbook
from openpyxl.compat import range
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
nlp = spacy.load('en')

from itertools import chain
from itertools import combinations


simpleNLG_outputs = 'SimpleNLG_Outputs.xls'
df_simpleNLG_outputs= pd.read_excel(simpleNLG_outputs, encoding = 'utf-8')
df_simpleNLG_outputs['StoryLine Revised US']  = df_simpleNLG_outputs['StoryLine Revised US'] .str.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u'\u201d', '"')

#---------------------------------SemSim- Pairwise between Outputs---------------------------#
df_simpleNLG_outputs_copy = pd.DataFrame()
df_simpleNLG_outputs_copy['StoryLine Revised US'] = df_simpleNLG_outputs['StoryLine Revised US'].copy()

docs_simpleNlG_outputs_copy = df_simpleNLG_outputs_copy['StoryLine Revised US'].tolist()
doc_outputs_copy = nlp.pipe(docs_simpleNlG_outputs_copy)

comb=combinations(docs_simpleNlG_outputs_copy, 2)
comb_list = list(comb)

pairwise_score=[]
pairwise_combo = []
for i in range(len(comb_list)):
    doca = nlp(comb_list[i][0])
    docb = nlp(comb_list[i][1])
    pairwise_score.append(docb.similarity(doca))
    pairwise_combo.append(comb_list[i])
# Process test_pairwise so that it can fit into df for writing to excel
df_pairwise_semsim = pd.DataFrame()

df_pairwise_semsim['Output US Combinations'] = pairwise_combo

for index, row in df_pairwise_semsim.iterrows():
    df_pairwise_semsim.loc[index,'Output US1'] = df_pairwise_semsim.loc[index,'Output US Combinations'][0]
    df_pairwise_semsim.loc[index,'Output US2'] = df_pairwise_semsim.loc[index,'Output US Combinations'][1]

df_pairwise_semsim['Pairwise SemSim Score'] = pairwise_score

# ############################### outputs to Excel for QFD#########################
writer = pd.ExcelWriter('Pairwise_SemSim.xlsx', engine='xlsxwriter')
df_pairwise_semsim.to_excel(writer, 'Pairwise Semantic Similarity')

writer.save()
writer.close()
