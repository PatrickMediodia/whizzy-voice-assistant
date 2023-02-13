#Main Imports
import os
import time
import threading
from ALSA_handler import noalsaerr
from text_to_speech import get_response
from speech_to_text import speech_to_text
from picovoice.detect_hotword import detect_hotword
from API_requests import get_logged_in, logout_user
from whizzy_avatar import initialize_avatar, set_mode_text, whizzy_speak, set_show_mic_state

#Interactive Discussion
from interactive_discussion import start_interactive_discussion

#Web Searching
from google_assistant.google_assistant import start_google_assistant

#Smart Controls
from smart_controls.smart_controls import initialize_devices, start_smart_controls, turn_off_devices

modes = (
    'web searching',
    'smart control',
    'interactive discussion'
)

mode_map = {
    'web searching': start_google_assistant,
    'smart control': start_smart_controls,
    'interactive discussion': start_interactive_discussion
}

current_mode = modes[1]

#new thread for avatar
initialize_avatar_thread = threading.Thread(target=initialize_avatar, daemon=True)
initialize_avatar_thread.name = 'Initialize avatar'
initialize_avatar_thread.start()

set_mode_text('Waiting for login')
new_login = True

def change_mode(command):
    global current_mode
    
    if 'switch' in command or 'change' in command:
        for mode in modes:
            if mode in command:
                if current_mode != mode:
                    current_mode = mode
                    set_mode_text(mode)
                    whizzy_speak(f'Switched to {mode}')
                    return True
                
                elif current_mode == mode:
                    whizzy_speak(f'Already in {current_mode} mode')
                    return True
    return False

def logout():
    set_show_mic_state(False)
    whizzy_speak(get_response('exit'))
                
    turn_off_devices()
    logout_user()
                    
    print('\nLogged out')
    set_mode_text('Waiting for login')
    
def main():
    global current_mode, new_login
    
    #check if logged into classroom
    if not get_logged_in():
        if new_login:
            print('\nWaiting for login .....\n')
            new_login = False
        return
    
    #start after authentication
    set_mode_text('Logged in')
    whizzy_speak('Logged in, welcome')
    
    #initializing devices in the classroom
    print('\nInitializing devices ......\n')
    initialize_devices()
    
    #initial speech of Whizzy
    time.sleep(5)
    whizzy_speak(get_response('entrance'))
    set_mode_text(current_mode)
    
    while True:
        print(f'\n{threading.enumerate()}')
        print(f'\nCurrent mode: {current_mode}')
            
        # accepting triggger of input
        set_show_mic_state(True)
        
        if detect_hotword():
            command = speech_to_text()
            
            #command is empty, ignore
            if command == '':
                #whizzy_speak(get_response('unknownValueError')) (uncomment if using vosk)
                continue
            
            #cancel the current command
            elif 'cancel' in command:
                whizzy_speak(get_response('cancel'))

            #change modes
            elif change_mode(command) == True:
                continue
            
            #to get the current mode of Whizzy
            elif 'current' and 'mode' in command:
                whizzy_speak(f'Currently I am in the {current_mode} mode')
                
            #exit message and turn off devices
            elif command == 'logout':
                logout()
                new_login = True
                break
            
            #send command to current mode
            else:
                mode_map[current_mode](command)
                
if __name__ == '__main__':
    with noalsaerr():
        while True:
            time.sleep(3)
            main()