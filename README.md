PubMed2CUI
=========
Parse xml data of PubMed articles; process the text (article title, abstract, keywords) with [QuickUMLS](https://github.com/Georgetown-IR-Lab/QuickUMLS) to get CUI's.

## Contents
- **parse_pubmed_xml.py** contains the class for parsing the PubMed xml data
- **explore_data.ipynb** shows a parsing example on a couple of files (the xml files can be found in the `data` folder)
- **quickUMLS.ipynb** shows how to run QuickUMLS on the output of the parsing

## Requirements
1) To run QuickUMLS, you will need to obtain a license from the National Library of Medicine and download all UMLS files. See instructions and links [here](https://github.com/Georgetown-IR-Lab/QuickUMLS). In the **quickUMLS.ipynb** notebook, it is assumed that a folder called `quickUMLS_eng` is located in `data`.
2) It is recommended to install a conda environment using the **environment.yml** file and the following additional steps:

```
# create and activate the environment
conda env create -f environment.yml
conda activate aihealth_lab

# create an ipykernel (to run the notebooks)
python -m ipykernel install --user --name aihealth_lab --display-name "aihealth_lab"

# download spaCy English model (required for QuickUMLS)
python -m spacy download en
```
