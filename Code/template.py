print("Please navigate to http://localhost:8080/StoryLine in your web browser.")

from bottle import get, post, request, route, run, template, os, static_file

@route('/StoryLine')
def index():
    return template('index')

@route('/')
def root():
    return static_file('test.html', root='.')

@route('/StoryLine', method='POST')
def do_upload():
    #category   = request.forms.get('category')
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    ambig_threshold = request.forms.get('athreshold')
    CD_threshold = request.forms.get('qthreshold')
    dup_threshold = request.forms.get('dthreshold')

    if ext not in ('.xlsx'):
        return "File extension not allowed."


    # error handling
    if ambig_threshold== '':
        ambig_threshold = 0.75
    if CD_threshold =='':
        CD_threshold = 0.75
    if dup_threshold =='':
        dup_threshold = 0.90

    ambig_threshold_float = float(ambig_threshold)
    CD_threshold_float = float(CD_threshold)
    dup_threshold_float = float(dup_threshold)

    if (ambig_threshold_float <0.00 or ambig_threshold_float> 1.00) or (CD_threshold_float <0.00 or CD_threshold_float> 1.00) or (dup_threshold_float <0.00 or dup_threshold_float> 1.00):
        return "Threshold values must be between 0.00 and 1.00."

    save_path = "C:\\Users\sussery\Desktop\Python Code"
    upload.save(save_path) # appends upload.filename automatically

    file = upload.filename

    #initiating StoryLine
    import subprocess
    process = subprocess.call(['python', 'StoryLine.py', file])
    process = subprocess.call(['python', 'Build_QFD.py', str(ambig_threshold), str(CD_threshold), str(dup_threshold)])
    return 'Your QFD report will be ready shortly.'

@route('/download/<Storyline QFD Report.xlsx:C:\\Users\sussery\Desktop\Python Code>')
def download(filename):
    return static_file(filename ='Storyline QFD Report.xlsx' , root='C:\\Users\sussery\Desktop\Python Code', download=filename)

if __name__ == '__main__':
    run(host='localhost', port=8080, debug = True, reloader=True)
