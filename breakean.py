import csv
import os

broken_dir = 'download/broken'
path = 'download/stamm_reifen.csv'

# read a csv file, in this case it is file with guid and ean
# for ean file, mandatory define encoding as latin-1, otherwise error when reading the original file
reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
# store/skip header
header = next(reader)
grupe = {}

# read line by line csv file
for row in reader:
    # grab text in the column Gruppe
    gruppe = row[header.index('Gruppe')]

    # if it is blank string, call it EMPTY
    if gruppe == '':
        gruppe = 'EMPTY'

    # if gruppe is not yet in array grupe, add it and assign value of 0
    if gruppe not in grupe:
        grupe[gruppe] = 0
    # else increase the count of gruppe type for 1
    else:
        grupe[gruppe] += 1


reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
# store/skip header and move reader to row 2, to actual data
header = next(reader)

# create directory if it does not exists
if not os.path.exists(broken_dir):
    os.makedirs(broken_dir)

# read line by line csv file
for row in reader:
    # go through the array grupe
    for value in grupe:
        # grab text in the column Gruppe
        gruppe = row[header.index('Gruppe')]

        # when csv column and array value match
        if gruppe == value:
            # if csv file does not exists, create it with name,
            # which contains type of tyre and total number of rows found for this tyre type
            if not os.path.exists(os.path.join(broken_dir,'stamm_'+value+'_'+str(grupe[value])+'.csv')):
                local = open(os.path.join(broken_dir,'stamm_'+value+'_'+str(grupe[value])+'.csv'), 'a', newline='')
                writer = csv.writer(local, delimiter=';')
                # write header at beginning of each broken csv file
                writer.writerow(header)

            # if file exists, open it to append next row
            local = open(os.path.join(broken_dir,'stamm_'+value+'_'+str(grupe[value])+'.csv'), 'a', newline='')
            writer = csv.writer(local, delimiter=';')
            writer.writerow(row)
        print(value, ':',  grupe[value])