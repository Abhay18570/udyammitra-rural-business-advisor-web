"""Transparent first-pass text intent rules, v1. No probabilities or LLMs.

Exact alias queries can use primary categories. More specific/unknown queries
need every meaningful query token in the name; partial overlap is only related.
Repair/production/rental intent never becomes direct from a retail category.
"""
import re

VERSION = 'business-query-v1'


def normalize_query(value):
    return ' '.join(value.split())


def words(value):
    return set(re.findall(r'\w+', value.casefold(), re.UNICODE))


# aliases, direct primary types, related types
INTENTS = (
    (('kirana', 'kirana store', 'general store', 'grocery shop', 'grocery store', 'किराना दुकान', 'किराणा दुकान'), {'grocery_store', 'supermarket', 'convenience_store'}, {'food_store', 'market'}),
    (('mobile repair', 'mobile repair shop', 'phone repair', 'mobile service centre'), set(), {'cell_phone_store', 'electronics_store'}),
    (('tailor', 'tailoring', 'tailoring shop', 'alteration shop'), {'tailor'}, {'clothing_store'}),
    (('medical store', 'pharmacy', 'chemist'), {'pharmacy'}, {'drugstore', 'health'}),
    (('beauty parlour', 'beauty salon'), {'beauty_salon'}, {'hair_salon', 'hair_care', 'spa'}),
    (('tea stall', 'tea shop'), {'tea_house'}, {'cafe', 'coffee_shop', 'restaurant'}),
    (('hardware shop', 'hardware store'), {'hardware_store'}, {'home_goods_store'}),
)
STOP = {'shop', 'store', 'business', 'centre', 'center', 'unit'}


def classify_query(query, name, tags, slug=''):
    query = normalize_query(query).casefold()
    primary = tags.get('primary_type', '')
    types = set(tags.get('types', '').split(';')) | {primary}
    intent = next((row for row in INTENTS if query in row[0]), None)
    meaningful = words(query) - STOP
    name_words = words(name)
    direct_name = bool(meaningful) and meaningful <= name_words
    # A known synonym in the name provides the same explicit intent evidence.
    if intent:
        direct_name = direct_name or any((words(alias) - STOP) <= name_words for alias in intent[0])
    direct_type = bool(intent and primary in intent[1]) or bool(meaningful and meaningful == (words(primary.replace('_', ' ')) - STOP))
    related = bool(intent and types & (intent[1] | intent[2])) or bool(meaningful & name_words)
    classification = 'DIRECT_COMPETITOR' if direct_name or direct_type else 'RELATED_BUSINESS' if related else 'GENERIC_POI'
    return {'classification': classification, 'matched_business_slug': slug,
            'matching_rule': VERSION + (':name-intent' if direct_name else ':primary-type' if direct_type else ':related' if related else ':uncertain'),
            'matching_evidence': [{'key': 'query', 'value': query}]}
