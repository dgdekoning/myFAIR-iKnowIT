import commands
import json
import csv
import re
import os
import hashlib
import time
import uuid

from time import strftime, gmtime
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.client import ConnectionError
from django.shortcuts import render_to_response, render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


"""
Login page with session storage.
"""
@csrf_exempt
def login(request):
    if request.method == 'POST':
        err = []
        server = request.POST.get('server')
        api = request.POST.get('api')
        storage = request.POST.get('storage')
        username = request.POST.get('username')
        password = request.POST.get('password')
        noexpire = request.POST.get('no-expire')
        if api != "":
            request.session['api'] = api
        else:
            err.append("No api key")
            request.session.flush()
            return render_to_response('login.html', context={'error': err})
        if storage != "":
            request.session['storage'] = storage
        else:
            request.session.flush()
        if server != "":
            request.session['server'] = server
        else:
            err.append("No server selected")
            request.session.flush()
            return render_to_response('login.html', context={'error': err})
        if username != "" and password != "":
            request.session['username'] = username
            request.session['password'] = password
        else:
            err.append("No valid username or password")
            request.session.flush()
            return render_to_response('login.html', context={'error': err})
        if noexpire == "yes":
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(43200)
        return render_to_response('home.html', context={'error': err})
    return render(request, 'login.html')


