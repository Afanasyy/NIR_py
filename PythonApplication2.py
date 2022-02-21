import requests, xmltodict, json, sqlite3
from OSMPythonTools.api import Api
import time


def re(url, retry=2):
    try:
        r = requests.get(url)
        assert (r.status_code == 200), ("Ошибка, Код ответа: ", r.status_code, url)
    except Exception as _e:
        if retry:
            print('retry=', retry, url)
            return re(url, retry=(retry - 1))  # retry fail
        else:
            raise  # fail
    else:
        return r  # ok

key_G="AIzaSyDrcM0eeiZE9cE-seAFvdsnc8iDBP8FvYk"
key_Y="7626e5f6-f640-43ef-b927-469881d57da7"
url3 = "https://api.openstreetmap.org/api/0.6/"
payload={}
headers = {}
con = sqlite3.connect('db2.db')
cur = con.cursor()

with open("school.json", "r", encoding='utf-8') as read_file:
    school = json.load(read_file)



s_addr=[]
arr=[]
ind=1;
s='CREATE TABLE if not exists schools(id text,addr text, cord text)'
#cur.execute(s)
s="delete from schools"
#cur.execute(s)
s='INSERT INTO schools VALUES (?, ?, ?)'
for i in school["elements"]:
    if i["type"]=="node":
        break
    addr="Нижний Новгород, "+i["tags"]["addr:street"]+', '+i["tags"]["addr:housenumber"]+', '+i["tags"]["addr:postcode"]
    url2="https://maps.googleapis.com/maps/api/geocode/json?address="+addr+"&key="+key_G
    response = requests.request("GET", url2 , headers=headers, data=payload)
    tmp=json.loads(response.text)
    cord=str(tmp["results"][0]["geometry"]["location"]["lat"])+','+str(tmp["results"][0]["geometry"]["location"]["lng"])
    print(addr,' / ', cord)
    arr.append(['s'+str(ind),cord])
    tmp=('s'+str(ind),addr,cord)
    s_addr.append(tmp)
    cur.execute(s,tmp)
    ind+=1
read_file.close()
print("###################################################")
con.commit()
s='CREATE TABLE if not exists final(cord text'
for i in arr:
    s+=',"'+i[0]+'" text not null'
s+=',addr text)'
#cur.execute(s)
s="delete from final"
#cur.execute(s)



count=0

try:
    file = open('text.txt')
except IOError as e:
    file=open("text.txt", "w")
    file.write("0")
else:
    count=int(file.read())
file.close()

with open("apartments.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)

max_len=len(data["elements"])

for i in range(count, max_len):
     if data["elements"][i]["type"]=="node":
        break 
     try:
        addr="Нижний+Новгород,"+data["elements"][i]["tags"]["addr:street"].replace(' ', '+')+','+data["elements"][i]["tags"]["addr:housenumber"]+','+data["elements"][i]["tags"]["addr:postcode"]
     except Exception as e:
        try:
            addr="Нижний+Новгород,"+data["elements"][i]["tags"]["addr:street"].replace(' ', '+')+','+data["elements"][i]["tags"]["addr:housenumber"]
        except Exception as e:
            count+=1
            continue
     
     url2="https://maps.googleapis.com/maps/api/geocode/json?address="+addr+"&key="+key_G
     res = requests.request("GET", url2 , headers=headers, data=payload)
     tmp=json.loads(res.text)
     cord=str(tmp["results"][0]["geometry"]["location"]["lat"])+','+str(tmp["results"][0]["geometry"]["location"]["lng"])
       
     file=open("text.txt", "w")
     file.write(str(count))
     file.close()
     l=[]
     for i in arr:
        url1 = "https://api.routing.yandex.net/v2/route?apikey="+key_Y+"&waypoints="+cord+"|"+i[1]+"&mode=walking"
        response = re(url1)
        tmp=json.loads(response.text)        
        l.append(tmp['route']['legs'][0]['steps'][0]['length'])
     count+=1
     addr=addr.replace('+', ' ')
     tmp2=[cord]+ l+ [addr]    
     print(cord)  
     s=len(l)*(",?")
     cur.execute("INSERT INTO final VALUES (?"+s+',?)',tmp2)
     con.commit()
    