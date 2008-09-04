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
import xmlrpclib
import ConfigParser
import traceback

workdir = os.path.dirname(__file__)
sys.path.insert(0, workdir)



def show_instance_list(req, hosts):
    try:
        stati = remotevm.getStati()
        dynconfenabled = remotevm.getDynconfEnabled()
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc())
        
    t = Template(file=tmpl_prefix + "instance_list.tmpl")
    t.workdir = workdir
    t.title = "Vermont Manager"
    t.hosts = hosts
    t.stati = stati
    t.dynconfenabled = dynconfenabled
    req.content_type = "text/html"
    req.write(str(t))


def show_error(req, error, text = ""):
    t = Template(file=tmpl_prefix + "error.tmpl")
    t.workdir = workdir
    t.title = "Error"
    t.error = error
    t.text = text
    req.write(str(t))


def perform_start(req, host, hosts):
    remotevm.start(host)
    
    return show_instance_list(req, hosts)


def perform_stop(req, host, hosts):
    remotevm.stop(host)
    
    return show_instance_list(req, hosts)
    

def perform_reload(req, host, hosts):
    remotevm.reload(host)
    
    return show_instance_list(req, hosts)


def show_configure(req, host, cfgtext = None):
    if cfgtext is not None:
        #sys.stderr.write("cfgtext: '%s'" % cfgtext)
        remotevm.setConfig(host, cfgtext)
        remotevm.reparseVermontConfigs()

    t = Template(file=tmpl_prefix + "configure.tmpl")
    t.title = "Configure host %s" % host
    t.host = host
    t.workdir = workdir
    (t.cfgtext, t.dyncfgtext) = [ cgi.escape(x) for x in remotevm.getConfigs(host) ]
    req.write(str(t))


def show_logfile(req, host):
    try:
        log = remotevm.getLog(host)
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc())     

    t = Template(file=tmpl_prefix + "logfile.tmpl")
    t.title = "Log from host %s" % host
    t.log = re.compile('\n').sub('<br>\n', log)
    t.host = host
    t.workdir = workdir
    req.write(str(t))


def show_sensor_data(req, host):
    try:
        sdata = remotevm.getSensorData(host)
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc()) 
    html = Ft.Xml.Xslt.Transform(Ft.Xml.InputSource.DefaultFactory.fromString(sdata), workdir+"/sensor_output.xsl")
    #sys.stderr.write("
    html = html.replace('%modulegraph_url%', "start.py?vi_host=%s&action=modulegraph" % host)

    t = Template(file=tmpl_prefix + "sensor_data.tmpl")
    t.title = "Statistics for host %s" % host
    t.host = host
    t.workdir = workdir

    t.stat = html
    statxml = cgi.escape(sdata)
    t.xml = statxml.replace("\n", "<br />\n")
    req.write(str(t))


def show_statistics(req, host):
    try:
        names = remotevm.getGraphList(host)
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc()) 
    t = Template(file=tmpl_prefix + "statistics.tmpl")
    t.title = "Statistics for host %s" % host
    t.host = host
    t.stats = []
    t.workdir = workdir
    
    i = 0
    for n in names:
        t.stats.append({'name': n, 'idx': i})
        i += 1

    req.write(str(t))
    

    
def show_modulegraph(req, host):    
    try:
        statxml = remotevm.getSensorData(host)
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc())
     
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
    fn = "/tmp/graph-%s.dot.tmp" % host
    gfn = "/tmp/graph-%s.png.tmp" % host
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


def show_statimg(req, host, idx1, idx2):
    png = base64.b64decode(remotevm.getGraph(host, int(idx1), int(idx2)))
    req.content_type = "image/png"
    req.write(png)
    
    
def show_manager_log(req):
    try:
        log = remotevm.getManagerLog()
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc())     

    t = Template(file=tmpl_prefix + "logfile.tmpl")
    t.title = "Log from Vermont Manager"
    t.log = re.compile('\n').sub('<br>\n', cgi.escape(log))
    t.host = url
    t.workdir = workdir
    req.write(str(t))
    
    
def set_dynconf(req, enable, hosts):
    try:
        remotevm.setDynconfEnabled(enable)
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc())
    return show_instance_list(req, hosts) 


def index(req, action = None, vi_host = None, cfgtext = None, idx1 = None, idx2 = None):
    req.content_type = "text/html"
    
    try:
        hosts = remotevm.getHosts()
    except:
        return show_error(req, "failed to contact manager", traceback.format_exc())
    
    if action is None:
        return show_instance_list(req, hosts)
    elif action=="disable_dynconf":
        return set_dynconf(req, False, hosts)
    elif action=="enable_dynconf":
        return set_dynconf(req, True, hosts)
    elif action=="show_manager_log":
        return show_manager_log(req)
    
    if vi_host is not None:
        if not vi_host in hosts:
            return show_error("failed to find vermont host %s" % vi_host)
    
        if action=="start":
            return perform_start(req, vi_host, hosts)
        elif action=="stop":
            return perform_stop(req, vi_host, hosts)
        elif action=="reload":
            return perform_reload(req, vi_host, hosts)
        elif action=="configure":
            return show_configure(req, vi_host, cfgtext)
        elif action=="logfile":
            return show_logfile(req, vi_host)
        elif action=="sensor_data":
            return show_sensor_data(req, vi_host)
        elif action=="statistics":
            return show_statistics(req, vi_host)
        elif action=="modulegraph":
            return show_modulegraph(req, vi_host)
        elif action=="statimg":
            if idx1 is None or idx2 is None:
                return show_error(req, "invalid parameters")
            else:
                return show_statimg(req, vi_host, idx1, idx2)
    return show_error(req, "invalid parameters")


# initialize application
cgitb.enable()
tmpl_prefix = workdir + "/templates/"

# read config
cp = ConfigParser.ConfigParser()
cp.read("%s/vermont_web.conf" % workdir)
sec = "Global"
url = cp.get(sec, "VManager")


remotevm = xmlrpclib.ServerProxy(url, None, None, 1, 1)

