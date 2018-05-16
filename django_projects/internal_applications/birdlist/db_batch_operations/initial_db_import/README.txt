DB import steps:
0.1 syncdb
0.2 evolve --execute
0.3 export birdlist and coupling list to xls format, export then to CSV

1. Cages
run cages.py to generate rooms and populate them with cages


2. Read in Bird list and populate:
    - name
    - birthday
    - age uncertainty
    - cage
    - sex
    - species
    - reserved
    - comment
    - exit_date
    - cause_of_exit


3. Take coupling list and do:

    - create Couple() with new ID
    - create CoupleLookup() with father and mother name, use couple_id from prev
      step
    - create Coupling(), use cage, couple_id, coupling_date, separation_date, comment


4. Go through birdlist again
    - for each bird that has a mother & father:

        - find CoupleLookup() id
        - take Couple() object
        - find Coupling() object, read out number of generations (N)
            - We imported the generations and put them into the comment field of 
              Coupling(). ';' identifies the generation string

        - find all brothers and sisters born in the same range of 
            coupling_date & separation_date & with same mother & father

            - find the unique birthdays for the N generations

        - figure out how many Broods() need to be generated - this should be N
          in general. but what if we got more birthdays / or less? whom should
          we trust? 

            - if # birthdays > N  -> look for +-1/+-2 day differences and pick 
              first one

            - if # birthdays < N  -> probably N is wrong.
               
       - create number of Broods() and assign each bird to the right brood
             - set the generation & date_of_birth fields correctly


5. How do I make sure I don't create too many broods? If a bird already has an
   entry in Brood() -> skip bird

