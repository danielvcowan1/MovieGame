import http.client
from api_key import api_key
from api_calls import * 
import time 

input_data = open("actors_list.txt", "r")
data = input_data.readlines()
input_data.close()

transfer_list = []

for actor in data: 
    actor = actor.strip() 
    transfer_list.append(actor)

counter = 0 
actors_dict = {}


for actor in transfer_list:
    if counter==40:
        time.sleep(10)
        counter=0

    request = search_actor(actor)
    request_final = get_json(request)
    
    
    actor_name = request_final['results'][0]["name"]
    known_for =  request_final['results'][0]["known_for"][0]['title']
    actor_id = request_final['results'][0]['id']
    print(actor_name) 
    print(known_for) 
    print(actor_id)

    actors_dict[actor_name] = {}
    actors_dict[actor_name]["known_for"] = known_for
    actors_dict[actor_name]["id"] = actor_id 
    counter +=1

print(actors_dict)



