import re

# pattern pour token
phone_in_token = re.compile(r'\(?(?:^0[1-9]\d{8}$|0[1-9]([\s\.\-\_]\d{2}){4}$)\)?')
phone_in_string = re.compile(r'(?:(\d{2})?-?(\d{2})[-_\s\.]?)?(\d{2})[-_\s\.]?-?(\d{2})[-_\s\.]?-?(\d{2})[-_\s\.]?(\d{2})\)?')


test = ["0612345678","0712345678","(0712345678)","02548","06 45 87 60 00","07-58-78-88-30","00798765432110","07_58_78_88_30"]
ttest = [ t for t in test if phone_in_token.search(t)]
print(ttest)

# TODO phone in string
# phone_in_string = re.compile(r'[-()\s\d]+?(?=\s*[+<])')

texte = "un exemple de texte avec un 0665349908 en plein milieu et au autre format comme 07 54 34 98 00 pour voir et aussi un dernier 05-98-45-00-23 pour la route et the ulime one 01_45_39_00_54 voila"

for r in re.findall(r'\(?(?:^0[1-9]\d{8}$|0[1-9]([\s\.\-\_]\d{2}){4}$)\)?', texte):
    print(r)

d = phone_in_token.search(texte)
print(d)

# m = re.match(r"(\d{1,2})\s(\d{1,2})",texte)
# print(m.groups())


a = re.compile(r'(?:(\d{2})?-?(\d{2})[-\s\.]?)?(\d{2})[-\s\.]?(\d{2})\)?')


OK = re.compile(r'(?:(\d{2})?-?(\d{2})[-\s\.]?)?(\d{2})[-\s\.]?-?(\d{2})[-\s\.]?-?(\d{2})[-\s\.]?(\d{2})\)?')

a = re.compile(r'(?:(\d{2})?-?(\d{2})[-_\s\.]?)?(\d{2})[-_\s\.]?-?(\d{2})[-_\s\.]?-?(\d{2})[-_\s\.]?(\d{2})\)?')

for t in re.findall(a,texte):
    print(t)

tex = re.sub(a, '', texte)
print(tex)
tt = tex.split(' ')
print(tt)
while '' in tt:
    tt.remove('')
print(tt)
    