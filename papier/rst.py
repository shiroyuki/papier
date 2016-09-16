""" ReStructureText services

    :Author: Juti Noppornpitak <jnopporn at shiroyuki.com>
    :Original: https://github.com/github/markup/blob/master/lib/github/commands/rest2html
    :Public Domain License: http://creativecommons.org/publicdomain/zero/1.0/

    This code is based on ``rest2html`` from GitHub and therefore it is belonged
    to the public domain. The big two differences are:

    * the main service of converting RST to HTML is reusable,
    * the code is primarily for Python 3.4 and 3.5.
"""
import codecs

from docutils import nodes
from docutils.parsers.rst import directives, roles
from docutils.parsers.rst.directives.body import CodeBlock
from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer, HTMLTranslator

SETTINGS = {
    'cloak_email_addresses'  : False,
    'file_insertion_enabled' : False,
    'raw_enabled'            : True,
    'strip_comments'         : True,
    'doctitle_xform'         : True,
    'sectsubtitle_xform'     : True,
    'initial_header_level'   : 2,
    'report_level'           : 5,
    'syntax_highlight'       : 'none',
    'math_output'            : 'latex',
    'field_name_limit'       : 50,
}


class GitHubHTMLTranslator(HTMLTranslator):
    # removes the <div class="document"> tag wrapped around docs
    # see also: http://bit.ly/1exfq2h (warning! sourceforge link.)
    def depart_document(self, node):
        HTMLTranslator.depart_document(self, node)
        self.html_body.pop(0)  # pop the starting <div> off
        self.html_body.pop()   # pop the ending </div> off

    # technique for visiting sections, without generating additional divs
    # see also: http://bit.ly/NHtyRx
    # the a is to support ::contents with ::sectnums: http://git.io/N1yC
    def visit_section(self, node):
        id_attribute = node.attributes['ids'][0]
        self.body.append('<a name="%s"></a>\n' % id_attribute)
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_literal_block(self, node):
        classes = node.attributes['classes']
        if len(classes) >= 2 and classes[0] == 'code':
            language = classes[1]
            del classes[:]
            self.body.append(self.starttag(node, 'pre', lang=language))
        else:
            self.body.append(self.starttag(node, 'pre'))

    # always wrap two-backtick rst inline literals in <code>, not <tt>
    # this also avoids the generation of superfluous <span> tags
    def visit_literal(self, node):
        self.body.append(self.starttag(node, 'code', suffix=''))

    def depart_literal(self, node):
        self.body.append('</code>')

    def visit_table(self, node):
        classes = ' '.join(['docutils', self.settings.table_style]).strip()
        self.body.append(
            self.starttag(node, 'table', CLASS=classes))

    def depart_table(self, node):
        self.body.append('</table>\n')

    def depart_image(self, node):
        uri = node['uri']
        ext = os.path.splitext(uri)[1].lower()
        # we need to swap RST's use of `object` with `img` tags
        # see http://git.io/5me3dA
        if ext == ".svg":
            # preserve essential attributes
            atts = {}
            for attribute, value in node.attributes.items():
                # we have no time for empty values
                if value:
                    if attribute == "uri":
                        atts['src'] = value
                    else:
                        atts[attribute] = value

            # toss off `object` tag
            self.body.pop()
        # add on `img` with attributes
            self.body.append(self.starttag(node, 'img', **atts))
        self.body.append(self.context.pop())


def kbd(name, rawtext, text, lineno, inliner, options=None, content=None):
    return [nodes.raw('', '<kbd>%s</kbd>' % text, format='html')], []


class DoctestDirective(CodeBlock):
    """ Render Sphinx 'doctest:: [group]' blocks as 'code:: python'

        Discard any doctest group argument, render contents as python code
    """
    def __init__(self, *args, **kwargs):
        super(DoctestDirective, self).__init__(*args, **kwargs)

        self.arguments = ['python']


class RSTService(object):
    def __init__(self):
        self.writer = Writer()
        self.writer.translator_class = GitHubHTMLTranslator

        roles.register_canonical_role('kbd', kbd)

        # Render source code in Sphinx doctest blocks
        directives.register_directive('doctest', DoctestDirective)

    def to_html(self, text : str):
        parts = publish_parts(
            text,
            writer = self.writer,
            settings_overrides = SETTINGS
        )

        if 'html_body' in parts:
            html = parts['html_body']

            # publish_parts() in python 2.x return dict values as Unicode type
            # in py3k Unicode is unavailable and values are of str type
            if isinstance(html, str):
                return html

            return html.encode('utf-8')

        return ''
