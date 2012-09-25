from __future__ import with_statement
import sys
import psycopg2
from datetime import date
from pprint import pprint
from autoapi.connection import get_connection

FOLDER = '/homes/eva/xr/xrylko00/spinn/spinn3r/master/DATA/'
OUT =  "/mnt/minerva1/nlp/projects/meco/mg4j/server/root/xrylko00/jstats/"

conn = get_connection()
cur = conn.cursor()

today = '%s' % date.today()

if (len(sys.argv) > 1 and sys.argv[1] == 'nocreate'):
    pass
else:
    cur.execute("""select create_stats()""")
    for i in cur:    pass
    conn.commit()


cur.execute("""SELECT type, param, value, EXTRACT(EPOCH FROM timestamp) FROM logs 
        WHERE timestamp >= (NOW() - interval '26 days')
        ORDER BY timestamp""")

results = dict()
for type, param, value, timestamp in cur:
    if not results.get(type):
        results[type] = dict()
    if not results[type].get(param):
        results[type][param] = list()
    results[type][param].append( (timestamp, value) )
#pprint( results )


for desc,vals in results.iteritems():
    filename = desc.replace(" ", "_") + ".html"
    print "creating:", filename
    with open(OUT + filename, 'w') as f:
        f.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>%s</title>
    <link href="layout.css" rel="stylesheet" type="text/css">
    <!--[if lte IE 8]><script language="javascript" type="text/javascript" src="../excanvas.min.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src="./jquery.js"></script>
    <script language="javascript" type="text/javascript" src="./flot/jquery.flot.js"></script>
 </head>
    <body>""" % desc)
        f.write("<h1>%s</h1>" % desc)
        f.write("""
                <p id="choices">Show:</p>
                <div id="placeholder" style="width:1000px;height:800px;"></div>
<script id="source">
$(function () {
    var datasets =""")
        f.write("[\n")
        after = False
        for k, v in vals.iteritems():
            if after:
                f.write(",")
            else:
                after = True
            f.write( "{\n")
            f.write( '\tlabel: "%s",\n' % k)
            f.write( '\tdata: [%s]\n' % ", ".join(map(
                lambda a: "[%d, %d]" % (int(a[0])*1000, a[1]), v)))
            f.write("}")
        f.write( "\n];\n")
        f.write("""    // hard-code color indices to prevent them from shifting as
    // countries are turned on/off
    var i = 0;
    $.each(datasets, function(key, val) {
        val.color = i;
        ++i;
    });
    
    // insert checkboxes 
    var choiceContainer = $("#choices");
    $.each(datasets, function(key, val) {
        choiceContainer.append('<br/><input type="checkbox" name="' + key +
                               '" checked="checked" id="id' + key + '">' +
                               '<label for="id' + key + '">'
                                + val.label + '</label>');
    });
    choiceContainer.find("input").click(plotAccordingToChoices);

    
    function plotAccordingToChoices() {
        var data = [];

        choiceContainer.find("input:checked").each(function () {
            var key = $(this).attr("name");
            if (key && datasets[key])
                data.push(datasets[key]);
        });

        if (data.length > 0)
            $.plot($("#placeholder"), data, { 
                xaxis: { 
                        mode: "time", 
                        timeformat: "%d. %m", 
                        minTickSize: [1, "day"],
                },
                series: {
                   lines: { show: true },
                   points: { show: true }
                },
                legend: {
                    position: "nw"
                }
            });
    }

    plotAccordingToChoices();
    });
    </script>
    </body>
    </html>""")
        continue

        f.write("""    $.plot($("#placeholder"), d, 
                { 
                xaxis: { 
                        mode: "time", 
                        timeformat: "%d. %m", 
                        minTickSize: [1, "day"],
                        tickSize: [2, "day"]
                },
                series: {
                   lines: { show: true },
                   points: { show: true }
                },
                legend: {
                    position: "nw"
                }
                });
});
</script>

 </body>
</html>
""")





