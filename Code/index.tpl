<!DOCTYPE html>
<html>
<head>
  <title>StoryLine: Automatic User Story Quality Improvement</title>
  <style>
    img {
        display: inline-block;
      }
</style>

</head>

<body>
<h1>
  <img src='https://github.com/usserysabrina/StoryLine/blob/master/StoryLine.jpg' /width="250" height="250">
</a>
Welcome to StoryLine!</h1>

<p>
StoryLine is an open source, research tool that is designed to help you write quality user stories according to both the Quality User Story(QUS) and INVEST frameworks (see references below).
The tool takes as its input a set of draft user stories and, as its output, provides modifications to the input user stories to increase their quality.
StoryLine's outputs are presented to the user in a Quality Function Deployment (QFD) based traceability report that allows the user to clearly see how each user story has evolved.
Within the QFD report, the following feedback is also provided, as illustrated below:<br><br>
a). Spelling errors corrected in each user story,<br>
b). Acronyms found in each user story (for use in requirements glossary),<br>
c). Writing Style metrics (i.e., word choice, sentence length, and grammar) and their impact on the clarity and conciseness of each each user story,<br>
d). A user story duplication matrix, and<br>
e). A user role coverage matrix (i.e., completeness of requirements set).<br><br>

<img src='https://github.com/usserysabrina/StoryLine/blob/master/qfd.png' /width="250" height="250">

<br><br>

To use the tool, please start by uploading a single column, Excel .xlsx file containing your draft user stories. A template has been provided below for your reference.
If you desire, you may also provide lower bounds value for the tool to use when reporting user story ambiguity, conceptual density, and duplication.
If no value is provided, the following default values will be used:
<li>Ambiguity - .75 (75%)</li><br>
<li>Conceptual Density - .75 (75%)</li><br>
<li>Duplication - .90 (90%)</li><br>
<br><br>

Upon finishing, the results of StoryLine's processing will be provided as an automatic download for your use.<br><br>

Thanks for visiting! And happy writing!
</p><br>
<b><p> Inputs</p></b>

<form action="/StoryLine" method="post" enctype="multipart/form-data">
    Select a file: <input type="file" name="upload" /><br><br>
    Ambiguity Threshold (values 0.00 - 1.00): <input type="text" name="athreshold"><br><br>
    Conceptual Density Threshold (values 0.00 - 1.00): <input type="text" name="qthreshold"><br><br>
    Duplication Threshold (values 0.00 - 1.00): <input type="text" name="dthreshold"><br><br>
    <input type="Submit" value="Run StoryLine" />
</form><br><br>

<b><p> Helpful Resources</p></b>
<p><a href="https://github.com/usserysabrina/StoryLine/blob/master/demo_input.xlsx">StoryLine Input Template</a></p>
<p><a href="https://github.com/usserysabrina/StoryLine">StoryLine GitHub page</a></p>

<p><u> Publications for StoryLine  </u></p>
<p>PLACEHOLDER 1</p>
<p>PLACEHOLDER 2</p>

<p><a href="https://link.springer.com/article/10.1007/s00766-016-0250-x">QUS Framework (full reference below)</a></p>
<p><i>Lucassen, G., Dalpiaz, F., van der Werf, J. M. E., & Brinkkemper, S. (2016). Improving agile requirements: the quality user story framework and tool. Requirements Engineering, 21(3), 383-403.</i></p>

<p><a href=mailto:usserysabrina@gmail.com>Got feedback? Contact me!</a><p>

</body>
</html>
