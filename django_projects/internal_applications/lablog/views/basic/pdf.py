from django.http import HttpResponse

def generate_dummy(request):

    try:
        # see http://docs.djangoproject.com/en/dev/howto/outputting-pdf/
        from cStringIO import StringIO
        from reportlab.pdfgen import canvas
        
        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'

        buffer = StringIO()

        # Create the PDF object, using the StringIO object as its "file."
        p = canvas.Canvas(buffer)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        p.drawString(100, 100, "no meaningful pdf file. Please make me general.")

        # Close the PDF object cleanly.
        p.showPage()
        p.save()

        # Get the value of the StringIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    except:
        return HttpResponse("Ups, something went wrong. You are probably missing 'reportlab'.")


