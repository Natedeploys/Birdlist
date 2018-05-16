
from birdlist.models import Activity, Animal_Experiment_Licence, Bird, Brood
from django.db.models import Q

import datetime

'''
On behalf of the cantonal veterinary office we need to report the following
numbers for all licences in use at the end of each year.

FORM C

IM KALENDERJAHR VERWENDETE TIERE
-------------------------------------------
41 - Anzahl unter dieser Bewilligungsnummer vom Vorjahr ins Berichtsjahr uebernommene Tiere
42 - Anzahl unter dieser Bewilligungsnummer im Berichtsjahr neu eingesetzte Tiere
43 - Total der im Berichtsjahr unter dieser Bewilligungsnummer verwendeten Tiere
     (explizit verlangt: n(41) + n(42) = n(43))
44 - Anzahl im Berichtsjahr unter dieser oder einer anderen Bewilligungsnummer mehrfach eingesetzte Tiere

HERKUNFT DER VERWENDETEN TIERE
-------------------------------------------
51 - Anzahl Tiere aus laufendem Tierversuch (41) oder aus abgeschlossenem frueherem Tierversuch
52 - Anzahl Tiere aus anerkannter Versuchstierzucht oder -handlung in der Schweiz
53 - Anzahl Tiere aus Versuchstierzucht oder -handlung im Ausland 
54 - Anzahl Tiere anderer Herkunft

SCHWEREGRAD DER BELASTUNG
-------------------------------------------
61 - Anzahl Tiere ohne Belastung (Schweregrad 0)
62 - Anzahl Tiere mit Schweregrad 1
63 - Anzahl Tiere mit Schweregrad 2
64 - Anzahl Tiere mit Schweregrad 3

AUSCHEIDEN resp. WEITERVERWENDUNG DER TIERE
-------------------------------------------
71 - Durch Toeten oder Verenden waehrend / am Ende des Versuchs ausgeschiedene Tiere
72 - Ueberlebende Tiere, fuer Weiterfuehrung des Versuchs im naechsten Jahr
73 - Ueberlebende Tiere am Versuchsende (Einsatz in spaeteren Versuchen, Ausscheiden als Versuchstiere)

plausibility checks:
- n(41) + n(42) = n(43)
- n(44) <= n(43)
- n(51) >= n(41)
- n(51) + n(52) + n(53) + n(54) = n(43)
- n(61) + n(62) + n(63) + n(64) = n(43)
- n(71) + n(72) + n(73) = n(43)

also check wether no experiments with unvalid licence were done

'''

# overall procedure:
# ------------------------------------------------
# find licences valid in given year
# find experiments for given year
# find set of birds involved in an experiment
# find experiments per bird with highest severity grade
# get licence fort this experiment
# assign bird to this licence
# for birds per licence figure out whether bird was in experiment before / is alive


def form_c_report(year, end_month=12, end_day=31, print_to_command_line=True,
        species='ZF'):
    
    '''
    form c report on behalf of veterinary office 

    report numbers asked for above from beginning of year to day given as arguments.
    '''
    
    report_dict = {}

    p = print_to_command_line
    
    # define the report period 
    start_day = datetime.datetime(year, 1, 1)
    end_day = datetime.datetime(year, end_month, end_day)
    last_year_start = datetime.datetime(year-1, 1,1)
    
    # get valid licences in report period
    valid_licences = Animal_Experiment_Licence.objects.filter(valid_until__gte=start_day).exclude(valid_from__gte=end_day)
    
    if p:
        print '\n\n'
        print 'FORM C - report on behalf of veterinary office'
        print '----------------------------------------------'
        print 'species : ', species
        print 'report period: ', start_day.date().isoformat(), ' - ', end_day.date().isoformat()
        print
        print 'VALID LICENCES:'
        for lic in valid_licences:
            print ' ', lic.title, ' : valid ', lic.valid_from.isoformat(), '-', lic.valid_until.isoformat()
        print

    for lic in valid_licences:
        report_dict[lic.title] =  {
                        '41' : 0, '42' : 0, '43' : 0, '44' : 0,
                        '51' : 0, '52' : 0, '53' : 0, '54' : 0,
                        '61' : 0, '62' : 0, '63' : 0, '64' : 0,
                        '71' : 0, '72' : 0, '73' : 0,
                        'sg3 exps' : [], 'birds' : [], 'birdsfromexternal' : {},
                        }


    # now get all birds that had an experiment in period
    birds_with_exp = birds_with_experiment_in_period(start_day, end_day, species=species)

    # we now go through all birds and fill in the numbers accordingly
    for bird in birds_with_exp:

        # all experiments with this bird
        exps = Activity.objects.filter(activity_type__name='Experiment', bird__id=bird.id)
       
        # licence wise number assignment
        lic_use_list = []
        for lic in valid_licences:

            # restrict experiments to licence
            lic_exps = exps.filter(animal_experiment_licence=lic)

            # count experiments in period and previous year
            lic_use = []
            # experiments done in period of interest, already sorted
            lic_exps_now = lic_exps.filter(q_for_period(start_day, end_day)).order_by('-start_date').order_by('-severity_grade')
            lic_use.append(lic_exps_now.count())
            # experiments done in previous year
            lic_use.append(lic_exps.filter(q_for_period(last_year_start, start_day)).count())
            lic_use_list.append(lic_use)
        
            # data verified in extracts
            #print bird.name, lic.title, lic_use

            # we only care about this bird if it was used under
            # this licence in our period of interest 
            if lic_use[0]:
                # if used increase count
                report_dict[lic.title]['43'] += 1
                report_dict[lic.title]['birds'].append(bird.name)

                # severity grades
                if lic_exps_now[0].severity_grade == 0:
                    report_dict[lic.title]['61'] +=1
                elif lic_exps_now[0].severity_grade == 1:
                    report_dict[lic.title]['62'] +=1
                elif lic_exps_now[0].severity_grade == 2:
                    report_dict[lic.title]['63'] +=1
                elif lic_exps_now[0].severity_grade == 3:
                    report_dict[lic.title]['64'] +=1
                    report_dict[lic.title]['sg3 exps'].append(lic_exps_now[0])

                # if bird was used in previous year
                if lic_use[1]:
                    # increase counts
                    report_dict[lic.title]['41'] += 1
                    report_dict[lic.title]['51'] += 1
                else:
                    # if it was not used in previous year we have to assume that this bird
                    # is used new (explicitly asked in form c)
                    report_dict[lic.title]['42'] += 1

                    # if it was used a longer time ago or using a different licence
                    if exps.exclude(q_for_period(start_day, end_day)).count():
                        report_dict[lic.title]['51'] += 1

                # origin outside of colony
                if bird.brood == None:
                    report_dict[lic.title]['54'] += 1
                    report_dict[lic.title]['birdsfromexternal'][bird.name] = bird.comment

                elif bird.brood.origin == Brood.ORIGIN_EXTERNAL:
                    report_dict[lic.title]['54'] += 1
                    report_dict[lic.title]['birdsfromexternal'][bird.name] = bird.comment
