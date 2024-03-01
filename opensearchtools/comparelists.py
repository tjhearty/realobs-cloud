# this program will compare the list of files I got from MOS and CMROS

# first read the files

f = open('MOSlist.txt','r')

moslist = f.readlines()

f.close()

f = open('CMROSlist.txt','r')

cmroslist = f.readlines()

f.close()

moslist.sort()

cmroslist.sort()


inmosbutnotcmros = list(set(moslist) - set(cmroslist))

incmrosbutnotinmos = list(set(cmroslist) - set(moslist))

inmosbutnotcmros.sort()

outfile = 'AIRS2RETdifferences2002.09.01through2017.08.31.txt'
output = open(outfile,'w')
for url in inmosbutnotcmros:
    output.write(url)
output.close()
