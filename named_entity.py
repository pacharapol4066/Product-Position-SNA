# -*- coding: utf-8 -*-
# Support pythainlp 2.0 ขึ้นไป (As-is 14 Sep 2020)
# https://www.thainlp.org/pythainlp/docs/2.0/api/tag.html
# https://thainlp.org/pythainlp/docs/2.0/_modules/pythainlp/tag/named_entity.html

__all__ = ["ThaiNameTagger"]

from typing import List, Tuple, Union

from pycrfsuite import Tagger as CRFTagger
from pythainlp.corpus import download, get_corpus_path, thai_stopwords
from pythainlp.corpus.common import thai_words
from pythainlp.tag import pos_tag
#from pythainlp.tokenize import word_tokenize
from pythainlp.tokenize import Tokenizer
from pythainlp.util import isthai, dict_trie

_CORPUS_NAME = "thainer"
_TOKENIZER_ENGINE = "newmm"  # should be the same as one used in training data

################## CUSTOM PART #########################

custom_list = ['ดัชมิลล์','ดัชมิล','ดัชมิว','dutch mill','dutch milk','ดัชชี่','เมจิ','ซีพีเมจิ','ซีพี เมจิ','cp meiji','betagen','บีทาเก้น','บีทาเกน'
               ,'โฟร์โมสต์','โฟร์โมส','โฟโมสต์','โฟโมต','โฟโมส','โฟโม้ส','โฟรโมสต์','โฟรโมสต','โชคชัย','แดรี่โฮม','dairy home','เดรี่โฮม','เดลี่โฮม','อืมม มิลค์'
               ,'umm milk','เอ็มมิลค์','m milk','mmilk','เอ็มมิ้ลค์','เอ็มมิลล์','แมคโนเลีย','นมฟาร์มโชคชัย','ไทยเดนมาร์ค','ไทยเดนมาร์ก','นมวัวแดง','หนองโพ','คาเนชั่น'
               ,'สตอเบอร์รี่','สตรอว์เบอร์รี','รสสตรอเบอรี่','สตรอเบอรี่','สตรอวเบอรี่','สตอเบอรี่','สตรอเบอรี่'
               ,'ชอคโกแล็ต','ช็อกโกแลต','ช็อคโกแลต','ช๊อกโกแลต','ช็อคโกแล็ต','ช็อกโกเลต','มิ้นท์ชอค','มิ้นต์ช้อก','รสกล้วย'
               ,'รสกาแฟ','รสหวาน','รสจืด','ไขมันต่ำ','ไขมัน 0%','low fat','0% fat','ขาดมันเนย','พร่องมันเนย','ไฮแคลเซียม'
               ,'high protein','whey formula','วานิลลา','วิปครีม','สูตรลดน้ำตาล'
               ,'ไฮโปรตีน','เวย์โปรตีน','whey','เวย์','อัลมอนด์','ซีเล็ค','ซีเล็คท์','กล้วยหอม','ไวท์คอฟฟี่','คาปูชิโน่','อเมริกาโน่'
               ,'grass fed','free lactose','lactose free','พาสเจอไรซ์','พาสเจอร์ไรซ์','พาสเจอร์ไรส์','พาซเจอไรซ์','พาสเจอร์ไลท์'
               ,'เมจิโกลด์ แม็กซ์','เมจิโกลด์','เมจิ โกลด์','เมจิโกล์ดแม็กซ์','เมจิ บัลแกเรีย','เมจิบัลแกเรีย','นมเปรี้ยว','รสธรรมชาติ','รสกลมกล่อม','ไพเกน'
               ,'โยเกิต','โยเกิรต','โยเกิร์ตพร้อมดื่ม','น้ำตาลมะพร้าว','นมฮอกไกโด','เบดไทม์','ฟรีแลคโตส','แลคโตสฟรี','ริชเอสเพสโซ่'
               ,'bedtime','bed time','เบดไทม์','ดาร์คช็อกโกแลต','ดาร์กช็อก','ดาร์กช็อกโกแลต'
               ,'คาราเมล','ช็อกโกมอลต์','เมล่อน','ชาเขียวมัจฉะ','ชาไทย','ฝาน้ำเงิน','ผลิตภันท์นม','เต้าฮวยนมสด','nondairy','non dairy'
               ,'7 eleven','เซเว่น อีเลฟเว่น','เซเว่นอีเลฟเว่น','เซเว่น','เซเวน','7 11','สตาร์บัค','อเมซอน'
               ,'ท็อปส์','ทอปส์','ท้อปส์','ท๊อปส์','แมคโคร','แม็คโคร','โลตัส','บิ๊กซี','bigc','golden place','big c'
               ,'ขายไม่ดี','แพคคู่','ค่าจัดส่ง','shelf life','พนักงานขายนม','ซื้อประจำ','หายาก','หาซื้อ','ของแถม','ราคาสูง','น้ำนมโค','นมโคแท้','นมแพะ','นมโรงเรียน','แพ้นม','แพ้นมวัว','นมอัดเม็ด'
               ,'เล่นเวท','นำ้หนัก','คุณแม่มือใหม่','นมอุ่น','ชานม','กินนม','ดื่มนม','ท้องเสีย','ขี้แตก','คุมอาหาร','นักวิ่ง','ร้านนมสด','ดูแลสุขภาพ','คนท้อง','มวลกระดูก'
               ,'คีเฟอร์นม','พันทิป','ร้านนม','เหมียวน้อย','ลูกสุนัข','ลูกหมา','คายทิ้ง','เจมส์ จิ','เจมส์จิ','ณเดช','ณเดชน์','สตอรี่' ,'อยากสูง','ส่วนสูง','สูงขึ้น','รักษามะเร็ง','รักษาเบาหวาน'
              ,'ไม่มี','ไม่ชอบ','ไม่ได้','ไม่อร่อย','ชาไข่มุก','ชานมไข่มุก','นมข้น','อเมซอน','นมเมจิสีฟ้า','ทำฟอง','ตีฟอง','โฟมนม','มื้อเช้า','ไขมันทรานส์','ดาราเดลี่','แดรี่ฟาร์ม','แดรี่ควีน']
