# import re
#
# def super_replace(text, before, after):
#     result = re.finditer(fr'''".*?"|'.*?'|(\b{before}\b)''', text, re.MULTILINE)
#     res = list(text)
#     for match in list(result)[::-1]:
#         if match.group(1):
#             del res[match.start(1): match.end(1)]
#             res.insert(match.start(1), after)
#     return "".join(res)
#
#
# text = '''Я люблю или ябл'ок'и " и " апельсин'ы, но не могу есть бананы и груши.'''
# print(super_replace(text, "и", "and"))
