
import docutils.core
from mako.template import Template
from mako.lookup import TemplateLookup
import sys, re, datetime, os, itertools, shutil, codecs

SITEPARAMS = {}
execfile("config.py",SITEPARAMS)

DOCSOURCE_DIR = os.path.abspath("docsource")
HTMLSOURCE_DIR = os.path.abspath("htmlsource")
OUTPUT_DIR = os.path.abspath("output")

TIMEZONE = "EST"
VERBOSE_DATE_FORMAT = "%A, %B %-d, %Y"
VERBOSE_DATETIME_FORMAT = VERBOSE_DATE_FORMAT+", %-I:%M %p"
TERSE_DATE_FORMAT = "%-m/%-d/%Y"
RSS_DATETIME_FORMAT = "%a, %d %b %Y %T {0}".format(TIMEZONE)

DATETIME_PARSE_FORMAT = VERBOSE_DATETIME_FORMAT.replace("%-","%")+" %Z"

TRIMEXTENSIONS_REGEX = re.compile(r"(.*?)\..*")
POSTEDDATETIME_REGEX = re.compile(r":Date:(.*?)\r?\n")

TEMPLATE_LOOKUP = TemplateLookup(directories=["templatescraps","doctemplates","htmlsource"])


def listAllDirContents(baseDirPath):
    for dirPath, _, filenames in os.walk(baseDirPath):
        for filename in filenames:
            yield os.path.relpath(os.path.join(dirPath, filename),baseDirPath)

class DocData(object):
    def __init__(self,rstString,docType,guid,outputFilename,outputPath,originalPath=None):
        self.docType = docType
        self.guid = guid
        self.outputFilename = outputFilename
        self.outputPath = outputPath
        self.originalPath = originalPath
        
        self.__dict__.update(docutils.core.publish_parts(rstString,writer_name="html"))
        
        postedDateTimeMatch = POSTEDDATETIME_REGEX.search(rstString)
        if postedDateTimeMatch:
            postedDateTimeVerbose = postedDateTimeMatch.group(1).strip()
            self.postedDateTime = datetime.datetime.strptime(postedDateTimeVerbose,DATETIME_PARSE_FORMAT)
            self.postedDateTerse = self.postedDateTime.strftime(TERSE_DATE_FORMAT)
            self.postedDateVerbose = self.postedDateTime.strftime(VERBOSE_DATE_FORMAT)
            self.postedRssDateTime = self.postedDateTime.strftime(RSS_DATETIME_FORMAT)
            self.dated = True
        else:
            self.dated = False
        
        self.teaser = self.subtitle
    
    def __cmp__(self,other):
        return cmp(self.postedDateTime,other.postedDateTime)
    def __repr__(self):
        return "<{0}: {1}>".format(self.docType,self.outputPath)

def writeToFile(path,data):
    with codecs.open(path,mode='w',encoding="utf-8") as f:
        f.write(data)
    print "Wrote to {0}.".format(path)


def buildSite(remote):
    if remote:
        SITEPARAMS["rootUrl"] = SITEPARAMS["remoteUrl"]
    else:
        SITEPARAMS["rootUrl"] = SITEPARAMS["localUrl"]
    SITEPARAMS["remote"] = remote
    print "Building site with root URL {0}".format(SITEPARAMS["rootUrl"])
    
    print "Processing {0}...".format(DOCSOURCE_DIR)
    docs = []
    for filePath in listAllDirContents(DOCSOURCE_DIR):
        if not filePath.endswith("~"):
            relativeLocation,filename = os.path.split(filePath)
            guid,extension = os.path.splitext(filename)
            outputFilename = guid+".html"
            extension = extension[1:] # Trim the leading dot.
            try:
                template = TEMPLATE_LOOKUP.get_template(extension+".mako")
            except:
                print 'Template not found for "{0}". Copying {1}...'.format(extension,filePath)
                shutil.copy(os.path.join(DOCSOURCE_DIR,filePath),os.path.join(OUTPUT_DIR,filePath))
            else:
                rstOutputPath = os.path.join(OUTPUT_DIR,relativeLocation,guid+".rst")
                if SITEPARAMS["copyRst"]:
                  shutil.copy(os.path.join(DOCSOURCE_DIR,filePath),rstOutputPath)
                newPath = os.path.join(relativeLocation,outputFilename)
                with codecs.open(os.path.join(DOCSOURCE_DIR,filePath),encoding="utf-8") as f:
                    rstString = f.read()
                print "Generating HTML for {0}...".format(filePath)
                docData = DocData(rstString,extension,guid,outputFilename,newPath,rstOutputPath)
                docs.append(docData)
    
    blogPosts = [doc for doc in docs if doc.docType == "blogpost" and doc.dated]
    blogPosts.sort(reverse=True)
    
    for doc in docs:
        template = TEMPLATE_LOOKUP.get_template(doc.docType+".mako")
        if doc.guid.startswith("test"):
            print doc.body
        print "Rendering {0}...".format(doc.outputPath)
        html = template.render_unicode(doc=doc,blogPosts=blogPosts,**SITEPARAMS)
        if doc.guid.startswith("test"):
            print html
        writeToFile(os.path.join(OUTPUT_DIR,doc.outputPath),html)
    
    
    print "Processing {0}...".format(HTMLSOURCE_DIR)
    for filePath in listAllDirContents(HTMLSOURCE_DIR):
        relativeLocation,filename = os.path.split(filePath)
        outputFilename,extension = os.path.splitext(filename)
        if extension == ".mako":
            template = TEMPLATE_LOOKUP.get_template(filePath)
            print "Rendering {0}...".format(filePath)
            html = template.render_unicode(blogPosts=blogPosts,**SITEPARAMS)
            writeToFile(os.path.join(OUTPUT_DIR,relativeLocation,outputFilename),html)
        elif not filePath.endswith("~"):
            print "Copying {0}...".format(filePath)
            shutil.copy(os.path.join(HTMLSOURCE_DIR,filePath),os.path.join(OUTPUT_DIR,filePath))
    print "Done!"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].strip().lower() == "remote":
        remote = True
    else:
        remote = False
    buildSite(remote)

