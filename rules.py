import textwrap

<<<<<<< HEAD
rules = "sääntöjä jne....." #TODO Joona lisää tähän ne sun muotoilemat säännöt
=======
rules = "Sääntöjä jne....."
>>>>>>> origin/main

wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
word_list = wrapper.wrap(text=rules)

def getRules():
    return word_list