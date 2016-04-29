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

def process_dates(value):
	dates = value.split('\xe2\x80\x93')
	start = dates[0]
	if len(dates) > 1:
		end = re.match(".*?(?P<number>\d+)",dates[-1])
		if end:
			end = end.group('number')
			if len(end) == 2:
				end = start[0:2]+end
	return [start,end]

def make_timeline_node(i,name):
	dates = process_dates(name.group('dates'))
	record = {'id':i,'type':"point",'content':"%s %s" % (name.group('given'),name.group('family')),'start':dates[0]}
	strip_formfeeds = re.sub(ur"(\d+\s+)?\x0c[\w+%s]"%companion_set_chars,'',name.group('role'),re.UNICODE)
	strip_formfeeds = strip_formfeeds.replace('  ',' ').replace('-**newline**','').replace('**newline**',' ').replace('ﬃ ','ffi').replace('ﬁ ','fi').replace('ﬂ ','fl').decode('UTF-8')
	record['bio'] = strip_formfeeds
	if len(dates) > 1:
		record['end'] = dates[-1]
	return record

src = "Companion_to_Irish_Traditional_Music_2nd_edition_text.txt"

companion_set_chars = u"A-Za-z\u00C1\u00E1\u00C9\u00E9\u00CD\u00ED\u00D3\u00F3\u00DA\u00FA\u2013(\-\(\)"

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
	# if i > 25:break
	names.append(name)

print len(names)

# names.sort(key=lambda x:x.group('dates').decode('utf-8').split(u'-'))
# timeline_nodes = []
# for i,name in enumerate(names):
# 	record = format_authority_record(name)
# 	node = make_timeline_node(i+1,name)
# 	mads_col.append(record)
# 	timeline_nodes.append(node)
# 	# if i > 100:break

# with open('/users/itma/documents/piaras_scripts/WorkCode/code/itma.timeline.test/timeline_data.json','w') as f:
# 	json.dump(timeline_nodes,f)

# mads_tree = etree.ElementTree(mads_col)
# mads_tree.write("itma.companion.mads.xml",xml_declaration=True,encoding='UTF-8',pretty_print=True)
