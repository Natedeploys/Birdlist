from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, legal, landscape, cm, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Frame, Table, TableStyle, XPreformatted, Image, Flowable, KeepTogether, PageBreak, CondPageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.rl_config import defaultPageSize

from cStringIO import StringIO
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from birdlist.models import Bird, Activity, Coupling, Cage
from birdlist.utils.bird import find_offspring
from birdlist.views.birdlist_main import not_implemented

from lablog.views.basic.lablog_main import server_error

import re

# default line break style.        
style = ParagraphStyle(
    name = 'Normal',
    fontName = 'Helvetica',
    fontSize = 9,
)

# line break style with 8pt size
style_small = ParagraphStyle(
    name = 'Normal',
    fontName = 'Helvetica',
    fontSize = 8,
)


blank = '&nbsp;\n'
blank_paragraph = Paragraph(blank * 1, style)  

def pdf_header(page_size = None, filename = 'somefile.pdf', rightMargin=15, leftMargin=20, topMargin=10, bottomMargin=10, title=None, author=None):

    # see http://docs.djangoproject.com/en/dev/howto/outputting-pdf/


    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % (filename)


    buffer = StringIO()
     
    if page_size == None:
        page_size = landscape(A4) 
                 
    doc = SimpleDocTemplate(buffer, pagesize=page_size,
                            rightMargin=rightMargin, leftMargin=leftMargin,
                            topMargin=topMargin, bottomMargin=bottomMargin, title=title, author=author)
    Story = []
    return Story, buffer, doc, response


def pdf_close_and_return(doc, Story, buffer, response):
    doc.build(Story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

    
def add_title(title, Story, request, title_size = 12):
    now = str(datetime.datetime.now())
    now = now[0:19]
    
    styles = getSampleStyleSheet() 
    
    ptext = "<font size=%s>%s</font>" %(title_size, title)
    ptext_add = '(generated ' + now + ' ' + ' for ' + request.user.get_full_name() + ')'
    ptext_add = "<font size=6>%s</font>" %ptext_add
    
    my_style = styles["Title"]
    my_style.spaceAfter = 0
    new_paragraph = Paragraph(ptext, my_style)
    new_paragraph.keepWithNext = True
    Story.append(new_paragraph)
     
    my_style.spaceBefore = 0
    my_style.spaceAfter = 3
    my_style.leading = 13
    new_paragraph = Paragraph(ptext_add, my_style)
    #new_paragraph.keepWithNext = True
    Story.append(new_paragraph)
    return Story


def generate_exp_sheet(request, bird_id, exp_id = None):

    try:
 
        bird = Bird.objects.filter(id = bird_id)
        if bird.__len__() == 0:
            return HttpResponseRedirect(reverse('index_bird', ))
            
            
        bird = bird[0]            
        experiment_name = ''
        
        if exp_id:
            experiment = Activity.objects.get(id = exp_id)
            experiment_name = experiment.activity_content
            licence = experiment.animal_experiment_licence.title
            
        


        title = 'Experiment sheet for ' + bird.name + ' ' + experiment_name
        author = 'https://zongbird-db.lan.ini.uzh.ch/birdlist/'

        Story, buffer, doc, response = pdf_header(filename = "experiment_sheet.pdf", title=title, author=author)



        data = [['Day',  'Date', 'age', 'Behaviour', 'Song', 'Incidents', 'comments / experiment phase']]

        # TODO: CHANGE HERE!!! Days elapse from License is start
        today = datetime.date.today()
        for i in range(27):
            timedelta = datetime.timedelta(days = i)
            reference_date = today + timedelta
            weekday = reference_date.strftime("%A")
            weekday = weekday[0:3]
            if bird.date_of_birth:
                age = reference_date - bird.date_of_birth
                age = age.days.__str__()
                data.append([weekday, str(reference_date), age])
            else:
                data.append([weekday, str(reference_date), 'unknown'])


        ts = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')]
            )


        date_of_birth = 'Date of birth: ' + str(bird.date_of_birth)
        data2 = [['Birdname: ',  bird.name, date_of_birth, '', 'Experimenter: ',  request.user.username],
                 ['Experiment Name:', experiment_name, 'Approx End of Experiment:', '', 'Licence:', licence] ]
        
        
        ts2 = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('FONT', (1,0), (1,0), 'Helvetica-Bold', 10),
            ('FONT', (5,0), (5,0), 'Helvetica-Bold', 10),
            ('ALIGN', (1,1), (-1,-1), 'LEFT')]
            )        
        
        
        colwidths = (100, 250, 150, 50, 65, 135)
        table2 = Table(data2, colwidths, style=ts2)
        Story.append(table2)

        Story.append(Spacer(1, 5))
        
        colwidths = (50, 80, 50, 120, 50, 80, 320)
        table = Table(data, colwidths, style=ts)
        Story.append(table)        

        Story.append(Spacer(1, 6))
        
        ptext = '<font size=10>Generated on %s </font> by birdlist' % (today)
        styles = getSampleStyleSheet()        
        Story.append(Paragraph(ptext, styles["Normal"]))

        return pdf_close_and_return(doc, Story, buffer, response)

    except:
        return server_error(request)



