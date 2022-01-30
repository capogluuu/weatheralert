import json
import requests
from base64 import b64encode
from config import Config 


class alertus_api_func():
    def __init__(self, numberAlert, text = "ALERT", priority = 0, alertProfileId=0,
                clientName="string",alertProfileName="string", 
                clientVersion="string",durationSeconds=0 ):

        #from config file
        self.alertus_api_url  = Config.alertus_api_url    
        self.auto_username    = Config.alertus_auto_username
        self.auto_password    = Config.alertus_auto_password
        self.sender           = Config.alertus_sender
        self.content_type     = Config.alertus_content_type
        self.presentId        = Config.alertus_presentId 
        self.presentName      = Config.alertus_presentName

        #from class variable
        self.numberAlert      = numberAlert
        self.text             = text
        self.priority         = priority
        self.alertProfileId   = alertProfileId
        self.clientName       = clientName
        self.alertProfileName = alertProfileName
        self.durationSeconds  = durationSeconds
        self.clientVersion    = clientVersion

    def post_request(self):
        response = "Invalid Request"
        resp = requests.post(f"{self.alertus_api_url}",
            headers={"Content-Type": self.content_type,"Authorization": self.create_auto_code()},
            data=json.dumps({
                    "durationSeconds": self.durationSeconds, "clientVersion": self.clientVersion,
                    "alertProfileName": self.alertProfileName, "sender": self.sender,
                    "clientName": self.clientName, "alertProfileId": self.alertProfileId,
                    "presetId": self.presentId, "presetName": self.presentName,
                    "priority": 0, "text": f"{self.text}: {self.numberAlert} time"}))

        response = resp.text
        
        return response
        

    def create_auto_code(self):
        BasicAuto = b64encode((f"{self.auto_username}:{self.auto_password}").encode()).decode("ascii")
        return f"Basic {BasicAuto}"
