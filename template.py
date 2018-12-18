from bottle import get, post, request, route, run, template, os, static_file

@route('/StoryLine')
def index():
    return template('index')

@route('/StoryLine', method='POST')
def do_upload():
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.xlsx'):
        return 'File extension not allowed.'
    upload.file()
    return 'OK'

@route('/')
def root():
    return static_file('test.html', root='.')

@route('/upload', method='POST')
def do_upload():
    #category   = request.forms.get('category')
    upload = request.files.get('upload')
    ambig_threshold = request.forms.get('athreshold', default='0.75')
    CD_threshold = request.forms.get('qthreshold', default='0.75')

    name, ext = os.path.splitext(upload.filename)

    if ext not in ('.xlsx'):
        return "File extension not allowed."

    save_path = "C:\\Users\sussery\Desktop\Python Code"
    upload.save(save_path) # appends upload.filename automatically

    file = upload.filename

    #initiating StoryLine
    import subprocess
    subprocess.call(['python', 'StoryLine.py', file])

    return  "Upload successful! Your results will be ready shortly."

# import subprocess
# subprocess.call(['python', 'StoryLine.py', file])

if __name__ == '__main__':
    run(host='localhost', port=8080, debug = True, reloader=True)
