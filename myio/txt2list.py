def txt2list(infile):
    '''
A simple program to write a list of strings to a text file
    '''
    f = open(infile,'r')
    outlist = f.read().splitlines()
    return outlist
    f.close()
