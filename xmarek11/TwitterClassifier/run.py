#!/usr/local/bin/python2.5

from optparse import OptionParser
from classifier import Classifier

parser = OptionParser()
# classifier details
parser.add_option("-l", "--language", default='en', dest="language", help="Specify LANGUAGE, if not specified, default is 'en'", metavar="LANGUAGE")
parser.add_option("-a", "--low", default='0.4', dest="low", help="low threshold for classifier", metavar="LOW")
parser.add_option("-b", "--high", default='0.6', dest="high", help="high threshold for classifier", metavar="HIGH")

parser.add_option("-c", "--human-classify", dest="human_classify", help="Allows user to classify tweets and put them into <File>", metavar="FILE")
parser.add_option("-t", "--train", action="store_true", dest="train", default=False, help="Train Bayesian network")
parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="Export wordlist to XML")
parser.add_option("-s", "--specification", default=None, dest="specification", help="Set specification variable - for exporting XML containing this specification.", metavar="SPECIFICATION")
parser.add_option("-r", "--run-tests", dest="tests", help="Run tests on pickled <File> with classified tweets", metavar="FILE")
parser.add_option("-f", "--fix_hc", dest="fix", help="Fix old human classification", metavar="FILE")
parser.add_option("-m", "--m", dest="merge", help="Merge Human classification files", metavar="FILE")


(options, args) = parser.parse_args()
cl = Classifier(options.low, options.high)

# training Bayesian network
if options.train:
    cl.train(language=options.language)
if options.human_classify:
    cl.human_classify(options.human_classify, options.language)
if options.tests:
    cl.run_tests(options.tests, options.language)
if options.fix:
    cl.fix_old_human_classification2(options.fix)
if options.merge:
    cl.train_from_human_classification(options.merge, options.language)
if options.export:
    cl.export_to_xml(language=options.language, specification=options.specification)
