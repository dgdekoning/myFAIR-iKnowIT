import commands
import json
import csv
import re

from time import strftime, gmtime
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.client import ConnectionError
from django.shortcuts import render_to_response, render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
    if request.method == 'POST':
        err = []
        server = request.POST.get('server')
        api = request.POST.get('api')
        storage = request.POST.get('storage')
        b2user = request.POST.get('username')
        b2pass = request.POST.get('password')
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
        if b2user != "" and b2pass != "":
            request.session['username'] = b2user
            request.session['password'] = b2pass
        else:
            err.append("No valid username or password")
            request.session.flush()
            return render_to_response('login.html', context={'error': err})
        request.session.set_expiry(0)
        return render_to_response('home.html', context={'error': err})
    return render(request, 'login.html')


@csrf_exempt
def index(request):
    try:
        login(request)
        if 'api' not in request.session or 'username' not in request.session or 'password' not in request.session:
            err = "Credentials are invalid. Please enter the correct values."
            login(request)
            return render_to_response('login.html', context={'error': err})
        else:
            api = request.session.get('api')
            b2user = request.session.get('username')
            b2pass = request.session.get('password')
            server = request.session.get('server')
            storage = request.session.get('storage')
            token = "ygcLQAJkWH2qSfawc39DI9tGxisceVSTgw9h2Diuh0z03QRx9Lgl91gneTok"
            b2folders = commands.getoutput(
                "curl -s -X PROPFIND -u " + b2user + ":" + b2pass +
                " '"+ storage +"' | grep -oPm100 '(?<=<d:href>)[^<]+'").split("\n")
            b2folders = filter(None, b2folders)
            # createMetadata(request)
            if not b2folders:
                request.session.flush()
                return HttpResponseRedirect('/')
        #     newturtle = open('new.ttl', 'w')
        #     if storage == "https://bioinf-galaxian.erasmusmc.nl/owncloud/remote.php/webdav":
        #         turtlefile = "/owncloud/remote.php/webdav/new.ttl"
        #     else:
        #         turtlefile = "/remote.php/webdav/new.ttl"
        #     if turtlefile in b2folders:
        #         oldturtle = commands.getoutput(
        #             "curl -s -u " + b2user + ":" + b2pass + " " + storage + "/new.ttl")
        #         for line in oldturtle:
        #             newturtle.write(line)
        #         newturtle.write("\n")
        #         newturtle.close()
        #         commands.getoutput("csv2rdf -b http://127.0.0.1:3030/ -p '#' -d ',' -i 1 new.csv >> new.ttl")
        #         commands.getoutput(
        #             "curl -X PUT -H Content-type:text/turtle -T new.ttl -G http://127.0.0.1:3030/ds/data "
        #         "--data-urlencode graph="+b2user.replace('@', ''))
        #         newturtle.close()
        #     else:
        #         commands.getoutput(
        #             "curl -X PUT -H Content-type:text/turtle -T new.ttl -G http://127.0.0.1:3030/ds/data "
        #         "--data-urlencode graph="+b2user.replace('@', ''))
        #         newturtle.write("")
        #         newturtle.close()
	    # commands.getoutput("rm new.ttl")
            gi = GalaxyInstance(url=server, key=api)
            user = gi.users.get_current_user()
            username = user['username']
            workflows = gi.workflows.get_workflows
            history = gi.histories.get_histories()
            hist = json.dumps(history)
            his = json.loads(hist)
            newhistid = his[0]['id']
            newhist = gi.histories.show_history(newhistid)
            okay = False
            if newhist['state'] == "ok":
                okay = True
            return render(request, 'home.html',
                                      context={'workflows': workflows, 'histories': his, 'user': username, 'api': api,
                                               'b2user': b2user, 'b2pass': b2pass, 'server': server, 'storage': storage})
    except ConnectionError as err:
        err = "Invalid API Key"
        request.session.flush()
        return render_to_response('login.html', context={'error': err})


