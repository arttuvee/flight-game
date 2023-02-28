import textwrap

rules = "Sääntöjä jne....."

wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
word_list = wrapper.wrap(text=rules)

def getRules():
    return word_list