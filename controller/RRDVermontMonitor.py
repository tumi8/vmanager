import os


class RRDVermontMonitor:

    xpaths = None
    names = None
    interval = None
    # record every 10  60  3600 seconds a value in rrd (multiplied by "step" size -s)
    rrdintervals = (2, 12, 720)
    rrdgraphhist = (120, 1440, 10080)

    def __init__(self, xpaths, names, interval):
        self.xpaths = xpaths
        self.names = names
        self.interval = interval

    def collect_data(self, xml):
        if not os.access("rrd", os.R_OK|os.W_OK):
            os.mkdir("rrd")
        rrdfn = "rrd/db_%d_%d.rrd"
        for i in range(0, len(self.xpaths)):
            data = xml.xpath(self.xpaths[i])
            print "inserting value %s for element '%s' (%s)" % (data, self.names[i], self.xpaths[i])
            for j in range(0, len(self.rrdintervals)):
                if not os.access(rrdfn % (i, j), os.R_OK|os.W_OK):
                    os.system("rrdtool create %s -s 5 DS:s:GAUGE:%d:U:U RRA:AVERAGE:0.5:%d:10000 RRA:MIN:0.5:%d:10000 RRA:MAX:0.5:%d:10000" % (rrdfn % (i, j), self.rrdintervals[j]*5*2, self.rrdintervals[j], self.rrdintervals[j], self.rrdintervals[j]))
                os.system("rrdtool update %s N:%f " % (rrdfn % (i, j), data))
        pass
    

    def get_graph(self, idx1, idx2):
        rrdfn = "rrd/db_%d_%d.rrd" % (idx1, idx2)
        pngfn = "rrd/db_%d_%d.png" % (idx1, idx2)
        os.system("rrdtool graph %s --imgformat PNG --end now --start end-%dm DEF:ds0b=%s:s:MAX LINE1:ds0b#9999FF:\"min/max\" DEF:ds0c=%s:s:MIN LINE1:ds0c#9999FF DEF:ds0a=%s:s:AVERAGE LINE2:ds0a#0000FF:\"average\"" % (pngfn, self.rrdgraphhist[idx2], rrdfn, rrdfn, rrdfn))
        pic = open(pngfn).read()
        return base64.b64encode(pic)
        