@csrf_exempt
def samples(request):
    samples = request.POST.get('samples')
    if samples is not None or samples != "[]":
        sample = samples.split(',')
        sampleselect = []
        for sam in sample:
            sampleselect.append(sam.replace('[', '').replace('"', '').replace(']', ''))
        return render(request, 'home.html', context={'samples': sampleselect})
    return render(request, 'home.html', context={'samples': sampleselect})


@csrf_exempt
def modify(request):
    dgroup = request.POST.get('delete')
    commands.getoutput(
        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=WITH <http://127.0.0.1:3030/ds/data/" + request.session['username'].replace('@', '') +
        "> DELETE {?s ?p ?o} WHERE { ?s <http://127.0.0.1:3030/ds/data?graph=" + request.session['username'].replace('@', '') +
        "#group_id> ?group . FILTER(?group = \"" + dgroup + "\") ?s ?p ?o }'")
    return HttpResponseRedirect('/')


def delete(request):
    return render(request, 'modify.html')


@csrf_exempt
def eudat(request):
    if request.session.get('username') == "" or request.session.get('username') is None:
        return HttpResponseRedirect('/')
    else:
        b2user = request.session.get('username')
        b2pass = request.session.get('password')
        storage = request.session.get('storage')
        b2folders = commands.getoutput(
            "curl -s -X PROPFIND -u " + b2user + ":" + b2pass +
            " '" + storage + "' | grep -oPm100 '(?<=<d:href>)[^<]+'").split("\n")
        folders = []
        for b in b2folders:
            if storage == "https://bioinf-galaxian.erasmusmc.nl/owncloud/remote.php/webdav":
                new = b.replace('/owncloud/remote.php/webdav/', '').replace('/', '')
                folders.append(new)
            elif storage == "https://b2drop.eudat.eu/remote.php/webdav":
                new = b.replace('/remote.php/webdav/', '').replace('/', '')
                folders.append(new)
        folders = filter(None, folders)
        if request.POST.get('folder') != "" and request.POST.get('folder') is not None:
            group = request.POST.get('folder')
        else:
            group = request.POST.get('selected_folder')
        if group != "" and group is not None:
            b2files = commands.getoutput(
                "curl -s -X PROPFIND -u " + b2user + ":" + b2pass +
                " '"+ storage + "/" + group + "' | grep -oPm100 '(?<=<d:href>)[^<]+'").split("\n")
            files = []
            for f in b2files:
                if storage == "https://bioinf-galaxian.erasmusmc.nl/owncloud/remote.php/webdav":
                    new = f.replace('/owncloud/remote.php/webdav/'+group, '').replace('/', '')
                    files.append(new)
                else:
                    new = f.replace('/remote.php/webdav/'+group, '').replace('/', '')
                    files.append(new)
            files = filter(None, files)
            metadata = []
            datafiles = []
            for i in files:
                if request.POST.get(i) != "" and request.POST.get(i) is not None:
                    if request.POST.get(i) == "m":
                        metadata.append(storage + "/" + group + "/" + i)
                    else:
                        datafiles.append(storage + "/" + group + "/" + i)
            if metadata or datafiles:
                return render(request, 'turtle.html', context={'metadata': metadata, 'datafiles': datafiles, 'group': group})
            return render(request, 'eudat.html', context={'folders': folders, 'files': files, 'selected': group})
        return render(request, 'eudat.html', context={'folders': folders})


