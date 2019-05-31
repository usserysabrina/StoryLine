# StoryLine

StoryLine is a simple Python API designed to facilitate the generation of quality Agile requirements, commonly referred to as user stories. The tool was originally developed by Sabrina Ussery in fulfillment of doctoral research requirements at the George Washington University. 

StoryLine is based on the Quality User Story (QUS framework) developed by Lucassen et. al. 2015, which consists of 14 quality criteria that user story writers should strive to conform to. The tool takes as its input a set of draft user stories in a .xlsx file (see demo_input.xlsx above) and, as its output, provides modifications to the input user stories to increase their quality. StoryLine's outputs are presented to the user in a Quality Function Deployment (QFD) based traceability report that allows the user to clearly see how each user story has evolved. Within the QFD report, the following feedback is also provided:

a). Spelling errors corrected in each user story,
b). Acronyms found in each user story (for use in requirements glossary),
c). Metrics indicating the level of ambiguity and conceptual density of each user story,
d). A user story duplication matrix, and
e). A user role coverage matrix.

To improve the quality of user stories, StoryLine depends on the linguistic processing capabilites of the Natural Language Toolkit (NLTK) and spaCy. To reconstruct user stories once their quality has been improved, StoryLine interfaces with SimpleNLG, simple Java API designed to facilitate the generation of Natural Language. Links to each of these dependencies is provided below in the Getting Started section.

# Current release (English)
The current release of StoryLine is V1.0 (API). The "official" version of StoryLine only produces texts in English. 

# Getting started: Dependencies
The successful execution of StoryLine depends on the following:

# Environments
Python v3.7.3

Java v8

# Python Libraries:
Note: to install these libraries, simply open cmd.exe, change your working directory to the same folder where you have Python and Java installed, and type "pip install" + library name. For example, for nltk, type "pip install nltk".

bottle

stanford-corenlp 

pycorenlp

openpyxl

pandas

numpy 

re2

itertools

xlutils

xlrd

xlwt

spacy

autocorrect 

num2words 

nltk

JAVA program SimpleNLG Installation Instructions - https://github.com/simplenlg/simplenlg
Spacy Installation Instructions - https://spacy.io/usage/models
Stanford NLP Installation Instructions - https://stanfordnlp.github.io/CoreNLP/

# Execution Instructions (v1.0)

To run StoryLine, verify that the following files are within your working directory:
1.StoryLine.py

2.SimpleNLG.java

3.Pairwise_SemSim.py (optional)

4.Requirements file (such as Requirements_Input.xlsx)

The name of your xlsx based requirements file must follow the schema of the provided Requirements_Input.xlsx. You can change the input filename within StoryLine.py as shown below in the provided "change_filename.jpg". Version 1.0 of StoryLine is executable from the command line only, where each component of the tool should be ran in the following order using the provided commands. A sequence diagram, including all file exchanges used during the tool's execution, are also provided for context.
1. Open terminal or run.cmd
2. Change your current directory to your working directory where Python is installed and all of the above files are saved.
3. Execute StoryLine by using the following commands:

python StoryLine.py

python Pairwise_SemSim.py (optional)

javac SimpleNLG.java

java SimpleNLG



If you have any questions, you can contact me at: usserysabrina@gmail.com.

# Citations

If you wish to cite StoryLine in an academic publication, please cite the following paper(s):
1. TBD
2. TBD

If you have other questions about StoryLine, please contact Sabrina Ussery via email: usserysabrina@gmail.com.
