try:
    import json
except:
    import simplejson as json
import datetime
import time
from webrss.model.feed import Feed


class ControlRESTService(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl
    
    exposed = True
    def GET(self):
        jobs= self.ctrl.getJobs()
        resp = []
        for a in jobs:
            d = {}
            d["status"] = a.status
            d["name"] = a.name
            d["url"] = a.url
            d["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(a.last_update))
            
            sec = a.update_time+a.last_update-time.time()
            if sec > 0:
                d["next_update"] = str(datetime.timedelta(seconds=int(sec)))
            else:
                d["next_update"] = "-"
            
            
            resp.append(d) 
        return json.dumps(resp)
    
    def POST(self):
        pass
        
    exposed = True
    def PUT(self, id, action, f_type):
        #print action
        print id, action, f_type
        f = Feed.findById(id)
        if f_type == "f_enable":
            if action == "enable":
                f.enable = 1
                f.save()
                self.ctrl.addJob(f)
                
            elif action == "disable":
                f.enable = 0
                f.save()
                self.ctrl.removeJob(id)
                
        if f_type == "f_backup":
            if action == "enable":
                f.backup = 1
                f.save()
                self.ctrl.updateJob(f)
            elif action == "disable":
                f.backup = 0
                f.save()
                self.ctrl.updateJob(f)
                
    
    def DELETE(self):
        pass