import re
import PyPDF2
import glob
import spacy
from spacy.training.example import Example
paths = glob.glob("*.pdf")

def detect_matching_sentence(text):
    nlp = spacy.load('en_core_web_sm')
    matcher = spacy.matcher.Matcher(nlp.vocab)

    # Define the pattern to match quantities
    pattern = [{'LIKE_NUM': True}, {'IS_ALPHA': True, 'OP': '?'}, {'LOWER': {'IN': ['kg', 'kgs']}}]

    # Add the pattern to the matcher
    matcher.add('QUANTITY_PATTERN', [pattern])

    doc = nlp(text)
    matching_sentences = []

    for sent in doc.sents:
        matches = matcher(sent)
        if matches:
            for match_id, start, end in matches:
                matching_sentences.append(sent.text)
    
    # print(*matching_sentences, sep='\n\n')

    return matching_sentences


def extract_value(text, pattern, extra=None):
    if not extra:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    else:
        match = re.search(pattern, text, re.MULTILINE | extra)
    if match:
        value = match.group(0).strip()
        return value
    return None


def extract_data_from_pdf(reader):
    page_content = reader.pages[0].extract_text()
    page_content_2 = reader.pages[1].extract_text()

    pot_life = extract_value(page_content, r'Pot life\s+(.*)', re.IGNORECASE)
    mixed_density = extract_value(page_content, r'Mixed density\s+(.*)')
    tensile_strength = extract_value(page_content, r'Tensile strength\s+(.*)')
    color = extract_value(page_content, r'Colour\s+(.*)')
    adhesion_bonding = extract_value(page_content, r'Adhesion Bonding\s+(.*)')
    adhesion_line = re.search(r'Adhesion.*', page_content, re.MULTILINE)
    if adhesion_line:
        adhesion_bonding = adhesion_line.group(0).strip()
    water_vapour = extract_value(
        page_content, r'^(.*)\sWater\sVapour\s+(.*)hrs(.*)|Water\svapor\s+(.*)hrs(.*)')
    if water_vapour:
        water_vapour = water_vapour.split('\n')[-1]
    water_absorption = extract_value(page_content, r'Water Absorption\s+(.*)')
    adhesion_to_concrete = extract_value(
        page_content, r'Adhesion to concrete\s+(.*)')
    toxicity = extract_value(page_content, r'Toxicity\s+(.*)')
    static_crack = extract_value(
        page_content, r'^(.*)\s((Static crack)|(Bridges crack)|(Crack Bridging))\s+(.*)mm(.*)').split('\n')[-1]
    elongation_at_break = extract_value(
        page_content, r'Elongation at break\s+(.*)')
    flexibility = extract_value(page_content, r'Flexibility[^%]*%\s+(.*)')
    hardness = extract_value(page_content, r'Hardness\s+(.*)')
    packaging_content = detect_matching_sentence(page_content_2)

    data = {
        'Pot life': pot_life,
        'Mixed density': mixed_density,
        'Tensile strength': tensile_strength,
        'Color': color,
        'Adhesion bonding': adhesion_bonding,
        'Water vapour': water_vapour,
        'Water absorption': water_absorption,
        'Adhesion to concrete': adhesion_to_concrete,
        'Toxicity': toxicity,
        'Crack Bridging': static_crack,
        'Flexibility': flexibility,
        'Elongation at break': elongation_at_break,
        'Hardness': hardness,
        'Packaging': packaging_content[0]
    }

    return data

if __name__=="__main__":
    # Example usage
    pdf_file_path = paths[0]
    print(pdf_file_path)

    with open(pdf_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        data = extract_data_from_pdf(reader)

    print(*[f'{k}:\t\t{v}' for k,v in data.items()], sep='\n')
