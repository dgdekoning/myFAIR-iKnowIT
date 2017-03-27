/*
** Creating a Saprql endpoint and sparql queries to retrieve the metadata based on the selection
** made in the web interface.
*/
var SPARQL_ENDPOINT = 'http://localhost:3030/ds/query?query='
var USER = document.getElementById('user').innerHTML.replace('@', '');
var TEMPLATE_QUERIES = {
        1 : {
            text : 'Search for sample',
            variables: ['sampleid'],
            query : "SELECT DISTINCT ?pid ?meta ?investigation ?study ?sex ?disease_iri ?method_iri ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?sample) {('#sampleid#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#investigation_id> ?investigation ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?study ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?sex ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#disgenet_iri> ?disease_iri ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#edam_iri> ?method_iri ." +
                        "}" +
                    "}" +
                    "ORDER BY (?sample)"
            },
        2 : {
            text : 'Search for study',
            variables: ['study'],
            query : "SELECT DISTINCT ?pid ?meta ?investigation ?study ?sex ?disease_iri ?method_iri ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?study) {('#study#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#investigation_id> ?investigation ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?study ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?sex ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#disgenet_iri> ?disease_iri ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#edam_iri> ?method_iri ." +
                        "}" +
                    "}" +
                    "ORDER BY (?study)"
            },
        3 : {
            text : 'Search for disease',
            variables: ['disease'],
            query : "SELECT DISTINCT ?pid ?meta ?investigation ?study ?sex ?disease ?disease_iri ?method_iri ?sample FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?disease) {('#disease#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#pid> ?pid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#meta> ?meta ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#investigation_id> ?investigation ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?study ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sex> ?sex ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?sample ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#disease> ?disease ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#disgenet_iri> ?disease_iri ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#edam_iri> ?method_iri ." +
                        "}" +
                    "}" +
                    "ORDER BY (?disease)"
        },
        4 : {
            text : '-------------------------------------------------------------------------------------------------' +
                   '-------------------------------------------------------------------------------------------------' +
                   '-------------------------------------------------------------------------------------------------',
        },
        5 : {
            text : 'Get results from study',
            variables: ['study'],
            query : "SELECT DISTINCT (?s as ?id) ?resultid ?investigation ?study ?date ?workflow FROM <http://127.0.0.1:3030/ds/data/"+USER+"> {" +
                    "VALUES (?study) {('#study#')}{" +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#results_id> ?resultid ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?study ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#investigation_id> ?investigation ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#workflow> ?workflow ." +
                        "?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#date> ?date ." +
                        "}" +
                    "}" +
                    "ORDER BY DESC (?date)"
        },
        };
var VARIABLE_QUERIES = {
        sampleid: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?sample <http://127.0.0.1:3030/ds/data?graph="+USER+"#sample_id> ?value }" +
                  "ORDER BY(?value)",
        study: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#group_id> ?value }" +
               "ORDER BY (?value)",
        disease: "SELECT DISTINCT ?value FROM <http://127.0.0.1:3030/ds/data/"+USER+"> WHERE { ?s <http://127.0.0.1:3030/ds/data?graph="+USER+"#disease> ?value }" +
                "ORDER BY (?value)",
}