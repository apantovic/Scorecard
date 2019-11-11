import os
import base64
import pandas as pd

def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(upload_directory()):
        path = os.path.join(upload_directory(), filename)
        if os.path.isfile(path):
            files.append(filename)
    return files

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(upload_directory(), name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def upload_directory():
    return os.path.abspath("upload")

def read_df(value,method):
    if method=='all':
        if value.find('.xls') > 0:
            df = pd.read_excel(upload_directory()+'/'+value)
        elif value.find('.csv') or value.find('.txt'):
            df = pd.read_csv(upload_directory()+'/'+value)
    else:
        if value.find('.xls') > 0:
            df = pd.read_excel(upload_directory()+'/'+value,nrows=1)
        elif value.find('.csv') or value.find('.txt'):
            with open(upload_directory()+'/'+value) as f:
                first_line = f.readline()
                df=pd.DataFrame(columns=first_line[:-1].split(','))
    return df





























def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)
