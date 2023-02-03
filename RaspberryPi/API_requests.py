import os
import json
import requests
from models.account import Account
from models.userData import UserData

room_number = os.environ.get('ROOM_NUMBER')
token = os.environ.get('BEARER_TOKEN')
url = os.environ.get('URL')

user_id = None
room_logged_in_id = None

def get_logged_in():
    global user_id, room_logged_in_id
    
    end_point = url + 'users?'
    end_point += 'populate=room_logged_in'
    end_point += f'&filters[room_logged_in][room][$eq]={room_number}'
    end_point += '&filters[room_logged_in][status][$eq]=True'
    
    headers = { 'Authorization': 'Bearer ' + token }
    
    response = requests.request("GET", end_point, headers=headers)
    logged_in_user = json.loads(response.text)
    
    #check if a user is logged in
    if len(logged_in_user) > 0:
        #store user id
        for user in logged_in_user:
            print(f'Logged in: {user["full_name"]}')
            user_id = user['id']
            room_logged_in_id = user['room_logged_in']['id']
        return True
    
    return False

def logout_user():
    global user_id, room_logged_in_id
    
    end_point = url + f'users/{user_id}'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "room_logged_in" : {
            "id" : room_logged_in_id,
            "room": None,
            "status": False
            }
        })
    
    response = requests.request("PUT", end_point, headers=headers, data=payload)
    
    user_id = None
    room_logged_in_id = None

def get_user_id():
    return user_id

def get_user_data():
    end_point = url + f'users/{user_id}?'
    end_point += 'populate[0]=courses'
    end_point += '&populate[1]=courses.modules'
    end_point += '&populate[2]=courses.modules.lessons'
    end_point += '&populate[4]=courses.modules.lessons.trivias'
    end_point += '&populate[3]=courses.modules.lessons.questions'
    end_point += '&fields=id,username,email'
    
    headers = { 'Authorization': 'Bearer ' + token }
    
    response = requests.request("GET", end_point, headers=headers)
    user_data_dict = json.loads(response.text)
    user_data_object = UserData(**user_data_dict)

    return user_data_object

def get_room_device_data():
    end_point = url + 'rooms?'
    end_point += 'populate=devices'
    end_point += f'&filters[name][$eq]={room_number}'
    
    headers = { 'Authorization': 'Bearer ' + token }
    
    response = requests.request("GET", end_point, headers=headers)
    room_device_data = json.loads(response.text)

    for data in room_device_data['data']:
        return data['attributes']['devices']['data']

    return None

def get_device_status(device_id):
    end_point = url + f'devices/{device_id}'

    headers = { 'Authorization': 'Bearer ' + token }

    response = requests.request("GET", end_point, headers=headers)
    device_status = json.loads(response.text)

    return device_status['data']

def set_device_status(device_id, status):
    end_point = url + f'devices/{device_id}'

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({ "data" : { "status" : status } })

    response = requests.request("PUT", end_point, headers=headers, data=payload)
    device_status_response = json.loads(response.text)

    return device_status_response['data']

def set_device_connectivity(device_id, connected):
    end_point = url + f'devices/{device_id}'

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    payload = json.dumps({ "data" : { "connected" : connected } })

    response = requests.request("PUT", end_point, headers=headers, data=payload)
    device_status_response = json.loads(response.text)

    return device_status_response['data']

def get_local_account_credentials():
    end_point = url + f'users/{user_id}'
    end_point += '?populate=local'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", end_point, headers=headers)
    response_json = json.loads(response.text)
    
    return response_json['local']