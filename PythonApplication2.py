import requests, xmltodict, json, sqlite3
from OSMPythonTools.api import Api


key=""
url3 = "https://api.openstreetmap.org/api/0.6/"
payload={}
headers = {}

with open("school.json", "r", encoding='utf-8') as read_file:
    school = json.load(read_file)

arr=[]
for i in school["elements"]:
    if i["type"]=="node":
        break
    addr=i["tags"]["addr:street"].replace(' ', '+')+','+i["tags"]["addr:housenumber"]+','+i["tags"]["addr:postcode"]
    url2="https://maps.googleapis.com/maps/api/geocode/json?address="+addr+"&key="+key
    response = requests.request("GET", url2 , headers=headers, data=payload)
    tmp=json.loads(response.text)
    cord=(tmp["results"][0]["geometry"]["location"]["lat"],tmp["results"][0]["geometry"]["location"]["lng"])
    print(cord)
    arr.append(cord)
read_file.close()
print("###################################################")
con = sqlite3.connect('db.db')

cur = con.cursor()
s='CREATE TABLE if not exists info(lat DOUBLE not null, lon DOUBLE not null'
for i in arr:
    s+=',"'+str(i[0])+' '+str(i[1])+'" DOUBLE not null'
s+=')'
cur.execute(s)



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
     
     url2="https://maps.googleapis.com/maps/api/geocode/json?address="+addr+"&key="+key
     res = requests.request("GET", url2 , headers=headers, data=payload)
     tmp=json.loads(res.text)
     cord=[tmp["results"][0]["geometry"]["location"]["lat"],tmp["results"][0]["geometry"]["location"]["lng"]]
       
     file=open("text.txt", "w")
     file.write(str(count))
     file.close()
     A=cord
     l=[]
     for i in arr:
        B=i
        url1 = "https://maps.googleapis.com/maps/api/directions/json?origin="+str(A[0])+"%2C"+str(A[1])+"&destination="+str(B[0])+"%2C"+str(B[1])+"&mode=walking&key="+key
        response = requests.request("GET", url1 , headers=headers, data=payload)
        tmp=json.loads(response.text)
        if ((tmp["routes"][0]["legs"][0]["distance"]["value"])==0):
            print("dcsdsc")
        l.append(tmp["routes"][0]["legs"][0]["distance"]["value"])
     count+=1
     tmp=cord + l     
     print(cord)  
     s=len(l)*(",?")
     cur.execute("INSERT INTO info VALUES (?,?"+s+')',tmp)
     con.commit()
    