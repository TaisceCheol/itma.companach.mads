# -*- coding: UTF-8 -*-
from lxml import etree
import re

def format_authority_record(name):
	global companion_set_chars
	mads = etree.Element("mads")
	authority = etree.Element("authority")
	mads.append(authority)
	person = etree.Element("name",type="personal")
	authority.append(person)
	family = etree.Element("namePart",type="family")
	family.text = name.group('family').decode('UTF-8')
	person.append((family))
	given = etree.Element("namePart",type="given")
	given.text = name.group('given').decode('UTF-8')
	person.append(given)
	date = etree.Element("namePart",type="date")
	date.text = name.group('dates').decode('UTF-8')
	person.append(date)
	field = etree.Element("fieldOfActivity")
	strip_formfeeds = re.sub(ur"(\d+\s+)?\x0c[\w+%s]"%companion_set_chars,'',name.group('role'),re.UNICODE)
	field.text = strip_formfeeds.replace('  ',' ').replace('-**newline**','').replace('**newline**',' ').replace('ﬃ ','ffi').replace('ﬁ ','fi').replace('ﬂ ','fl').decode('UTF-8')
	authority.append(field)
	return mads

src = "Companion_to_Irish_Traditional_Music_2nd_edition_text.txt"

companion_set_chars = u"A-Za-z\xe2\x80\x99\xc3\x81\xc3\x89\xc3\x8d\xc3\x93\xc3\x9a\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\.\xe2\x80\x93\-\(\)"

family_group = ur"(?P<family>[%s]{1,}\s{,1}[%s]+?(?=\,))" % (companion_set_chars,companion_set_chars)
given_group = ur"(?P<given>[%s]*\s*[%s]*\s*[%s]+?(?=\.))" % (companion_set_chars,companion_set_chars,companion_set_chars)

name_and_date = re.compile(ur"%s\,\s*%s\.\s*\((?P<dates>\d+\xe2\x80\x93[c\.\d\s]*)\)\.\s*(?P<role>.+?(?=\.)\.)" % (family_group,given_group),re.UNICODE)

with open(src,'r') as f:
	data = f.read().replace("\n",'**newline**')
	pages = data.split('\x0c')
	lines = data.split('\n')

mads_col = etree.Element("madsCollection")
names = []
for i,name in enumerate(name_and_date.finditer(data)):
	names.append(name)

print len(names)

names.sort(key=lambda x:x.group('dates').decode('utf-8').split(u'-'))

for name in names:
	record = format_authority_record(name)
	mads_col.append(record)

mads_tree = etree.ElementTree(mads_col)
mads_tree.write("itma.companion.mads.xml",xml_declaration=True,encoding='UTF-8',pretty_print=True)
