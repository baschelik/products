import csv
import os
from smalltask import dd

path = 'download/stamm_reifen.csv'

# read a csv file, in this case it is file with guid and ean
# for ean file, mandatory define encoding as latin-1, otherwise error when reading the original file
reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
# store/skip header
header = next(reader)
nested = {}
grupe = {}
columns = {'Gruppe', 'GruppeText', 'GruppeSymbol', 'EinsatzZweck', 'EinsatzZweckText', 'EinsatzZweckSymbol',
           'DIMENSION', 'BREITE', 'HOEHE', 'BAUART', 'FELGE', 'LI', 'GI', 'GESCHW', 'TT_TL', 'Hersteller', 'HerstellerText', 'HerstellerSymbol',
           'Profil', 'ProfilText', 'ProfilSymbol', 'LagerHoehe'}

for column in columns:
    nested[column] = []

# read line by line csv file
for row in reader:

    for column in columns:

        # grab text in the column Gruppe
        gruppe = row[header.index(column)]
        if column == 'GESCHW': gruppe = int(gruppe)
        # if it is blank string, skip
        if gruppe == '':
            continue

        # if gruppe is not yet in array grupe, add it and assign value of 0
        if gruppe not in nested[column]:
            nested[column].append(gruppe)
        # else increase the count of gruppe type for 1
        else:
            continue
        nested[column].sort()

dd(nested)

reader = csv.reader(open(path, encoding='latin-1'), delimiter=';')
# store/skip header and move reader to row 2, to actual data
header = next(reader)

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