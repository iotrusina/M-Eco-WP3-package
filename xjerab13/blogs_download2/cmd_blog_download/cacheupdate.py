import glob
import cPickle as pickle
import os

def updatecache(fi):
    f = open(fi,"rb")
    cache = pickle.load(f)
    f.close()
    os.rename(fi, os.path.splitext(fi)[0]+".OLD")
    newcache = {}
    for key,data in cache.items():
        item = {}
        item["allEntries"] = len(data)
        item["content"] = data
        newcache[key] = item
    f = open(fi,"wb")
    pickle.dump(newcache, f, protocol=2)
    f.close()
    
    
def main():
    list = glob.glob(".cacheFiles/*.cache")
    for f in list:
        updatecache(f)
    

if __name__ == '__main__':
    main()