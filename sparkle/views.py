from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required, permission_required
from sparkle.models import Application, Version, SystemProfileReport, SystemProfileReportRecord

def appcast(request, name):
    """Generate the appcast for the given application while recording any system profile reports"""
    
    application = get_object_or_404(Application, name=name)
    
    # if there are get parameters from the system profiling abilities
    if len(request.GET):
        # create a report and records of the keys/values
        report = SystemProfileReport.objects.create(ip_address=request.META.get('REMOTE_ADDR'))
        for key, value in request.GET.iteritems():
            record = SystemProfileReportRecord.objects.create(report=report, key=key, value=value)
    
    # get the latest versions
    versions = Version.objects.filter(application__name=name, active=True).order_by('-published')
    
    # get the current site for the domain
    site = Site.objects.get_current()
    
    return render_to_response('sparkle/appcast.xml', {'application': application, 'versions': versions, 'site': site})

@login_required(redirect_field_name='')
def index(request):
    apps = Version.objects.all()
    site = Site.objects.get_current()
    context = {'apps':apps,'site':site}
    
    return render(request, 'sparkle/index.html',context) 
