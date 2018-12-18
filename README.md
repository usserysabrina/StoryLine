# StoryLine

StoryLine is a simple Python API designed to facilitate the generation of quality Agile requirements, commonly referred to as user stories. The tool was originally developed by Sabrina Ussery in fulfillment of doctoral research requirements at the George Washington University. 

StoryLine is based on the Quality User Story (QUS framework) developed by Lucassen et. al. 2015, which consists of 14 quality criteria that user story writers should strive to conform to. The tool takes as its input a set of draft user stories and, as its output, provides modifications to the input user stories to increase their quality. StoryLine's outputs are presented to the user in a Quality Function Deployment (QFD) based traceability report that allows the user to clearly see how each user story has evolved. Within the QFD report, the following feedback is also provided:

a). Spelling errors corrected in each user story,
b). Acronyms found in each user story (for use in requirements glossary),
c). Metrics indicating the level of ambiguity and conceptual density of each user story,
d). A user story duplication matrix, and
e). A user role coverage matrix.

To improve the quality of user stories, StoryLine depends on the linguistic processing capabilites of the Natural Language Toolkit (NLTK) and spaCy. To reconstruct user stories once their quality has been improved, StoryLine interfaces with SimpleNLG, simple Java API designed to facilitate the generation of Natural Language. Links to each of these dependencies is provided below in the Getting Started section.

Current release (English)
The current release of StoryLine is V1.0 (API). The "official" version of StoryLine only produces texts in English. 

Getting started: Dependencies
The successful execution of StoryLine depends on the following:

Environments
Python v3.5.0
Java v9.0.4

Python Libraries:
Note: to install these libraries, simply open cmd.exe, change your working directory to the same folder where you have Python and Java installed, and type "pip install" + library name. For example, for nltk, type "pip install nltk".

bottle
nltk
openpyxl
pandas 
numpy 
re
itertools
xlutils
xlrd
xlwt
collections 
spacy
autocorrect 
num2words 

JAVA program SimpleNLG Installation Instructions - https://github.com/simplenlg/simplenlg

For information on how to use SimpleNLG, please see the tutorial.

If you wish to cite StoryLine in an academic publication, please cite the following paper(s):
1. TBD
2. TBD

If you have other questions about StoryLine, please contact Sabrina Ussery via email: usserysabrina@gmail.com.

Reference (QUS): Lucassen, G., Dalpiaz, F., van der Werf, J. M. E., & Brinkkemper, S. (2015, August). Forging high-quality user stories: towards a discipline for agile requirements. In Requirements Engineering Conference (RE), 2015 IEEE 23rd International (pp. 126-135). IEEE.

Reference(NLTK): https://www.nltk.org/

Reference(spaCy): https://spacy.io/