def show_common_reservations_pdf(request):
    try:
        queryset = Bird.objects.filter(reserved_by__isnull=False).order_by('reserved_by__username')
        title = 'All reserved birds'
        author = 'Andreas Kotowicz'    
        Story, buffer, doc, response = pdf_header(page_size = portrait(A4), filename = "reserved_animals.pdf", title=title, author=author)
        
        data = [['Name',  'Cage', 'Birthday', 'Date of death', 'Sex', 'Father', 'Reserved by', 'Reserved until']]

        for i in queryset:
            data.append([i.name, i.cage.name, i.date_of_birth, i.exit_date, i.sex, i.get_father(), i.reserved_by, i.reserved_until])

        ts = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('FONT', (0,1), (-1,-1), 'Helvetica', 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')]
            )
        
        colwidths = (50, 60, 70, 70, 30, 60, 70, 80)
        table = Table(data, colwidths, style=ts, repeatRows = 1)
        
        Story = add_title(title, Story, request)
        Story.append(table)
        
        return pdf_close_and_return(doc, Story, buffer, response)
        
    except:
        return server_error(request)
        
def show_juveniles_by_age_pdf(request):
    try:
        from birdlist.utils.bird import get_juveniles
        queryset = get_juveniles().order_by('date_of_birth')
        title = "all juvenile birds younger 70 days - sorted by age"
        author = 'Andreas Kotowicz'
        transfer_at_age = 60
            
        Story, buffer, doc, response = pdf_header(page_size = portrait(A4), filename = "juveniles_younger_70days.pdf", title=title, author=author)
        
        data = [['Name', 'Age (-)', 'Cage', 'Birthday', 'Transfer', 'Sex', 'Father', 'Reserved by', 'Reserved until']]

        for i in queryset:
            data.append([i.name, i.get_phd() + ' (' + i.age_uncertainty.__str__() + ')', \
            i.cage.name, i.date_of_birth, i.date_of_birth + datetime.timedelta(transfer_at_age), \
            i.sex, i.get_father(), i.reserved_by, i.reserved_until])

        ts = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.15, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('FONT', (0,1), (-1,-1), 'Helvetica', 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')]
            )
        
        colwidths = (50, 40, 60, 60, 60, 30, 60, 70, 80)
        table = Table(data, colwidths, style=ts, repeatRows = 1)
        
        Story = add_title(title, Story, request)
        Story.append(table)
        
        return pdf_close_and_return(doc, Story, buffer, response)
        
    except:
        return server_error(request)


