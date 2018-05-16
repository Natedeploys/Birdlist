
import birds, coupling, cages, brood

DEBUG = 0

cages.populate_rooms()
cages.import_cages(debug=DEBUG)

birds.import_birds(debug=DEBUG)
coupling.import_couples(debug=DEBUG)

#brood.generate_broods(debug=DEBUG)
