
import os
import codecs

def getAllWords():
    words = []
    for filename in os.listdir("./track_files/"):
        File = codecs.open("./track_files/" + filename, "r", "utf-8")
        for line in File:
            line = line.replace("track=", "")
            word = ""
            for character in line:
                if character == ",":
                    words.append(word)
                    word = ""
                    continue
                word = word + character
            words.append(word)
                
    return words
        
                
def createOneTrackFile(allWords):
    File = codecs.open("allKeywords", "w", "utf-8")
    File.write("track=")
    i = 1
    for word in allWords:
        if i == 1:
            i = 2
            File.write(word)
        else:
            File.write("," + word)
        
if __name__ == "__main__":
    allWords = getAllWords()
    createOneTrackFile(allWords)