def current_couples_pdf(request):
    queryset = Coupling.objects.filter(separation_date=None).select_related().order_by('cage__name')
    title = "Current Couples"
    author = 'Andreas Kotowicz'
    today = datetime.date.today()
        
    Story, buffer, doc, response = pdf_header(page_size = landscape(A4), filename = "current_couples.pdf", title=title, author=author)
    
    data = [['male', 'female', 'cage', 'coupling date', '# days \n coupled', '# days \n since last \n hatch', '# \n broods', 'comment']]

    for i in queryset:
        last_brood = i.get_last_brood()
        last_brood_diff = ''
        if last_brood:
            last_brood_diff = today - last_brood.get_broods_birthday()
            last_brood_diff = last_brood_diff.days
            
        coupling_diff = today - i.coupling_date
        coupling_diff = coupling_diff.days
        
        comment = i.comment
        if comment:
            comment = comment.replace('&', '&amp;')
            comment = Paragraph(comment * 1, style)   
            
        data.append([i.couple.get_male().name, i.couple.get_female().name, \
        i.cage.name, i.coupling_date, coupling_diff, \
        last_brood_diff, i.get_number_of_broods(), comment])

    ts = TableStyle(
        [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
        ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.15, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 9),
        ('FONT', (4,0), (4,0), 'Helvetica-Bold', 9),    
        ('FONT', (5,0), (5,0), 'Helvetica-Bold', 6),        
        ('FONT', (6,0), (6,0), 'Helvetica-Bold', 9),            
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), 
        ('ALIGN', (7,1), (-1,-1), 'LEFT')]
        )
    
    colwidths = (50, 40, 35, 75, 55, 45, 45, 400)
    table = Table(data, colwidths, style=ts, repeatRows = 1)
    
    Story = add_title(title, Story, request)
    Story.append(table)
    
    return pdf_close_and_return(doc, Story, buffer, response)
    
    
def show_birds_in_cage_pdf(request, cagename):
        
    try:
    
        cage = get_object_or_404(Cage, name=cagename)
        if cage.function == cage.FUNCTION_BREEDING:
            queryset = Bird.objects.filter(cage=cage).order_by('date_of_birth')
        else:
            queryset = Bird.objects.filter(cage=cage).order_by('name')

        title = "Birds in Cage %s" % cage.name
        author = 'Andreas Kotowicz'
            
        Story, buffer, doc, response = pdf_header(page_size = landscape(A4), filename = "birds_in_cage.pdf", title=title, author=author)
        
        data = [['Name',  'Sex', 'Age (-)', 'Birthday', 'Father', 'Mother', 'Reserved by', 'Reserved until', 'Coupling status /\n Previous Mates', 'Comment']]

        for i in queryset:
            coupling_status = i.get_coupling_status_display()
            mates = i.get_mates_string()
            couple_mates_str = '<b>' + coupling_status + '</b><br></br>' + mates
            couple_mates_str = Paragraph(couple_mates_str * 1, style)
            
            comment = i.comment
            if comment:
                comment = comment.replace('&', '&amp;')
                comment = Paragraph(comment * 1, style)                    
                
            data.append([i.name, i.sex, i.get_phd() + ' (' + i.age_uncertainty.__str__() + ')', \
            i.date_of_birth, i.get_father(), i.get_mother(), \
            i.reserved_by, i.reserved_until, couple_mates_str, comment ])

        ts = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.15, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('FONT', (0,1), (-1,-1), 'Helvetica', 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (9,1), (-1,-1), 'LEFT')]
            )
        
        colwidths = (60, 40, 40, 60, 60, 60, 70, 80, 120, 210)
        table = Table(data, colwidths, style=ts, repeatRows = 1)
        
        Story = add_title(title, Story, request)
        Story.append(table)
        
        return pdf_close_and_return(doc, Story, buffer, response)
        
    except:
        return server_error(request)    


