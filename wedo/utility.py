import re
import pandas as pd
import numpy as np
import requests
import random
import json

class Game(object):
    def __init__(self):
        self.dict = {}
        self.appid = None
        self.name = None #正常存储的游戏名
        self.genre = []
        self.description = []
        self.categories=[]#是否支持多人联机
        self.good_rate =None#好评率
        self.platforms =[] #游戏平台
        if self.name:
           self.special_name = self.namereplace(' ','_').replace('-','')
    def getNameByID(self,id):
        if id == self.appid:
            return self.name
def link_get_id(link):
    lk = re.search( r'\d+',link, flags=0)
    return lk.group()
def getid_byname(path,name):
    df = pd.read_csv(path,encoding='utf-8')
    for index in df.index:
        d = dict(df.loc[index])
        if d['name'] == name:
            return d['appid']
       
    return random.randrange(100000,190000,1)

def getatt_byname(path,name):
    df = pd.read_csv(path,encoding='utf-8')
    for index in df.index:
        d = dict(df.loc[index])
        if d['name'] == name:
            genre = d['genres'].split(";")
            return  d['appid'],genre[0],d['price'],int(d['positive_ratings']),int(d['negative_ratings'])
    return random.randrange(100000,190000,1),0,0,0,0
def read_files(path,game_list):
    df = pd.read_csv(path)
    for index in df.index:
       game_list.append(dict(df.loc(index)))
def get_recom(name,depth = 1):
    url = "http://118.195.235.177:5000/recommendation?name="+name+"&topk=5"
    content=requests.get(url).text.encode('utf-8').decode('utf-8')
    game_dict=json.loads(content)
    gamelist = list()
    links = []
    source = None
    for i in range(len(game_dict['names'])):
        game = {}
        game['name'] = game_dict['names'][i]
        game['coordinates'] = game_dict['coordinates'][i]
        game['x'] = game_dict['coordinates'][i][0]
        game['y'] = game_dict['coordinates'][i][1]
        game['id'],game['genres'],game['price'],game['positive_ratings'],game['negative_ratings'] = getatt_byname('D:\\CSE6242\\final project\web\\app\static\steam.csv',game_dict['names'][i])
        game['goodrate'] = float(game['positive_ratings']*1.0 /(game['positive_ratings']+game['negative_ratings']))
        game['id'] = str(game['id'])
        game['symbolSize'] = depth * 15
        if game['price'] == 0:
            game['category'] = 0
        elif game['price'] < 10:
            game['category'] =1
        elif game['price'] < 20:
            game['category'] =2
        else:
            game['category'] =3
        gamelist.append(game)
        link = {}
        if i == 0:
            source =gamelist[i]['id']
        else:
            link['source'] = source
            link['target'] = gamelist[i]['id']
            links.append(link)
    return gamelist,links
def find_all_genres(games):
    genre = set()
    for i in range(len(games)):
        genre.add(games[i]['genres'])
    return genre
def store_all_game(games):
    gamelist = []
    gamename = []
    links = []
    game_set= set()
    source = '730'
    for i in range(len(games)):
        g,l = get_recom(games[i],3)
        for k in range(len(g)):
            if g[k]['name'] not in game_set and g[k]['name'] not in gamename:
                gamelist.append(g[k])
                gamename.append(g[k]['name'])
                if k !=0:
                    link ={}
                    link['source'] = source
                    link['target'] = g[k]['id']
                    links.append(link)
                else:
                    source = g[k]['id']
        game_set.add(games[i])#存的是name
    length= len(gamelist)
    game_2 =set()
    for j in range(length): 
        if gamelist[j]['name']  not in game_set and gamelist[j]['name'] not in game_2:
            game_set.add(gamelist[j]['name'])#去重
            g,l = get_recom(gamelist[j]['name'],2)
            game_2.add( gamelist[j]['name'])
            for k in range(len(g)):
                if g[k]['name'] not in game_set and  g[k]['name'] not in game_2 and g[k]['name']not in gamename:
                    gamelist.append(g[k])
                    gamename.append(g[k]['name'])
                    game_2.add( g[k]['name'])
                    link ={}
                    link['source'] = gamelist[j]['id']
                    link['target'] = g[k]['id']
                    links.append(link)
    leng = len(gamelist)
    print(game_set)
    for j in range(length,leng): 
        if gamelist[j]['name']  not in game_set:
            game_set.add(gamelist[j]['name'])#去重
            g,l = get_recom(gamelist[j]['name'],1)
            for k in range(len(g)):
                if g[k]['name'] not in game_set and g[k]['name'] not in gamename:
                    gamelist.append(g[k])
                    gamename.append(g[k]['name'])
                    game_set.add(g[k]['name'])
                    link ={}
                    link['source'] = gamelist[j]['id']
                    link['target'] = g[k]['id']
                    links.append(link)
    print(game_set)
    # print("最后",links)
    dic = {}
    dic['nodes'] = gamelist
    dic['links'] = links
    categories = []
    genre = find_all_genres(gamelist)
    for i in genre:
        game_tag = {}
        game_tag['name']=i
        categories.append(game_tag)
    dic['categories'] = categories
    # print("dic",dic)
    return dic

def writetojson(dic):
    dict_json = json.dumps(dic,ensure_ascii=False)
    with open("D:\\CSE6242\\final project\web\\app\static\steam.json", 'w+') as file:
        file.write(dict_json)
# dic = store_all_game(['Counter-Strike: Global Offensive'])
# writetojson(dic)
def whatif(name,change,require):
    # url = "http://118.195.235.177:5000/recommendation?name="+name+"&topk=5"
    params = {}
    params["name"] = name
    params["change"] = change
    params["require"] = require
    url = "http://118.195.235.177:5000/whatif"
    res=requests.post(url=url,json=params)
    
    response=eval(res.text)
    content=res.text.encode('utf-8').decode('utf-8')
    game_dict=json.loads(content)
    return response
##如何使用whatif函数
name = "Day of Defeated"
change = {"release_year":"+11","required_age" :"=18"}
require = ["price","positive_ratings" ,"negative_ratings","median_playtime","owners bot","owners_top"]
content = whatif(name,change,require)
print(content)
print(content['result']['price'])