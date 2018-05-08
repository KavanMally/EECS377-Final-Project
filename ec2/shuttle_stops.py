#!/usr/bin/python
import unirest 
import json 

def fun(d):
    if 'name' in d:
        yield d['name'].encode("utf-8")

response = unirest.get("https://transloc-api-1-2.p.mashape.com/stops.json?agencies=1199",
  headers={
    "X-Mashape-Key": "LJJSa7y5V6mshHSJB4rKmlbBon5cp1tUfZ7jsn0iEqV4YsNNvK",
    "Accept": "application/json"
  }
)

for x in response.body['data']:
    print list(fun(x))