def bird_generate_pdf(request, bird_id):
        
    try:
    
        bird = get_object_or_404(Bird, id=bird_id)
        offspring = find_offspring(bird.id)
        activities = Activity.objects.filter(bird=bird).order_by('start_date').reverse()


        title = bird.name
        author = 'Andreas Kotowicz'
            
        Story, buffer, doc, response = pdf_header(page_size = portrait(A4), filename = "birdsheet.pdf", title=title, author=author)
        
        Story = add_title(title, Story, request, title_size=14)

        ''' INFO '''        
        Story.append(Spacer(1, 15))
        ptext = '<font size=13>Info</font>'
        styles = getSampleStyleSheet()        
        Story.append(Paragraph(ptext, styles["Heading1"]))     
        

        comment = bird.comment
        if comment:
            comment = comment.replace('&', '&amp;')
            comment = Paragraph(comment * 1, style)
            
        tags = bird.tags     
        if tags:
            tags = Paragraph(tags * 1, style)


        data = [ ['Birthday:', bird.date_of_birth, 'Age Uncertainty:', bird.age_uncertainty],
                 ['Sex:', bird.get_sex_display(), 'Species:', bird.species],
                 ['Father:', bird.get_father(), 'Mother:', bird.get_mother()],
                 ['Cage:', bird.cage.name, 'Brood:', bird.brood],
                 ['Missing since:', bird.date_of_birth, 'Tags:', tags],
                 ['Reserved until:', bird.reserved_until, 'Reserved by:', bird.reserved_by ],
                 ['Exit Date:', bird.exit_date, 'Cause of exit:', bird.get_cause_of_exit_display()],
                 ['Comment:', comment, ] ]


        ts = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('FONT', (0,1), (-1,-1), 'Helvetica', 9),
            ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 10),
            ('FONT', (2,0), (2,-1), 'Helvetica-Bold', 10),            
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
            ('SPAN', (1, 7), (3, 7)), ]
            )
        
        colwidths = (90, 170, 90, 200)
        table = Table(data, colwidths, style=ts, repeatRows = 1)        
        Story.append(table)
        

        ''' OFFSPRING '''        
        Story.append(Spacer(1, 15))
        ptext = '<font size=13>Offspring</font>'
        styles = getSampleStyleSheet()        
        Story.append(Paragraph(ptext, styles["Heading1"]))
        

        offspring_str = ''
        nbr_offspring = offspring.__len__()
        nbr_offspring = nbr_offspring - 1
        if nbr_offspring > 0:
            for i in enumerate(offspring):
                if i[0] == 0:
                    offspring_str = i[1].name
                elif i[0] == nbr_offspring:
                    offspring_str = offspring_str + ', ' + i[1].name + '.'
                else:                    
                    offspring_str = offspring_str + ', ' + i[1].name
        else:
            offspring_str = 'No offspring.'                            
        
        ptext = '<font size=10>%s</font>' % offspring_str
        styles = getSampleStyleSheet()        
        Story.append(Paragraph(ptext, styles["Normal"]))        
        
        
        
        ''' ACTIVITIES '''        
        Story.append(Spacer(1, 15))
        ptext = '<font size=13>Activities</font>'
        styles = getSampleStyleSheet()        
        Story.append(Paragraph(ptext, styles["Heading1"]))        
        
        data = [['type',  'content', 'start date', 'end date', 'user']]
        
        
        for i in activities:
            content = i.activity_content
            if content:
                content = content.replace('&', '&amp;')
                content = Paragraph(content * 1, style) 
            data.append([i.activity_type, content, i.start_date, i.end_date, i.originator])
        
        ts = TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
            ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.15, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('FONT', (0,1), (-1,-1), 'Helvetica', 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (4,1), (-1,-1), 'LEFT'),
            ('ALIGN', (1,1), (-1,-1), 'LEFT')]            
            )
        
        colwidths = (90, 270, 60, 60, 60)
        table = Table(data, colwidths, style=ts, repeatRows = 1)        
        Story.append(table)        
        
        
        return pdf_close_and_return(doc, Story, buffer, response)
        
    except:
        return server_error(request)    


def generate_calendar(year, month):
    
    ts = TableStyle(
        [('FONT', (0,0), (-1,-1), 'Helvetica-Bold', 8),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black) ]
        )
        
    ts2 = TableStyle(
        [('ALIGN', (0,0), (-1,-1), 'LEFT'),]      
        )  
        
    style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=8,
    )        
    
    import calendar        
    cal = calendar.monthcalendar(year, month)    
    for rowindex, row in enumerate(cal):
        for item_index, item in enumerate(row):
            if item == 0:
                cal[rowindex][item_index] = None

    cal = Table(cal, style=ts)

    header = '    ' + str(year) + ' / ' + str(month)
    header = Paragraph(header * 1, style)

    data = [[ [header, blank_paragraph, cal]],]
    return Table(data, style=ts2)

def get_prev_month(month, year):
    prev_month = month - 1
    if month == 1:
        prev_month = 12
        year = year - 1
        
    return prev_month, year

