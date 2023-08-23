import os, shutil, time, sys, pathlib, re, requests
from datetime import datetime, timezone
from EASGen import EASGen
from EAS2Text import EAS2Text
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
from urllib.request import Request, urlopen

#TTS that will workies across OSes
import pyttsx3

# Overall TODO
# [x] Generate a SAME header system
#   [-] complete the CAPCP Geocodes to SAME CLC conversion
# [x] Complete Heartbeat processor
# [x] Implement a config system
# [-] Audio Playout/Pass thru system
# [X] Complete the QuantumENDEC.py code that starts everything

# Test commit from VScode

def GenTTS(stringy):
        print("Generating TTS...")
        engine = pyttsx3.init()
        engine.save_to_file(str(stringy), "Audio/audio.wav")
        engine.runAndWait()

class Check:
    def __init__(self):
        pass

    def GetXMLQue(self):
        return os.listdir("./XMLqueue")
        
    def ReadRelayXML(self):
        with open("./relay.xml", "r") as f:
            file = str(f.read())
            f.close()
            
        return file

    def start(self):
        while True:
            ExitTicketCheck = "False"
            # Main for loop for files in /XMLqueue
            print("Waiting for alert...")
            for file in self.GetXMLQue():
                # We have a file here and need to do stuff with it
                print(f"New alert: ({file})")

                # Copy it to XMLhistory
                if file in os.listdir("./XMLhistory"):
                    print("Files matched... no relay...")
                    os.remove(f"./XMLqueue/{file}")
                    exit()
                
                shutil.copyfile(f"./XMLqueue/{file}", f"./XMLhistory/{file}")

                # Create the relay.xml file
                shutil.copyfile(f"./XMLqueue/{file}", f"./relay.xml")

                os.remove(f"./XMLqueue/{file}")
                ExitTicketCheck = "True"
                break

            if 'True' in ExitTicketCheck:
                break
            else:
                pass

            # Wait a little bit between looking for new files 
            time.sleep(2)
        return file
        
    # working on this on test.py... will be overridden!
    def Heartbeat(self):
        References = re.search(r'<references>\s*(.*?)\s*</references>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        RefList = References.split(" ")
        for i in RefList:
            j = re.sub(r'^.*?,', '', i)
            j = j.split(",")
            sent = j[1]
            sentDT = sent.split("T", 1)[0]
            sent = sent.replace("-","_").replace("+", "p").replace(":","_")
            identifier = j[0]
            identifier = identifier.replace("-","_").replace("+", "p").replace(":","_")
            
            Dom1 = 'capcp1.naad-adna.pelmorex.com'
            Dom2 = 'capcp2.naad-adna.pelmorex.com'
            Output = f"XMLqueue/{sent}I{identifier}.xml"

            if f"{sent}I{identifier}.xml" in os.listdir("./XMLhistory"):
                print("Files matched... no Heartbeat download...")
                pass
            else:
                req1 = Request(
                    url = f'http://{Dom1}/{sentDT}/{sent}I{identifier}.xml', 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                req2 = Request(
                    url = f'http://{Dom2}/{sentDT}/{sent}I{identifier}.xml', 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                try:
                    xml = urlopen(req1).read()
                except:
                    try:
                        xml = urlopen(req2).read()
                    except:
                        pass
                f = open(Output, "wb")
                f.write(xml)
                f.close()
        exit()
    
    def ConfigFilters(self):
        def CapAllowsCheck(stat):
            if ConfigData[stat] is True:
                print("allowed")
            else:
                print("not allowed, exiting")
                exit()

        CapAllowsCheck(re.search(r'<status>\s*(.*?)\s*</status>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1))
        CapAllowsCheck(re.search(r'<severity>\s*(.*?)\s*</severity>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1))
        CapAllowsCheck(re.search(r'<urgency>\s*(.*?)\s*</urgency>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1))
        
        if len(ConfigData['AllowedLocations_Geocodes']) == 0:
            pass
        else:
            Geocodes = re.findall(r'<geocode><valueName>profile:CAP-CP:Location:0.3</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            GeoMatch = False
            for i in Geocodes:
                if i in ConfigData['AllowedLocations_Geocodes']:
                    GeoMatch = True
            if GeoMatch is True:
                pass
            else:
                exit()

# TODO complete this
class Generation:
    def __init__(self):
        pass
        
    def start(self):
        import Conversions
        file = open("relay.xml", "r")
        RelayXML = "".join(line.strip() for line in file.read().splitlines())
        file.close()
        InfoEN = re.search(r'<info><language>en-CA</language>\s*(.*?)\s*</info>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)

        ORG = re.search(r'<category>\s*(.*?)\s*</category>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        try:
            ORG = Conversions.CapCatToSameOrg[ORG]
        except:
            ORG = "CIV"

        if("<valueName>SAME</valueName>" in InfoEN):
            EEE = re.search(r'<eventCode><valueName>SAME</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        else:
            EEE = re.search(r'<event>\s*(.*?)\s*</event>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            try:
                EEE = Conversions.CapEventToSameEvent[EEE]
            except:
                EEE = "CEM"

        # TODO: just complete the Conversions.py "CapGeocodesToSameCLC" thingy
        # also this is a little nasty but it works and don't gotta crap about global vars
        
        def GeoToCLC():
            Geocodes = re.findall(r'<geocode><valueName>profile:CAP-CP:Location:0.3</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            filepath = './GeoToCLC.csv'
            SameDict = {}
            with open(filepath) as fp:
                line = fp.readline()
                cnt = 1
                while line:
                    line = line.replace('\n', '')
                    SAMESPLIT = line.split(",")
                    SameDict[SAMESPLIT[0]] = SAMESPLIT[1]
                    line = fp.readline()
                    cnt += 1
            CLC = ""
            for i in Geocodes:
                try:
                    C = SameDict[i]
                except:
                    C = ""
                if C == "":
                    pass
                else:
                    CLC = f"{CLC}" + f"{C},"
            # Aaron i know you're kinda gonna cringe at this, but we need it
            CLC = "".join(CLC.rsplit(",",1))
            CLC = CLC.split(",")
            CLC = "-".join(CLC)
            CLC = CLC.split("-")
            CLC = list(set(CLC))
            CLC = "-".join(CLC)
            return CLC
    
        if("EC-MSC-SMC:1.1:Newly_Active_Areas" in InfoEN):
            try:
                CLC = re.search(r'<parameter><valueName>layer:EC-MSC-SMC:1.1:Newly_Active_Areas</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace(",","-")
            except:
                CLC = GeoToCLC()
        else:
            CLC = GeoToCLC()
        if CLC == "":
            CLC = "000000"

        if("<effective>" in InfoEN):
            EffDate = re.search(r'<effective>\s*(.*?)\s*</effective>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            DT = datetime.fromisoformat(datetime.fromisoformat(EffDate).astimezone(timezone.utc).isoformat()).strftime("%j%H%M")
        else:
            DT = datetime.now()
            DT = DT.strftime("%j%H%M")

        GeneratedHeader = f"ZCZC-{ORG}-{EEE}-{CLC}+0600-{DT}-{Callsign}-"
        print(GeneratedHeader)
        
        # wow this is a little ulgy but it works...
        # makes sure not to relay a previous same SAME header
        # no two SAMEs can be the same
        try:
            f = open('SameHistory.txt', 'r')
        except:
            with open("SameHistory.txt", "a") as f:
                f.write(f"ZXZX-STARTER-\n")
            f.close()
            f = open('SameHistory.txt', 'r')
        if GeneratedHeader in f.read():
            print("Found previous SAME header match... exiting...")
            f.close()
            exit()
        f.close()
        with open("SameHistory.txt", "a") as f:
            f.write(f"{GeneratedHeader}\n")
        
        #prepare for playout
        Header = EASGen.genEAS(header=GeneratedHeader, attentionTone=False, endOfMessage=False)
        Eom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav("Audio/same.wav", Header)
        EASGen.export_wav("Audio/eom.wav", Eom)
        
        # switch to determine if to use alert ready attention tone or not based on an XML tag
        BroadI = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Immediately</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        if("Yes" in BroadI):
            shutil.copyfile("Audio/AlertReadyTone.wav", "Audio/attn.wav")
        else:
            shutil.copyfile("Audio/1050.wav", "Audio/attn.wav")

        #Generate the BroadcastText
        if("<valueName>layer:SOREM:1.0:Broadcast_Text</valueName>" in InfoEN):
            BroadcastText = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Text</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        else:
            #Manually generates the BroadcastText if there's no broadcast text value
            Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            DATE = datetime.fromisoformat(Sent).strftime("%H:%M UTC, %B %d, %Y.")
            SENDER = re.search(r'<senderName>\s*(.*?)\s*</senderName>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            HEADLINE = EAS2Text(GeneratedHeader).evntText
            if("layer:EC-MSC-SMC:1.0:Alert_Coverage" in InfoEN):
                regexcoverage = re.search(r'<valueName>layer:EC-MSC-SMC:1.0:Alert_Coverage</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                COVERAGE = f"In {regexcoverage} for:"
            else:
                COVERAGE = "For:"
            
            if("EC-MSC-SMC:1.1:Newly_Active_Areas" in InfoEN):
                try:
                    regexnewactive = re.search(r'<parameter><valueName>layer:EC-MSC-SMC:1.1:Newly_Active_Areas</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    if(len(regexnewactive) == 0):
                        AREAS = re.findall(r'<areaDesc>\s*(.*?)\s*</areaDesc>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                        AREAS = ", ".join(AREAS)
                    else:
                        AREAS = ""
                        updatedLocations = regexnewactive.split(",")
                        CLC = re.findall(r'<area><areaDesc>\s*(.*?)\s*</areaDesc><polygon>.*?</polygon><geocode><valueName>layer:EC-MSC-SMC:1\.0:CLC</valueName><value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                        for CLCLocation in CLC:
                            if(CLCLocation[1] in updatedLocations):
                                AREAS += f"{CLCLocation[0]}, "
                except:
                    AREAS = re.findall(r'<areaDesc>\s*(.*?)\s*</areaDesc>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    AREAS = ", ".join(AREAS)
            else:
                AREAS = re.findall(r'<areaDesc>\s*(.*?)\s*</areaDesc>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                AREAS = ", ".join(AREAS)
            AREAS = ".".join(AREAS.rsplit(",",1))
            AREAS = AREAS + "."
            try:
                DESCRIPTION =  re.search(r'<description>\s*(.*?)\s*</description>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("###","")
            except:
                DESCRIPTION = ""
            
            try:
                INSTRUCTION =  re.search(r'<instruction>\s*(.*?)\s*</instruction>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("###","")
            except:
                INSTRUCTION = ""
            
            BroadcastText = f"At {DATE} {SENDER} has issued {HEADLINE} {COVERAGE} {AREAS} {DESCRIPTION}. {INSTRUCTION}."

        #Generate PlayoutAudio
        print("Generating playout audio...")
        if("<resourceDesc>Broadcast Audio</resourceDesc>" in InfoEN):
            #TODO there has to be a better way of detecting how to downlaod/decode the audio file
            print("Downloading broadcast audio...")
            BcAuR = re.search(r'<resource><resourceDesc>Broadcast Audio</resourceDesc>\s*(.*?)\s*</resource>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)
            URIaudio = re.search(r'<uri>\s*(.*?)\s*</uri>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            if("https://" in URIaudio):
                os.system(f"ffmpeg -hide_banner -loglevel warning -y -i {URIaudio} -filter:a 'volume=3.5' -ac 1 Audio/audio.wav")
            else:
                print("Screw that, generating TTS")
                GenTTS(BroadcastText)
        else:
            GenTTS(BroadcastText)
        
        if ConfigData['enable_discord_webhook'] is True:
            print("Sending to discord webhook...")
            webhook = DiscordWebhook(url=WebhookURL, rate_limit_retry=True, content=GeneratedHeader)
            embed = DiscordEmbed(title="EMEGRENCY ALERT // ALERTE D'URGENCE", description=BroadcastText, color=Color,)
            embed.set_author(name=AuthorName, url=AuthorURL, icon_url=AuthroIconURL)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/589599667323404288/1091540081497624716/QuantumENDEC_Logo.png?width=467&height=467")
            embed.set_footer(text="QuantumENDEC 2: The Python Edition")
            webhook.add_embed(embed)
            webhook.execute()
        
        f = open("Broadcast.txt", "w")
        f.write(BroadcastText)
        f.close()

Check = Check()
Generation = Generation()

#This is the beginning, only checking the XMLqueue
alertfile = Check.start()
print(alertfile)
print("Start the relay process...")

#configs the config
with open("config.json", "r") as JCfile:
    config = JCfile.read()
    JCfile.close()
ConfigData = json.loads(config)
Color = ConfigData['webhook_color']
AuthorName = ConfigData['webhook_author_name']
AuthorURL = ConfigData['webhook_author_URL']
AuthroIconURL = ConfigData['webhook_author_iconURL']
WebhookURL = ConfigData['webhook_URL']
Callsign = ConfigData['SAME_callsign']
if len(Callsign) > 8:
    Callsign = "QUANTUM0"
    print("Callsign contains an error, please check config... Too long")
elif len(Callsign) < 8:
    Callsign = "QUANTUM0"
    print("Callsign contains an error, please check config... Too short")
elif "-" in Callsign:
    Callsign = "QUANTUM0"
    print("Callsign contains an error, please check config... Invalid symbol")

file = open("relay.xml", "r")
RelayXML = "".join(line.strip() for line in file.read().splitlines())
file.close()

if("<sender>NAADS-Heartbeat</sender>" in RelayXML):
    print("Heartbeat detected, running heartbeat processor...")
    os.remove(f"./XMLhistory/{alertfile}")
    Check.Heartbeat()
else:
    InfoEN = re.search(r'<info><language>en-CA</language>\s*(.*?)\s*</info>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(0)
    print("Checking config filter...")
    Check.ConfigFilters()
    print("Starting Generation...")
    Generation.start()


print("Playing out alert")

#All is playout below
UseSpecDevice = ConfigData['UseSpecifiedAudioDevice']
SpecDevice = ConfigData['SpecifiedAudioDevice']
MuteV = ConfigData['MuteVirturalAudioCable']
Vcable = ConfigData['VirturalAudioCable']

# mute V
if MuteV is True:
    os.system(f"pactl set-sink-mute {Vcable} 1")

time.sleep(0.5)

# TODO: (Later, find a better way of playing the audio cross platform and on a specific device)

# play pre
if os.path.exists("./Audio/pre.wav"):
    print("Playing Pre Audio")
    os.system("ffplay -hide_banner -loglevel warning -nodisp -autoexit ./Audio/pre.wav")

# play same
print("Playing SAME Tones")
os.system("ffplay -hide_banner -loglevel warning -nodisp -autoexit ./Audio/same.wav")

# play attn
print("Playing ATTN Tone")
os.system("ffplay -hide_banner -loglevel warning -nodisp -autoexit ./Audio/attn.wav")

# play audio
print("Playing Main Audio")
os.system("ffplay -hide_banner -loglevel warning -nodisp -autoexit ./Audio/audio.wav")

# play eom
print("Playing EOM Tones")
os.system("ffplay -hide_banner -loglevel warning -nodisp -autoexit ./Audio/eom.wav")

# unmute V
if MuteV is True:
    os.system(f"pactl set-sink-mute {Vcable} 0")

# end of code