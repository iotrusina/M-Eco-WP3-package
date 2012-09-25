import logging
import pickle

class HumanClassification:
    'Class ensures that all human input wont be lost after changing for instance word tokenization.'
    def __init__(self, pickle_filename):
        self._logger = logging.getLogger()
	self.filename = pickle_filename + '.pickle'
	self.classification = {}

    def load(self):
	try:
	    filehandler = open(self.filename,'rb')
	except IOError:
	    self._logger.warning('Pickle file ' + self.filename + ' does not exist, no previous classifications loaded')
	    return
	self.classification = pickle.load(filehandler)

    def store(self):
	filehandler = open(self.filename, 'wb')
	pickle.dump(self.classification, filehandler)

    def to_xml(self, db, filename, language=None):
        if language:
            self._logger.info('Generating human input XML to file: ' + filename + '_' + language + '.xml ...')
            f = open(filename + '_' + language + '.xml', 'w')
        else:
            self._logger.info('Generating human input XML to file: ' + filename + '.xml ...')
            f = open(filename + '.xml', 'w')
        print >> f, '<?xml version="1.0" encoding="UTF-8"?>'
        print >> f, '<human_input>'
        for entry_id in self.classification:
            if language:
                if list(self.classification[entry_id])[2] == language:
                    print >> f, '   <entry classification="' + str(list(self.classification[entry_id])[0]) + '" guid="' + str(list(self.classification[entry_id])[1]) + '" language="' + list(self.classification[entry_id])[3] + '" id="' + str(entry_id) + '">' + list(self.classification[entry_id])[2] + '</entry>'
            else:
                print >> f, '   <entry classification="' + str(list(self.classification[entry_id])[0]) + '" guid="' + str(list(self.classification[entry_id])[1]) + '" language="' + list(self.classification[entry_id])[3] + '" id="' + str(entry_id) + '">' + list(self.classification[entry_id])[2] + '</entry>'
        print >> f, '</human_input>'
        f.close()

    def get_positively_classified_count(self, language):
        count = 0
        for id in self.classification:
            tmp = list(self.classification[id])
            if tmp[0] == True:
                if tmp[3] == language:
                    count += 1
        return count

    def get_negatively_classified_count(self, language):
        count = 0
        for id in self.classification:
            tmp = list(self.classification[id])
            if tmp[0] == False:
                if tmp[3] == language:
                    count += 1
        return count