def birdcare_worksheet(request):

    try:

        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleH = styles['Heading3']
        styleH2 = styles['Heading4']

        today = datetime.date.today()
        
        from birdlist.views.breeding.birdcare_main import get_checklist_information
        cage_list = get_checklist_information()

        title = "Birdcare Worksheet"
        author = 'Andreas Kotowicz'
        
        Story, buffer, doc, response = pdf_header(page_size = portrait(A4), filename = "birdcare_worksheet.pdf", title=title, author=author)
        Story = add_title(title, Story, request, title_size=14)
        


        ''' calendar of this and previous month '''
        NOW = datetime.datetime.now()        
        year = NOW.year
        month = NOW.month
        this_month = generate_calendar(year, month)
        
        
        prev_month, year = get_prev_month(month, year)
        prev = generate_calendar(year, prev_month)
        
        prev_month, year = get_prev_month(prev_month, year)
        prev2 = generate_calendar(year, prev_month)        

        ts = TableStyle(
            [('VALIGN', (0,0), (-1,-1), 'TOP'),
             ('ALIGN', (0,0), (-1,-1), 'CENTER'),]      
            )
      
        data = [[[prev2], [prev], [this_month]],]      
        table = Table(data, (180, 180, 180), style = ts)
        Story.append(table)
        
        # add horizontal line
        Story.append(HRFlowable(width = '100%', thickness = 2, lineCap = 'round', spaceBefore = 0, spaceAfter = 0, hAlign = 'CENTER', vAlign = 'BOTTOM', dash = None))
        
        
        ''' for each cage do: '''
      
        for i in cage_list:
        
            cage = i['cage']
            coupling = i['coupling']
            juveniles = i['juveniles']
            
            # first cage might have no coupling, because a new couple has to be 
            # created, therefore we set reasonable defaults there.
            days_since_data = None
            transferred_to_string = ''
            juv_table = None
            
            header_string = cage.name
      
            # coupling in cage found
            if coupling:
                last_brood = coupling.get_last_brood()
                days_since_last_brood = ''
                if last_brood:
                    days_since_last_brood = last_brood.get_broods_birthday()
                    days_since_last_brood = today - days_since_last_brood
                    days_since_last_brood = days_since_last_brood.days.__str__()
                    days_since_data = True

                days_since_coupled = today - coupling.coupling_date
                days_since_coupled = days_since_coupled.days.__str__()

                comment = coupling.comment
                if comment:
                    comment = comment.replace('&', '&amp;')
                    comment = Paragraph(comment * 1, style)
                
                couple_separate = coupling.is_to_be_separated()
                couple_remove_nest = coupling.nest_has_to_be_removed()
                if couple_separate or couple_remove_nest:
                    header_string = header_string + '- Please '

                    if couple_remove_nest:
                        header_string = header_string + 'remove nest '

                    if couple_separate:
                        if couple_remove_nest:
                            header_string = header_string + 'and'
                        header_string = header_string + ' separate this couple'
                        transferred_to_string = 'transferred to:'

                # quite ugly because of duplicate code but I don't know python 
                # enough to figure out how to only insert the part that's extra.
                if days_since_data:
                    couple = [[ 'father', coupling.couple.get_male().name, transferred_to_string, ''],
                              [ 'mother', coupling.couple.get_female().name, transferred_to_string, ''],
                              [ 'coupling date', coupling.coupling_date ],
                              [ '# days coupled', days_since_coupled  ],
                              [ '# days since\n last hatch', days_since_last_brood ],
                              [ '# broods', coupling.get_number_of_broods()],
                              [ 'comment', comment ],
                              [ 'Has white offspring? - Yes / No', '' ],]
                else:
                    couple = [[ 'father', coupling.couple.get_male().name, transferred_to_string, ''],
                              [ 'mother', coupling.couple.get_female().name, transferred_to_string, ''],
                              [ 'coupling date', coupling.coupling_date ],
                              [ '# days coupled', days_since_coupled  ],
                              [ 'comment', comment ],
                              [ 'Has white offspring? - Yes / No', '' ],]
                              
            else: # no coupling in cage
                couple = [['father:', 'taken from:'],
                          ['mother:', 'taken from:']]
                if cage.bird_set.count() == 0:
                    # cage is empty
                    header_string = header_string + ' - Please add new couple'
                else:
                    # sometimes, birds are found inside a breeding cage, show the list!
                    header_string = header_string + ' - Non empty breeding cage - Please check status'
                    juv_table = [[ 'bird', 'dph (-)', 'renamed to', 'transferred to', 'sex(ed)']]
                    juv_table = create_table_of_birds(juv_table, cage.bird_set.all())
                          
            # juveniles found in cage                          
            if juveniles:
                juv_table = [[ 'juvenile', 'dph (-)', 'renamed to', 'transferred to', 'sex(ed)']]
                juv_table = create_table_of_birds(juv_table, juveniles)
                

            # table for newborns
            newborns = [[ 'nbr newborns', 'first birthday', 'last birthday'],
                        [ '# ', '', '']]
            

            ''' styles '''                
            ts2 = TableStyle(
                [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black),
                ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.black),
                ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
                ('FONT', (0,1), (1,-1), 'Helvetica', 8),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('ALIGN', (1,1), (-1,-1), 'LEFT'), ]
                )        

            span_id = 4
            if days_since_data:
                span_id = 6
                
            ts3 = TableStyle(
                    [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                    ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
                    ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 7),
                    ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
                    ('SPAN', (1, span_id), (3, span_id)),
                    ('ALIGN', (1,1), (-1,-1), 'LEFT'), ]
                    ) 
                    
            if transferred_to_string.__len__() > 0:
                ts3.add('LINEBELOW', (2,0), (3,0), 0.5, colors.black)
                ts3.add('LINEBELOW', (2,1), (3,1), 0.5, colors.black)


            bst = TableStyle(
                    [ ('VALIGN', (0,0), (-1,-1), 'TOP'), ]
                    )
            
            ''' put together the tables '''
            if coupling and juveniles:
                table1 = Table(juv_table, (52, 43, 65, 60, 40), style=ts2)
                table2 = Table(couple, (60, 60, 60, 50), style=ts3)
                table3 = Table(newborns, (70, 95, 95), style=ts2)
                data = [[[table2], [table1, blank_paragraph, table3]],]

                table = Table(data, style=bst)
                
                paragraph = Paragraph(header_string, styleH)
                paragraph.keepWithNext = True
                Story.append(paragraph)
                Story.append(table)              

            
            elif not coupling:
            
                ts1 = TableStyle(
                    [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                    ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
                    ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 7),
                    ('FONT', (1,0), (1,-1), 'Helvetica-Bold', 7),                    
                    ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('ALIGN', (1,1), (-1,-1), 'LEFT'), ]
                    )              
            

                if juv_table == None:
                    # by default, a cage without a couple is empty
                    table2 = Table(couple, (140, 160), style=ts1)
                    data = [[table2]]
                    table = Table(data, style=bst)
                
                else:
                    # sometimes, birds are found inside a breeding cage, show the list!
                    table1 = Table(juv_table, (52, 43, 65, 60, 40), style=ts2)
                    table2 = Table(couple, (140, 160), style=ts1)
                    data = [[[table2], [table1]],]
                    table = Table(data, style=bst)                    
                
                paragraph = Paragraph(header_string, styleH)
                paragraph.keepWithNext = True
                Story.append(paragraph)
                Story.append(table)
                
            elif coupling:
            
                ts1 = TableStyle(
                    [('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                    ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
                    ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 7),
                    ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (1,1), (-1,-1), 'LEFT'), ]
                    )  
            
                table1 = Paragraph("No previous juveniles", styleH2)
                table2 = Table(couple, (60, 60, 60, 50), style=ts3)
                table3 = Table(newborns, (70, 95, 95), style=ts2)          
                data = [[[table2], [table1, blank_paragraph, table3]],]

                table = Table(data, style=bst)
                
                paragraph = Paragraph(header_string, styleH)
                paragraph.keepWithNext = True                
                Story.append(paragraph)
                Story.append(table)                                 
            
            
            #colwidths = (350, 250)    
            #table = Table(data, colwidths, style=bst)
            
            # add space after table
            Story.append(Spacer(1, 15))
            # add horizontal line
            Story.append(HRFlowable(width = '100%', thickness = 2, lineCap = 'round', spaceBefore = 0, spaceAfter = 0, hAlign = 'CENTER', vAlign = 'BOTTOM', dash = None))
            #table._argW[0]=100*mm
            #table._argW[1]=100*mm
            
        
        return pdf_close_and_return(doc, Story, buffer, response)
    
    except:
        return server_error(request)    


