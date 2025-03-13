from PIserver.clients.net import send_post_request
import time
import json
import requests
import threading

class LLMClient:
    def __init__(self, host):
        self.host = host
        self.response = None
    
    def make_resData_stream(self, data, chat=False, time_now = 0, start=False):
        resData = {
            "id": "chatcmpl" if (chat) else "cmpl",
            "object": "chat.completion.chunk" if (chat) else "text_completion.chunk",
            "created": time_now,
            "model": "LLaMA_CPP",
            "choices": [
                {
                    "finish_reason": None,
                    "index": 0
                }
            ]
        }
        # slot_id = data["slot_id"]
        if (chat):
            if (start):
                resData["choices"][0]["delta"] =  {
                    "role": "assistant"
                }
            else:
                resData["choices"][0]["delta"] =  {
                    "content": data["content"]
                }
                if (data["stop"]):
                    resData["choices"][0]["finish_reason"] = "stop" if (data["stopped_eos"] or data["stopped_word"]) else "length"
        else:
            resData["choices"][0]["text"] = data["content"]
            if (data["stop"]):
                resData["choices"][0]["finish_reason"] = "stop" if (data["stopped_eos"] or data["stopped_word"]) else "length"

        return resData
    
    def generate(self, data):
        self.response = requests.post(self.host, json.dumps(data), stream=True)
        time_now = int(time.time())
        resData = self.make_resData_stream({}, chat=True, time_now=time_now, start=True)
        yield '{}\n'.format(json.dumps(resData))
        for line in self.response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                resData = self.make_resData_stream(json.loads(decoded_line[6:]), chat=True, time_now=time_now)
                yield '{}\n'.format(json.dumps(resData))
                
    def close(self):
        self.response.close()

class StopHandler():
    def __init__(self):
        self.stopper = threading.Event()
        self.thread = threading.Thread(target=self.keyboard_listener)
        
    def keyboard_listener(self):
        while not self.stopper.is_set():
            if input("") == ':':
                self.stopper.set()
                break
            
    def start(self):
        self.thread.start()

    def stop(self):
        if not self.stopper.is_set():
            self.stopper.set()
            self.thread.join()
        
    def has_stoppend(self):
        return self.stopper.is_set()