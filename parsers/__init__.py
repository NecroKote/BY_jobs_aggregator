# -*- coding: utf-8 -*-
import re

def text_cleanup(text):
    cleaner = re.compile('[\.;,-:!()]', re.MULTILINE)
    text = cleaner.sub('', text)
    return text