def create_table_of_birds(juv_table, juveniles):
    for j in juveniles:
        sex = j.sex
        if (sex == j.SEX_UNKNOWN_JUVENILE) or (sex == j.SEX_UNKNOWN_NOT_VISIBLE):
            sex = ''
        else:
            sex = j.get_sex_display()         
            
        name = j.name
        reserved = j.reserved_until
        transfer = ''
        # highlight animals that need to be transferred, in bold face.
        if j.is_juvenile_to_be_transferred():
            transfer = '<b>*</b>'
            transfer = Paragraph(transfer * 1, style_small)
            name = '<b>' + name + '</b>'

        # highlight reserved animals.
        if reserved:
            name = name + ' <i>(R)</i>'
        
        name = Paragraph(name * 1, style_small)
        juv_table.append([name, j.get_phd() + ' (' + str(j.age_uncertainty) + ')', '', transfer,  sex])


    return juv_table
    

def cages_with_occupancy_pdf(request):
    try:
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleH = styles['Heading3']
        styleH2 = styles['Heading4']
    
        ts = TableStyle(
            [
            
            ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),]            
            )    
    
    
        cages = Cage.objects.filter(function__lte = Cage.FUNCTION_SOCIAL).order_by('room', 'name')
        rooms = cages.values_list('room', flat = True).order_by('room').distinct()
        title = "Cages and Occupancy"
        author = 'Andreas Kotowicz'

        Story, buffer, doc, response = pdf_header(page_size = portrait(A4), filename = "cages.pdf", title=title, author=author)
        Story = add_title(title, Story, request, title_size=14)
        
        Story.append(Spacer(1, 15))
        paragraph = Paragraph('For each cage the (occupancy / capacity) are shown. Overcrowded cages are highlighted in bold face.', styleH2)
        Story.append(paragraph)
        Story.append(Spacer(1, 15))
        
        for i in rooms:
            cages_this_room = cages.filter(room__id = i)
            this_room = cages_this_room[0].room
            header_string = this_room.__str__()
            
            data = []
            

            counter = 0
            counter2 = 0
            nbr_cols = 4
            this_row = ['', '', '', '']
            nbr_cages_in_room = cages_this_room.__len__()
            for j in cages_this_room:
                counter = counter + 1
                counter2 = counter2 + 1
                
                this_cage = j.name + ' - (' + str(j.occupancy()) + '/' + str(j.max_occupancy) + ')'
                if j.occupancy() > j.max_occupancy:
                    this_cage = '<b>' + this_cage + '</b>'
                    
                this_cage = Paragraph(this_cage * 1, style)                    
                    
                this_row[counter-1] = this_cage
                if nbr_cols.__rmod__(counter2) == 0 or nbr_cages_in_room == counter2:
                    data.append(this_row)
                    this_row = ['', '', '', '']
                    counter = 0           

            paragraph = Paragraph(header_string, styleH)
            paragraph.keepWithNext = True                
            Story.append(paragraph)
            
            colwidths = (140, 140, 140, 140)
            table = Table(data, colwidths, style=ts, repeatRows = 1) 
            Story.append(table) 
        

        return pdf_close_and_return(doc, Story, buffer, response)
    except:
        return server_error(request)    


