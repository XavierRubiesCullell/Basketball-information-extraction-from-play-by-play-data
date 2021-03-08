import re

text = "La paquita fa titiu!"
dist = re.search("(\d+)(?!.*\d).+?(?=ft)", text)
try:
    print(dist.group(1))
except:
    AttributeError