'''
Must be ran with admin priviledges
Add to task scheduler on user login
'''

import os
import socket
import threading
from dotenv import load_dotenv
from blackboard import open_blackboard
from msteams.teams import open_teams, close_teams

load_dotenv()

#static IP address and port
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))

application_instance = {
    'teams' : None,
    'blackboard' : None,
}

def server():
    global application_instance
    
    try: 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            print("Server has started, waiting for client to connect")
            s.listen(5)
            connection, address = s.accept()

            with connection:
                print(f'Connection established with address : {address}')
                data = str(connection.recv(1024).decode('utf-8'))
                command, token, user_id = data.split(',') # command,token,user_id
                message = 'Application not found'
                    
                if 'open' in command:
                    if 'blackboard learn' in command:
                        threading.Thread(target=open_blackboard, daemon=True, args=[token, user_id, application_instance]).start()
                        message = 'blackboard learn has been opened'

                    elif 'microsoft teams' in command:
                        threading.Thread(target=open_teams, daemon=True, args=[token, user_id]).start()
                        application_instance['teams'] = 'Open'
                        message = 'microsoft teams has been opened'

                elif 'close' in command:
                    if 'blackboard learn' in command:
                        if application_instance['blackboard'] is None:
                            message = 'blackboard learn is not open'
                        else:
                            application_instance['blackboard'].close()
                            message = 'blackboard has been closed'

                    elif 'microsoft teams' in command:
                        if application_instance['teams'] is None:
                            message = 'microsoft teams learn is not open'
                        else:
                            close_teams()
                            application_instance['teams'] = None
                            message = 'microsoft teams has been closed'

                connection.sendall(message.encode('utf-8'))
    except Exception as e:
        print(e)
        pass

if __name__ == '__main__':
    print('Trying to start connection ......')
    while True:
        server()