#               elif bird.brood.origin == Brood.ORIGIN_BREEDING and not lic_use[1] and not exps.exclude(q_for_period(start_day, end_day)).count():
#                   report_dict[lic.title]['52'] += 1

                # the birds state at end of period - paragraph 7 
                # still alive
                if bird.exit_date == None:
                    # has experiments that ended after period
                    if lic_exps_now.filter(end_date=None).count() or lic_exps.filter(end_date__gte=end_day):
                        report_dict[lic.title]['72'] += 1

                # bird died in period from experiment
                elif (bird.exit_date < end_day.date()) and\
                        (bird.cause_of_exit == Bird.EXIT_SLEEP or bird.cause_of_exit == Bird.EXIT_SURGERY or bird.cause_of_exit == Bird.EXIT_PERISHED):
                    report_dict[lic.title]['71'] += 1
                    

        # check whether bird was used in period under different licences
        num_lic_used = 0
        for lic_use in lic_use_list:
            if lic_use[0]:
                num_lic_used += 1 

        # TODO : this readout is only superficial and at all only valid if there are only two licences!!
        for lic in valid_licences:
            if num_lic_used > 1:
                report_dict[lic.title]['44'] += 1

    for rep in report_dict.keys():
        # fill in remaining 
        report_dict[rep]['52'] = report_dict[rep]['43'] - report_dict[rep]['51'] - report_dict[rep]['54'] 
        report_dict[rep]['73'] = report_dict[rep]['43'] - report_dict[rep]['71'] - report_dict[rep]['72'] 
   
    # print summary
    if p:
        for lic in report_dict.keys():
            print
            print lic, '\n-------------------------------------'
            for num in report_dict[lic].keys():
                print num, ' : ', report_dict[lic][num]

        print
        print
        print

    return report_dict





def q_for_period(start_day, end_day):
    '''
    date restrictions (data consistency is assumed, ie: sd < ed)
    started before start and ended after end 
    started before end and ended after end
    started before end and ended in period
    started before end and still open
    '''
    q = Q(\
           Q( Q(start_date__lte=start_day) & Q(end_date__gte=end_day) ) |\
           Q( Q(start_date__lte=end_day) & Q(end_date__gte=end_day) ) |\
           Q( Q(start_date__lte=end_day) & Q(end_date__lte=end_day) & Q(end_date__gte=start_day) ) |\
           Q( Q(start_date__lte=end_day) & Q(end_date=None) ) \
         )

    return q


def birds_with_experiment_in_period(start_day, end_day, species='ZF'):
    # get all experiments
    experiments = Activity.objects.filter(activity_type__name='Experiment')
    q = q_for_period(start_day, end_day)
    experiments = experiments.filter(q)

    birds_in_experiments = []
    
    for exp in experiments:
        if exp.bird in birds_in_experiments:
            continue
        else:
            if species == None:
                birds_in_experiments.append(exp.bird)

            elif exp.bird.species == species:
                birds_in_experiments.append(exp.bird)

    return birds_in_experiments


