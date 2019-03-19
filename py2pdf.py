#!/usr/bin/env python3
'''
Converts Python source code to PDF

Based on code2pdf (see: https://pypi.org/project/Code2pdf/)
'''


import argparse
import logging
import os
import sys
from io import StringIO

# Uses this package to create PDF version
from xhtml2pdf import pisa

try:
    import pygments
    from pygments import lexers, formatters, styles
except ImportError as ex:
    logging.warning('\nCould not import the required "pygments" module:\n%s', ex)
    sys.exit(1)

__version__ = '1.0.0'


def logger(func):
    ''' Defines function for logging '''
    def log_wrap(self, ifile=None, ofile=None):
        logging.getLogger().name = "py2pdf> "
        logging.getLogger().setLevel(logging.INFO)
        func(self, ifile, ofile)
    return log_wrap


class Py2pdf:

    '''
    Converts a source file into a pdf with syntax highlighting.
    '''
    @logger
    def __init__(self, ifile=None, ofile=None, linewrap=99):
        if not ifile:
            raise Exception("input file is required")
        self.input_file = ifile
        self.pdf_file = ofile or "{}.pdf".format(ifile.split('.')[0])
        self.linewrap = linewrap

    def highlight_file(self, style='default'):
        '''
        Highlight the input file, and return HTML as a string.

        Uses same highlighting code as in: https://pypi.org/project/Code2pdf/,
        but makes sure that there is visible line break 
        '''
        try:
            lexer = lexers.get_lexer_for_filename(self.input_file)
        except pygments.util.ClassNotFound:
            # Try guessing the lexer (file type) later.
            lexer = None

        try:
            formatter = formatters.HtmlFormatter( # pylint: disable=no-member
                linenos=False,
                style=style,
                full=True)
        except pygments.util.ClassNotFound:
            logging.error("\nInvalid style name: %s\nExpecting one of:\n%s",
                          style,
                          "\n    ".join(sorted(styles.STYLE_MAP)))
            sys.exit(1)

        content = ''
        try:
            with open(self.input_file, "r") as f_input_file:
                lines = f_input_file.readlines()
                for line in lines:
                    # if line starts with space add another one
                    # as when regenerating code this space somehow disappears
                    if line[0] == ' ':
                        line = ' ' + line

                    # Makes sure that we wrap long lines
                    if len(line) > self.linewrap:
                        left = len(line)
                        take = self.linewrap - 1
                        while left > 0:
                            if len(line) > (self.linewrap - 1):
                                content += line[:take] + u'\u21a9' + '\n'
                            else:
                                content += line[:take]
                                break

                            left = max(len(line) - take, 0)
                            if left > 0:
                                line = u'\u21aa' + line[take:]
                                take = min((left + 1), (self.linewrap - 1))
                    else:
                        content += line
                try:
                    lexer = lexer or lexers.guess_lexer(content)
                except pygments.util.ClassNotFound:
                    # No lexer could be guessed.
                    lexer = lexers.get_lexer_by_name("text")
        except EnvironmentError as exread:
            logging.error("\nUnable to read file: %s\n%s", self.input_file, exread)
            sys.exit(2)

        return pygments.highlight(content, lexer, formatter)

    def init_print(self, style="default"):
        '''
        Generates PDF from HTML file
        '''
        html = self.highlight_file(style=style)
        result_pdf = open(self.pdf_file, "w+b")
        pisa.CreatePDF(StringIO(html),
                       dest=result_pdf,
                       encoding='utf-8',
                       default_css=open("./templates/default.css", "r").read())
        result_pdf.close()

        logging.info("PDF created at %s", self.pdf_file)


def get_output_file(inputname, outputname=None):
    """ If the output name is set, then return it.
        Otherwise, build an output name using the current directory,
        replacing the input name's extension.
    """
    if outputname:
        return outputname

    inputbase = os.path.split(inputname)[-1]
    outputbase = "{}.pdf".format(os.path.splitext(inputbase)[0])
    return os.path.join(os.getcwd(), outputbase)


def parse_arg():
    '''
    Parses command line arguments
    '''
    parser = argparse.ArgumentParser(
        description=(
            "Convert given Python source code into .pdf with syntax highlighting"))

    parser.add_argument(
        "filename",
        help="absolute path of the python file",
        type=str)
    parser.add_argument(
        "outputfile",
        help="absolute path of the output pdf file",
        nargs="?",
        type=str)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s v. {}".format(__version__))
    return parser.parse_args()


def main():
    '''
    Main entry point
    '''
    args = parse_arg()
    pdf_file = get_output_file(args.filename, args.outputfile)
    pdf = Py2pdf(args.filename, pdf_file)
    pdf.init_print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
