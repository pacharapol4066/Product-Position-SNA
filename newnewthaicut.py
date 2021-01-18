#!/usr/bin/env python
# coding: utf-8

# Inside–outside–beginning (tagging)
# https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)


#from pythainlp.tag.named_entity import ThaiNameTagger
#thainer = ThaiNameTagger()

from named_entity import ThaiNameTagger
thainer = ThaiNameTagger()

def word_tokenize(txt):
    global thainer
    _ws = thainer.get_ner(text=txt,pos=False)
    list_w = []
    bi = ""
    tag = ""
    for i,t in _ws:
        if t.startswith('B-'):
            if bi!="":
                list_w.append(bi)
            bi=""
            bi += i
            tag = t.replace('B-','')
        elif t.startswith('I-') and t.replace('I-','')==tag:
            bi += i
        elif t == "O" and tag!="":
            list_w.append(bi)
            bi=""
            tag = ""
            list_w.append(i)
        else:
            bi=""
            tag = ""
            list_w.append(i)
    if bi!="":
        list_w.append(bi)
    return list_w

