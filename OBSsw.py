import time
import json 
import obsws_python as obs

Pactive = False

if Pactive is True:
    #config OBS websocket here...
    cl = obs.ReqClient(host='localhost', port=4000)
    
    resp = cl.send("GetSceneList", raw=True)
    BackScene = resp["currentProgramSceneName"]

def EASin():
    if Pactive is True:
        cl.set_current_program_scene("EAS")

def EASout():
    if Pactive is True:
        cl.set_current_program_scene(BackScene)