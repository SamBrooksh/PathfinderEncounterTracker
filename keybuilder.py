import pprint
from enum import Enum

def get_spacing(string: str) -> int:
    # Gets the number of spaces at the beginning of a string
    x = 0
    for i in string:
        if i.isspace():
            x += 1
        else:
            return x
    return x

def load_keys(file:str="possiblekeys.txt"):
    details = {}
    with open (file, 'r') as fin:
        spacing = [0]
        previous_item = [details]
        temp_holder = None 
        for line in fin:
            if line.isspace():
                continue
            # Make it able to have multiple levels
            if get_spacing(line) > spacing[-1]: #New Level
                spacing.append(get_spacing(line))
                previous_item.append(temp_holder)
            while get_spacing(line) < spacing[-1]: # Remove level
                #Has current error, where need to allow multiple tabs being removed
                previous_item[-2][previous_item[-1]['KEY']] = previous_item[-1]
                previous_item.pop()
                spacing.pop()
                #spacing = get_spacing(line)
            
            key_detail = {}
            terms = line.split(':')
            for i in range(len(terms)):
                terms[i] = terms[i].strip()

            key_detail['KEY'] = terms[0]
            if 'Enum' in terms[1]:
                temp = terms[1].split('-')
                for j in range(len(temp)):
                    temp[j] = temp[j].strip()
                enum_members = {}
                for j in range(1, len(temp)):
                    enum_members[temp[j]] = j
                key_detail['TYPE'] = Enum(terms[0], enum_members)
            else:
                key_detail['TYPE'] = terms[1]
            for i in range (2, len(terms)):
                #Add the rest of the details
                if '-' in terms[i]:
                    temp = terms[i].split('-')
                    for j in range(len(temp)):
                        temp[j] = temp[j].strip()
                    key_detail[temp[0]] = temp[1]
                else:
                    key_detail[terms[i]] = True
            if get_spacing(line) > 0:
                previous_item[-1][key_detail['KEY']] = key_detail
            else:
                details[key_detail['KEY']] = key_detail
            
            temp_holder = key_detail
                
        return details


def main():
    pprint.pp(load_keys())

if __name__ == '__main__':
    main()