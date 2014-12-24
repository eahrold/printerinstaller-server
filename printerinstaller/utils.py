import os, subprocess, urllib2
import json

from django.contrib.sites.models import Site, RequestSite

def get_client_ip(request):
    '''simple method to get client ip''' 
    forward_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward_ip:
        ip_addr = forward_ip.split(',')[0]
    else:
        ip_addr = request.META.get('REMOTE_ADDR')
    
    return ip_addr   

def delete_file_on_change(sender, instance, attr):
    '''if object is changed remove outdated fs file'''
    try:
        pre_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    old_file = getattr(pre_instance, attr, None)
    new_file = getattr(instance, attr, None)

    if old_file and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

def delete_file_on_delete(instance, attr):
    '''If a object with a reference to a file
    is deleted, delete the actual file too'''
    the_file = getattr(instance, attr, None)
    if the_file and os.path.isfile(the_file.path):
        os.remove(the_file.path)

def site_info(request):
    '''return info relating to the site'''
    _site_info = {'protocol': request.is_secure() and 'https' or 'http'}
    _site_info['port'] = request.META.get('SERVER_PORT')
    _site_info['subpath'] = request.META.get('SCRIPT_NAME')
    
    # Getting the site domain and name is more secure if we can get it
    # from Site._meta so use that first, and fall back using the request.
    if Site._meta.installed:
        _site_info['domain'] = Site.objects.get_current().domain
        _site_info['name'] = Site.objects.get_current().name
    else:
        _site_info['domain'] = RequestSite(request).domain
        _site_info['name'] = RequestSite(request).name
    _site_info['root'] = _site_info['protocol'] + '://' + _site_info['domain']
    if _site_info['port'] and not _site_info['port'] in ('443', '80',):
        _site_info['root'] = _site_info['root']+':'+ _site_info['port']
    return _site_info

