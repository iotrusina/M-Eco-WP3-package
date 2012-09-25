#!/usr/local/bin/python2.5

from src.connection import Connection
from src.entry import Entry
from src.worddictionary import WordDictionary
from src.humanclassification import HumanClassification
from src.tests import Tests
from math import sqrt
import logging
import pickle
import timeit
import time

class Classifier:
    '''Class using for classification of tweets. Use classify() method for classification, train() method for training of bayesian filter.'''
    MAX_TOKEN_SIZE = 6 # defines word count in dictionary tuples
    HUMAN_RATING_PROBABILITY = 0.99
    def __init__(self, low=0.5, high=0.5):
        # classification thresholds
        self._low = float(low)
        self._high = float(high)
        # add and setup logger
        self._logger = logging.getLogger()
        logging.basicConfig(level=logging.DEBUG)
        # db connection
	self.db = Connection()
	# load info about allready classified entries
        self._logger.info('Loading Allready classified entries...')
	self.human = HumanClassification('/mnt/minerva1/nlp/projects/twitter_classification/TwitterClassifier/pickles/HumanClassification')
	self.human.load()
	# load database of words
        self._logger.info('Loading word dictionary...')
	self.word_dict = WordDictionary('/mnt/minerva1/nlp/projects/twitter_classification/TwitterClassifier/pickles/WordDictionary')
	self.word_dict.load()
        # timer
        self._timer = timeit.Timer()

    def _add_classification(self, entry, classification):
        'Add each token to word dictionary for futher classification.'
        language = entry.get_language()
	for i in xrange(1, self.MAX_TOKEN_SIZE + 1):
            # for each token add to word dictionary
	    for token in entry.get_token(i):
                self.word_dict.words.setdefault(language, {}).setdefault(token, {'count':0, 'weight':0})['count'] += 1
                if classification:
                    self.word_dict.words[language][token]['weight'] += self.HUMAN_RATING_PROBABILITY
                else:
                    self.word_dict.words[language][token]['weight'] += (1 - self.HUMAN_RATING_PROBABILITY)

    def _add_to_human_classification(self, entry, classification):
        'Adds classified text to human classification. Stores classification, text and language of each text.'
	self.human.classification[entry.get_id()] = (classification, entry.get_guid(), entry.get_original_entry(), entry.get_language())
	if classification is None:
	    return
	self._add_classification(entry, classification)

    def train(self, language, count=None, offset=0):
	'Given the language and optionaly count or offset shows dialog for realning'
	self.db.connect(user='meco', database='meco', host='localhost', port=5432)
	try:
	    for entry in self.db.entries(language=language, entry_count=10000, entry_offset=offset):
                # when entry was allready processed apply and skip
		if entry.id in self.human.classification:
		    continue
		# ask whether entry is relevant
                automatic_classification = self.classify(entry.original_entry, language)
		print 'Original entry(' + str(entry.id) + '): \n"'+ entry.original_entry + '"\n automatic classification = ' + str(automatic_classification)
                if automatic_classification < self._low:
                    auto = 'n'
                    continue # TODO:odstranit
                elif automatic_classification >= self._high:
                    auto = 'y'
                else:
                    auto = '?'

		answer = raw_input('Is this entry relevant? (y/n/?/END))[' + auto + ']: ')
		if answer == 'y':
		    self._add_to_human_classification(entry, True)
		elif answer == 'n':
		    self._add_to_human_classification(entry, False)
		elif answer == '?':
		    continue
		elif answer == 'END':
		    break
		else:
                    if automatic_classification < self._low:
                        self._add_to_human_classification(entry, False)
                    elif automatic_classification >= self._high:
                        self._add_to_human_classification(entry, True)
                    else:
                        continue

		print 'after classification: ' + str(self.classify(entry.original_entry, language))
	except KeyboardInterrupt:
	    pass
	# store human input and word_dictionary
	self.human.store()
	self.word_dict.store()

    def manual_train(self, text, language, classification):
        'Method for manual training of bayesian filter.'
        e = Entry(None, text, language)
        if classification is True:
            self._add_classification(e, True)
        if classification is False:
            self._add_classification(e, False)
        self.word_dict.store()
        
    def train_from_human_classification(self, filename, language):
        'Method for training current bayesian filter from external human classification file'
	filehandler = open(filename, 'rb')
        content = pickle.load(filehandler)

        for entry_id in content:
            e = Entry(entry_id, list(content[entry_id])[1], list(content[entry_id])[2])
            if e.get_language() == language:
                self._add_to_human_classification(e, list(content[entry_id])[0])
        self.human.store()
        self.word_dict.store()

    def regenerate_word_dict(self):
        'regenerate word dictionary according to human_input.'
        print self.human.classification
        self.word_dict.words = {}
        # go through human classification and create new word dictionary using classification
        for entry_id in self.human.classification:
            e = Entry(entry_id, list(self.human.classification[entry_id])[1], list(self.human.classification[entry_id])[2])
            if list(self.human.classification[entry_id])[0] == True:
                self._add_classification(e, True)
            if list(self.human.classification[entry_id])[0] == False:
                self._add_classification(e, False)
        self.word_dict.store()

    def human_classify(self, output_pickle, language):
	'This method creates output_pickle file containing user defined classifications of entries. May be used for creating test data.'
	self.db.connect(user='meco', database='meco', host='localhost', port=5432)
	new_human_classify = HumanClassification(output_pickle)
	new_human_classify.load()
	try:
	    for entry in self.db.entries(language=language, entry_count=None, entry_offset=0):
		# when entry was allready processed skip
		if entry.id in new_human_classify.classification:
		    continue
		print 'Original entry: \n"'+ entry.original_entry + '"\n automatic classification = ' + str(self.classify(entry.original_entry, language))
                automatic_classification = self.classify(entry.original_entry, language)
		if automatic_classification < self._low:
                    auto = 'n'
                    continue # TODO: odstranit
                elif automatic_classification >= self._high:
                    auto = 'y'
                else:
                    auto = '?'
                answer = raw_input('Is this entry relevant? (y/n/?/END))['+ auto +']: ')
		if answer == 'y':
		    new_human_classify.classification[entry.id] = True
		elif answer == 'n':
		    new_human_classify.classification[entry.id] = False
		elif answer == 'END':
		    break
		else:
                    if automatic_classification < self._low:
                        new_human_classify.classification[entry.id] = False
                    elif automatic_classification >= self._high:
                        new_human_classify.classification[entry.id] = True
                    else:
                        new_human_classify.classification[entry.id] = None
                print 'Cassified count = ' + str(len(new_human_classify.classification))
	except KeyboardInterrupt:
	    pass
	new_human_classify.store()


    def classify(self, text, language):
	'''Given input text and language, method calculates probability of text being relevant to topic. @result probability that text is relevant'''
	input_entry = Entry(id=None, guid=None, entry=text, language=language)
	self.word_dict.words.setdefault(language, {})
	# for each token claculate probability of being relevant to topic
	# and calculate according to bayes theorem
	#
	#		  p1p2p3........pn		      a
	# P = ------------------------------------------ = -------
	#	p1p2p3........pn + (1-p1)(1-p2)...(1-pn)    a + b
	#
	a = 1.0
	b = 1.0
	for i in xrange(1, self.MAX_TOKEN_SIZE + 1):
	    for token in input_entry.get_token(i):
		if not token in self.word_dict.words[language]:
		    probability = 0.5
		else:
		    token_stats = self.word_dict.words[language][token]
		    probability = token_stats['weight'] / token_stats['count']
		a *= probability
		b *= 1 - probability

        if a + b == 0:
            return 0
        else:
            result = a / (a + b)
            if result == 0.5:
                return -1
            else:
                return a / (a + b)

    def _test_corelation(self, human_classified_pickle, language):
	'This method prints corelation between user defined input in human_classified_pickle and automatic classification.'
	#
	#		    covariance
	#		        |
	#		     C(X,Y)		          E(XY) - E(X)E(Y)
	# corelation = ------------------ = -------------------------------------------  , a = E(XY), b = E(X), c = E(Y), d,= E(X^2), e = E(Y^2)
	#		    d(X)d(Y)	    sqrt(E(X^2) - E(X)^2) sqrt(E(Y^2) - E(Y)^2)
	#		       |
	#	       standard deviations
	#
	# X - automatically calculated probabilities
	# Y - human input probabilities
	#
	human_classified = HumanClassification(human_classified_pickle)
	human_classified.load()
	entry_count = len(human_classified.classification)
	a = 0.0
	b = 0.0
	c = 0.0
	d = 0.0
	e = 0.0
	for entry_id in human_classified.classification:
	    processed_entry = self.db.get_entry_by_id(entry_id)
	    probability_auto = self.classify(processed_entry.original_entry, language)
	    if human_classified.classification[entry_id]:
		probability_human = self.HUMAN_RATING_PROBABILITY
	    else:
		probability_human = (1 - self.HUMAN_RATING_PROBABILITY)

	    a += probability_human * probability_auto
	    b += probability_auto
	    c += probability_human
	    d += probability_auto * probability_auto
	    e += probability_human * probability_human

	# E() values
	a /= entry_count
	b /= entry_count
	c /= entry_count
	d /= entry_count
	e /= entry_count

	return (a - (b * c)) / (sqrt(d - (b * b)) * sqrt(e - (c * c)))

    def _test_percents(self, human_classified_pickle, language):
	'This method returns ntuple containing (matches, false_positive, false_negative, unknown)'
	human_classified = HumanClassification(human_classified_pickle)
	human_classified.load()
	entry_count = len(human_classified.classification)
	true_positive = 0.0
        true_negative = 0.0
        matches = 0.0
	false_positive = 0.0
	false_negative = 0.0
	unknown = 0.0
	for entry_id in human_classified.classification:
	    processed_entry = self.db.get_entry_by_id(entry_id)
	    probability = self.classify(processed_entry.original_entry, language)
	    if probability < self._low:
		if not human_classified.classification[entry_id]:
		    matches += 1
                    true_negative += 1
		else:
		    false_negative += 1
	    elif probability >= self._high:
		if  human_classified.classification[entry_id]:
		    matches += 1
                    true_positive += 1
		else:
		    false_positive += 1
	    else:
		unknown += 1
	return (matches, true_positive, true_negative, false_positive, false_negative, unknown, entry_count)

    def run_tests(self, input_file, language):
	'Method for running tests on input file and get time elapsed for classification of one entry'
	self.db.connect(user='meco', database='meco', host='localhost', port=5432)
	tmp = HumanClassification(input_file)
	tmp.load()
	self._logger.info('Running tests...')
        tests = Tests()
        tests.set_test_len(len(tmp.classification))
        tests.set_train_len(len(self.human.classification))
        tests.set_train_positive_len(self.human.get_positively_classified_count(language))
        tests.set_train_negative_len(self.human.get_negatively_classified_count(language))
        self._logger.info('Calculating corelation...')
        tests.set_corelation(self._test_corelation(input_file, language))
        self._logger.info('Calculating percentage of classification accuracy...')
        tests.set_percents(self._test_percents(input_file, language))
        print tests


    def get_time(self):
        'Method for calculating time needed for one entry classification'
        self._logger.info('Downloading entries to run tests on...')
        i = 0
        imax = 1000
        entries = []
        for entry in self.db.entries(language='en', entry_count=imax):
            i += 1
            if i >= imax:
                break
            entries.append(entry.original_entry)


        self._logger.info('Masuring amount of entries to be calculated in 1sec')
        repetitions = 100
        result_avg = 0.0
        for i in xrange(0, repetitions):
            average = 0
            for j in xrange(0, imax - 1):
                start = time.time()
                self.classify(entries[j], 'en')
                average += time.time() - start
            average /= imax
            result_avg += average
        result_avg /= repetitions
        return 'Classifier is able to classify ' + str(round(1/result_avg, 2)) + ' entries in one second.'

    def export_to_xml(self, language, specification):
        'Method exports all data to xml files'
        self.word_dict.to_xml(filename='XML/word_dict', specification=specification)
        self.human.to_xml(self.db, 'XML/human_classification', language=language)

    def fix_old_human_classification(self, filename):
        'method converts old human classification file to new one inlcluding text of tweets'
	self.db.connect(user='meco', database='meco', host='localhost', port=5432)
        file = open(filename, 'rb')
        content = pickle.load(file)
        new_content = {}

        for entry_id in content:
            e = self.db.get_entry_by_id(entry_id)
            if e:
                new_content[entry_id] = (content[entry_id], e.original_entry, e.get_language())

        new_file = open(filename +'new', 'wb')
        pickle.dump(new_content, new_file)
        
    def fix_old_human_classification2(self, filename):
        'method converts old human classification file to new one inlcluding text of tweets'
	self.db.connect(user='meco', database='meco', host='localhost', port=5432)
        file = open(filename, 'rb')
        content = pickle.load(file)
        new_content = {}

        for entry_id in content:
            e = self.db.get_entry_by_id(entry_id)
            if e:
                new_content[entry_id] = (list(content[entry_id])[0], e.get_guid(), e.get_original_entry(), e.get_language())

        new_file = open(filename +'_new', 'wb')
        pickle.dump(new_content, new_file)

    def train_from_file(self, filename, language, classification):
        'method trains classifier from some file'
	file = open(filename, 'r')
	for line in file:
            e = Entry(None, None, line, language)
            self._add_to_human_classification(e, classification)
        self.human.store()
        self.word_dict.store()