words = set(thai_words()).union(set(custom_list))
_trie = dict_trie(dict_source=words)
_tokenizer = Tokenizer(custom_dict=_trie, engine=_TOKENIZER_ENGINE)

########################################################


def _is_stopword(word: str) -> bool:  # เช็คว่าเป็นคำฟุ่มเฟือย
    return word in thai_stopwords()


def _doc2features(doc, i) -> dict:
    word = doc[i][0]
    postag = doc[i][1]

    # Features from current word
    features = {
        "word.word": word,
        "word.stopword": _is_stopword(word),
        "word.isthai": isthai(word),
        "word.isspace": word.isspace(),
        "postag": postag,
        "word.isdigit": word.isdigit(),
    }
    if word.isdigit() and len(word) == 5:
        features["word.islen5"] = True

    # Features from previous word
    if i > 0:
        prevword = doc[i - 1][0]
        prevpostag = doc[i - 1][1]
        prev_features = {
            "word.prevword": prevword,
            "word.previsspace": prevword.isspace(),
            "word.previsthai": isthai(prevword),
            "word.prevstopword": _is_stopword(prevword),
            "word.prevpostag": prevpostag,
            "word.prevwordisdigit": prevword.isdigit(),
        }
        features.update(prev_features)
    else:
        features["BOS"] = True  # Special "Beginning of Sequence" tag

    # Features from next word
    if i < len(doc) - 1:
        nextword = doc[i + 1][0]
        nextpostag = doc[i + 1][1]
        next_features = {
            "word.nextword": nextword,
            "word.nextisspace": nextword.isspace(),
            "word.nextpostag": nextpostag,
            "word.nextisthai": isthai(nextword),
            "word.nextstopword": _is_stopword(nextword),
            "word.nextwordisdigit": nextword.isdigit(),
        }
        features.update(next_features)
    else:
        features["EOS"] = True  # Special "End of Sequence" tag

    return features


