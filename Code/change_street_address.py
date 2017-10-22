import xml.etree.cElementTree as ET
import re
import pprint
import string


def modify_street_address(address,reg_ex,re_len):
    if reg_ex.search(address) is not None:
        pos=0
        is_full_address = 0             # this will be turned to 1 if it is found that the value in "Addr:Street" contains more than just the street name
        for p in reg_ex.finditer(address):
            pos = (p.end())
        street_address = address[0:pos+1]   # Slice the string from the beginning up to the end of the end word
        address_len = len(re_len.findall(address)) # length of the original address string
        street_address_len = len(re_len.findall(street_address)) #check no of words (length) of the extracted street address
        if address_len > street_address_len: #if the original address string contains more words than the extracted street address, then it is actually a full address, and we need to create a new field for it
            is_full_address = 1
    else:
        street_address = "" #if not end words found, replace street address with blank, and put the entire address in full address field
        is_full_address = 1

    street_address = string.strip(street_address,", ") # remove trailing characters if any
    return street_address, is_full_address

def create_full_address(elem): #This function generates a full address for the element, by combining all the attributes such as name, housename, houseno, street, city, state and postcode.
                               # Will be called to create a full address if we detect that the string in addr:street contains more than just street address
    name = elem.find('.tag[@k="name"]')
    house_no = elem.find('.tag[@k="addr:housenumber"]')
    house_name = elem.find('.tag[@k="addr:housename"]')
    street = elem.find('.tag[@k="addr:street"]')
    city = elem.find('.tag[@k="addr:city"]')
    state = elem.find('.tag[@k="addr:state"]')
    postcode = elem.find('.tag[@k="addr:postcode"]')

    name = name.attrib['v'] if name is not None else ""
    addr_housename = house_name.attrib['v'] if house_name is not None else ""
    addr_houseno = house_no.attrib['v'] if house_no is not None else ""
    addr_street = street.attrib['v'] if street is not None else ""
    addr_city = city.attrib['v'] if city is not None else ""
    addr_state = state.attrib['v'] if state is not None else ""
    addr_postcode = postcode.attrib['v'] if postcode is not None else ""

    addr_full = ", ".join(filter(None, [name, addr_houseno, addr_housename, addr_street, addr_city, addr_state, addr_postcode]))


    return addr_full

if __name__ == "__main__":
#if 1==1:

    end_words = ["Avenue","Circle","Colony","Cross","Lane","Main","Layout","Mall","Rd","Zone","EPIP Area","Road(?:\sno\.\s[1-9]|\s[1-9])?"] #list of possible end words for street addresses
# Create regular expression list
    expression = r"\b" + "({:s})".format('|'.join(end_words)) + r"\b"
    reg_ex = re.compile(expression, re.IGNORECASE) #regular expression to check for any of the above end words in a street address
    re_len = re.compile(r'\w+')

    old_addresses = set()
    new_addresses = set()
    full_addr_set = set()
    filename = "Whitefield.osm"
    count = 0
    for event, elem in ET.iterparse(filename, events=('end',)):

        if elem.tag == "node" or elem.tag =="way":

            subelem = elem.find('.tag[@k="addr:street"]')
            if subelem is None:
                continue
            else:
                (new_address,is_full_address) = modify_street_address(subelem.attrib['v'],reg_ex,re_len)
                #print(new_address)

            if is_full_address == 1:
                #print("yes")
                addr_full = create_full_address(elem)
                full_addr_set.add(addr_full)
                count+=1
    print ("no of ful addresses made-{:d}").format(count)


