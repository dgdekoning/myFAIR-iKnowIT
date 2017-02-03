/*
** Creating a Saprql endpoint and sparql queries to retrieve the metadata based on the selection
** made in the web interface.
*/
var SPARQL_ENDPOINT = 'http://localhost:3030/ds/query?query='
var USER = document.getElementById('user').innerHTML.replace('@', '');
var TEMPLATE_QUERIES = {
        1 : {
            text : 'Get all samples from all files',
            variables: ['all'],
            query : "SELECT DISTINCT ?pid ?meta ?group ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+">" +
                    "WHERE{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                    "}" + 
                    "ORDER BY (?sample)"
            },
        2 : {
            text : 'Get all available files',
            variables: ['all'],
            query : "SELECT DISTINCT ?pid ?meta ?group FROM <http://127.0.0.1:3030/ds/data/"+USER+">" +
                    "WHERE{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                    "}" +
                    "ORDER BY (?group)"
            },
		3 : {
            text : 'Get file(s) from sample',
            variables: ['sampleid'],
            query : "SELECT DISTINCT ?pid ?meta ?group ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?sample) {('#sampleid#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "}" +
                    "}" +
                    "ORDER BY (?sample)"
            },
        4 : {
            text : 'Get samples from group',
            variables: ['group'],
            query : "SELECT DISTINCT ?pid ?meta ?group ?sex ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?group) {('#group#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?sex ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "}" +
                    "}" +
                    "ORDER BY (?group)"
            },
        5 : {
            text : 'Get samples from sex',
            variables: ['sex'],
            query : "SELECT DISTINCT ?pid ?meta ?group ?sex ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?sex) {('#sex#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?sex ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "}" +
                    "}" +
                    "ORDER BY (?sex)"
        },
        6 : {
            text : 'Get samples from disease',
            variables: ['disease'],
            query : "SELECT DISTINCT ?pid ?meta ?group ?sex ?disease ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?disease) {('#disease#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?sex ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#characteristics_ch1> ?disease ." +
                        "}" +
                    "}" +
                    "ORDER BY (?disease)"
        },
        7 : {
            text : 'Get results from group',
            variables: ['group'],
            query : "SELECT DISTINCT (?s as ?id) ?resultid ?group ?workflow FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?group) {('#group#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#results_id> ?resultid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?group ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#workflow> ?workflow ." +
                        "}" +
                    "}" +
                    "ORDER BY (?results)"
        },
        };
var VARIABLE_QUERIES = {
        sampleid: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?sample <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?value }" +
                  "ORDER BY(?value)",
        group: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?value }" +
               "ORDER BY (?value)",
        sex: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?value }" +
            "ORDER BY (?value)",
        disease: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#characteristics_ch1> ?value }" +
                "ORDER BY (?value)",
}