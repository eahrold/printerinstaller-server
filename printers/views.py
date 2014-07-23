from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template import RequestContext, Template, Context, loader
from django.template.loader import get_template
from django.forms.models import inlineformset_factory
from django.conf import settings
from urlparse import urlunparse
from plistlib import writePlistToString

from models import *
from forms import *

from sparkle.models import *
from printerinstaller.utils import github_latest_release, site_info

def index(request):
    printerlists = PrinterList.objects.filter(public=True)
    version_url = None
    if settings.HOST_SPARKLE_UPDATES:
        version = Version.objects.filter(application__name='Printer-Installer', active=True).order_by('-published')
        if version:
            version_url = version[0].update.url
    
    if not version_url:
        version_url = github_latest_release(settings.GITHUB_LATEST_RELEASE)

    host = request.get_host()
    subpath = request.META.get('SCRIPT_NAME')
    scheme = request.is_secure() and 'printerinstallers' or 'printerinstaller'

    pr_uri = urlunparse([scheme,host,subpath,None,None,None])
    context = {'domain':pr_uri,'printerlists': printerlists, 'version':version_url}
    
    return render(request, 'printers/index.html', context)

@login_required(redirect_field_name='')
def manage(request):
    #show list of printers and groups
    printerlists = PrinterList.objects.all()
    printers = Printer.objects.all()
    options = Option.objects.all()
    
    context = {'printerlists': printerlists,'printers' : printers,'options':options}
    return render(request, 'printers/manage.html', context)


###################################
######  Printer Methods ###########
###################################
@login_required(redirect_field_name='')
def printer_details(request, id):
    printer = get_object_or_404(Printer, pk=id)
    return render(request, 'printers/printer_details.html', {'printer': printer})

@login_required(redirect_field_name='')
def printer_add(request):
    if request.method == 'POST':
        form = PrinterForm(request.POST,request.FILES)
        if form.is_valid():
            printer = form.save(commit=True)
            new_option = form.cleaned_data['new_option']
            if new_option:
                 printer.option.create(option=new_option)
            printer.save()
            return redirect('printers.views.manage')            
    else:
        form = PrinterForm()
        
    return render_to_response('printers/forms/printer.html', {'form': form,}, context_instance=RequestContext(request))


@login_required(redirect_field_name='')
def printer_edit(request, id):
    printer=get_object_or_404(Printer, pk=id)
    if request.POST:
        form = PrinterForm(request.POST,request.FILES,instance=printer)
        if form.is_valid(): 
            form.save()            
            new_option = form.cleaned_data['new_option']
            if new_option:
                 printer.option.create(option=new_option)            
            printer.save()
            return redirect('printers.views.manage')            
    else:
        form = PrinterForm(instance=printer)
        
    return render_to_response('printers/forms/printer.html', {'form': form,'printer':printer}, context_instance=RequestContext(request))
    
@login_required(redirect_field_name='')
def printer_delete(request, id):
    printer = get_object_or_404(Printer, pk=id)
    if printer:
        printer.delete()
    return redirect('printers.views.manage')
    


########################################
######  Printer List Methods ###########
########################################  
@login_required(redirect_field_name='')
def printerlist_add(request):
    if request.method == 'POST':
        form = PrinterListForm(request.POST)
        if form.is_valid():
            printerlist = form.save(commit=True)
            printerlist.save()
            return redirect('printers.views.manage')            
    else:
        form = PrinterListForm()
    return render_to_response('printers/forms/printerlist.html', {'form': form,}, context_instance=RequestContext(request))
    
@login_required(redirect_field_name='')
def printerlist_details(request, id):
    printerlist = get_object_or_404(PrinterList, pk=id)
    return render(request, 'printers/printerlist_details.html', {'printerlist': printerlist})

@login_required(redirect_field_name='')
def printerlist_edit(request, id):
    printerlist = PrinterList.objects.get(id=id)  
    if request.POST:
        form = PrinterListForm(request.POST,instance=printerlist)
        if form.is_valid():
            form.save()
            return redirect('printers.views.manage')            
    else:
        form = PrinterListForm(instance=printerlist)
    return render_to_response('printers/forms/printerlist.html', {'form': form,'printerlist':printerlist}, context_instance=RequestContext(request))
    
@login_required(redirect_field_name='')
def printerlist_delete(request, id):
    printerlist = get_object_or_404(PrinterList, pk=id)
    printerlist.delete()
    return redirect('printers.views.manage')

@login_required(redirect_field_name='')
def printerlist_public(request, id):
    printerlist = get_object_or_404(PrinterList, pk=id)
    if printerlist.public:
        printerlist.public=False
    else:
        printerlist.public=True
    printerlist.save()
    return redirect('printers.views.manage')



########################################
#########  Option Methods ##############
########################################  
@login_required(redirect_field_name='')
def options_add(request):
    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('printers.views.manage')
    else:
        form = OptionForm()
    return render_to_response('printers/forms/option.html', {'form': form,}, context_instance=RequestContext(request))
    
def options_edit(request, id):
    options = get_object_or_404(Option, pk=id)
    if request.POST:
        form = OptionForm(request.POST,instance=options)
        if form.is_valid():
            form.save()
            return redirect('printers.views.manage')            
    else:
        form = OptionForm(instance=options)
    return render_to_response('printers/forms/option.html', {'form': form,'options':options}, context_instance=RequestContext(request))
   
@login_required(redirect_field_name='')
def options_delete(request,id):
    option = get_object_or_404(Option, pk=id)
    option.delete()
    return redirect('printers.views.manage')
    

## This is the request that returns the plist for the Printer-Installer.app
## it should be the only area that requires no login
def getlist(request, name):       
    pl = get_object_or_404(PrinterList, name=name)    
    printers=pl.printer.all()
    plist = []
    
    if settings.SERVE_FILES and Version.objects.all():
        _site_info = site_info(request)
        updateServer=os.path.join(_site_info['root'],
                                    _site_info['subpath'],
                                    'sparkle/Printer-Installer/appcast.xml',
                                    )
    else:
        updateServer = settings.GITHUB_APPCAST_URL


    for p in printers:
        if(p.ppd_file):
            ppd_url=os.path.join(_site_info['root'])+p.ppd_file.url
        else:
            ppd_url=''
            
        d = {
        'name':p.name,
        'host':p.host,
        'protocol':p.protocol,
        'description':p.description,
        'location':p.location,
        'model':p.model,
        'ppd_url':ppd_url,
        }
        
        opts = p.option.all()
        addopt = []
        for o in opts:
            addopt.append(o.option)
        
        if addopt:
            d['options'] = addopt
            
        plist.append(d)
        
    detail=writePlistToString({'printerList':plist,'updateServer':updateServer})
    return HttpResponse(detail)
    