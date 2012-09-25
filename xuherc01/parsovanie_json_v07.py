


from sys import argv
import re
import datetime
import time
import os
from xml.sax import saxutils
import codecs
import sys
import json

sys.path.append("/mnt/minerva1/nlp/projects/twitter_classification/TwitterClassifier/") 

from tweetclassify import TwitterClassifier


class createTweetDocument:
    
    clasificator = None
    score = 0.0
    lang = True
    
    allWords = {}
    outFiles = {}
    
    
    def __init__(self, fileIn, fileOut, fileOutFiltered):
        self.clasificator = TwitterClassifier()
        self.__initKeywords()
        self.__initDirectories()
        self.__initOutFiles(fileOut, fileOutFiltered)
        self.__createDocument(fileIn)
        self.__closeOutFiles()
        
    def now_dateTime(self):
        """Product ISO 8601 dateTime stamp."""
        try:
            now = datetime.datetime.now()
            return now.isoformat()
        except ValueError:
            pass
        return 0 
        
    # funkcia ktora vytvara datum
    def make_ISOdate(self, datum):
        pom = datum
        now = datetime.datetime(*time.strptime(datum,"%a %b %d %H:%M:%S %Y")[0:6])
        pubdate = "        <pubDate>"+now.strftime("%Y-%m-%dT%H:%M:%S")+"</pubDate>\n"
        return pubdate
        
    def __initKeywords(self):
        for filename in os.listdir("./track_files/"):
            File = codecs.open("./track_files/" + filename, "r", "utf-8")
            self.allWords[filename] = []
            for line in File:
                line = line.replace("track=", "")
                word = ""
                for character in line:
                    if character == ",":
                        self.allWords[filename].append(word)
                        word = ""
                        continue
                    word = word + character
                self.allWords[filename].append(word)
    
    def __initDirectories(self):
        for directory in self.allWords:
            try:
                os.mkdir(directory + "_outputs")
            except OSError:
                pass
            
    def __initOutFiles(self, fileOut, fileOutFiltered):
        for directory in self.allWords:
            File_all = codecs.open("./" + directory + "_outputs/" + fileOut, "w", "utf-8")
            File_all.write(unicode('<?xml version="1.0" encoding="UTF-8"?>\n'))
            File_all.write(unicode('<channel author="xuherc01" timestamp="'+self.now_dateTime()+'">\n'))
            self.outFiles[directory] = {}
            self.outFiles[directory]["all"] = File_all
            
            # project M-Eco
            if directory == "track_all_DE_EN":
                File_filtered = codecs.open("./" + directory + "_outputs/" + fileOutFiltered, "w", "utf-8")
                File_filtered.write(unicode('<?xml version="1.0" encoding="UTF-8"?>\n'))
                File_filtered.write(unicode('<channel author="xuherc01" timestamp="'+self.now_dateTime()+'">\n'))
                self.outFiles[directory]["filtered"] = File_filtered
            
    def __closeOutFiles(self):
        for File in self.outFiles:
            self.outFiles[File]["all"].write(unicode('</channel>'))
            self.outFiles[File]["all"].close()
            try:
                self.outFiles[File]["filtered"].write(unicode('</channel>'))
                self.outFiles[File]["filtered"].close()
            except KeyError:
                pass
    
    def __getRelevantWords(self, word):
        relevantWords = [word+" ", word + ".", word + "<", word + "!", word + "?", word + ","]
        return relevantWords
    
    def __findWord(self, words, tweet):
        for word in self.allWords[words]:
            relevantWords = self.__getRelevantWords(word)
            for relevantWord in relevantWords:
                if (relevantWord.lower()) in (tweet.lower() + "<"):
                    #print words
                    return 1
        return 0
    
    def __writeTweet(self, tweet):
        
        try:
            text = tweet[0]['text']
        except KeyError:
            return {"text": ""}
        
        fileOut = ""
        for words in self.allWords:
            if self.__findWord(words, tweet[0]['text']) == 1:
                fileOut = words
                break
                #print self.allWords
                #if words == "track_DE_WORD":
                #    exit(0)
            
        if fileOut == "":
            return {"text": ""}
        
        self.lang = True
        self.score = self.clasificator.classify(tweet[0]['text'], tweet[0]['user']['lang'])
        
        if tweet[0]['user']['lang'] == "en":
            self.MinScore = 0.2
        elif tweet[0]['user']['lang'] == "de":
            self.MinScore = 0.9
        else:
            self.lang = False
        
        tweetString = u""
        tweetString = tweetString + unicode('    <item section="Twitter">\n')

        try:
            if fileOut == "track_OlympicGames":
                tweetString = tweetString + unicode("        <guid>london2012:"+str(tweet[0]['id_str'])+"</guid>\n")
            else:
                tweetString = tweetString + unicode("        <guid>tw:"+str(tweet[0]['id_str'])+"</guid>\n")
        except KeyError:
            return {"text": ""}

        tweetString = tweetString + unicode("        <section>Twitter</section>\n")
        tweetString = tweetString + unicode("        <timestamp>"+self.now_dateTime()+"</timestamp>\n")
        tweetString = tweetString + unicode("        <publisher_type>TWEET</publisher_type>\n")
        tweetString = tweetString + unicode("        <source>twitter.com</source>\n")
        tweetString = tweetString + unicode("        <lang>"+tweet[0]['user']['lang']+"</lang>\n")
        tweetString = tweetString + unicode("        <link>http://twitter.com/"+tweet[0]['user']['screen_name'].encode("utf-8")+"/status/"+str(tweet[0]['id']).encode("utf-8")+"</link>\n")
        try:
            date = tweet[0]['created_at']
            date1 = re.search("\+.* ", date)
            date = date.replace(date1.group(), "")
            tweetString = tweetString +  self.make_ISOdate(date)
        except ValueError:
            tweetString = tweetString + unicode("        <pubDate>"+self.now_dateTime()+"</pubDate>\n")
        tweetString = tweetString +  unicode("        <text>"+tweet[0]['text']+"</text>\n")
        tweetString = tweetString +  unicode("        <author>\n")
        tweetString = tweetString +  unicode("            <name>"+tweet[0]['user']['screen_name']+"</name>\n")
        tweetString = tweetString +  unicode("            <id>"+str(tweet[0]['user']['id'])+"</id>\n")
        if tweet[0]['user']['location'] == "" or tweet[0]['user']['location'] == None:
            tweetString = tweetString +  unicode("            <location />\n")
        else:
            location = "            <location>"+tweet[0]['user']['location']+"</location>\n"
            tweetString = tweetString +  unicode(location)
        if tweet[0]['user']['description'] == "" or tweet[0]['user']['description'] == None:
            tweetString = tweetString +  unicode("            <description />\n")
        else:
            description = "            <description>"+tweet[0]['user']['description']+"</description>\n"
            tweetString = tweetString +  unicode(description)
        tweetString = tweetString +  unicode("            <occupation />\n")
        tweetString = tweetString +  unicode("        </author>\n")
        if tweet[0]['coordinates'] != None:
            tweetString = tweetString +  unicode('        <georss lat="'+str(tweet[0]['coordinates']['coordinates'][1])+'" lon="'+str(tweet[0]['coordinates']['coordinates'][0])+'"></georss>\n')
        else:
            tweetString = tweetString +  unicode("        <georss />\n")
        tweetString = tweetString +  unicode("        <html_meta>\n")
        tweetString = tweetString +  unicode("            <description />\n")
        tweetString = tweetString +  unicode("            <keywords />\n")
        tweetString = tweetString +  unicode("        </html_meta>\n")
        tweetString = tweetString +  unicode("    </item>\n")
        
        
        return {"text": tweetString, "fileOut": fileOut}
    
    def __createDocument(self, fileIn):
        fileIn = codecs.open(fileIn,"r", "utf-8")
        
        for riadok in fileIn:
            reg1 = re.findall("{",riadok)
            reg2 = re.findall("}",riadok)
            riadok = riadok.replace("&", saxutils.escape("&"))
            if (reg1.count("{") == reg2.count("}")) and (reg1.count("{") != 0):
                tweet =  json.loads("["+riadok+"]")
                result = self.__writeTweet(tweet)
                if result["text"] != "":
                    self.outFiles[result["fileOut"]]["all"].write(result["text"])
                    if result["fileOut"] == "track_all_DE_EN":
                        if self.lang == True:
                            if self.score < 0:
                                self.outFiles[result["fileOut"]]["filtered"].write(result["text"])
                            elif self.score > self.MinScore:
                                self.outFiles[result["fileOut"]]["filtered"].write(result["text"])

if __name__ == "__main__":
    
    fileIn = argv[1]
    fileOut = argv[2]
    fileOutFiltered = argv[3]
    
    tweetDocument = createTweetDocument(fileIn, fileOut, fileOutFiltered)
    
    os.remove(fileIn)
    
    
