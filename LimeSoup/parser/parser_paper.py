"""
ParserPaper is a class to parse HTML, XML papers from different publishers into
simples text. It can be used to feed a database.
This is the first version, I tried to separate things 
related to a specific publisher in the ParsePaper in order to help
to think how to reuse code in new publishers.
This class is not yet finished, just a security copy in GitHub.
"""

__author__ = "Tiago Botari"
__copyright__ = ""
__version__ = "1.0"
__maintainer__ = "Tiago Botari"
__email__ = "tiagobotari@gmail.com"
__date__ = "Feb 18 2018"

import itertools
import re

import bs4

import LimeSoup.parser.tools as tl


class ParserPaper:

    def __init__(self, raw_html, parser_type='lxml-xml', debugging=False):
        """
        :param raw_html:
        :param parser_type: can be 'html.parser', 'lxml', 'html5lib', 'lxml-xml'
        :param debugging: True or False
        """
        self.debugging = debugging
        self.soup = bs4.BeautifulSoup('{:}'.format(raw_html), parser_type)
        self.parser_type = parser_type
        self.title = []
        self.keywords = []
        self.data_sections = []
        self.headings_sections = []
        self.number_paragraphs_sections = []
        if debugging:
            self.soup_orig = self.soup

    @staticmethod
    def compile(pattern):
        return re.compile(pattern)

    @staticmethod
    def create_soup(html_xlm, parser_type='html.parser'):
        # parser_types = ['html.parser', 'lxml', 'html5lib', 'lxml-xml']
        return bs4.BeautifulSoup(html_xlm, parser_type)

    def save_soup_to_file(self, filename='soup.html', prettify=True):
        """
        Save the soup to a file to be analysed. This can be used during the
        debugging process.
        :param filename: str that contain the name of the file
        :param prettify: boolean to add spaces on children tags
        :return: None - just save a file on disk
        """
        with open(filename, 'w', encoding='utf-8') as fd_div:
            if prettify:
                fd_div.write(self.soup.prettify())
                fd_div.write('\n')
            else:
                # for item in self.soup:
                #     #fd_div.write(item)
                fd_div.write(str(self.soup))
                fd_div.write('\n')

    def extract_meta(self, *meta_names):
        """
        Extract metadata from <head> section. The <meta> tags will be removed.

        :param meta_names: List of names that should be extracted.
        :return: list of strings.
        """
        results = []
        for name in meta_names:
            for item in self.soup.find_all('meta', attrs={'name': name}):
                if item.has_attr('content'):
                    results.append(item['content'].strip())
                item.extract()
        return results

    def extract_first_meta(self, *meta_names):
        """
        Extract the first metadata from <head> section. The <meta> tag will be removed.

        :param meta_names: List of names that should be extracted.
        :return: a string containing the metadata value.
        """
        for name in meta_names:
            for item in self.soup.find_all('meta', attrs={'name': name}):
                if item.has_attr('content'):
                    value = item['content'].strip()
                    item.extract()
                    return value
        return None

    def get(self, rules):
        results = list()
        for rule in rules:
            finds = self.soup.find_all(**rule)
            for item in finds:
                text = tl.convert_to_text(item.get_text())
                results.append(text)
                item.extract()
        return results

    def get_keywords(self, rules):
        self.keywords = []
        for rule in rules:
            for keyword in self.soup.find_all(**rule):
                self.keywords.append(tl.convert_to_text(keyword.get_text()))
                keyword.extract()

    def remove_tags(self, rules):
        """
        Remove tags from bs4 soup object using a list of bs4 rules to find_all()
        :param rules: list() of dict() of rules of bs4 find_all()
        :return: None
        """
        for rule in rules:
            for s in self.soup.find_all(**rule):
                s.extract()

    def remove_first_tag(self, rules):
        """
        Remove the first found tag from bs4 soup object using
        a list of bs4 rules to find_all() Remove the first tag.
        :param rules: rules: list() of dict() of rules of bs4 find_all()
        :return: None
        """
        for rule in rules:
            for s in self.soup.find_all(limit=1, **rule):
                s.extract()
                return

    def create_tag_from_selection(self, rule, name_new_tag, name_section='Abstract'):
        """
        Create a tag inside a bs4 soup object from a selection using a rule.
        :param rule: a dict() of rules of bs4 find_all()
        :param name_new_tag: new tag's name
        :param name_section: create a <h2> tag with the name_section content
        :return: None
        """
        inside_tags = self.soup.find_all(**rule)
        section = self.soup.new_tag('section_{}'.format(name_new_tag))
        heading = self.soup.new_tag('h2')
        heading.append(name_section)
        section.append(heading)
        for tag in inside_tags:
            tag.wrap(section)
            section.append(tag)

    def create_tag_to_paragraphs_inside_tag(self, rule, name_new_tag, name_section='Abstract'):
        inside_tags_inter = self.soup.find_all(**rule)
        if len(inside_tags_inter) == 0:
            # self.save_soup_to_file('selction_found_nothing.html')
            # input('Section not created, selection found nothing')
            return 'Section not created, number of paragraphs equal zero.'
        inside_tags = inside_tags_inter[0].find_all(re.compile('(p|ol)|span'), recursive=False)
        # inside_tags = inside_tags_inter[0].find_all('p', recursive=False)
        # inside_tags_ol = inside_tags_inter[0].find_all('ol', recursive=False)
        # inside_tags = inside_tags_p + inside_tags_ol
        if len(inside_tags) == 0:
            # self.save_soup_to_file('selction_found_nothing.html')
            # input('Section not created, number of paragraphs equal zero.')
            return 'Section not created, number of paragraphs equal zero.'
        section = self.soup.new_tag('section_{}'.format(name_new_tag))
        heading = self.soup.new_tag('h2')
        heading.append(name_section)
        section.append(heading)
        for tag in inside_tags:
            tag_next_sibling = tag
            while True:
                tag_next_sibling = tag_next_sibling.next_sibling
                if tag_next_sibling is None:
                    break
                if tag_next_sibling.name is None:
                    continue
                else:
                    break
            tag.wrap(section)
            section.append(tag)
            if tag_next_sibling is None: break
            if 'section_h' in tag_next_sibling.name:
                break

    def operation_tag_remove_space(self, rules):
        for rule in rules:
            tags = self.soup.find_all(**rule)
            for tag in tags:
                if tag is not None:
                    if tag.name is not None:
                        tag.string = tag.get_text().rstrip()

    def create_tag_sections(self, rule=None):
        """
        Create the standard tags (<section_#>) using a rule to bs4 find_all()
        :param rule:
        :return:
        """
        tag_names = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        for tag_name in tag_names:
            tags = self.soup.find_all(tag_name)  # Tags corresponded to headings
            for each_tag in tags:
                inside_tags = [item for item in itertools.takewhile(
                    lambda t: t.name not in [each_tag.name, 'script'],
                    each_tag.next_siblings)]
                section = self.soup.new_tag('section_{}'.format(tag_name))
                each_tag.wrap(section)
                for tag in inside_tags:
                    section.append(tag)

    def rename_tag(self, rule, new_name='section_h4'):
        tags = self.soup.find_all(**rule)
        for tag in tags:
            tag.name = new_name

    def strip_tags(self, rules):
        """
        Replace some tag with the children tag.
        :param rules: list of rules for bs4 find_all()
        :return: None
        """
        tags = list()
        for rule in rules:
            for tag in self.soup.find_all(**rule):
                tag.replace_with_children()
                tags.append(tag.name)
        return tags

    def change_name_tag_sections(self):
        tags = self.soup.find_all(re.compile('^h[2-6]'))
        for each_tag in tags:
            each_tag.parent.name = 'section_{}'.format(each_tag.name)

    @property
    def raw_html(self):
        return self.soup.prettify()
