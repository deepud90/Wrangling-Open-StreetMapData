import xml.etree.cElementTree as ET
import re
import pprint
import string

regex = re.compile(r'1800')

def check_and_clean_number(number_string):
    number_list = number_string.replace(",", ";").replace("-", "").replace("+", "").replace("(", "").replace(")","").replace(" ", "").replace("\"", "").split(";") #replace special characters with blank,
                                                                                                                                                                # comma with semi-colon, and then split at semi colon.
                                                                                                                                                                # semi-colon separates multiple numbers

    number_list = filter(None, number_list)


    new_number_list = []

    for number in number_list:
        if number[0:3]=="910":                              # if number begins with 91, but has a zero before area code (hence 910), remove the zero and add +
            new_number = "+"+ number[0:2] + number[3:]

        elif number[0]=="0":                                # if number begins with 0, remove it and add +91 at the beginning
            new_number = "+91" + number[1:]

        elif number[0:2]=="91":                             # if number begins with 91, and not followed by zero, just prefix a +
            new_number  = "+" + number
        else:

            if len(number)==8:                              # landline numbers without country and area code

                new_number = "+9180"+number

            elif len(number)==10:                           #cell phone numbers

                new_number = "+91"+number
            else:

                new_number = number                         # leave the number as it is

        if regex.search(new_number[0:8]):                   #searching for hotline numbers. Do not prefix +91 in case of these

            for p in regex.finditer(new_number):
                pos = p.start()
            new_number = new_number[pos:]

        new_number_list.append(new_number)
    new_number_string = ','.join(new_number_list)

    return new_number_string



if __name__ == "__main__":
#if 1==1:
    filename = "Whitefield.osm"
    wrong_phones = {}
    all_phones = set()
    modified_phones = set()
    ten_twelve_nos = set()

    for event, elem in ET.iterparse(filename, events=('end',)):

            subelem = elem.find('.tag[@k="phone"]')

            if subelem is None:
                continue
            else:
               all_phones.add(subelem.attrib['v'])
               number_string = subelem.attrib['v']


               modified_phones.add(check_and_clean_number(number_string))
               #print(check_and_clean_number(number_string))










