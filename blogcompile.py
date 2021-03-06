#!/usr/bin/python3

import sys
import re
import os
import shutil
import codecs
import datetime

import docutils.core
from mako.lookup import TemplateLookup

# TODO: Avoid using exec().
# TODO: Move this logic into __main__ section or function.
SITE_PARAMS = {}
with open("config.py") as f:
    exec(f.read(), SITE_PARAMS)

# TODO: Move these paths to config file.
DOC_SOURCE_DIR = os.path.abspath("content")
HTML_SOURCE_DIR = os.path.abspath("htmlsource")
OUTPUT_DIR = os.path.abspath("output")

# TODO: Move some of these to config files, as appropriate.
TIMEZONE = "EST"
VERBOSE_DATE_FORMAT = "%A, %B %-d, %Y"
VERBOSE_DATETIME_FORMAT = VERBOSE_DATE_FORMAT+", %-I:%M %p"
TERSE_DATE_FORMAT = "%-m/%-d/%Y"
RSS_DATETIME_FORMAT = "%a, %d %b %Y %T {0}".format(TIMEZONE)

DATETIME_PARSE_FORMAT = VERBOSE_DATETIME_FORMAT.replace("%-", "%")+" %Z"

TRIM_EXTENSIONS_REGEX = re.compile(r"(.*?)\..*")
POSTED_DATETIME_REGEX = re.compile(r":Date:(.*?)\r?\n")

TEMPLATE_LOOKUP = TemplateLookup(
    directories=["templatescraps", "doctemplates", "htmlsource"])


def list_all_dir_contents(base_dir_path):
    """Generator iterating through all filenames (as relative paths under a
    given directory).
    """
    for dir_path, _, filenames in os.walk(base_dir_path):
        for filename in filenames:
            yield os.path.relpath(
                os.path.join(dir_path, filename), base_dir_path)


class DocData(object):
    """Class representing a document (blog post or page) loaded from a
    reStructuredText source.

    The instance of DocData will have as attributes all "parts" provided
    by the docutils HTML writer, as documented here:
    http://docutils.sourceforge.net/docs/api/publisher.html

    The following attributes are also accessible:
        doc_type            The document type (e.g. "page" or "blogpost") as
                            dictated by source file extension.
        guid                The document's unique identifier (stub), as
                            dictated by the first part of the filename (before
                            extension.)
        output_filename     The filename where the output file will end up.
        output_path         Relative path to the documents output location
                            (including filename).
        original_path       Path to the outputted RST source (when the config
                            setting copy_rst is True.
        teaser              Same as the RST document's subtitle.
        dated               True if the document has a date attribute.
        posted_datetime     Python datetime of post date.
        posted_date_terse   String with post date in "terse" format.
        posted_date_verbose String with post date in "verbose" format.
        posted_rss_datetime String with post date/time in RSS-friendly format.
    """
    def __init__(self, rst_string, doc_type, guid, output_filename,
                 output_path, original_path=None):
        """Create a DocData from a string of reStructuredText input data.

        Arguments:
            rst_string      Raw input data in reStructuredText format.
            doc_type        The document type ("blogpost" or "page")
                            as specified by input file extension.
            guid            The document's unique ID (stub), usually the base
                            filename (the part before the extension).
            output_filename The filename where the generated HTML will end up.
            output_path     The relative path to the document's output location
                            (including filename).
            original_path   The path where a copy of the original source
                            will be placed. (Default: None)
        """
        self.doc_type = doc_type
        self.guid = guid
        self.output_filename = output_filename
        self.output_path = output_path
        self.original_path = original_path

        self.__dict__.update(
            docutils.core.publish_parts(rst_string, writer_name="html"))

        posted_datetime_match = POSTED_DATETIME_REGEX.search(rst_string)
        if posted_datetime_match:
            posted_datetime_verbose = posted_datetime_match.group(1).strip()
            self.posted_datetime = datetime.datetime.strptime(
                posted_datetime_verbose, DATETIME_PARSE_FORMAT)
            self.posted_date_terse = self.posted_datetime.strftime(
                TERSE_DATE_FORMAT)
            self.posted_date_verbose = self.posted_datetime.strftime(
                VERBOSE_DATE_FORMAT)
            self.posted_rss_datetime = self.posted_datetime.strftime(
                RSS_DATETIME_FORMAT)
            self.dated = True
        else:
            self.dated = False

        self.teaser = self.subtitle

    def __cmp__(self, other):
        """Order with other DocDatas by date. (Earlier dates are "less than"
        later dates.)
        """
        return cmp(self.posted_datetime, other.posted_datetime)

    def __repr__(self):
        return "<{0}: {1}>".format(self.doc_type, self.output_path)


