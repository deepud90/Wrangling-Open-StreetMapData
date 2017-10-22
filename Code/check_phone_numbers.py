import xml.etree.cElementTree as ET
import re
import pprint
import string

regex = re.compile(r'1800') # regular expression to check for hotline numbers


if __name__ == "__main__":
#if 1==1:
    filename = "Whitefield.osm"
#    wrong_phones = {}
    all_phones= set()
#    modified_phones = set()
#    ten_twelve_nos = set()

    for event, elem in ET.iterparse(filename, events=('end',)):

            subelem = elem.find('.tag[@k="phone"]')

            if subelem is None:
                continue
            else:
               all_phones.add(subelem.attrib['v'])

    pprint.pprint(all_phones)








