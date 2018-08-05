import requests
import json
import threading
import os
from django.shortcuts import render
from django.template.defaulttags import register
from django.http import HttpResponseRedirect
from django.urls import reverse
from socket import gaierror, gethostbyname
from multiprocessing.dummy import Pool as ThreadPool
from urllib.parse import urlparse
from time import gmtime, strftime

from .settings import refresh_interval, filename, site_down, number_threads, include_search
from .models import Site
from .forms import SearchForm


@register.filter
def get_item(dictionary, key):
    """ This is a custom filter for django templates allowing you to easily get
    a value from a dictionary."""
    return dictionary.get(key)


def is_reachable(url):
    """ This function checks to see if a host name has a DNS entry
    by checking for socket info."""
    try:
        gethostbyname(url)
    except gaierror:
        return False
    else:
        return True


def get_status_code(url):
	""" This function returns the status code of the url."""
	try:
	    status_code = requests.get(url, timeout=30).status_code
	    return status_code
	except requests.ConnectionError:
	    return site_down


def check_single_url(url):
    """This function checks a single url and if connectable returns
    the status code, else returns variable site_down (default: UNREACHABLE)."""
    if is_reachable(urlparse(url).hostname) == True:
        return str(get_status_code(url))
    else:
        return site_down


def launch_checker():
    """This function launches the check_multiple_urls function every x seconds
    (defined in refresh interval variable)."""
    t = threading.Timer(refresh_interval, launch_checker)
    t.start()
    global returned_statuses
    global returned_uptimes
    returned_statuses = check_multiple_urls()
    returned_uptimes = update_uptimes()


def check_multiple_urls():
    """This function checks through urls specified in the checkurls.json file
    (specified in the filename variable) and
    returns their statuses as a dictionary."""
    statuses = {}
    temp_list_statuses = []
    global last_update_time
    pool = ThreadPool(number_threads)
    temp_list_statuses = pool.map(check_single_url, list_urls)
    for i in range(len(list_urls)):
        statuses[list_urls[i]] = temp_list_statuses[i]
    last_update_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return statuses


def update_uptimes():
    """ This function updates the db with the latest status codes and
    calculates the current % uptime, finally returning a dictionary containing
    urls and keys and uptimes as values. """
    uptimes = {}
    temp_list_uptimes = []
    for urly in list_urls:
        try:
            working_url = Site.objects.get(url=urly)
        except Site.DoesNotExist:
            working_url = Site()
            working_url.url = urly
        working_url.status = returned_statuses[urly]
        if returned_statuses[urly] == '200':
            working_url.was_checked += 1
            working_url.was_up += 1
        else:
            working_url.was_checked += 1
        working_url.uptime = float((working_url.was_up / working_url.was_checked) * 100)
        working_url.save()
        temp_list_uptimes.append(working_url.uptime)
    for i in range(len(list_urls)):
        uptimes[list_urls[i]] = temp_list_uptimes[i]
    return uptimes


def compare_submitted(submitted):
    """This function checks whether the value in the dictionary is found in 
    the checkurls.json file. """
    stripped_submission = https_start_strip(submitted)
    if stripped_submission in list_urls:
        flaggy = True
    else:
        flaggy = False
    return (flaggy, stripped_submission)


def https_start_strip(url):
    """ This function strips whitespace from the user input and ensures the url
    starts with https/http."""
    url = url.strip().lower()
    if url[:7] == 'http://':
        return url
    elif url[:8] == 'https://':
        return url
    else:
        url = "https://" + url
        return url


def generate_list_urls(input_dict):
    """ Generates a current list of all urls in checkurls.json."""
    list_urls = []
    for group, urls in input_dict.items():
        for url in urls:
            list_urls.append(url)
    return list_urls


def index(request):
    """The home page for statuscheck"""
    form = SearchForm()
    context = {
        'form': form,
        'list_urls': list_urls,
        'last_update_time': last_update_time,
        'returned_statuses': returned_statuses,
        'checkurls': checkurls,
        'include_search': include_search, 'returned_uptimes': returned_uptimes
        }
    return render(request, 'statuscheck/index.html', context)


def result(request):
    """ Django view to return search results."""
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            results = compare_submitted(form.cleaned_data['submitted'])
            context = {
'results': results,
'last_update_time': last_update_time,
'returned_statuses': returned_statuses,
'checkurls': checkurls,
'include_search': include_search, 'returned_uptimes': returned_uptimes
}
            return render(request, 'statuscheck/index.html', context)
    else:
        return HttpResponseRedirect(reverse('statuscheck:index'))

### Get the current directory to open the checkurls.json file
module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, filename)
with open(file_path) as f:
    checkurls = json.load(f)
list_urls = generate_list_urls(checkurls)
returned_statuses = {}
returned_uptimes = {}
last_update_time = 'time string'


launch_checker()