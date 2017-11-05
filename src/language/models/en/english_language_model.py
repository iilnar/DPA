from pycorenlp import StanfordCoreNLP

from configs.config_constants import CoreNLPServerAddress
from language.models.named_entity_recognition import NERType
from language.models.part_of_speech import POS
from language.models.token import Token
from src.language.models.LanguageModel import LanguageModel


class EnglishLanguageModel(LanguageModel):
    def __init__(self, config):
        self.__server = StanfordCoreNLP(config[CoreNLPServerAddress])
        self.pos_map = {"VB": POS.VERB,
                        "NOUN": POS.NOUN,
                        "ADJ": POS.ADJ,
                        "CD": POS.CARDINAL_NUMBER}

        self.ner_map = {"DATE": NERType.DATE,
                        "PERSON": NERType.PERSON,
                        "NUMBER": NERType.NUMBER}

    def tokenize(self, string):
        output = self.__server.annotate(string, properties={
            'annotators': 'tokenize,pos,lemma,ner',
            'outputFormat': 'json'})

        tokens_description = output["sentences"][0]["tokens"]
        token_list = []
        for description in tokens_description:
            lemma = description["lemma"]
            word = description["originalText"]
            pos_tag = description["pos"]
            pos_tag = self.convert_pos(pos_tag)
            token = Token(word, lemma, pos_tag)
            token_list.append(token)

            ner_type = description.get("ner", None)
            if ner_type is not None:
                ner_type = self.convert_ner(ner_type)
                token.set_NER_type(ner_type)

        return token_list

    def convert_pos(self, pos_str):
        return self.pos_map.get(pos_str, POS.UNKOWN)

    def convert_ner(self, ner):
        ner = ner.upper()
        return self.ner_map.get(ner, None)
