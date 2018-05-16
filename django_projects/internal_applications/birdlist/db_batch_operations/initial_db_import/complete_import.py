'''
I M P O R T   R E P O R T   A N D   S C R I P T

here the final report is documented bringing the birdlist data into the database
already present on the server. all procedures are first tested on local dev systems.

the birdlist db was exported to excel and saved as .csv (Macintosh) into csv files
these files still contained mixed DOS/Mac characters. the  characters had to be replaced
by newlines (vim :%s/\r/\r/g )

the birdlist within the django db will only be connected to other models via the experiments.
these connections we will have to be made manually after the import (roughly 60).
for the rest of the import we can drop the existing tables befor the import and repopulate them
again in a consistent way.

below a commented script is provided which can be executed when running $python manage.py shell
from your songbird project folder, with ln [1]:run complete_import

'''

do_debug = 1 

# -1- IMPORT CAGES
from birdlist.dbconversion import cages
cages.populate_rooms()
cages.import_cages(debug=do_debug)

# -2- IMPORT BIRDS
# some new cages were used since the development of bird import
# i had to check for these or add them respectively
from birdlist.dbconversion import birds
birds.import_birds(debug=do_debug)

# -3- IMPORT COUPLES
# import couples and generate couplings @ same step
from birdlist.dbconversion import coupling
coupling.import_couples(debug=do_debug)

# -4- GENERATE BROODS
from birdlist.dbconversion import brood_revised
brood_revised.generate_broods(debug=do_debug)

# -5- IMPORT ACTIVITIES
# this import imports both experiments and cage transfers
from birdlist.dbconversion import activities
# to be able to map activities to users we have to add missing users
activities.add_users()
# now we can generate the activities from cage transfers and experiments
activities.generate_activities(debug=do_debug)
# had to manually manipulate/clean the exported csv-files to make them smoothly running 