def write_to_file(path, data):
    """Write data to a file with UTF-8 encoding, first creating any necessary
    directories.

    Arguments:
        path    Full path to the file to be written.
        data    Data to be written.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with codecs.open(path, mode='w', encoding="utf-8") as f:
        f.write(data)
    print("Wrote to {0}.".format(path))


def build_site(remote):
    """Builds the website, reading reStructuredText source files and outputting
    HTML. The remote argument specifies whether to generate version for local
    testing or online deployment.
    """
    if remote:
        SITE_PARAMS["root_url"] = SITE_PARAMS["remote_url"]
    else:
        SITE_PARAMS["root_url"] = SITE_PARAMS["local_url"]
    SITE_PARAMS["remote"] = remote
    print("Building site with root URL {0}".format(SITE_PARAMS["root_url"]))

    print("Processing {0}...".format(DOC_SOURCE_DIR))
    docs = []
    for file_path in list_all_dir_contents(DOC_SOURCE_DIR):
        if not file_path.endswith("~"):
            relative_location, filename = os.path.split(file_path)
            guid, extension = os.path.splitext(filename)
            output_filename = guid+".html"
            extension = extension[1:]  # Trim the leading dot.
            try:
                template = TEMPLATE_LOOKUP.get_template(extension+".mako")
            except:
                print('Template not found for "{0}". Copying {1}...'.format(
                    extension, file_path))
                shutil.copy(
                    os.path.join(DOC_SOURCE_DIR, file_path),
                    os.path.join(OUTPUT_DIR, file_path))
            else:
                rst_output_path = os.path.join(
                    OUTPUT_DIR, relative_location, guid+".rst")
                if SITE_PARAMS["copy_rst"]:
                    shutil.copy(
                        os.path.join(DOC_SOURCE_DIR, file_path),
                        rst_output_path)
                new_path = os.path.join(relative_location, output_filename)
                with codecs.open(
                        os.path.join(DOC_SOURCE_DIR, file_path),
                        encoding="utf-8") as f:
                    rst_string = f.read()
                print("Generating HTML for {0}...".format(file_path))
                doc_data = DocData(
                    rst_string, extension, guid, output_filename, new_path,
                    rst_output_path)
                docs.append(doc_data)

    blog_posts = [
        doc for doc in docs if doc.doc_type == "blogpost" and doc.dated]
    blog_posts.sort(reverse=True)

    for doc in docs:
        template = TEMPLATE_LOOKUP.get_template(doc.doc_type+".mako")
        if doc.guid.startswith("test"):
            print(doc.body)
        print("Rendering {0}...".format(doc.output_path))
        html = template.render_unicode(
            doc=doc, blog_posts=blog_posts, **SITE_PARAMS)
        if doc.guid.startswith("test"):
            print(html)
        write_to_file(os.path.join(OUTPUT_DIR, doc.output_path), html)

    print("Processing {0}...".format(HTML_SOURCE_DIR))
    for file_path in list_all_dir_contents(HTML_SOURCE_DIR):
        relative_location, filename = os.path.split(file_path)
        output_filename, extension = os.path.splitext(filename)
        if extension == ".mako":
            template = TEMPLATE_LOOKUP.get_template(file_path)
            print("Rendering {0}...".format(file_path))
            html = template.render_unicode(
                blog_posts=blog_posts, **SITE_PARAMS)
            write_to_file(
                os.path.join(OUTPUT_DIR, relative_location, output_filename),
                html)
        elif not file_path.endswith("~"):
            print("Copying {0}...".format(file_path))
            shutil.copy(
                os.path.join(HTML_SOURCE_DIR, file_path),
                os.path.join(OUTPUT_DIR, file_path))
    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].strip().lower() == "remote":
        remote = True
    else:
        remote = False
    build_site(remote)