class ThaiNameTagger:
    def __init__(self):
        """
        Thai named-entity recognizer.
        """
        self.crf = CRFTagger()
        self.crf.open(get_corpus_path(_CORPUS_NAME))

    def get_ner(
        self, text: str, pos: bool = True, tag: bool = False
    ) -> Union[List[Tuple[str, str]], List[Tuple[str, str, str]]]:
        """
        This function tags named-entitiy from text in IOB format.

        :param str text: text in Thai to be tagged
        :param bool pos: To include POS tags in the results (`True`) or
                            exclude (`False`). The defualt value is `True`
        :param bool tag: output like html tag.
        :return: a list of tuple associated with tokenized word, NER tag,
                 POS tag (if the parameter `pos` is specified as `True`),
                 and output like html tag (if the parameter `tag` is
                 specified as `True`).
                 Otherwise, return a list of tuple associated with tokenized
                 word and NER tag
        :rtype: Union[list[tuple[str, str]], list[tuple[str, str, str]]], str

        :Note:
            * For the POS tags to be included in the results, this function
              uses :func:`pythainlp.tag.pos_tag` with engine as `perceptron`
              and corpus as orchid_ud`.

        :Example:

            >>> from pythainlp.tag.named_entity import ThaiNameTagger
            >>>
            >>> ner = ThaiNameTagger()
            >>> ner.get_ner("วันที่ 15 ก.ย. 61 ทดสอบระบบเวลา 14:49 น.")
            [('วันที่', 'NOUN', 'O'), (' ', 'PUNCT', 'O'),
            ('15', 'NUM', 'B-DATE'), (' ', 'PUNCT', 'I-DATE'),
            ('ก.ย.', 'NOUN', 'I-DATE'), (' ', 'PUNCT', 'I-DATE'),
            ('61', 'NUM', 'I-DATE'), (' ', 'PUNCT', 'O'),
            ('ทดสอบ', 'VERB', 'O'), ('ระบบ', 'NOUN', 'O'),
            ('เวลา', 'NOUN', 'O'), (' ', 'PUNCT', 'O'),
            ('14', 'NOUN', 'B-TIME'), (':', 'PUNCT', 'I-TIME'),
            ('49', 'NUM', 'I-TIME'), (' ', 'PUNCT', 'I-TIME'),
            ('น.', 'NOUN', 'I-TIME')]
            >>>
            >>> ner.get_ner("วันที่ 15 ก.ย. 61 ทดสอบระบบเวลา 14:49 น.",
                            pos=False)
            [('วันที่', 'O'), (' ', 'O'),
            ('15', 'B-DATE'), (' ', 'I-DATE'),
            ('ก.ย.', 'I-DATE'), (' ', 'I-DATE'),
            ('61', 'I-DATE'), (' ', 'O'),
            ('ทดสอบ', 'O'), ('ระบบ', 'O'),
            ('เวลา', 'O'), (' ', 'O'),
            ('14', 'B-TIME'), (':', 'I-TIME'),
            ('49', 'I-TIME'), (' ', 'I-TIME'),
            ('น.', 'I-TIME')]
            >>> ner.get_ner("วันที่ 15 ก.ย. 61 ทดสอบระบบเวลา 14:49 น.",
                            tag=True)
            'วันที่ <DATE>15 ก.ย. 61</DATE> ทดสอบระบบเวลา <TIME>14:49 น.</TIME>'
        """
        #tokens = word_tokenize(text, engine=_TOKENIZER_ENGINE, keep_whitespace=False)
        tokens = _tokenizer.word_tokenize(text)
        pos_tags = pos_tag(tokens, engine="perceptron", corpus="orchid_ud")
        x_test = ThaiNameTagger.__extract_features(pos_tags)
        y = self.crf.tag(x_test)

        sent_ner = [(pos_tags[i][0], data) for i, data in enumerate(y)]

        if tag:
            temp = ""
            sent = ""
            for idx, (word, ner) in enumerate(sent_ner):
                if ner.startswith("B-") and temp != "":
                    sent += "</" + temp + ">"
                    temp = ner[2:]
                    sent += "<" + temp + ">"
                elif ner.startswith("B-"):
                    temp = ner[2:]
                    sent += "<" + temp + ">"
                elif ner == "O" and temp != "":
                    sent += "</" + temp + ">"
                    temp = ""
                sent += word

                if idx == len(sent_ner) - 1 and temp != "":
                    sent += "</" + temp + ">"

            return sent

        if pos:
            return [
                (pos_tags[i][0], pos_tags[i][1], data)
                for i, data in enumerate(y)
            ]

        return sent_ner

    @staticmethod
    def __extract_features(doc):
        return [_doc2features(doc, i) for i in range(len(doc))]