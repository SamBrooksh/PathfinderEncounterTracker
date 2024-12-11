import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from random import uniform
from math import log

@dataclass
class item:
    name: str = ""
    value: float = 0.0 # in gold pieces
    chance: float = 1.0 #If its more or less common
    
    def __str__(self) -> str:
        return f"{self.name.replace(',', '')},{self.value},{self.chance}"

def rebalance_chances(items):
    total_gp = (sum(x.value for x in items['values']))
    items['total'] = total_gp
    for i in items['values']:
        i.chance = 1/(i.value)
    total_chance = (sum(x.chance for x in items['values']))
    items['total_chance'] = int(total_chance)
    items['weights'] = [i.chance for i in items['values']]
    return items

def get_random_item(items, starting_value:int=0):
    #if starting_value > items['total_chance']:
        #print("Over Max")
    #    return items['values'][-1], starting_value
    if starting_value < 0.0:
        starting_value = 0.0
    total = sum(i for i in items['weights'])
    normalized_weights = [i/total for i in items['weights']]
    new_weights = []
    total = 0.0
    for i in normalized_weights:
        if starting_value > 50:
            scale_factor = log(starting_value + 1)
        else:
            scale_factor = log(51 - starting_value)
        total += i * scale_factor 
        new_weights.append(total)
    roll = uniform(0.0, total)
    for i, val in enumerate(new_weights):
        if roll <= val:
            return items['values'][i], roll
    #for i, chance = 
    

def sample_highest(items, value_bonus, count=1000):
    curr_high = item()
    highroll = 0
    for _ in range(count):
        val, roll = get_random_item(items, value_bonus)
        if val.value > curr_high.value:
            curr_high = val
            highroll = roll
    return curr_high, highroll

def sample_lowest(items, value_bonus, count=1000):
    curr_high = item(value=max(x.value for x in items['values']) + 1)
    highroll = 0
    for _ in range(count):
        val, roll = get_random_item(items, value_bonus)
        if val.value < curr_high.value:
            curr_high = val
            highroll = roll
    return curr_high, highroll

def get_average_value(items, value_bonus, count=1000):
    total = 0
    rolls = 0
    for _ in range(count):
        val, roll = get_random_item(items, value_bonus)
        total += val.value
        rolls += roll
    return total/count, rolls/count

def tests(information, value_bonuses, count=1000):
    for b in value_bonuses:
        print(f"HIGH with {b}: {sample_highest(information, b, count)}")
        print(f"LOW with {b}: {sample_lowest(information, b, count)}")
        print(f"AVERAGE with {b}: {get_average_value(information, b, count)}")

def main():    
    sites = "https://legacy.aonprd.com/corerulebook/magicItems/wondrousItems.html"
    items = []
    r = requests.get(sites)
    soup = BeautifulSoup(r.content, 'html.parser')
    with open("site.txt", 'w') as fout:
        print(soup.prettify(), file=fout)
    results = soup.find_all('div', class_="table")
    count = 0
    total = 3
    for table in results:
        first = True
        if count >= total:
            break
        info = table.find_all('tr')
        for tr in info:
            if first:
                first = False
                continue
            values = tr.find_all('td')
            gp = values[2].get_text().strip()
            gp = gp.replace(',', '')
            if "gp" in gp:
                gp = float(gp.split(" ")[0])
            elif "sp" in gp:
                gp = float(gp.split(" ")[0]) * 10
            elif "cp" in gp:
                gp = float(gp.split(" ")[0]) * 100
            elif "pp" in gp:
                gp = float(gp.split(" ")[0]) / 10
            items.append(item(values[1].get_text().strip(), gp))
        count += 1
    information = {}
    items.sort(key=lambda x: x.value)
    information['values'] = items
    information = rebalance_chances(information)
    #print(information)
    tests(information, [x for x in range(1, 100, 10)], 10000)
    

if __name__ == "__main__":
    main()