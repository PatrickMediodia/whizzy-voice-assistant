import os
import logging
import json

import click
import sounddevice as sd
import google.oauth2.credentials
import google.auth.transport.grpc
import google.auth.transport.requests

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)

try:
    from . import (
        assistant_helpers,
        audio_helpers,
        browser_helpers,
    )
except (SystemError, ImportError):
    import assistant_helpers
    import audio_helpers
    import browser_helpers

#import avatar
from whizzy_avatar import whizzy_speak, change_avatar_state

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5
PLAYING = embedded_assistant_pb2.ScreenOutConfig.PLAYING

class GoogleAssistant(object):  
    def __init__(self, language_code, device_model_id, device_id,
                 display, channel, deadline_sec):
        self.language_code = language_code
        self.device_model_id = device_model_id
        self.device_id = device_id
        self.conversation_state = None
        self.is_new_conversation = True
        self.display = display
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(channel)
        self.deadline = deadline_sec

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False

    def assist(self, text_query):
        def iter_assist_requests():
            config = embedded_assistant_pb2.AssistConfig(
                audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=16000,
                    volume_percentage=0,
                ),
                dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                    language_code=self.language_code,
                    conversation_state=self.conversation_state,
                    is_new_conversation=self.is_new_conversation,
                ),
                device_config=embedded_assistant_pb2.DeviceConfig(
                    device_id=self.device_id,
                    device_model_id=self.device_model_id,
                ),
                text_query=text_query,
            )
            self.is_new_conversation = False
            if self.display:
                config.screen_out_config.screen_mode = PLAYING
            req = embedded_assistant_pb2.AssistRequest(config=config)
            assistant_helpers.log_assist_request_without_audio(req)
            yield req
        
        output_audio_file = 'audio/out.wav'
        audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
        audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
        
        #configured conversation stream
        audio_device = None
        audio_source = audio_device = (
            audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE,
                sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
                block_size=audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
                flush_size=audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
            )
        )
      
        if output_audio_file:
            audio_sink = audio_helpers.WaveSink(
                open(output_audio_file, 'wb'),
                sample_rate=audio_sample_rate,
                sample_width=audio_sample_width
            )
        else:
            audio_sink = audio_device = (
                audio_device or audio_helpers.SoundDeviceStream(
                    sample_rate=audio_sample_rate,
                    sample_width=audio_sample_width,
                    block_size=audio_block_size,
                    flush_size=audio_flush_size
                )
            )
        
        conversation_stream = audio_helpers.ConversationStream(
            source=audio_source,
            sink=audio_sink,
            iter_size=audio_helpers.DEFAULT_AUDIO_ITER_SIZE,
            sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
        )
        
        text_response = None
        html_response = None
        for resp in self.assistant.Assist(iter_assist_requests(),
                                          self.deadline):
            assistant_helpers.log_assist_response_without_audio(resp)
            if resp.screen_out.data:
                html_response = resp.screen_out.data
            if resp.dialog_state_out.conversation_state:
                conversation_state = resp.dialog_state_out.conversation_state
                self.conversation_state = conversation_state
            if resp.dialog_state_out.supplemental_display_text:
                text_response = resp.dialog_state_out.supplemental_display_text
                '''
                print(f'Transcript of response: {text_response}')
                whizzy_speak(text_response)
                conversation_stream.stop_recording()
                conversation_stream.stop_playback()
                break
                '''
            
            #added sound output
            if len(resp.audio_out.audio_data) > 0:
                if not conversation_stream.playing:
                    conversation_stream.stop_recording()
                    conversation_stream.start_playback()
                    print('Playing assistant response.....')
                conversation_stream.write(resp.audio_out.audio_data)
                
        conversation_stream.stop_playback()
        conversation_stream.close()
        
        return text_response, html_response

def main(command, device_model_id, device_id):
    lang = 'en-US'
    display = False
    verbose = False
    grpc_deadline = DEFAULT_GRPC_DEADLINE
    api_endpoint = ASSISTANT_API_ENDPOINT
    credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'), 'credentials.json')
    
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        return

    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, api_endpoint)
    
    from pygame import mixer
    
    with GoogleAssistant(lang, device_model_id, device_id, display,
                             grpc_channel, grpc_deadline) as assistant:
        response_text, response_html = assistant.assist(text_query=command)
        if display and response_html:
            system_browser = browser_helpers.system_browser
            system_browser.display(response_html)
        
        if response_text:
            print(f'Transcript of response: {response_text}')
            whizzy_speak(response_text)
            
        else:
            #play audio
            mixer.init()
            mixer.music.load("audio/out.wav")
            #change_avatar_state(True) #start avatar talking
            mixer.music.play()
            #change_avatar_state(False) #stop avatar talking
            os.remove("audio/out.wav")