@csrf_exempt
def turtle(request):
    if request.method == 'POST':
        b2user = request.session.get('username')
        b2pass = request.session.get('password')
        storage = request.session.get('storage')
        group = request.POST.get('group')
        metadata = request.POST.get('metadata')
        datafile = request.POST.get('datafile')
        # token = "ygcLQAJkWH2qSfawc39DI9tGxisceVSTgw9h2Diuh0z03QRx9Lgl91gneTok"
        '''
########################################################################################################################
########################################################################################################################
        # Create deposition start
        #
        #
        #
        create_deposition = commands.getoutput(
            "curl -s -k -X POST https://trng-b2share.eudat.eu/api/depositions?access_token=" + token)
        deposition = json.loads(create_deposition)
        dep = deposition['deposit_id']
        #
        #
        #
        # Create deposition end

########################################################################################################################

        # Create new file to upload start
        #
        #
        #
        f = open('newfile.txt', 'w')
        f.write(datafile)
        f.close()
        commands.getoutput(
            " curl -s -k -X POST -F file=@newfile.txt https://trng-b2share.eudat.eu/api/deposition/"
            + dep + "/files?access_token=" + token)
        commands.getoutput("rm newfile.txt")
        #
        #
        #
        # Create new file to upload end

########################################################################################################################

        # Commit deposition start
        #
        #
        #
        commit_deposition = commands.getoutput(
            "curl -s -k -X POST -H \"Content-Type: application/json\" -d '{\"domain\":\"generic\", "
            "\"title\":\"" + datafile + "\", \"description\":\"Description\", \"open_access\":\"true\", \"creator\":\"EMC\"}' "
            "https://trng-b2share.eudat.eu/api/deposition/" + dep + "/commit?access_token=" + token)
        commit = json.loads(commit_deposition)
        record = commit['location']
        url = "https://trng-b2share.eudat.eu" + record
        #
        #
        #
        # Commit deposition end
        pids = commands.getoutput("curl -k -s " + url + "?access_token=" + token +
                                  " | python -mjson.tool | grep PID | awk '{print $2}'").rsplit("\n")
        for p in pids:
            pid = p.strip(',')
########################################################################################################################
########################################################################################################################
        '''
        if b2user == "" or b2user is None:
            login()
        else:
            pid = datafile
            line = ""
            if metadata is not None:
                metafile = commands.getoutput("curl -s -k -u " + b2user + ":" + b2pass + " " + metadata)
                metaf = open('metafile.csv', 'w')
                metaf.write(metafile)
                metaf.close()
                filemeta = "metafile.csv"
            else:
                createMetadata(request, datafile)
                # metaf = open('metafile.csv', 'w')
                # metaf.write('')
                # metaf.close()
                filemeta = "meta.txt"
            with open(filemeta, 'rb') as csvfile:
                count = 0
                reader = csv.DictReader(csvfile)
                cnt = 0
                if metadata is None:
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                        b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                        b2user.replace('@', '')+"#pid> \""+pid+"\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                        b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                        b2user.replace('@', '')+"#group_id> \""+group+"\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                        b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                        b2user.replace('@', '')+"#sample_id> \"None\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    commands.getoutput(
                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                        b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                        b2user.replace('@', '')+"#meta> \"No metadata\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                    cnt += 1
                else:
                    for row in reader:
                        commands.getoutput(
                            "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                            b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                            b2user.replace('@', '')+"#pid> \""+pid+"\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                        commands.getoutput(
                            "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                            b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                            b2user.replace('@', '')+"#group_id> \""+group+"\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                        commands.getoutput(
                            "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                            b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                            b2user.replace('@', '')+"#meta> \""+metadata+"\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                        for (k, v) in row.items():
                            for h in range(0, len(k.split('\t'))):
                                if k.split('\t')[h] != "":
                                    value = v.split('\t')[h]
                                    header = k.split('\t')[h]
                                    commands.getoutput(
                                        "curl http://127.0.0.1:3030/ds/update -X POST --data 'update=INSERT DATA { GRAPH <http://127.0.0.1:3030/ds/data/"+
                                        b2user.replace('@', '')+"> { <http://127.0.0.1:3030/"+group+str(cnt)+"> <http://127.0.0.1:3030/ds/data?graph="+
                                        b2user.replace('@', '')+"#"+header.replace('"', '')+"> \""+value.replace('"', '')+"\" } }' -H 'Accept: text/plain,*/*;q=0.9'")
                        count += 1
                        cnt += 1
            commands.getoutput("rm metafile.csv")
            # commands.getoutput("rm meta.txt")
        return HttpResponseRedirect('/')


def get_history_id(api, server):
    gi = GalaxyInstance(url=server, key=api)
    cur_hist = gi.histories.get_current_history()
    current = json.dumps(cur_hist)
    current_hist = json.loads(current)
    history_id = current_hist['id']
    return history_id


def get_input_data(api, server):
    gi = GalaxyInstance(url=server, key=api)
    history_id = get_history_id(api, server)
    hist_contents = gi.histories.show_history(history_id, contents=True)
    input1 = []
    input2 = []
    input3 = []
    input4 = []
    datacount = 0
    datasets = [dataset for dataset in hist_contents if not dataset['deleted']]
    for dataset in datasets:
        if dataset['hid'] == 1:
            datacount = 1
            input1.append(dataset['id'])
        elif dataset['hid'] == 2:
            datacount = 2
            input2.append(dataset['id'])
        elif dataset['hid'] == 3:
            datacount = 3
            input3.append(dataset['id'])
        elif dataset['hid'] == 4:
            datacount = 4
            input4.append(dataset['id'])
    return {'input1': input1, 'input2': input2, 'input3': input3, 'input4': input4, 'datacount': datacount}


def createMetadata(request, datafile):
    samples = []
    filename = datafile
    # filename = "https://bioinf-galaxian.erasmusmc.nl/owncloud/remote.php/webdav/transmart/GSE7621_series_matrix.txt"
    cont = commands.getoutput("curl -u " + request.session.get('username') + ":" + request.session.get('password') + " -k -s " + filename)
    with open("data.txt", "w") as datafile:
        datafile.write(cont)
    with open(datafile.name, "r") as tfile:
        for line in tfile:
            if "!Sample_geo_accession" in line:
                line = line.split('\t')
                for x in range(0, len(line)):
                    samples.append(line[x].replace('\n', ''))
        samples = filter(None, samples)
        tfile.seek(0)
        with open("meta.txt", "w") as meta:
            headers = []
            for i in range(0, len(samples)):
                for line in tfile:
                    if "!Sample" in line:
                        line = line.split('\t')
                        htitle = line[0].replace("!Sample_", "").replace("\n", "")
                        meta.write(htitle + '\t')
                tfile.seek(0)
        meta.close()
        with open("meta.txt", "w") as meta:
            for i in range(0, len(samples)):
                for line in tfile:
                    if "!Sample" in line:
                        line = line.split('\t')
                        line[i] = line[i].replace("!Sample_", "").replace("\n", "").replace("'", "").replace(",", "").replace("\"", "")
                        if line[i]  == "geo_accession":
                            line[i] = "sample_id"
                        elif line[1] == "\"female\"" or line[1] == "\"male\"":
                            line[0] = "sex"
                        meta.write(re.sub(r'[^\x00-\x7F]+', ' ', line[i]) + '\t')
                meta.write('\n')
                tfile.seek(0)
        meta.close()
    datafile.close()
    commands.getoutput("rm data.txt")
    return meta


@csrf_exempt
def upload(request):
    server = request.session.get('server')
    api = request.session.get('api')
    gi = GalaxyInstance(url=server, key=api)
    selected = request.POST.get('selected')
    selectedmeta = request.POST.get('meta')
    token = request.POST.get('token')
    filetype = request.POST.get('filetype')
    dbkey = request.POST.get('dbkey')
    username = request.session.get('username')
    password = request.session.get('password')
    workflowid = request.POST.get('workflowid')
    pid = request.POST.get('data_id')
    metaid = request.POST.get('meta_id')
    onlydata = request.POST.get('onlydata')
    gurl = request.POST.get('datasets')
    control = request.POST.get('samples')
    test = request.POST.get('samplesb')
    new_hist = request.POST.get('historyname')
    files = []
    mfiles = []
    select = selected.split(',')
    mselect = selectedmeta.split(',')
    groups = False
    for s in select:
        if s.replace('[', '').replace('"', '').replace(']', '') not in files:
            files.append(s.replace('[', '').replace('"', '').replace(']', ''))
    for m in mselect:
        if m.replace('[', '').replace('"', '').replace(']', '') not in mfiles:
            mfiles.append(m.replace('[', '').replace('"', '').replace(']', ''))
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
    """
    Variables for getting the input files.
    These are used in the for loops to get to the id's of the datasets
    """
    inputs = {}
    inputs2 = {}
    if len(filter(None, files)) <= 0:
        return HttpResponseRedirect("/")
    else:
        if onlydata == "true":
            for file in files:
                nfile = str(file).split('/')
                filename = nfile[len(nfile)-1]
                cont = commands.getoutput("curl -u " + username + ":" + password + " -k -s " + file)
                with open("input_all_" + filename, "w") as dfile:
                    dfile.write(cont)
                with open("input_all_" + filename, "r") as tfile:
                    """
                    Trim file based on selected samples.
                    """
                    matrix = False
                    samples_a = []
                    samples_b = []
                    if control != "[]" or test != "[]":
                        with open("input_" + filename, "w") as ndfile:
                            for line in tfile:
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
                                                ndfile.write(line[p].replace('\"', '').replace('\n', '') + '\t')
                                        for pb in (pb for pb,x in enumerate(line) if pb in samples_b):
                                            if "!series_matrix_table_begin" not in line[pb] and "!series_matrix_table_end" not in line[pb]:
                                                ndfile.write(line[pb].replace('\"', '').replace('\n', '') + '\t')
                                        ndfile.write('\n')
                                    else:
                                        line.strip()
                        if len(samples_a) > 1 or len(samples_b) > 1:
                            gi.tools.upload_file(ndfile.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file)
                        ndfile.close()
                        commands.getoutput("rm " + ndfile.name)
                    else:
                        gi.tools.upload_file(dfile.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file)
                dfile.close()
                commands.getoutput("rm " + dfile.name)
        else:
            for file in files:
                nfile = str(file).split('/')
                filename = nfile[len(nfile)-1]
                cont = commands.getoutput("curl -u " + username + ":" + password + " -k -s " + file)
                with open("input_all_" + filename, "w") as dfile:
                    dfile.write(cont)
                matrix = False
                samples_a = []
                samples_b = []
                samples = []
                with open("input_all_" + filename, "r") as tfile:
                    if control != "[]" or test != "[]":
                        with open("input_" + filename, "w") as ndfile:
                            for line in tfile:
                                if "!Sample_geo_accession" in line:
                                    line = line.split('\t')
                                    for x in range(0, len(line)):
                                        if line[x].replace('\n', '') in control:
                                            samples_a.append(x)
                                        if line[x].replace('\n', '') in test:
                                            samples_b.append(x)
                                        samples.append(line[x])
                                else:
                                    if "!series_matrix_table_begin" in line:
                                        matrix = True
                                        samples_a.append(0)
                                    if matrix:
                                        line = line.split('\t')
                                        for p in (p for p,x in enumerate(line) if p in samples_a):
                                            if "!series_matrix_table_begin" not in line[p] and "!series_matrix_table_end" not in line[p]:
                                                ndfile.write(line[p].replace('\"', '').replace('\n', '') + '\t')
                                        for pb in (pb for pb,x in enumerate(line) if pb in samples_b):
                                            if "!series_matrix_table_begin" not in line[pb] and "!series_matrix_table_end" not in line[pb]:
                                                ndfile.write(line[pb].replace('\"', '').replace('\n', '') + '\t')
                                        ndfile.write('\n')
                                    else:
                                        line.strip()
                        if len(samples_a) > 1 and ndfile.name != "input_meta.txt":
                            gi.tools.upload_file(ndfile.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file)
                        ndfile.close()
                        commands.getoutput("rm " + ndfile.name)
                        with open("meta.txt", "r") as metadatafile:
                            with open("input_classmeta.txt", "w") as nmeta:
                                groups = True
                                linenr = 0
                                for l in metadatafile:
                                    if linenr > 0:
                                        if linenr in samples_a:
                                            l = l.replace('\n', '')
                                            nmeta.write(l + "\tA")
                                            nmeta.write("\n")
                                        if linenr in samples_b:
                                            l = l.replace('\n', '')
                                            nmeta.write(l + "\tB")
                                            nmeta.write("\n")
                                    else:
                                        l = l.replace('\n', '')
                                        nmeta.write(l + "\tclass_id" + "\n")
                                    linenr += 1
                        commands.getoutput("tar -czvf datafiles.tar.gz " + nmeta.name + " " + dfile.name)
                        gi.tools.upload_file("datafiles.tar.gz", history_id, file_type='auto', dbkey='?', prefix=file)
                        gi.tools.upload_file(nmeta.name, history_id, file_type='auto', dbkey='?', prefix=file)
                    else:
                        gi.tools.upload_file(dfile.name, history_id, file_type=filetype, dbkey=dbkey, prefix=file)
                        dfile.close()
                        commands.getoutput("rm " + dfile.name)
            commands.getoutput("rm " + tfile.name)
            for mfile in mfiles:
                nfile = str(mfile).split('/')
                filename = nfile[len(nfile)-1]
                if mfile == "No metadata":
                    pass
                else:
                    cont = commands.getoutput("curl -u " + username + ":" + password + " -k -s " + mfile)
                    with open("input_" + filename, "w") as dfile:
                        dfile.write(cont)
                    if groups:
                        pass
                    else:
                        gi.tools.upload_file(dfile.name, history_id, file_type='auto', dbkey='?', prefix=mfile)
                        dfile.close()
                    # commands.getoutput("rm " + dfile.name)
        if workflowid != "0":
            datamap = dict()
            # Find a more generic label to use with the Galaxy workflow
            in1 = gi.workflows.get_workflow_inputs(workflowid, label='VCF')[0]
            if get_input_data(api, server)['datacount'] >= 2:
                in2 = gi.workflows.get_workflow_inputs(workflowid, label='PED')[0]
            elif get_input_data(api, server)['datacount'] >= 3:
                in3 = gi.workflows.get_workflow_inputs(workflowid, label='None')[0]
            for c in range(0, get_input_data(api, server)['datacount']):
                if c == 0:
                    datamap[in1] = {'src': "hda", 'id': get_input_data(api, server)['input1'][0]}
                elif c >= 1:
                    datamap[in2] = {'src': "hda", 'id': get_input_data(api, server)['input2'][0]}
                elif c >= 2:
                    datamap[in3] = {'src': "hda", 'id': get_input_data(api, server)['input3'][0]}
                elif c >= 3:
                    datamap[in4] = {'src': "hda", 'id': get_input_data(api, server)['input4'][0]}
            gi.workflows.invoke_workflow(workflowid, datamap, history_id=history_id)
            return render_to_response('output.html', context={'workflowid': workflowid, 'inputs': inputs, 'pid': pid, 'server': server})
        else:
            return HttpResponseRedirect("/")


@csrf_exempt
def output(request):
    if request.session.get('api') is None:
        return HttpResponseRedirect("/")
    else:
        server = request.session.get('server')
        api = request.POST.get('api')
        gi = GalaxyInstance(url=server, key=api)
        workflow = request.POST.get('workflowid')
        if request.method == 'POST':
            historyid = request.POST.get('history')
            pid = request.POST.get('pid')
            """
            Variables for getting the input files.
            These are used in the for loops to get to the id's of the datasets
            """
            inputs = []
            input_ids = []
            """
            Variables for getting the output files.
            These are used to get all the files with the OK status.
            In the HTML we will remove all the input files.
            """
            output = []
            hist = gi.histories.show_history(historyid)
            histories = hist['state_ids']
            dump = json.dumps(histories)
            ok = json.loads(dump)
            files = ok['ok']
            for o in files:
                oug = gi.datasets.show_dataset(o, deleted=False, hda_ldda='hda')
                if "input_" in oug['name']:
                    inputs.append(oug['id'])
                else:
                    output.append(oug)
            for i in inputs:
                iug = gi.datasets.show_dataset(i, deleted=False, hda_ldda='hda')
                input_ids.append(iug)
            print len(inputs)
            ug_context = {'outputs': output, 'inputs': input_ids, 'hist': hist, 'server': server}
            return render(request, 'output.html', ug_context)


def logout(request):
    request.session.flush()
    return HttpResponseRedirect("/")