"""
myFAIR index. Shows all important information on the homepage.
"""
@csrf_exempt
def index(request):
    try:
        login(request)
        if 'api' not in request.session or 'username' not in request.session or 'password' not in request.session:
            err = ""
            login(request)
            return render_to_response('login.html', context={'error': err})
        else:
            if request.POST.get('inv') is not None:
                investigation = request.POST.get('inv')
            else:
                investigation = ""
            folders = []
            investigations = []
            if investigation is not None and investigation != "":
                username = request.POST.get('username')
                password = request.POST.get('password')
                storage = request.POST.get('storage')
                api = request.POST.get('api')
                server = request.POST.get('server')
                oc_folders = commands.getoutput(
                    "curl -s -X PROPFIND -u " + username + ":" + password + " '" + storage + "/" + investigation +
                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                inv_folders = commands.getoutput(
                    "curl -s -X PROPFIND -u " + username + ":" + password + " '" + storage +
                    "/' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                check_folder = commands.getoutput(
                    "curl -s -X PROPFIND -u " + username + ":" + password + " '" + storage +
                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'")
            else:
                username = request.session.get('username')
                password = request.session.get('password')
                storage = request.session.get('storage')
                api = request.session.get('api')
                server = request.session.get('server')
                commands.getoutput("mkdir " + username)
                oc_folders = ""
                inv_folders = commands.getoutput(
                    "curl -s -X PROPFIND -u " + username + ":" + password + " '" + storage +
                    "/' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                check_folder = commands.getoutput(
                    "curl -s -X PROPFIND -u " + username + ":" + password + " '" + storage +
                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'")
                if "MYFAIR" not in check_folder:
                    commands.getoutput(
                        "curl -s -k -u " + username + ":" + password + " -X MKCOL " + storage + "/")
            for inv in inv_folders:
                if "/owncloud/" in request.session.get('storage'):
                    new = inv.replace('/owncloud/remote.php/webdav/', '').replace('/', '')
                    investigations.append(new)
                else:
                    new = inv.replace('/remote.php/webdav/', '').replace('/', '')
                    investigations.append(new)
            for oc in oc_folders:
                if "/owncloud/" in request.session.get('storage'):
                    new = oc.replace('/owncloud/remote.php/webdav/', '').replace('/', '').replace(investigation, '')
                    folders.append(new)
                else:
                    new = oc.replace('/remote.php/webdav/', '').replace('/', '').replace(investigation, '')
                    folders.append(new)
            folders = filter(None, folders)
            investigations = filter(None, investigations)
            if 'webdav' in storage:
                if not check_folder:
                    err = "Credentials are invalid. Please try again."
                    request.session.flush()
                    return render_to_response('login.html', context={'error': err})
            gi = GalaxyInstance(url=request.session.get('server'), key=request.session.get('api'))
            user = gi.users.get_current_user()
            gusername = user['username']
            workflows = gi.workflows.get_workflows
            history = gi.histories.get_histories()
            hist = json.dumps(history)
            his = json.loads(hist)
            return render(request, 'home.html',
                          context={'workflows': workflows, 'histories': his, 'user': gusername, 'api': api,
                                   'username': username, 'password': password, 'server': server,
                                   'storage': storage, 'investigations': investigations, 'studies': folders,
                                   'inv': investigation})

    except ConnectionError as err:
        err = "Invalid API Key"
        request.session.flush()
        return render_to_response('login.html', context={'error': err})


"""
Get all the samples that are selected.
"""
@csrf_exempt
def samples(request):
    samples = request.POST.get('samples')
    sampleselect = []
    if samples is not None or samples != "[]":
        sample = samples.split(',')
        for sam in sample:
            sampleselect.append(sam.replace('[', '').replace('"', '').replace(']', ''))
        return render(request, 'home.html', context={'samples': sampleselect})
    return render(request, 'home.html', context={'samples': sampleselect})


"""
Delete triples based on study name.
"""
@csrf_exempt
def modify(request):
    if request.session.get('username') is not None:
        if request.POST.get('ok') == 'ok':
            if request.POST.get('dstudy') != "":
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=WITH <http://127.0.0.1:3030/ds/data/" +
                    request.session['username'].replace('@', '') + "> DELETE {?s ?p ?o} WHERE { ?s <http://127.0.0.1:3030/ds/data?graph=" +
                    request.session['username'].replace('@', '') + "#group_id> ?group . FILTER(?group = \"" +
                    request.POST.get('dstudy') + "\") ?s ?p ?o }'")
            elif request.POST.get('dinvestigation') != "":
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=WITH <http://127.0.0.1:3030/ds/data/" +
                    request.session['username'].replace('@', '') + "> DELETE {?s ?p ?o} WHERE { ?s <http://127.0.0.1:3030/ds/data?graph=" +
                    request.session['username'].replace('@', '') + "#investigation_id> ?group . FILTER(?group = \"" +
                    request.POST.get('dinvestigation') + "\") ?s ?p ?o }'")
        else:
            err = "Please check accept to delete study or investigation"
            return render(request, "modify.html", context={'error': err})
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


"""
Call the modify/delete page.
"""
def delete(request):
    return render(request, 'modify.html')


"""
Select what files need to be stored in the triple store.
"""
@csrf_exempt
def triples(request):
    if request.session.get('username') == "" or request.session.get('username') is None:
        return HttpResponseRedirect('/')
    else:
        folders = []
        studies = []
        inv = request.POST.get('inv')
        oc_folders = commands.getoutput(
            "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') +
            " '" + request.session.get('storage') + "/' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
        if filter(None, oc_folders):
            for oc in oc_folders:
                if "/owncloud/" in request.session.get('storage'):
                    new = oc.replace('/owncloud/remote.php/webdav/', '').replace('/', '')
                    folders.append(new)
                else:
                    new = oc.replace('/remote.php/webdav/', '').replace('/', '')
                    folders.append(new)
            folders = filter(None, folders)
            if request.POST.get('inv') != "" and request.POST.get('inv') is not None:
                oc_studies = commands.getoutput(
                    "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') +
                    " '" + request.session.get('storage') + "/" + request.POST.get('inv') +
                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                for s in oc_studies:
                    if request.POST.get('inv') != "" and request.POST.get('inv') is not None:
                        if "/owncloud/" in request.session.get('storage'):
                            new = s.replace('/owncloud/remote.php/webdav/' + request.POST.get('inv') + "/", '').replace('/', '')
                            studies.append(new)
                        else:
                            new = s.replace('/remote.php/webdav/' + request.POST.get('inv') + "/", '').replace('/', '')
                            studies.append(new)
                    elif request.POST.get('selected_folder') != "" and request.POST.get('selected_folder') is not None:
                        if "/owncloud/" in request.session.get('storage'):
                            new = s.replace('/owncloud/remote.php/webdav/' + request.POST.get('selected_folder') + "/", '').replace('/', '')
                            studies.append(new)
                        else:
                            new = s.replace('/remote.php/webdav/' + request.POST.get('selected_folder') + "/", '').replace('/', '')
                            studies.append(new)
                studies = filter(None, studies)
        if request.method == 'POST':
            datalist = request.POST.get('datalist')
            metalist = request.POST.get('metalist')
            disgenet = request.POST.get('disgenet-tag')
            edam = request.POST.get('edam-tag')
            if request.POST.get('selected_folder') is not None:
                inv = request.POST.get('selected_folder')
            if inv != "" and inv is not None:
                files = []
                filelist = ''
                if request.POST.get('study') != "" and request.POST.get('study') is not None:
                    study = request.POST.get('study')
                    filelist = commands.getoutput(
                        "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') +
                        " '" + request.session.get('storage') + "/" + inv + "/" + study +
                        "' | grep -oPm100 '(?<=<d:href>)[^<]+'").split("\n")
                for f in filelist:
                    if "/owncloud/" in request.session.get('storage'):
                        new = f.replace('/owncloud/remote.php/webdav/' + inv + "/" + study, '').replace('/', '')
                        files.append(new)
                    else:
                        new = f.replace('/remote.php/webdav/' + inv + "/" + study, '').replace('/', '')
                        files.append(new)
                files = filter(None, files)
                if not filter(None, filelist):
                    if request.POST.get('selected_study') is not None:
                        study = request.POST.get('selected_study')
            metadata = []
            datafiles = []
            if datalist is not None or metalist is not None:
                if request.POST.get('selected_study') is not None:
                    study = request.POST.get('selected_study')
                datalist = datalist.split(',')
                metalist = metalist.split(',')
                for d in datalist:
                    if 'webdav' not in request.session.get('storage'):
                        datafiles.append(d)
                    else:
                        datafiles.append(request.session.get('storage') + "/" + inv + "/" + study + "/" + d)
                for m in metalist:
                    if 'webdav' not in request.session.get('storage'):
                        metadata.append(m)
                    else:
                        metadata.append(request.session.get('storage') + "/" + inv + "/" + study + "/" + m)
            if metadata or datafiles:
                return render(request, 'store.html', context={'metadata': metadata, 'datafiles': datafiles,
                                                              'inv': inv, 'study': study, 'edam': edam,
                                                              'disgenet': disgenet})
            return render(request, 'triples.html', context={'folders': folders, 'files': files, 'studies': studies,
                                                            'inv': inv, 'sstudy': study})
        return render(request, 'triples.html', context={'folders': folders, 'studies': studies, 'investigation': inv})


"""
Get studies based on the investigation selected in the indexing menu.
"""
@csrf_exempt
def investigation(request):
    if request.session.get('username') is not None:
        oc_folders = commands.getoutput(
            "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') +
            " '" + request.session.get('storage') + "/' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
        if filter(None, oc_folders):
            folders = []
            studies = []
            oc_studies = ""
            for oc in oc_folders:
                if "/owncloud/" in request.session.get('storage'):
                    new = oc.replace('/owncloud/remote.php/webdav/', '').replace('/', '')
                    folders.append(new)
                else:
                    new = oc.replace('/remote.php/webdav/', '').replace('/', '')
                    folders.append(new)
            folders = filter(None, folders)
            if request.POST.get('folder') != "" and request.POST.get('folder') is not None:
                oc_studies = commands.getoutput(
                    "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') +
                    " '" + request.session.get('storage') + "/" + request.POST.get('folder') +
                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
            else:
                if request.POST.get('selected_folder') is not None:
                    oc_studies = commands.getoutput(
                        "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') +
                        " '" + request.session.get('storage') + "/" + request.POST.get('selected_folder') +
                        "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
            if oc_studies != "":
                for s in oc_studies:
                    if request.POST.get('folder') != "" and request.POST.get('folder') is not None:
                        if "/owncloud/" in request.session.get('storage'):
                            new = s.replace('/owncloud/remote.php/webdav/' + request.POST.get('folder') + "/", '').replace('/', '')
                            studies.append(new)
                        else:
                            new = s.replace('/remote.php/webdav/' + request.POST.get('folder') + "/", '').replace('/', '')
                            studies.append(new)
                    elif request.POST.get('selected_folder') != "" and request.POST.get('selected_folder') is not None:
                        if "/owncloud/" in request.session.get('storage'):
                            new = s.replace('/owncloud/remote.php/webdav/' +
                                            request.POST.get('selected_folder') + "/", '').replace('/', '')
                            studies.append(new)
                        else:
                            new = s.replace('/remote.php/webdav/' + request.POST.get('selected_folder') + "/", '').replace('/', '')
                            studies.append(new)
                studies = filter(None, studies)
                inv = request.POST.get('folder')
                return render(request, 'triples.html', context={'folders': folders, 'studies': studies, 'inv': inv})
            else:
                return HttpResponseRedirect('/triples')
    else:
        return HttpResponseRedirect('/')


"""
Read the metadata file and store all the information in the Fuseki triple store.
"""
@csrf_exempt
def store(request):
    if request.method == 'POST':
        username = request.session.get('username')
        password = request.session.get('password')
        storage = request.session.get('storage')
        inv = request.POST.get('inv')
        study = request.POST.get('study')
        metadata = request.POST.get('metadata')
        datafile = request.POST.get('datafile')
        disgenet = onto(request.POST.get('disgenet'), request.POST.get('edam'))[0]
        edam = onto(request.POST.get('disgenet'), request.POST.get('edam'))[1]
        if username == "" or username is None:
            login()
        else:
            pid = datafile
            metadata = metadata.split(',')
            if metadata is not None:
                for m in metadata:
                    mfile = m.replace('[', '').replace(']', '').replace('"', '').replace(' ', '')
                    metafile = commands.getoutput("curl -s -k -u " + username + ":" + password + " " + mfile[1:])
                    metaf = open(username + '/metafile.csv', 'w')
                    metaf.write(metafile)
                    metaf.close()
                    filemeta = "metafile.csv"
                    if "This is the WebDAV interface. It can only be accessed by WebDAV clients such as the ownCloud desktop sync client." in metafile:
                        createMetadata(request, datafile)
                        filemeta = "meta.txt"
                        commands.getoutput("curl -s -k -u " + username + ":" + password + " -T " + '\'' + "meta.txt" + '\'' +
                                           " " + storage + "/" + inv + "/" + study + "/meta.txt")
            with open(username + "/" + filemeta, 'rb') as csvfile:
                count = 0
                reader = csv.DictReader(csvfile)
                cnt = 0
                for row in reader:
                    for p in pid.split(','):
                        data = p.replace('[', '').replace(']', '').replace("'", "").replace('"', '').replace(' ', '')[1:]
                        commands.getoutput(
                            "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                            username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                            username.replace('@', '') + "#pid> \"" + data + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#investigation_id> \"" + inv + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#group_id> \"" + study + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#disgenet_iri> \"" + disgenet + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#edam_iri> \"" + edam + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#disease> \"" + request.POST.get('disgenet') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    if filemeta == "meta.txt":
                        commands.getoutput(
                            "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                            username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                            username.replace('@', '') + "#meta> \"" + storage + "/" + inv + "/" + study +
                            "/meta.txt" + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    else:
                        for m in metadata:
                            mfile = m.replace('[', '').replace(']', '').replace('"', '').replace("'", "").replace(' ', '')
                            commands.getoutput(
                                "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                                username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) +
                                "> <http://127.0.0.1:3030/ds/data?graph=" + username.replace('@', '') + "#meta> \"" + mfile[1:] + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    headers = []
                    for (k, v) in row.items():
                        for h in range(0, len(k.split('\t'))):
                            if k.split('\t')[h] != "":
                                value = v.split('\t')[h]
                                header = k.split('\t')[h]
                                headers.append(header.replace('"', ''))
                                commands.getoutput(
                                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                                    username.replace('@', '') + "#" + header.replace('"', '') + "> \"" + value.replace('"', '').replace('+', '%2B') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    if "sex" not in headers:
                        commands.getoutput(
                            "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                            username.replace('@', '') + "> { <http://127.0.0.1:3030/" + study + "_" + str(cnt) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                            username.replace('@', '') + "#sex> \"" + 'Unknown' + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    count += 1
                    cnt += 1
            commands.getoutput("rm " + username + "/metafile.csv")
            commands.getoutput("rm " + username + "/meta.txt")
        return HttpResponseRedirect('/')


"""
Get the current history id.
"""
def get_history_id(api, server):
    gi = GalaxyInstance(url=server, key=api)
    cur_hist = gi.histories.get_current_history()
    current = json.dumps(cur_hist)
    current_hist = json.loads(current)
    history_id = current_hist['id']
    return history_id


"""
Get input data based on the selected history.
Find the number of uploaded files and return the id's of the files.
"""
def get_input_data(api, server):
    gi = GalaxyInstance(url=server, key=api)
    history_id = get_history_id(api, server)
    hist_contents = gi.histories.show_history(history_id, contents=True)
    inputs = []
    datacount = 0
    datasets = [dataset for dataset in hist_contents if not dataset['deleted']]
    for dataset in datasets:
        inputs.append(dataset['id'])
        datacount += 1
    return inputs, datacount


"""
Create a metadata file when there is none available.
This only works on GEO data matrices.
"""
def createMetadata(request, datafile):
    samples = []
    datafile = datafile.split(',')
    for f in datafile:
        filename = f.replace('[', '').replace(']', '').replace('"', '').replace(' ', '')
        cont = commands.getoutput("curl -u " + request.session.get('username') + ":" + request.session.get('password') + " -k -s " + filename[1:])
    with open(request.session.get('username') + "/data.txt", "w") as datafile:
        datafile.write(cont)
    with open(datafile.name, "r") as tfile:
        for line in tfile:
            if "!Sample_geo_accession" in line:
                line = line.split('\t')
                for x in range(0, len(line)):
                    samples.append(line[x].replace('\n', ''))
        samples = filter(None, samples)
        tfile.seek(0)
        with open(request.session.get('username') + "/meta.txt", "w") as meta:
            for i in range(0, len(samples)):
                for line in tfile:
                    if "!Sample" in line:
                        line = line.split('\t')
                        line[i] = line[i].replace("!Sample_", "").replace("\n", "").replace("'", "").replace(",", "").replace("\"", "")
                        if line[i] == "geo_accession":
                            line[i] = "sample_id"
                        elif line[1] == "\"female\"" or line[1] == "\"male\"":
                            line[0] = "sex"
                        if "title" not in line[0]:
                            meta.write(re.sub(r'[^\x00-\x7F]+', ' ', line[i]) + '\t')
                meta.write('\n')
                tfile.seek(0)
        meta.close()
    datafile.close()
    commands.getoutput("rm  " + request.session.get('username') + "/data.txt")
    return meta


"""
Fill lists with study names, data files and metadata files.
"""
def get_selection(iselect, gselect, select, mselect):
    groups = []
    files = []
    mfiles = []
    investigations = []
    for g in gselect:
        groups.append(g.replace('[', '').replace('"', '').replace(']', ''))
    for s in select:
        if s.replace('[', '').replace('"', '').replace(']', '') not in files:
            files.append(s.replace('[', '').replace('"', '').replace(']', ''))
    for m in mselect:
        if m.replace('[', '').replace('"', '').replace(']', '') not in mfiles:
            mfiles.append(m.replace('[', '').replace('"', '').replace(']', ''))
    for i in iselect:
        if i.replace('[', '').replace('"', '').replace(']', '') not in investigations:
            investigations.append(i.replace('[', '').replace('"', '').replace(']', ''))
    return files, mfiles, groups, investigations


"""
Create a new history when uploading data to Galaxy.
"""
def create_new_hist(gi, api, server, workflowid, files, new_hist):
    if workflowid != "0":
        if len(filter(None, files)) > 0:
            workflow = gi.workflows.show_workflow(workflowid)
            if new_hist is None or new_hist == "":
                new_hist_name = strftime(workflow['name'] + "_%d_%b_%Y_%H:%M:%S", gmtime())
            else:
                new_hist_name = new_hist
            gi.histories.create_history(name=new_hist_name)
            history_id = get_history_id(api, server)
        else:
            pass
    else:
        if len(filter(None, files)) > 0:
            if new_hist is None or new_hist == "":
                new_hist_name = strftime("Use_Galaxy_%d_%b_%Y_%H:%M:%S", gmtime())
            else:
                new_hist_name = new_hist
            gi.histories.create_history(name=new_hist_name)
            history_id = get_history_id(api, server)
        else:
            pass
    return history_id


"""
Create new data files based on the selected samples or send entire file
"""
def make_data_files(gi, files, username, password, control, test, history_id, filetype, dbkey):
    for file in files:
        nfile = str(file).split('/')
        filename = nfile[len(nfile)-1]
        cont = commands.getoutput("curl -u " + username + ":" + password + " -k -s " + file)
        with open(username + "/input_all_" + filename, "w") as dfile:
            dfile.write(cont)
        with open(username + "/input_all_" + filename, "r") as tfile:
            """
            Trim file based on selected samples.
            """
            matrix = False
            noheader = False
            samples_a = []
            samples_b = []
            linenr = 0
            if control != "[]" or test != "[]":
                with open(username + "/input_A_" + filename, "w") as ndfilea:
                    with open(username + "/input_B_" + filename, "w") as ndfileb:
                        for line in tfile:
                            if linenr == 0:
                                samples_a.append(0)
                                samples_b.append(0)
                                if "!" not in line:
                                    noheader = True
                            if not noheader:
                                if "!Sample_geo_accession" in line:
                                    line = line.split('\t')
                                    for x in range(0, len(line)):
                                        if line[x].replace('\n', '') in control:
                                            samples_a.append(x)
                                        if line[x].replace('\n', '') in test:
                                            samples_b.append(x)
                                else:
                                    if "!series_matrix_table_begin" in line:
                                        matrix = True
                                        samples_a.append(0)
                                    if matrix:
                                        line = line.split('\t')
                                        for p in (p for p,x in enumerate(line) if p in samples_a):
                                            if "!series_matrix_table_begin" not in line[p] and "!series_matrix_table_end" not in line[p]:
                                                ndfilea.write(line[p].replace('\"', '').replace('\n', '') + '\t')
                                        for pb in (pb for pb,x in enumerate(line) if pb in samples_b):
                                            if "!series_matrix_table_begin" not in line[pb] and "!series_matrix_table_end" not in line[pb]:
                                                ndfilea.write(line[pb].replace('\"', '').replace('\n', '') + '\t')
                                        ndfilea.write('\n')
                                    else:
                                        line.strip()
                            else:
                                line = line.split('\t')
                                if linenr == 0:
                                    column = 0
                                    control = control.split(',')
                                    test = test.split(',')
                                    for l in line:
                                        for c in control:
                                            if str(c.replace('[', '').replace(']', '').replace('"', '')) == l.replace('\n', ''):
                                                samples_a.append(column)
                                        for t in test:
                                            if str(t.replace('[', '').replace(']', '').replace('"', '')) == l.replace('\n', ''):
                                                samples_b.append(column)
                                        column += 1
                                column = 0
                                for l in line:
                                    if column in samples_a:
                                        ndfilea.write(line[column].replace('\"', '').replace('\n', '') + '\t')
                                    if column in samples_b:
                                        ndfileb.write(line[column].replace('\"', '').replace('\n', '') + '\t')
                                    column += 1
                                ndfilea.write('\n')
                                ndfileb.write('\n')
                            linenr += 1
                if len(samples_a) > 1:
                    gi.tools.upload_file(ndfilea.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file, label='control')
                if len(samples_b) > 1:
                    gi.tools.upload_file(ndfileb.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file, label='test')
                ndfilea.close()
                ndfileb.close()
                commands.getoutput("rm " + ndfilea.name)
                commands.getoutput("rm " + ndfileb.name)
            else:
                gi.tools.upload_file(dfile.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file)
        dfile.close()
        commands.getoutput("rm " + dfile.name)
        commands.getoutput("rm " + tfile.name)


"""
Create new metadata files based on the selected samples or send entire file
"""
def make_meta_files(gi, mfiles, username, password, control, test, history_id):
    control = control.split(',')
    test = test.split(',')
    for meta in mfiles:
        mfile = str(meta).split('/')
        mfilename = mfile[len(mfile)-1]
        if meta == "No metadata":
            pass
        else:
            mcont = commands.getoutput("curl -u " + username + ":" + password + " -k -s " + meta)
            with open(username + "/input_" + mfilename, "w") as metfile:
                metfile.write(mcont)
            metfile.close()
            linenr = 0
            with open(username + "/input_" + mfilename, "r") as metadatafile:
                if control[0] != "[]" or test[0] != "[]":
                    with open(username + "/input_classmeta.txt", "w") as nmeta:
                        for l in metadatafile:
                            columns = l.split('\t')
                            if len(columns) > 0:
                                if linenr > 0:
                                    if len(columns) > 0:
                                        for c in control:
                                            if str(c.replace('[', '').replace(']', '').replace('"', '')) == columns[0].replace('[', '').replace(']', '').replace('"', '').replace('\n', ''):
                                                l = l.replace('\n', '').replace('\r', '')
                                                nmeta.write(l + "\tA")
                                                nmeta.write("\n")
                                        for t in test:
                                            if str(t.replace('[', '').replace(']', '').replace('"', '')) == columns[0].replace('[', '').replace(']', '').replace('"', '').replace('\n', ''):
                                                l = l.replace('\n', '').replace('\r', '')
                                                nmeta.write(l + "\tB")
                                                nmeta.write("\n")
                                else:
                                    l = l.replace('\n', '').replace('\r', '')
                                    nmeta.write(l + "\tclass_id" + "\n")
                            linenr += 1
                    gi.tools.upload_file(nmeta.name, history_id, file_type='auto', dbkey='?', prefix=file)
                    commands.getoutput("rm " + nmeta.name)
                    commands.getoutput("rm " + metadatafile.name)
                else:
                    gi.tools.upload_file(metadatafile.name, history_id, file_type='auto', dbkey='?', prefix=file)
                    commands.getoutput("rm " + metadatafile.name)


"""
Upload selected files to a new Galaxy history.
"""
@csrf_exempt
def upload(request):
    gi = GalaxyInstance(url=request.session.get('server'), key=request.session.get('api'))
    selected = request.POST.get('selected')
    selectedmeta = request.POST.get('meta')
    filetype = request.POST.get('filetype')
    dbkey = request.POST.get('dbkey')
    workflowid = request.POST.get('workflowid')
    pid = request.POST.get('data_id')
    onlydata = request.POST.get('onlydata')
    makecol = request.POST.get('col')
    data_ids = []
    control = request.POST.get('samples')
    test = request.POST.get('samplesb')
    new_hist = request.POST.get('historyname')
    group = request.POST.get('group')
    investigation = request.POST.get('investigation')
    date = strftime("%d_%b_%Y_%H:%M:%S", gmtime())
    select = selected.split(',')
    mselect = selectedmeta.split(',')
    gselect = group.split(',')
    iselect = investigation.split(',')
    files = get_selection(iselect, gselect, select, mselect)[0]
    mfiles = get_selection(iselect, gselect, select, mselect)[1]
    groups = get_selection(iselect, gselect, select, mselect)[2]
    investigations = get_selection(iselect, gselect, select, mselect)[3]
    history_id = create_new_hist(gi, request.session.get('api'), request.session.get('server'),
                                 workflowid, files, new_hist)
    inputs = {}
    if len(filter(None, files)) <= 0:
        return HttpResponseRedirect("/")
    else:
        if onlydata == "true":
            make_data_files(gi, files, request.session.get('username'), request.session.get('password'),
                            control, test, history_id, filetype, dbkey)
        else:
            make_data_files(gi, files, request.session.get('username'), request.session.get('password'),
                            control, test, history_id, filetype, dbkey)
            make_meta_files(gi, mfiles, request.session.get('username'), request.session.get('password'),
                            control, test, history_id)
        if workflowid != "0":
            in_count = 0
            resultid = uuid.uuid1()
            datamap = dict()
            mydict = {}
            jsonwf = gi.workflows.export_workflow_json(workflowid)
            for i in range(len(jsonwf["steps"])):
                if jsonwf["steps"][str(i)]["name"] == "Input dataset":
                    try:
                        label = jsonwf["steps"][str(i)]["inputs"][0]["name"]
                    except IndexError:
                        label = jsonwf["steps"][str(i)]["label"]
                    mydict["in%s" % (str(i + 1))] = gi.workflows.get_workflow_inputs(workflowid, label=label)[0]
            for k, v in mydict.items():
                datamap[v] = {'src': "hda", 'id': get_input_data(request.session.get('api'),
                                                                 request.session.get('server'))[0][in_count]}
                data_ids.append(get_input_data(request.session.get('api'), request.session.get('server'))[0][in_count])
                in_count += 1
            if makecol == "true":
                gi.histories.create_dataset_collection(history_id, make_collection(data_ids))
            gi.workflows.invoke_workflow(workflowid, datamap, history_id=history_id)
            gi.workflows.export_workflow_to_local_path(workflowid, request.session.get('username'), True)
            datafiles = get_output(request.session.get('api'), request.session.get('server'))
            store_results(1, datafiles, request.session.get('server'), request.session.get('username'),
                          request.session.get('password'), request.session.get('storage'),
                          groups, resultid, investigations, date)
            store_results(3, datafiles, request.session.get('server'), request.session.get('username'),
                          request.session.get('password'), request.session.get('storage'),
                          groups, resultid, investigations, date)
            ga_store_results(request.session.get('username'), request.session.get('password'), workflowid,
                             request.session.get('storage'), resultid, groups, investigations)
            commands.getoutput("rm " + request.session.get('username') + "/input_test")
            return render_to_response('results.html', context={'workflowid': workflowid, 'inputs': inputs, 'pid': pid,
                                                               'server': request.session.get('server')})
        else:
            if makecol == "true":
                history_data = gi.histories.show_history(history_id, contents=True)
                for c in range(0, len(history_data)):
                    data_ids.append(history_data[c]['id'])
                gi.histories.create_dataset_collection(history_id, make_collection(data_ids))
            ug_store_results(
                request.session.get('api'), request.session.get('server'), workflowid, request.session.get('username'),
                request.session.get('password'), request.session.get('storage'), groups, investigations, date)
            return HttpResponseRedirect("/")


"""
Make a collection based on the uploaded data files.
"""
def make_collection(data_ids):
    idlist = []
    count = 0
    for c in range(0, len(data_ids)):
        data_id = data_ids[c]
        idlist.append({'src': "hda", 'id': data_id, 'name': str(count)})
        count += 1
    collection = {'collection_type': 'list', 'element_identifiers': idlist, 'name': 'collection'}
    return collection


"""
Store input and output files created or used in a workflow.
"""
def store_results(column, datafiles, server, username, password, storage, groups, resultid, investigations, date):
    o = 0
    for name in datafiles[column]:
        cont = commands.getoutput("curl -s -k " + server + datafiles[column-1][o])
        old_name = strftime("%d_%b_%Y_%H:%M:%S", gmtime()) + "_" + name.replace('/', '_').replace(' ', '_')
        with open(username + "/" + old_name, "w") as outputfile:
            outputfile.write(cont)
        new_name = sha1sum(username + "/" + old_name) + "_" + old_name
        os.rename(username + "/" + old_name, username + "/" + new_name)
        """
        tar archiving the output.
        """
        for i in investigations:
            for g in groups:
                commands.getoutput(
                    "curl -s -k -u " + username + ":" + password + " -X MKCOL " +
                    storage + "/" + i.replace('"', '') + "/" + g.replace('"', '') + "/results_" + str(resultid))
                commands.getoutput(
                    "curl -s -k -u " + username + ":" + password + " -T " + '\'' + username + "/" + new_name + '\'' + " " + storage +
                    "/" + i.replace('"', '') + "/" + g.replace('"', '') + "/results_" + str(resultid) + "/" + new_name)
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#pid> \"" + storage + "/" + i.replace('"', '') + "/" + g.replace('"', '') +
                    "/results_" + str(resultid) + "/" + new_name + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#results_id> \"" + str(resultid) + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#group_id> \"" + g.replace('"', '') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#investigation_id> \"" + i.replace('"', '') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(
                        resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#date> \"" + date + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
        commands.getoutput("rm " + username + "/" + new_name)
        commands.getoutput("rm " + username + "/" + old_name)
        o += 1


"""
Store information about the Galaxy workflow file
"""
def ga_store_results(username, password, workflowid, storage, resultid, groups, investigations):
    for filename in os.listdir(username + "/"):
        if ".ga" in filename:
            new_name = sha1sum(username + "/" + filename) + "_" + filename
            os.rename(username + "/" + filename, username + "/" + new_name)
            for i in investigations:
                for g in groups:
                    commands.getoutput("curl -s -k -u " + username + ":" + password + " -T " + username + "/" + new_name + " " +
                                       storage + "/" + i.replace('"', '') + "/" + g.replace('"', '') + "/results_" +
                                       str(resultid) + "/" + new_name)
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#workflow> \"" + username + "/" + new_name + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#workflowid> \"" + workflowid + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
            commands.getoutput("rm " + username + "/" + new_name)


"""
Store results in triple store that have been created withoud using a workflow.
"""
def ug_store_results(api, server, workflowid, username, password, storage, groups, investigations, date):
    resultid = uuid.uuid1()
    outputs = get_output(api, server)
    n = 0
    for iname in outputs[1]:
        cont = commands.getoutput("curl -s -k " + server + outputs[0][n])
        old_name = strftime("%d_%b_%Y_%H:%M:%S", gmtime()) + "_" + iname
        with open(username + "/" + old_name, "w") as inputfile:
            inputfile.write(cont)
        new_name = sha1sum(username + "/" + old_name) + "_" + old_name
        os.rename(username + "/" + old_name, username + "/" + new_name)
        time.sleep(5)
        for i in investigations:
            for g in groups:
                commands.getoutput("curl -s -k -u " + username + ":" + password + " -X MKCOL " + storage + "/" +
                                   i.replace('"', '') + "/" + g.replace('"', '') + "/results_" + str(resultid))
                commands.getoutput("curl -s -k -u " + username + ":" + password + " -T " + username + "/" + new_name + " " + storage +
                                   "/" + i.replace('"', '') + "/" + g.replace('"', '') + "/results_" + str(resultid) +
                                   "/" + new_name + " ")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#pid> \"" + storage + "/" + i.replace('"', '') + "/" + g.replace('"', '') +
                    "/results_" + str(resultid) + "/" + new_name + " \" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#results_id> \"" + str(resultid) + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#group_id> \"" + g.replace('"', '') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#workflow> \"No Workflow used\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#workflowid> \"" + workflowid + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#investigation_id> \"" + i.replace('"', '') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput(
                    "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                    username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(
                        resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                    username.replace('@', '') + "#date> \"" + date + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
        commands.getoutput("rm " + username + "/" + new_name)
        commands.getoutput("rm " + username + "/" + old_name)
        n += 1


"""
Get the sha1 from a file to give it an id based on the file contents.
"""
def sha1sum(filename, blocksize=65536):
    hash = hashlib.sha1()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()


"""
Show results that are stored in Owncloud.
This is based on the search results in myFAIR.
"""
@csrf_exempt
def show_results(request):
    username = request.session.get('username')
    password = request.session.get('password')
    storage = request.session.get('storage')
    groups = []
    results = []
    inputs = []
    out = []
    result = ""
    workflow = []
    wf = False
    if request.method == 'POST':
        request.session['stored_results'] = request.POST
        return render_to_response('results.html', context={'outputs': out})
    else:
        if username is not None:
            old_post = request.session.get('stored_results')
            investigations = old_post['investigations']
            group = old_post['group']
            group = group.split(',')
            resultid = old_post['resultid']
            resultid = resultid.split(',')
            for g in group:
                groups.append(g.replace('[', '').replace('"', '').replace(']', ''))
            for r in resultid:
                results.append(r.replace('[', '').replace('"', '').replace(']', ''))
            for invest in investigations.split(','):
                investigation = invest.replace('[', '').replace('"', '').replace(']', '')
                for group in groups:
                    if investigation != "-":
                        oc_folders = commands.getoutput(
                            "curl -s -X PROPFIND -u " + username + ":" + password +
                            " '" + storage + '/' + investigation + '/' + group +
                            "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                    else:
                        oc_folders = commands.getoutput(
                            "curl -s -X PROPFIND -u " + username + ":" + password +
                            " '" + storage + '/' + group + "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                    oc_folders = filter(None, oc_folders)
                    for folder in oc_folders:
                        if "results_" in folder:
                            if investigation != "-":
                                result = commands.getoutput(
                                    "curl -s -X PROPFIND -u " + username + ":" + password +
                                    " '" + storage + '/' + investigation + '/' + group + '/' + 'results_' + results[0] +
                                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
                            else:
                                result = commands.getoutput(
                                    "curl -s -X PROPFIND -u " + username + ":" + password +
                                    " '" + storage + '/' + group + '/' + 'results_' + results[0] +
                                    "' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
            for r in result:
                if ".ga" in r:
                    wf = True
                    nres = r.split('/')
                    cont = commands.getoutput(
                        "curl -s -k -u " + username + ":" + password + " " + storage + "/" + nres[len(nres)-4] + "/" +
                        nres[len(nres)-3] + "/" + nres[len(nres)-2] + "/" + nres[len(nres)-1])
                    with open(username + "/" + nres[len(nres)-1], "w") as ga:
                        ga.write(cont)
                    workflow = read_workflow(ga.name)
                    workflowid = commands.getoutput(
                        "curl -s -k http://127.0.0.1:3030/ds/query -X POST --data 'query=SELECT DISTINCT ?workflowid FROM <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { VALUES (?workflow) {(\"" + ga.name + "\")}{ ?s <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#workflowid> ?workflowid . ?s <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#workflow> ?workflow . } } ORDER BY (?workflowid)' -H 'Accept: application/sparql-results+json,*/*;q=0.9'")
                    wid = json.dumps(workflowid)
                    wfid = json.loads(workflowid)
                    wid = json.dumps(wfid["results"]["bindings"][0]["workflowid"]["value"])
                if not wf:
                    wid = "0"
                if "input_" in r:
                    nres = r.split('/')
                    inputs.append(nres[len(nres)-1])
                else:
                    nres = r.split('/')
                    out.append(nres[len(nres)-1])
                if investigation == "-":
                    resid = nres[len(nres)-3] + "/" + nres[len(nres)-2]
                else:
                    resid = nres[len(nres)-4] + "/" + nres[len(nres)-3] + "/" + nres[len(nres)-2]
                out = filter(None, out)
                inputs = filter(None, inputs)
            return render(request, 'results.html', context={'inputs': inputs, 'outputs': out, 'workflow': workflow,
                            'storage': storage, 'resultid': resid, 'workflowid': wid})
        else:
            return HttpResponseRedirect('/')


"""
Remove session to log out.
"""
def logout(request):
    if request.session.get('username') is not None:
        commands.getoutput("rm -r " + request.session.get('username'))
        request.session.flush()
    return HttpResponseRedirect("/")


"""
Get all inputs and outputs from a Galaxy workflow.
This information will be used to store the files in Owncloud.
"""
def get_output(api, server):
    if api is None:
        return HttpResponseRedirect("/")
    else:
        gi = GalaxyInstance(url=server, key=api)
        historyid = get_history_id(api, server)
        inputs = []
        input_ids = []
        outputs = []
        time.sleep(30)
        hist = gi.histories.show_history(historyid)
        state = hist['state_ids']
        dump = json.dumps(state)
        status = json.loads(dump)
        # Stop process after workflow is done
        while status['running'] or status['queued'] or status['new'] or status['upload']:
            time.sleep(20)
            hist = gi.histories.show_history(historyid)
            state = hist['state_ids']
            dump = json.dumps(state)
            status = json.loads(dump)
            if not status['running'] and not status['queued'] and not status['new'] and not status['upload']:
                break
        files = status['ok']
        for o in files:
            oug = gi.datasets.show_dataset(o, deleted=False, hda_ldda='hda')
            if "input_" in oug['name']:
                inputs.append(oug['id'])
            else:
                outputs.append(oug)
        for i in inputs:
            iug = gi.datasets.show_dataset(i, deleted=False, hda_ldda='hda')
            input_ids.append(iug)
        in_url = []
        in_name = []
        out_url = []
        out_name = []
        for input_id in input_ids:
            in_name.append(input_id["name"])
            in_url.append(input_id["download_url"])
        for out in outputs:
            if out['visible']:
                out_name.append(out["name"])
                out_url.append(out["download_url"])
        return in_url, in_name, out_url, out_name


"""
Store results from Galaxy history to Owncloud/B2DROP.
Create new triples.
"""
@csrf_exempt
def store_history(request):
    if request.session.get('api') is None:
        return HttpResponseRedirect("/")
    else:
        server = request.POST.get('server')
        api = request.POST.get('api')
        gi = GalaxyInstance(url=server, key=api)
        username = request.POST.get('username')
        password = request.POST.get('password')
        storage = request.POST.get('storage')
        groups = request.POST.get('folder')
        investigation = request.POST.get('inv')
        date = strftime("%d_%b_%Y_%H:%M:%S", gmtime())
        url = []
        names = []
        resultid = uuid.uuid1()
        if request.method == 'POST':
            historyid = request.POST.get('history')
            inputs = []
            input_ids = []
            output = []
            hist = gi.histories.show_history(historyid)
            state = hist['state_ids']
            dump = json.dumps(state)
            status = json.loads(dump)
            files = status['ok']
            for o in files:
                oug = gi.datasets.show_dataset(o, deleted=False, hda_ldda='hda')
                if "input_" in oug['name']:
                    if oug['visible']:
                        url.append(server + oug['download_url'])
                        names.append(oug['name'])
                    inputs.append(oug['id'])
                else:
                    if oug['visible']:
                        url.append(server + oug['download_url'])
                        names.append(oug['name'])
                    output.append(oug)
            for i in inputs:
                iug = gi.datasets.show_dataset(i, deleted=False, hda_ldda='hda')
                input_ids.append(iug)
            count = 0
            for u in url:
                cont = commands.getoutput("curl -s -k " + u)
                old_name = strftime("%d_%b_%Y_%H:%M:%S", gmtime()) + "_" + names[count].replace('/', '_').replace(' ', '_')
                with open(username + "/" + old_name, "w") as newfile:
                    newfile.write(cont)
                new_name = sha1sum(newfile.name) + "_" + old_name
                os.rename(username + "/" + old_name, username + "/" + new_name)
                count += 1
                for g in groups.split(','):
                    commands.getoutput("curl -s -k -u " + username + ":" + password + " -X MKCOL " + storage + "/" +
                                       investigation + "/" + g.replace('"', '') + "/results_" + str(resultid))
                    commands.getoutput("curl -s -k -u " + username + ":" + password + " -T " + '\'' + username + "/" + new_name + '\'' +
                                       " " + storage + "/" + investigation + "/" + g.replace('"', '') + "/results_" +
                                       str(resultid) + "/" + new_name)
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#pid> \"" + storage + "/" + g.replace('"', '') + "/results_" + str(resultid) + "/" + new_name +
                        "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#results_id> \"" + str(resultid) + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#group_id> \"" + g.replace('"', '') + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#investigation_id> \"" + investigation + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#workflow> \"" + hist['name'] + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#workflowid> \"" + "0" + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/" +
                        username.replace('@', '') + "> { <http://127.0.0.1:3030/" + str(resultid) + "> <http://127.0.0.1:3030/ds/data?graph=" +
                        username.replace('@', '') + "#date> \"" + date + "\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                commands.getoutput("rm " + username + "/" + new_name)
            ug_context = {'outputs': output, 'inputs': input_ids, 'hist': hist, 'server': server}
            return render(request, 'history.html', ug_context)


"""
Read the Galaxy workflow file and return the analysis steps.
"""
def read_workflow(filename):
    json_data = open(filename).read()
    data = json.loads(json_data)
    steps = data["steps"]
    steplist = []
    count = 0
    for s in steps:
        steplist.append(steps[str(count)])
        count += 1
    commands.getoutput("rm " + filename)
    return steplist


"""
Rerun a previous analysis based on your search results.
"""
@csrf_exempt
def rerun_analysis(request):
    workflowid = request.POST.get('workflowid')
    workflowid = workflowid.replace('"', '')
    resultid = request.POST.get('resultid')
    gi = GalaxyInstance(url=request.session.get('server'), key=request.session.get('api'))
    urls = request.POST.get('urls')
    urls = urls.split(',')
    gi.histories.create_history(name=resultid)
    history_id = get_history_id(request.session.get('api'), request.session.get('server'))
    for u in urls:
        filename = u.replace("[", "").replace("]", "").replace(" ", "").replace('"', '')
        cont = commands.getoutput(
            "curl -s -u " + request.session.get('username') + ":" + request.session.get('password') + " " +
            request.session.get('storage') + "/" + filename)
        file = filename.split('/')
        with open(request.session.get('username') + "/" + file[len(file)-1], "w") as infile:
            infile.write(cont)
        gi.tools.upload_file(infile.name, history_id, file_type="auto", dbkey="?", prefix=file)
        commands.getoutput("rm " + infile.name)
    oc_folders = commands.getoutput(
        "curl -s -X PROPFIND -u " + request.session.get('username') + ":" + request.session.get('password') + " '" + request.session.get('storage') +
        "/" + resultid +"' | grep -oPm250 '(?<=<d:href>)[^<]+'").split("\n")
    for f in oc_folders:
        if ".ga" in f:
            if "/owncloud/" in request.session.get('storage'):
                ga = f.replace('/owncloud/remote.php/webdav/', '')
            else:
                ga = f.replace('/remote.php/webdav/', '')
            gacont = commands.getoutput(
                "curl -s -u " + request.session.get('username') + ":" + request.session.get('password') + " " +
                request.session.get('storage') + "/" + ga)
            ga = ga.split('/')
            with open(request.session.get('username') + "/" + ga[len(ga)-1], "w") as gafile:
                gafile.write(gacont)
    time.sleep(30)
    if workflowid != "0":
        gi.workflows.import_workflow_from_local_path(gafile.name)
        workflows = gi.workflows.get_workflows()
        in_count = 0
        datamap = dict()
        mydict = {}
        for workflow in workflows:
            if "API" in workflow["name"]:
                newworkflowid = workflow["id"]
        jsonwf = gi.workflows.export_workflow_json(newworkflowid)
        for i in range(len(jsonwf["steps"])):
            if jsonwf["steps"][str(i)]["name"] == "Input dataset":
                try:
                    label = jsonwf["steps"][str(i)]["inputs"][0]["name"]
                except IndexError:
                    label = jsonwf["steps"][str(i)]["label"]
                mydict["in%s" % (str(i+1))] = gi.workflows.get_workflow_inputs(newworkflowid, label=label)[0]
        for k, v in mydict.items():
            datamap[v] = {'src': "hda", 'id': get_input_data(request.session.get('api'), request.session.get('server'))[0][in_count]}
            in_count += 1
        gi.workflows.invoke_workflow(newworkflowid, datamap, history_id=history_id)
        gi.workflows.delete_workflow(newworkflowid)
        commands.getoutput("rm " + gafile.name)
    return HttpResponseRedirect("/")


"""
Find ontology iri based on tagged data when indexing.
"""
@csrf_exempt
def onto(disgenet, edam):
    disgenet = disgenet.replace(' ', '+').replace("'", "%27")
    edam = edam.replace(' ', '+').replace("'", "%27")
    disid = commands.getoutput(
        "curl -s -k http://127.0.0.1:3030/ds/query -X POST --data " +
        "'query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0A" +
        "PREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0A" +
        "PREFIX+ncit%3A+%3Chttp%3A%2F%2Fncicb.nci.nih.gov%2Fxml%2Fowl%2FEVS%2FThesaurus.owl%23%3E%0A" +
        "SELECT+DISTINCT+%0A%09%3Fdisease+%0AFROM+%3Chttp%3A%2F%2Frdf.disgenet.org%3E+%0AWHERE+%7B%0A++" +
        "SERVICE+%3Chttp%3A%2F%2Frdf.disgenet.org%2Fsparql%2F%3E+%7B%0A++++" +
        "%3Fdisease+rdf%3Atype+ncit%3AC7057+%3B%0A++++%09dcterms%3Atitle+%22" + disgenet +
        "%22%40en+.%0A%7D%0A%7D' -H 'Accept: application/sparql-results+json,*/*;q=0.9'")
    edam_id = commands.getoutput(
        "curl -s 'http://www.ebi.ac.uk/ols/api/search?q=" + edam + "&ontology=edam' 'Accept: application/json'")
    try:
        jdisease = json.loads(disid)
        umllist = []
        umls = jdisease['results']['bindings'][0]['disease']['value']
    except (IndexError, ValueError):
        umls = "No disgenet record"
    try:
        jedam = json.loads(edam_id)
        eid = jedam['response']['docs'][0]['iri']
    except (IndexError, ValueError):
        eid = "No EDAM record"
    return umls, eid