/*
** Creating the interface to make queries and show the data.
** It also sends some important data to views.py to be able to upload data to Galaxy.
*/
var count = 0;
$(document).ready(function () {
    $("#samples").addClass('hidden');
    $("#step2").addClass('hidden');
    $("#step3").addClass('hidden');
    $("#errorPanel").addClass('hidden');
    $("#infoPanel").addClass('hidden');
    $("#noResultPanel").addClass('hidden');
    /* load template queries */
    var template = document.getElementById('template');
    var templQuerySize = 0;
    for (var key in TEMPLATE_QUERIES) {
        var text = TEMPLATE_QUERIES[key].text;
        var keyIndex = parseInt(key) - 1;
        template.options[template.options.length] = new Option(text, key);
        console.log("Template Text" + text);
        templQuerySize += 1;
    }
    template.setAttribute("size", templQuerySize);
});
document.getElementById("template").onchange = function () {
    $("#sampleid").addClass('hidden');
    $("#family").addClass('hidden');
    $("#group").addClass('hidden');
    $("#sex").addClass('hidden');
    $("#disease").addClass('hidden');
    $("#errorPanel").addClass('hidden');
    $('#results_table').empty();
    $("#noResultPanel").addClass('hidden');
    var selected = $("#template").val();
    console.log(TEMPLATE_QUERIES[selected]);
    if (TEMPLATE_QUERIES[selected].variables.indexOf('sampleid') > -1) {
        $("#sampleid").removeClass('hidden');
    }
    if (TEMPLATE_QUERIES[selected].variables.indexOf('family') > -1) {
        $("#family").removeClass('hidden');
    }
    if (TEMPLATE_QUERIES[selected].variables.indexOf('group') > -1) {
        $("#group").removeClass('hidden');
    }
    if (TEMPLATE_QUERIES[selected].variables.indexOf('sex') > -1) {
        $("#sex").removeClass('hidden');
    }
    if (TEMPLATE_QUERIES[selected].variables.indexOf('disease') > -1) {
        $("#disease").removeClass('hidden');
    }
    if (TEMPLATE_QUERIES[selected].variables.indexOf('all') > -1) {
        $("#all").removeClass('hidden');
    }
    // Fill step2
    TEMPLATE_QUERIES[selected].variables.forEach(function (entry) {
        var service = encodeURI(SPARQL_ENDPOINT + VARIABLE_QUERIES[entry]
            + '&format=json').replace(/#/g, "%23");
        $.ajax({
            url: service, dataType: 'jsonp', async: false,
            success: function (result) {
                console.log(result);
                var inputOption = document.getElementById(entry + 'Option');
                var dataList = document.getElementById(entry + 'Datalist');
                $(inputOption).empty();
                $(inputOption).val('');
                if (dataList != null) {
                    $(dataList).empty();
                }
                result.results.bindings.forEach(function (v) {
                    var option = document.createElement('option');
                    option.setAttribute('width', '70%');
                    if (v.url !== undefined) {
                        option.value = v.value.value;
                        option.setAttribute('data-input-value', v.url.value);
                    }
                    else {
                        option.value = v.value.value;
                        option.setAttribute('data-input-value', v.value.value);
                    }
                    if (dataList !== null) {
                        dataList.appendChild(option);
                    }
                });
            },
            error: function (xhr) {
                alert("An error occured: " + xhr.status + " " + xhr.statusText);
            }
        });
    });
    $("#samples").removeClass('hidden');
    $("#step2").removeClass('hidden');
    $("#step3").addClass('hidden');
}
document.getElementById("process").onclick = function () {
    $("#errorPanel").addClass('hidden');
    $("#infoPanel").addClass('hidden');
    $("#step3").addClass('hidden');
    $("#noResultPanel").addClass('hidden');
    var selected = $("#template").val();
    var query = TEMPLATE_QUERIES[selected].query
    var isValueMissing = false;

    //Replace variable values in the query
    TEMPLATE_QUERIES[selected].variables.forEach(function (entry) {
        var selectedValue = null;
        var selectedOption = $('#' + (entry + 'Option'));
        if (selectedOption.val() === '') {
            var errorMessage = "<strong>Input error : </strong>Choose a value for "
            errorMessage = errorMessage + "<strong>" + entry + "</strong> ";
            isValueMissing = true;
            $("#errorPanel").html(errorMessage);
            $("#errorPanel").removeClass('hidden');
            return false;
        }
        else {
            $('#' + (entry + 'Datalist') + ' option').each(function (index, value) {
                if ($(value).val() === selectedOption.val()) {
                    selectedValue = $(value).attr('data-input-value');
                    console.log('selected option = [' + selectedValue + "]");
                    return false;
                }
            });
        }
        query = query.replace('#' + entry + '#', selectedValue);
    });
    if (!isValueMissing) {
        $('#process').buttonLoader('start');
        console.log("SPARQL query \n" + query);
        var service = encodeURI(SPARQL_ENDPOINT + query + '&format=json').
            replace(/#/g, '%23');
        $("#infoPanel").html('<strong>Info :</strong> Some queries take more time to process,' +
            'thanks for being patient');

        $.ajax({
            url: service, dataType: 'jsonp', success: function (result) {
                console.log(result);
                fillTable(result)
            },
            error: function (xhr) {
                alert("An error occured: " + xhr.status + " " + xhr.statusText);
            }
        });
    }
}
function fillTable(result) {
    $("#infoPanel").addClass('hidden');
    $("#noResultPanel").addClass('hidden');
    $('#process').buttonLoader('stop');
    $("#step3").removeClass('hidden');
    $("#results_table").removeClass('hidden');
    var hasResult = false;
    var table = '<thead><tr>'
    table += '<th>select file</th>'
    result.head.vars.forEach(function (entry) {
        if (entry.indexOf("URI") === -1) {
            table += '<th><a>' + entry + '</a></th>'
        }
    });
    table += '</tr></thead><tbody>'
    var rownr = 1;
    result.results.bindings.forEach(function (value) {

        table += '<tr>'
        if(hasCol) {
            table+='<td><button id="index_buttons" onclick="getoutput()">Show results</button></td>';
        }
        table += '<td><input type="checkbox" name="select" value="'+ rownr +'"></td>';
        rownr = rownr + 1;
        result.head.vars.forEach(function (head) {
            if (head.indexOf("URI") === -1 && value[head] !== undefined) {
                var resource = value[head + "URI"];
                var displayName = value[head].value;
                hasResult = true;
                if (resource !== undefined) {
                    var resourceURI = resource.value;
                    var sampleTypeURI = value["sampleTypeURI"];
                    if (head === "group" && sampleTypeURI !== undefined) {
                        var sampleid = value["sampleid"];
                        var family = value["family"];
                        var group = value["group"];
                        var sex = value["sex"];
                        var galaxy = "galaxy"
                        table += '</span></span></div></td>';
                    }
                    else {
                        table += '<td><a target="_blank" href="' + resourceURI
                            + '" resource="' + resourceURI + '"> <span property="rdfs:label">'
                            + displayName + '</span></a></td>';
                    }
                }
                else {
                    table += '<td><span>' + displayName + '</span></td>';
                }
                // Start if head is group
                if (head === "sample" && rownr >= 2) {
                    table +='<td>'+
                            '<input type="checkbox" name="samplea" value="' + displayName + '"> A' + 
                            // '<br />' +
                            '<input type="checkbox" name="sampleb" value="' + displayName +'"> B' +
                            '</td>';
                }
                //end if head is group
            }
        });
        table += '</tr>';
    });
    table += '</tr></tbody>'
    $("#pagingContainer").empty();
    $('#results_table').html(table);
    $('#results_table').simplePagination({
        perPage: 30,
        previousButtonText: 'Prev',
        nextButtonText: 'Next',
        previousButtonClass: "btn btn-primary btn-xs",
        nextButtonClass: "btn btn-primary btn-xs"
    });
    function hasColumn(tblSel, content) {
        var ths = document.querySelectorAll(tblSel + ' th');
        return Array.prototype.some.call(ths, function(el) {
            return el.textContent === content;
        });
    };
    var hasCol = hasColumn("#results_table thead", "workflow");
    if(hasCol) {
        document.getElementById('show_results').style.display = "block";
        document.getElementById('select').style.display = "none";
        $('#galaxy').html(
            '<p>Select a result and press the Show results button</p>'
        );
    } else {
        $('#galaxy').html(
            '<select name="filetype" id="filetype">' +
                '<optgroup label="File Type:">' +
                '<option value="vcf">vcf</option>' +
                '<option value="tabular">tabular</option>' +
                '<option value="fasta">fasta</option>' +
                '<option value="fastq">fastq</option>' +
                '<option value="auto">auto</option>' +
                '</optgroup>' +
                '</select>' +
                '<select name="dbkey" id="dbkey">' +
                '<optgroup label="Database">' +
                '<option value="hg19">HG19</option>' +
                '<option value="hg18">HG18</option>' +
                '<option value="?">?</option>' +
                '</optgroup>' +
                '</select>' +
                '<input type="text" id="historyname" name="historyname" placeholder="Enter new history name."/>' +
            '<button id="index_buttons" onclick="postdata(\'group\')">send to galaxy</button>'
        );
    }

    // Sort table
    $('th').click(function(){
        var table = $(this).parents('table').eq(0)
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
        this.desc = !this.desc
        if (!this.desc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
    })
    function comparer(index) {
        return function(a, b) {
            var valA = getCellValue(a, index), valB = getCellValue(b, index)
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.localeCompare(valB)
        }
    }
    function getCellValue(row, index){ return $(row).children('td').eq(index).html() }
    // Sort table end
    if (!hasResult) {
        $("#noResultPanel").removeClass('hidden');
        $("#results_table").addClass('hidden');
    }
}

function postdata(g) {
    document.getElementById('loading').style.display = "block";
    var workflowid = document.getElementById('workflow').value;
    var selected = new Array;
    var selectout = new Array;
    var onlydata = "";
    if(document.getElementById('onlydata').checked) {
        var onlydata = document.getElementById('onlydata').value;
    }
    var dat = [];
    var meta = [];
    var group = [];
    var samples = new Array;
    var samplesb = new Array;
    $("input:checkbox[name=samplea]:checked").each(function(){
        samples.push($(this).val());
    });
    $("input:checkbox[name=sampleb]:checked").each(function(){
        samplesb.push($(this).val());
    });
    $("input:checkbox[name=select]:checked").each(function(){
        selected.push($(this).val());
    });
    for (s = 0; s < selected.length; s++) {
        dat.push(getrow(selected[s])[0]);
        meta.push(getrow(selected[s])[1]);
        group.push(getrow(selected[s])[2]);
    }
    var jsonSamples = JSON.stringify(samples);
    var jsonSamplesb = JSON.stringify(samplesb);
    var jsonSelected = JSON.stringify(dat);
    var jsonMeta = JSON.stringify(meta);
    var jsonGroup = JSON.stringify(group);
    var data_id = checkData(g);
    var meta_id = checkMeta(g);
    var token = "ygcLQAJkWH2qSfawc39DI9tGxisceVSTgw9h2Diuh0z03QRx9Lgl91gneTok";
    var filetype = document.getElementById('filetype').value;
    var dbkey = document.getElementById('dbkey').value;
    var historyname = document.getElementById('historyname').value;
    $.ajax({
        type: 'POST',
        url: "upload/",
        data: { 'data_id': data_id, 'token': token, 'workflowid': workflowid, 
        'filetype': filetype, 'dbkey': dbkey, 'meta_id': meta_id, 
        'selected': jsonSelected, 'meta': jsonMeta, 'onlydata': onlydata, 
        'samples': jsonSamples, 'samplesb': jsonSamplesb, 'historyname': historyname, 
        'group': jsonGroup},
        success: function (data) {
            if(dat.length <= 0) {
                document.getElementById('errormessage').innerHTML = "No file selected, please try again."
                document.getElementById('error').style.display = "block";
                document.getElementById('finished').style.display = "none";
                document.getElementById('loading').style.display = "none";
            } else {
                document.getElementById('loading').style.display = "none";
                document.getElementById('error').style.display = "none";
                document.getElementById('finished').style.display = "block";
            }
            setTimeout(refresh, 5000);
        },
        error: function (data) {
            document.getElementById('loading').style.display = "none";
            document.getElementById('finished').style.display = "none";
            document.getElementById('error').style.display = "block";
            setTimeout(refresh, 5000);
        }
    });
}
function getoutput() {
    var selected = new Array;
    var group = [];
    var resultid = new Array;
    $("input:checkbox[name=select]:checked").each(function(){
        selected.push($(this).val());
    });
    for (s = 0; s < selected.length; s++) {
        resultid.push(getrow(selected[s])[1]);
        group.push(getrow(selected[s])[2]);
    }
    var jsonGroup = JSON.stringify(group);
    var jsonResultid = JSON.stringify(resultid);
    $.ajax({
        type: 'POST',
        url: "results",
        data: { 'group': jsonGroup, 'resultid': jsonResultid},
        success: function (data) {
            window.location.href = "/results"
        },
        error: function (data) {
            alert(data);
        }
    });
}
function refresh () {
    window.location.href = "/";
}
function checkData(g) {
    var n1 = document.getElementById('results_table').rows.length;
    var i = 0, j = 0;
    var str = "";
    // Loop through the results_table.
    for (i = 0; i < n1; i++) {
        var groups = document.getElementById('results_table').rows[i].cells.item(3).innerText;
        if (groups == g) {
            var n = i;
            var n2 = document.getElementById('results_table').rows[i].length;
            // Get the first column (PID)
            for (i = 1; i < n1; i++) {
                var x = document.getElementById('results_table').rows[n].cells.item(j + 1).innerText;
            }
        }
        else {
            x = "";
        }
        str = str + x;
    }
    return str;
}
function checkMeta(g) {
    var n1 = document.getElementById('results_table').rows.length;
    var i = 0, j = 0;
    var str = "";
    // Loop through the results_table.
    for (i = 0; i < n1; i++) {
        var groups = document.getElementById('results_table').rows[i].cells.item(3).innerText;
        if (groups == g) {
            var n = i;
            var n2 = document.getElementById('results_table').rows[i].length;
            // Get the first column (PID)
            for (i = 1; i < n1; i++) {
                var x = document.getElementById('results_table').rows[n].cells.item(j + 2).innerText;
            }
        }
        else {
            x = "";
        }
        str = str + x;
    }
    return str;
}
function getrow(r) {
    var str = "";
    var str2 = "";
    var str3 = "";
    var x = document.getElementById('results_table').rows[r].cells.item(1).innerText;
    var y = document.getElementById('results_table').rows[r].cells.item(2).innerText;
    var z = document.getElementById('results_table').rows[r].cells.item(3).innerText;
    str = str + x;
    str2 = str2 + y;
    str3 = str3 + z;
    return [str, str2, str3];
}
function getsamples() {
    var samples = new Array;
    var samplesb = new Array;
    var values = new Array;
    var valuesb = new Array;
    $("input:checkbox[name=samplea]:checked").each(function(){
        samples.push($(this).val());
    });
    $("input:checkbox[name=sampleb]:checked").each(function(){
        samplesb.push($(this).val());
    });
    var jsonSamples = JSON.stringify(samples);
    var jsonSamplesb = JSON.stringify(samplesb);
    sample = jsonSamples.split(",");
    for (var i = 0; i < samples.length; i++) {
        values.push(Math.floor(Math.random() * 10) + 1);
    }
    for (var i = 0; i < samplesb.length; i++) {
        valuesb.push(Math.floor(Math.random() * 10) + 1);
    }
    $.ajax({
            type: 'POST',
            url: "samples/",
            data: {'samples': jsonSamples},
            success: function (data) {
                makeplot(samples, samplesb, values, valuesb);
            },
            error: function(data) {},
    });
}

function rerun_analysis() {
    wid = document.getElementById("workflowid").innerText; 
    inputs = document.getElementById("input-list").innerText;
    inputs = inputs.split(',');
    resultid = document.getElementById("title").innerText;
    var urls = new Array;
    for(i=0; i<=(inputs.length-1); i++) {
        urls.push(resultid.replace(" ", "") + "/" + inputs[i].replace(" ", "").replace("\n", "").replace("'", "").replace("[", "").replace("]", "").replace("'", ""))
    }
    var jsonURLS = JSON.stringify(urls);
    document.getElementById('running').style.display = "block";
    $.ajax({
        type: 'POST',
        url: "rerun",
        data: {'workflowid': wid, 'inputs': inputs, 'urls': jsonURLS, 'resultid': resultid},
        success: function (data) {
            document.getElementById('running').style.display = "none";
            document.getElementById('finished').style.display = "block";
            setTimeout(refresh, 5000);
        },
        error: function(data) {
            document.getElementById('error').style.display = "block";
            setTimeout(refresh, 5000);
        },
    });
}