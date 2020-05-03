"""
A class for parsing and storing xml data of PubMed articles.

- The xml can be viewed under the 'Format' drop-down in the upper-left corner of an article webpage. This xml format is different from the MEDLINE XML format downloadable in bulk from PubMed's E-util interface (https://www.nlm.nih.gov/databases/download/pubmed_medline.html). To parse the MEDLINE XML, use other available libraries (e.g. https://github.com/titipata/pubmed_parser). This class is useful when you have only a few specific articles that you manually copy from the webpage and want to process.
"""


import pandas as pd
from lxml import etree
from pathlib import Path


class PubMedData(object):
    """
    A class for parsing and storing xml data of PubMed articles.

    Attributes:
    ----------
    xml_paths: dict
        xml paths to the various elements parsed
    pubinfo: pd DataFrame
        index pmid; columns [pub_date_year, pub_date_month, journal_name]
    text: pd DataFrame
        index pmid; columns [article_title, abstract_text, keywords]
    pubtype: pd DataFrame
        index pmid; columns [ui, publication_type]
    chems: pd DataFrame
        index pmid; columns [ui, chemicals]
    mesh: pd DataFrame
        index pmid; columns [ui, mesh_headings]

    Methods:
    -------
    CLASS
    from_dir: return PubMedData
        instantiate a PubMedData object by parsing xml files in a given directory
    parse_xml: return dict
        parse an xml file to return a dictionary with all extracted elements

    STATIC
    parse_abstract: return str
        convert an xml abstract element to a string
    """

    xml_paths = {
        'pmid': 'MedlineCitation/PMID',
        'pub_date_year': 'MedlineCitation/Article/Journal/JournalIssue/PubDate/Year',
        'pub_date_month': 'MedlineCitation/Article/Journal/JournalIssue/PubDate/Month',
        'journal_name': 'MedlineCitation/Article/Journal/Title',
        'article_title': 'MedlineCitation/Article/ArticleTitle',
        'abstract': 'MedlineCitation/Article/Abstract/AbstractText',
        'keywords': 'MedlineCitation/KeywordList/Keyword',
        'pubtype': 'MedlineCitation/Article/PublicationTypeList/PublicationType',
        'chems': 'MedlineCitation/ChemicalList/Chemical/NameOfSubstance',
        'mesh': 'MedlineCitation/MeshHeadingList/MeshHeading/DescriptorName',
    }


    def __init__(self, pubinfo, text, pubtype, chems, mesh):
        self.pubinfo = pubinfo
        self.text = text
        self.pubtype = pubtype
        self.chems = chems
        self.mesh = mesh


    @classmethod
    def from_dir(cls, path):
        pubinfo = dict()
        text = dict()
        pubtype = dict()
        chems = dict()
        mesh = dict()

        pubinfo_cols = ['pub_date_year', 'pub_date_month', 'journal_name']
        text_cols = ['article_title', 'abstract_text', 'keywords']

        path = Path(path)
        for filename in path.glob('*.xml'):
            data = cls.parse_xml(str(filename))
            key = data['pmid']
            pubinfo[key] = [data[col] for col in pubinfo_cols]
            text[key] = [data[col] for col in text_cols]
            pubtype[key] = data['publication_type']
            chems[key] = data['chemicals']
            mesh[key] = data['mesh_headings']

        def convert_to_df(dct, col):
            return pd.DataFrame(
                data=dct.values(),
                index=dct.keys(),
                columns=col,
            )

        pubinfo = convert_to_df(pubinfo, pubinfo_cols)
        text = convert_to_df(text, text_cols)

        def convert_to_df(dct, col):
            df = pd.DataFrame(dct).stack().reset_index(level=0).sort_index()
            df.columns = ['ui', col]
            return df

        pubtype = convert_to_df(pubtype, 'publication_type')
        chems = convert_to_df(chems, 'chemicals')
        mesh = convert_to_df(mesh, 'mesh_headings')

        return cls(pubinfo, text, pubtype, chems, mesh)


    @classmethod
    def parse_xml(cls, filename):
        tree = etree.parse(filename)
        root = tree.getroot()

        pmid = int(root.find(cls.xml_paths['pmid']).text)
        pub_date_year = root.find(cls.xml_paths['pub_date_year']).text
        pub_date_month = root.find(cls.xml_paths['pub_date_month']).text
        journal_name = root.find(cls.xml_paths['journal_name']).text
        article_title = root.find(cls.xml_paths['article_title']).text

        # abstract text
        els = root.findall(cls.xml_paths['abstract'])
        abstract_text = ' '.join([cls.parse_abstract(el) for el in els])

        # keywords
        els = root.findall(cls.xml_paths['keywords'])
        keywords = '; '.join([el.text for el in els])

        # publication type
        els = root.findall(cls.xml_paths['pubtype'])
        publication_type = {el.get('UI'): el.text for el in els}

        # chemicals
        els = root.findall(cls.xml_paths['chems'])
        chemicals = {el.get('UI'): el.text for el in els}

        # mesh headings
        els = root.findall(cls.xml_paths['mesh'])
        mesh_headings = {el.get('UI'): el.text for el in els}

        return {
            'pmid': pmid,
            'pub_date_year': pub_date_year,
            'pub_date_month': pub_date_month,
            'journal_name': journal_name,
            'article_title': article_title,
            'abstract_text': abstract_text if abstract_text else None,
            'keywords': keywords if keywords else None,
            'publication_type': publication_type if publication_type else None,
            'chemicals': chemicals if chemicals else None,
            'mesh_headings': mesh_headings if mesh_headings else None,
        }


    @staticmethod
    def parse_abstract(el):
        if el.text == None:
            el_text = str(etree.tostring(el))
            el_text = el_text.replace('<AbstractText>', '').replace('</AbstractText>', '').replace('<b>', '').replace('</b>', '').replace("b'", '')
            return el_text
        elif el.get('Label') == None:
            return el.text
        else:
            return el.get('Label') + ': ' + el.text