def birds_with_experiment_within_year(year):
    
    experiments = Activity.objects.filter(activity_type__name='Experiment')
    experiments = experiments.filter(Q(Q(start_date__year=year) | Q(end_date__year=year)))

    birds_in_experiments = []
    
    for exp in experiments:
        if exp.bird in birds_in_experiments:
            continue
        else:
            birds_in_experiments.append(exp.bird)

    return birds_in_experiments


def find_decisive_experiment_for_bird_within_year(bird_list, year):
    '''
    for each bird find experiments and assing experiment with
    highest severity_grade or last experiment to bird
    '''
    bird_exp_dict = {}
    for bird in bird_list:
        exps = bird.activity_set.filter(activity_type__name='Experiment')
        exps = exps.filter(Q(Q(start_date__year=year) | Q(end_date__year=year)))
        exps = exps.order_by('-start_date').order_by('-severity_grade')
        # take experiment with highest severity grade as reference experiment
        bird_exp_dict[bird.name] = exps[0]

    return bird_exp_dict


def split_birds_into_licences(bird_exp_dict):
    '''
    '''
    lic_dict = { 'nolic': [], }

    for bird in bird_exp_dict:
        if bird_exp_dict[bird].animal_experiment_licence:
            lic = bird_exp_dict[bird].animal_experiment_licence.title
            if lic in lic_dict:
                lic_dict[lic].append(bird_exp_dict[bird])
            else:
                lic_dict[bird_exp_dict[bird].animal_experiment_licence.title] = [bird_exp_dict[bird], ]
        else:
            lic_dict['nolic'].append(bird_exp_dict[bird])

    return lic_dict


def licence_summary(year):
    '''
    old (pre report end 2011) summary function
    '''
    birds_in_exps = birds_with_experiment_within_year(year)
    bird_exp_dict = find_decisive_experiment_for_bird_within_year(birds_in_exps, year)
    lic_dict = split_birds_into_licences(bird_exp_dict)
    
    print 
    print 
    print 'LICENCE SUMMARY YEAR ', year
    print '------------------------------------------'
    for lic in lic_dict:
        print
        print lic
        print '**********************'
        # count severity grades etc
        num_sg0 = 0
        num_sg1 = 0
        num_sg2 = 0
        num_sg3 = 0
        birds_dead = 0
        birds_from_prev_year = 0
        birds_with_open_exps = 0

        for exp in lic_dict[lic]:
            if exp.severity_grade == 0:
                num_sg0 += 1
            elif exp.severity_grade == 1:
                num_sg1 += 1
            elif exp.severity_grade == 2:
                num_sg2 += 1
            elif exp.severity_grade == 3:
                num_sg3 += 1
            if exp.bird.exit_date:
                if exp.bird.exit_date <= datetime.date(year, 12, 31):
                    birds_dead +=1

            # figure out whether bird was in experiment in previous year
            # TODO: this has to be changed, cause we do now know for every experiment
            # the licence and can figure out for 41 whether it was the same licence number
            bird_exps = Activity.objects.filter(bird=exp.bird, activity_type__name='Experiment')
            bird_exps_prev_year = bird_exps.filter(Q(Q(start_date__year=year-1) | Q(end_date__year=year-1)))
            if bird_exps_prev_year:
                birds_from_prev_year += 1

            # find experiments with open exeriment at end of year -> 72
            # experiments started in year and are open today or ended in year+1
            # what about experiments that started before year and are open or enden in year+1??
            queryfilter = Q(
                    Q(Q(start_date__year=year) & Q(end_date=None)) |\
                    Q(Q(start_date__year=year) & Q(end_date__year=year+1)) \
                    )
            bird_exps_open = bird_exps.filter(queryfilter)

            if bird_exps_open:
                birds_with_open_exps += 1

            '''
            some testing/debug info

            print exp.bird.name + '\t' + str(exp.severity_grade) + '\t' + exp.originator.username
            print exp.activity_content

            print exp.bird.name, ': ', bird_exps_open.count()
            '''

        print '41 - birds with experiment in previous year: ', birds_from_prev_year 
        print '42 - new birds: ', lic_dict[lic].__len__() - birds_from_prev_year
        print '43 - total number of animals: ', lic_dict[lic].__len__()
        print '61 - number of animals with sg 0: ', num_sg0 
        print '62 - number of animals with sg 1: ', num_sg1 
        print '63 - number of animals with sg 2: ', num_sg2 
        print '64 - number of animals with sg 3: ', num_sg3
        print '71 - birds finally dead:', birds_dead
        print '72 - birds with open experiment at end of year:', birds_with_open_exps



def write_birdinfo(birdlist, path):
    '''
    write bunch of information for a list of birds into a file
    '''

    fid = file(path, 'w')
    
    for bird in birdlist:
        fid.write('\n\n\n*******************\n'+str(bird.name)+'\n********************\n'+str(bird.exit_date)+'\n'+str(bird.cage)+'\n------------------------------')
        for act in bird.activity_set.filter(activity_type__name='Experiment'):
            fid.write('\n'+str(act.activity_type) + '\t' + str(act.originator) + '\t' + str(act.start_date) + '\t' + str(act.end_date) + '\t' + str(act.severity_grade)\
                    + '\n' + str(act.activity_content))
    fid.close()
