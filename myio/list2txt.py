def list2txt(inlist,outfile):
    '''
A simple program to write a list of strings to a text file
    '''
    f = open(outfile,'w')
    for line in inlist:
        f.write(line+'\n')
    f.close()
    
