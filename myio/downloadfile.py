import requests

def downloadfile(url,localfilename=None):
    """
    this program will download a file and use the .netrc credentials by default
    If a localfilename is not given it will strip it from the url.
    """
    if localfilename == None:
        localfilename = url.split("/")[-1]
    r = requests.get(url, timeout=None)
    if r.status_code == 200:
        with open(localfilename, 'wb') as f:
            f.write(r.content)
    
