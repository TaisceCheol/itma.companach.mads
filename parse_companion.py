# -*- coding: utf-8 -*-
from lxml import etree
import re

def format_authority_record(name):
	mads = etree.Element("mads")
	authority = etree.Element("authority")
	mads.append(authority)
	person = etree.Element("name",type="personal")
	authority.append(person)
	family = etree.Element("namePart",type="family")
	family.text = name.group('family').decode("utf-8")
	person.append((family))
	given = etree.Element("namePart",type="given")
	given.text = name.group('given').decode('utf-8')
	person.append(given)
	date = etree.Element("namePart",type="date")
	date.text = name.group('dates').decode('utf-8')
	person.append(date)
	field = etree.Element("fieldOfActivity")
	field.text = name.group("bio").replace('  ',' ').replace('- ','-').replace('ﬂ ','fl').replace('ﬁ ','fi').decode('utf-8')
	authority.append(field)
	return mads

src = "Companion_to_Irish_Traditional_Music_2nd_edition_text.txt"

family_group = ur"(?P<family>[A-Za-z\xe2\x80\x99\xc3\x81\xc3\x89\xc3\x8d\xc3\x93\xc3\x9a\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba]{1,}\s{,1}[A-Za-z\xe2\x80\x99\xc3\x81\xc3\x89\xc3\x8d\xc3\x93\xc3\x9a\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba]+?(?=\,))"
given_group = ur"(?P<given>[A-Za-z\xe2\x80\x99\xc3\x81\xc3\x89\xc3\x8d\xc3\x93\xc3\x9a\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba]*\s*[A-Za-z\xe2\x80\x99\xc3\x81\xc3\x89\xc3\x8d\xc3\x93\xc3\x9a\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba]+?(?=\.))"

name_and_date = re.compile(ur"%s\,\s*%s\.\s*\((?P<dates>\d+\xe2\x80\x93\d*\s*)\)\.\s*(?P<bio>.+?(?=\.)\.)" % (family_group,given_group),re.UNICODE)

with open(src,'r') as f:
	data = f.read().replace("\n",' ')
	pages = data.split('\x0c')
	lines = data.split('\n')

mads_col = etree.Element("madsCollection")

for i,name in enumerate(name_and_date.finditer(data)):
	record = format_authority_record(name)
	mads_col.append(record)

mads_tree = etree.ElementTree(mads_col)
mads_tree.write("itma.companion.mads.xml",xml_declaration=True,encoding='UTF-8',pretty_print=True)