def birds_for_breeding_pdf(request, exact_method=False):
    try:
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleH = styles['Heading3']
        styleH2 = styles['Heading4']
    
        ts = TableStyle(
            [
            ('FONT', (0,0), (-1,-1), 'Helvetica', 9),   
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),            
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),]      
            )
            
        ts2 = TableStyle(
            [
            ('FONT', (0,0), (-1,-1), 'Helvetica', 7),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 9),
            ('FONT', (6,0), (6,0), 'Helvetica-Bold', 6),
            ('FONT', (7,0), (7,0), 'Helvetica-Bold', 8),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),]      
            )                
    
        style = ParagraphStyle(
            name='Normal',
            fontName='Helvetica',
            fontSize=7,
        )    


        ''' get list of animals '''    
        from birdlist.utils.breeding import sort_birds_for_breeding, get_birds_for_breeding
        couples, males, females, males_id, females_id = get_birds_for_breeding(request.session, exact_method)
        couples, males, females, sort_by = sort_birds_for_breeding(couples, males, females, request.GET)


        ''' start document '''
        title = "Birds for breeding"
        author = 'Andreas Kotowicz'

        Story, buffer, doc, response = pdf_header(page_size = portrait(A4), filename = "birds_for_breeding.pdf", title=title, author=author)
        Story = add_title(title, Story, request, title_size=14)
        
        Story.append(Spacer(1, 15))
        paragraph = Paragraph('Please do not use birds that have been separated (previous breeding couple) less than 60 days ago!', styleH2)
        Story.append(paragraph)
        Story.append(Spacer(1, 15))
        

        colwidth0 = 40
        colwidth = 65
        colwidth2 = 80
        colwidth3 = 130

        ''' previous couples '''
        paragraph = Paragraph("Previously successful couples - available today (%s)" %couples.__len__(), styleH)
        paragraph.keepWithNext = True
        Story.append(paragraph)
        data = [['male', 'cage', 'age', 'female', 'cage', 'age', 'avg # broods', 'avg # juveniles', '# days separated (m/f)' ]]
        for c in couples:
            data.append([c['male'], c['male_cage'], c['male_age'], c['female'], \
            c['female_cage'], c['female_age'], str(round(c['AvgNoBroods'], 1)), str(round(c['AvgNoJuvs'], 1)), \
            str(c['male_last_separation']) + ' / ' + str(c['female_last_separation'])])       
        
        colwidths = (colwidth0, colwidth0, colwidth0, colwidth0, colwidth0, colwidth0, colwidth2, colwidth2, colwidth3)
        table = Table(data, colwidths, style=ts, repeatRows = 1)
        # table.keepWithNext = True
        Story.append(table)
        Story.append(Spacer(1, 15))        
        
        ''' males '''
        paragraph = Paragraph("Males for breeding - %s found" % males.__len__(), styleH)
        paragraph.keepWithNext = True
        Story.append(paragraph)
        data = [['name', 'cage', 'age (+-)', 'father', 'mother', 'prev. mates', '# days\n separated', 'reserv.', 'comment']]
        for b in males:
            bird = b['bird']
            bird_name = bird.name
            if bird_name:
                bird_name = Paragraph(bird_name * 1, style)
            
            reserved = bird.reserved_until
            if reserved:
                reserved = 'Yes'

            mates = b['mates']
            if mates:
                mates = Paragraph(mates * 1, style)
                
            comment = bird.comment
            if comment:
                comment = Paragraph(comment * 1, style)
                
            father = b['father']
            if father:
                father = Paragraph(father.name * 1, style)

            mother = b['mother']                
            if mother:
                mother = Paragraph(mother.name * 1, style)                       

                          
            data.append([bird_name, bird.cage.name, \
            str(b['age']) + ' (' + str(bird.age_uncertainty) +' )', \
            father, mother, mates, b['last_separation'], \
            reserved, comment  ])
        
        colwidths = (47, 35, 45, 47, 47, \
                     colwidth3, colwidth0, colwidth0, colwidth3)
        table = Table(data, colwidths, style=ts2, repeatRows = 1) 
        table.keepWithNext = True
        Story.append(table)
        
        ''' space between '''
        
        spacer = Spacer(1, 15)
        spacer.keepWithNext = True
        Story.append(spacer)        

        ''' females '''
        paragraph = Paragraph("females for breeding - %s found" % females.__len__(), styleH)
        paragraph.keepWithNext = True
        Story.append(paragraph)
        data = [['name', 'cage', 'age (+-)', 'father', 'mother', 'prev. mates', '# days\n separated', 'reserv.', 'comment']]
        for b in females:
            bird = b['bird']
            bird_name = bird.name
            if bird_name:
                bird_name = Paragraph(bird_name * 1, style)
            
            reserved = bird.reserved_until
            if reserved:
                reserved = 'Yes'

            mates = b['mates']
            if mates:
                mates = Paragraph(mates * 1, style)
                
            comment = bird.comment
            if comment:
                comment = Paragraph(comment * 1, style)
                
            father = b['father']
            if father:
                father = Paragraph(father.name * 1, style)

            mother = b['mother']                
            if mother:
                mother = Paragraph(mother.name * 1, style)                       

                          
            data.append([bird_name, bird.cage.name, \
            bird.get_phd() + ' (' + str(bird.age_uncertainty) +' )', \
            father, mother, mates, b['last_separation'], \
            reserved, comment  ])
        
        colwidths = (47, 35, 45, 47, 47, \
                     colwidth3, colwidth0, colwidth0, colwidth3)
        table = Table(data, colwidths, style=ts2, repeatRows = 1) 
        Story.append(table)
        
        return pdf_close_and_return(doc, Story, buffer, response)
        
    except:
        return server_error(request)

