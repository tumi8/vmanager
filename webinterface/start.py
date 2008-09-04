#!/usr/bin/python


from Cheetah.Template import Template

import cgi
import cgitb
import sys
import Ft.Xml.Xslt
import Ft.Xml
import re
from Ft.Xml.Domlette import NonvalidatingReader
import os
import base64

workdir = os.path.dirname(__file__)
sys.path.insert(0, workdir)

from VermontInstanceManager import VermontInstanceManager


def show_instance_list(req):
    # check status of all Vermont instances
    for i in vimanager.vermontInstances:
        i.retrieveStatus()

    t = Template(file=tmpl_prefix + "instance_list.tmpl")
    t.workdir = workdir
    t.title = "Vermont instances"
    t.vinstances = vimanager.vermontInstances
    req.content_type = "text/html"
    req.write(str(t))


def show_error(req, error):
    t = Template(file=tmpl_prefix + "error.tmpl")
    t.workdir = workdir
    t.title = "Error"
    t.error = error
    req.write(str(t))


def perform_start(req, instance):
    instance.start()
    
    return show_instance_list(req)


def perform_stop(req, instance):
    instance.stop()
    
    return show_instance_list(req)
    

def perform_reload(req, instance):
    instance.reload()
    
    return show_instance_list(req)


def show_configure(req, instance, cfgtext = None):
    if cfgtext is not None and cfgtext!=instance.cfgText:
        #sys.stderr.write("cfgtext: '%s'" % cfgtext)
        instance.setConfig(cfgtext)
        vimanager.reparseVermontConfigs()

    t = Template(file=tmpl_prefix + "configure.tmpl")
    t.title = "Configure host %s" % instance.host
    t.vi = instance
    t.workdir = workdir
    t.dyncfgtext = cgi.escape(instance.dynCfgText)
    req.write(str(t))


def show_logfile(req, instance):
    try:
        instance.retrieveLog()
        log = instance.logText
    except:
        log = "failed to read log file"

    t = Template(file=tmpl_prefix + "logfile.tmpl")
    t.title = "Log from host %s" % instance.host
    t.log = re.compile('\n').sub('<br>\n', log)
    t.vi = instance
    t.workdir = workdir
    req.write(str(t))


def show_sensor_data(req, instance):
    instance.retrieveSensorData()
    statxml = instance.sensorDataText
    html = Ft.Xml.Xslt.Transform(Ft.Xml.InputSource.DefaultFactory.fromString(statxml), workdir+"/sensor_output.xsl")
    #sys.stderr.write("
    html = html.replace('%modulegraph_url%', "start.py?vi_host=%s&action=modulegraph" % instance.host)

    t = Template(file=tmpl_prefix + "sensor_data.tmpl")
    t.title = "Statistics for host %s" % instance.host
    t.vi = instance
    t.workdir = workdir

    t.stat = html
    statxml = cgi.escape(statxml)
    t.xml = statxml.replace("\n", "<br />\n")
    req.write(str(t))


def show_statistics(req, instance):
    t = Template(file=tmpl_prefix + "statistics.tmpl")
    t.title = "Statistics for host %s" % instance.host
    t.vi = instance
    t.stats = []
    t.workdir = workdir
    names = instance.getGraphList()
    i = 0
    for n in names:
        t.stats.append({'name': n, 'idx': i})
        i += 1

    req.write(str(t))
    

    
def show_modulegraph(req, instance):
    statxml = instance.sensorDataText
    doc = NonvalidatingReader.parseString(statxml)
    g = "digraph G {\n"
    g += "\tnode[fontsize=8,shape=box,fontname=Helvetica,height=.3]\n"
    g += "\trankdir=LR;\n"
    for m in doc.xpath('/vermont/sensorData/sensor[@type=\'module\']'):
        mid = m.xpath('@id')[0].nodeValue
        mname =  "%s(%s)" % (m.xpath('@name')[0].nodeValue, mid)
        g += "\t%s [label=\"%s\"];\n" % (mid, mname)
        for n in m.xpath('next'):
            nid = n.childNodes[0].nodeValue
            g += "\t%s -> %s;\n" % (mid, nid)

    g += "}\n"
    fn = "/tmp/graph-%s.dot.tmp" % instance.host
    gfn = "/tmp/graph-%s.png.tmp" % instance.host
    fh = open(fn, "w")
    fh.write(g)
    fh.close()
    err = os.system("cat %s | dot -Tpng -o %s" % (fn, gfn))
    if err != 0:
        raise Exception("failed to execute dot (error code %d)" % err)
    fh = open(gfn, "r")
    req.content_type = "image/png"
    req.write(fh.read())
    fh.close()


def show_statimg(req, instance, idx1, idx2):
    png = base64.b64decode(instance.getGraph(int(idx1), int(idx2)))
    req.content_type = "image/png"
    req.write(png)


def index(req, action = None, vi_host = None, cfgtext = None, idx1 = None, idx2 = None):
    req.content_type = "text/html"
    if action is None or vi_host is None:
        return show_instance_list(req)

    instance = None
    for i in vimanager.vermontInstances:
        if i.host==vi_host:
            instance = i
            break
    if instance is None:
        return show_error("failed to find instance %s" % vi_host)

    if action=="start":
        return perform_start(req, instance)
    elif action=="stop":
        return perform_stop(req, instance)
    elif action=="reload":
        return perform_reload(req, instance)
    elif action=="configure":
        return show_configure(req, instance, cfgtext)
    elif action=="logfile":
        return show_logfile(req, instance)
    elif action=="sensor_data":
        return show_sensor_data(req, instance)
    elif action=="statistics":
        return show_statistics(req, instance)
    elif action=="modulegraph":
        return show_modulegraph(req, instance)
    elif action=="statimg":
        if idx1 is None or idx2 is None:
            return show_error(req, "invalid parameters")
        else:
            return show_statimg(req, instance, idx1, idx2)
    else:
        return show_error(req, "invalid parameters")
    
    return show_instance_list(req)


# initialize application
cgitb.enable()
tmpl_prefix = workdir + "/templates/"

vimanager = VermontInstanceManager(workdir)
vimanager.setup()

