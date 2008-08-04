#!/usr/bin/python


from Cheetah.Template import Template

import MySQLdb
import cgi
import cgitb
import urllib
import sys
import xmlrpclib
import ConfigParser
import Ft.Xml.Xslt
import Ft.Xml
import re
from Ft.Xml.Domlette import NonvalidatingReader
import os
import base64
from mod_python import apache

workdir = os.path.dirname(__file__)
sys.path.insert(0, workdir)
from VermontInstance import VermontInstance


def read_config():
	cp = ConfigParser.ConfigParser()
	cp.read(workdir+"/vermont_web.conf")
	sec = "VermontInstances"
	instances = []
	i = 1
	try:
		while True:
			instance = VermontInstance(cp.get(sec, "host_%d" % i))
			instances.append(instance)
			i += 1
	except ConfigParser.NoOptionError:
		pass
	if i==1:
		raise Exception("no valid remote Vermont instance entries in config!")
	return instances


def show_instance_list(req):
	# check status of all Vermont instances
	for i in vinstances:
		i.get_status()

	t = Template(file=tmpl_prefix + "instance_list.tmpl")
	t.workdir = workdir
	t.title = "Vermont instances"
	t.vinstances = vinstances
	req.content_type = "text/html"
	req.write(str(t))


def show_error(req, error):
	t = Template(file=tmpl_prefix + "error.tmpl")
	t.workdir = workdir
	t.title = "Error"
	t.error = error
	req.write(str(t))


def perform_start(req, instance):
	if instance.conn.get_config()=="":
		return show_error(req, "no configuration was set for this Vermont instance!")
	instance.conn.start()
	
	return show_instance_list(req)


def perform_stop(req, instance):
	if instance.conn.get_config()=="":
		return show_error(req, "no configuration was set for this Vermont instance!")
	if not instance.conn.stop():
		return show_error(req, "failed to stop Vermont instance on host %s" % instance.host)
	
	return show_instance_list(req)
	

def perform_reload(req, instance):
	if instance.conn.get_config()=="":
		return show_error(req, "no configuration was set for this Vermont instance!")
	instance.conn.reload()
	
	return show_instance_list(req)


def show_configure(req, instance, cfgtext = None):
	instance.get_cfgtext()
	if cfgtext is not None and cfgtext!=instance.cfgtext:
		#sys.stderr.write("cfgtext: '%s'" % cfgtext)
		instance.set_cfgtext(cfgtext)


	t = Template(file=tmpl_prefix + "configure.tmpl")
	t.title = "Configure host %s" % instance.host
	t.vi = instance
	t.workdir = workdir
	req.write(str(t))


def show_logfile(req, instance):
	log = instance.conn.get_logfile()

	t = Template(file=tmpl_prefix + "logfile.tmpl")
	t.title = "Log from host %s" % instance.host
	t.log = re.compile('\n').sub('<br>\n', log)
	t.vi = instance
	t.workdir = workdir
	req.write(str(t))


def show_sensor_data(req, instance):
	statxml = instance.conn.get_stats()
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
	names = instance.conn.get_stat_list()
	i = 0
	for n in names:
		t.stats.append({'name': n, 'idx': i})
		i += 1

	req.write(str(t))
	

	
def show_modulegraph(req, instance):
	statxml = instance.conn.get_stats()
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
	png = base64.b64decode(instance.conn.get_graph(int(idx1), int(idx2)))
	req.content_type = "image/png"
	req.write(png)


def index(req, action = None, vi_host = None, cfgtext = None, idx1 = None, idx2 = None):
	req.content_type = "text/html"
	if action is None or vi_host is None:
		return show_instance_list(req)

	instance = None
	for i in vinstances:
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

# =======================================
# start main processing of http request

cgitb.enable()

# default parameters, if not given in URL
action = "instance_list"
vi_host = ""
t = None


# check parameters
#cfgtext = None
#cgiparams = cgi.FieldStorage()
#apache.log_error("fieldstorage:" + str(cgiparams))
#if cgiparams.has_key("action"):
#	action = cgiparams.getvalue("action")
#	apache.log_error("action: '%s'" % action)
#if cgiparams.has_key("vi_host"):
#	vi_host = cgiparams.getvalue("vi_host")
#if cgiparams.has_key("cfgtext"):
#	cfgtext = cgiparams.getvalue("cfgtext")
#
#
vinstances = read_config()
tmpl_prefix = workdir + "/templates/"
#
## check vi_host parameter
#if action!="instance_list": 
#	instance = None
#	for i in vinstances:
#		if i.host==vi_host:
#			instance = i
#			break
#
#if t is None:
#	if action=="instance_list":
#		t = show_instance_list()
#	else:
#		if instance is None: 
#			t = show_error("failed to find instance %s" % host)
#
#if t is None:
#	if action=="start":
#		t = perform_start(instance)
#	elif action=="stop":
#		t = perform_stop(instance)
#	elif action=="reload":
#		t = perform_reload(instance)
#	elif action=="configure":
#		t = show_configure(instance, cfgtext)
#	elif action=="logfile":
#		t = show_logfile(instance)
#	elif action=="sensor_data":
#		t = show_sensor_data(instance)
#	elif action=="statistics":
#		t = show_statistics(instance)
#	elif action=="modulegraph":
#		t = show_modulegraph(instance)
#	elif action=="statimg":
#		if not (cgiparams.has_key("idx1") and cgiparams.has_key("idx2")):
#			t = show_error("invalid parameters")
#		else:
#			t = show_statimg(instance, cgiparams.getvalue("idx1"), cgiparams.getvalue("idx2"))
#	else:
#		t = show_error("invalid parameters")
#	
#if t is not None:
#	print "Content-Type: text/html\n\n"
#	print t
