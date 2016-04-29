# -*- coding: UTF-8 -*-
from lxml import etree
from datetime import datetime
import re,json

def format_authority_record(name):
	global companion_set_chars
	mads = etree.Element("mads")
	authority = etree.Element("authority")
	mads.append(authority)
	person = etree.Element("name",type="personal")
	authority.append(person)
	family = etree.Element("namePart",type="family")
	family.text = name['family']
	person.append((family))
	given = etree.Element("namePart",type="given")
	given.text = name['given']
	person.append(given)
	date = etree.Element("namePart",type="date")
	date.text = name['dates']
	person.append(date)
	fields = re.split(ur'((?<!Co|Mr|Dr|Ms)\.)',name['bio'])[0].replace('and',';')
	fields = filter(lambda x:x.find('born')==-1 and x.find('Co.') == -1 and x.find('From') == -1 and x.find('His') ==-1 and x.find('Her') == -1 and len(x.split()) <= 3,[x.strip() for x in re.split(ur'[\,\;]+',fields)])
	for f in fields:
		if len(f) > 0:
			field = etree.Element("fieldOfActivity")
			field.text = f.capitalize()
			mads.append(field)
	bio = etree.Element("note",type="biographical/historical")
	bio.text = name['bio']
	mads.append(bio)
	note= etree.Element("note",type="source",authority="oclc")
	mads.append(note)
	note.text = r"<http://www.worldcat.org/oclc/821726214>"
	return mads

def process_name(group):
	family = group.group('family')
	given = group.group('given')
	bio = group.group('bio')
	bio = re.sub(ur"(\d+\s+)?\x0c[\w+%s]"%companion_set_chars,'',bio,re.UNICODE).replace('  ',' ').replace('- ','')
	bio = bio.replace(u'ﬁ ','fi').replace(u'ﬂ ','fl').replace('Th ','Th')
	dates = group.group('dates')
	datestr = list(filter(lambda x:len(x.strip()),re.match(ur"(\d+)\s?(?:\u2013)([c\.\d\s]+)?",dates).groups()))
	if len(datestr) == 2:
		if len(datestr[-1]) == 2:
			datestr[-1] = datestr[0][0:2]+datestr[-1]
		datestr="%s-%s" % tuple(datestr)
	else:
		datestr="%s-" % tuple(datestr)
	return {'family':family,'given':given,'dates':datestr,'bio':bio}



src = "Companion_to_Irish_Traditional_Music_2nd_edition_text.txt"

companion_set_chars = u"A-Za-z\u00C1\u00E1\u00C9\u00E9\u00CD\u00ED\u00D3\u00F3\u00DA\u00FA\u2013\u2019(\-\(\)"

family_group = ur"(?P<family>[%s]{1,}\s{,1}[%s]+?(?=\,))" % (companion_set_chars,companion_set_chars)
given_group = ur"(?P<given>[%s\.]*\s*[%s\.]*\s*[%s\.]+?(?=\.))" % (companion_set_chars,companion_set_chars,companion_set_chars)

name_date_bio = re.compile(ur"%s\,\s*%s\.\s*\((?P<dates>\d+[\u2013\d\s\.c]+)\)\.\s*(?P<bio>(?:.+?(?<!Co|Mr|Dr|Ms)\.){1,2})" % (family_group,given_group))

with open(src,'r') as f:
	data = f.read().replace("\n",' ').decode('utf-8')
	pages = data.split('\x0c')
	lines = data.split('\n')

mads_col = etree.Element("madsCollection")
names = []
for i,name in enumerate(name_date_bio.finditer(data)):
	# print [name.group('family'),name.group('given')]
	data_node = process_name(name)
	names.append(data_node)

print len(names)

for i,name in enumerate(names):
	record = format_authority_record(name)
	mads_col.append(record)


mads_tree = etree.ElementTree(mads_col)
mads_tree.write("itma.companion.mads.xml",xml_declaration=True,encoding='UTF-8',pretty_print=True)
