import os

import folders

###############################################################################
# Določene datoteke se niso dobro prenesle, ta programček jih izbriše
###############################################################################


def clean(directory=folders.top_directory):
    to_delete = []
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), encoding='utf-8') as file:
            if file.read() == 'Too Many Requests\n':
                to_delete.append(os.path.join(directory, filename))
    print('Deleted: ', len(to_delete), ' files. ')
    for file in to_delete:
        os.remove(file)

clean(directory=folders.full_directory)
