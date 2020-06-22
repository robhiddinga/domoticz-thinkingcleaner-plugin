#           Domoticz ThinkingCleaner Plugin for Roomba
#
#           Author:     RobH 2020.
#
"""
<plugin key="ThinkingCleaner" name="Thinking Cleaner" author="RobH" version="0.8.0" wikilink="https://github.com/robhiddinga/domoticz-thinkingcleaner-plugin.git" externallink="http://www.thinkingcleaner.com">
    <params>
        <param field="Mode1" label="IP Address Thinking Cleaner" required="true" width="200px" />
        <param field="Mode2" label="IP Address Domoticz" required="true" width="200px" />
        <param field="Mode3" label="Port Domoticz" required="true" width="200px" />
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True"    value="Debug"/>
                <option label="False"   value="Normal" default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import sys
import json
import datetime
import requests
import urllib.request
import urllib.error

class BasePlugin:
    RoombaWorking       = True
    intervalCounter     = None
    name                = "Roomba"
    heartbeat           = 30
    battery             = 0
    state               = ""
    cleaning            = ""
    previousBattery     = 0
    previousState       = ""
    previousCleaning    = ""
    previousName        = "Roomba"

    def onStart(self):
        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        logDebugMessage(str(Devices))
        if (len(Devices) == 0):
            Domoticz.Device(Name=self.name,  Unit=1, TypeName="Custom", Options = { "Custom" : "1;%"}, Used=1).Create()

            logDebugMessage("Device " + self.name  + " created.")

        Domoticz.Heartbeat(self.heartbeat)
        self.intervalCounter = 0

        if ('RoombaOn' not in Images): Domoticz.Image('roombaVacuum.zip').Create()
        if ('RoombaOff' not in Images): Domoticz.Image('roombaVacuum.zip').Create()

        try:
         Devices[1].Update(0, sValue=str(Devices[1].sValue), Image=Images["RoombaOff"].ID)
        except:
            logDebugMessage("Error @ device create or exists allraedy.")

        return True


    def onHeartbeat(self):

        if self.intervalCounter == 1:

            ipAddress       = Parameters["Mode1"]
            jsonObject      = self.getStatus(ipAddress)
            logDebugMessage(str(jsonObject))
            status = self.isRoombaActive(jsonObject)
            logDebugMessage("Status = " + str(status))

            self.getRoombaStatusData(status, jsonObject)

            if (status != "Off"):

                self.updateDeviceCurrent()

                if (self.RoombaWorking == False):
                    self.RoombaWorking = True

            else:
                self.logErrorCode(jsonObject)

                if (self.RoombaWorking == True):
                    self.RoombaWorking = False
                    self.updateDeviceOff()


            self.intervalCounter = 0

        else:
            self.intervalCounter = 1
            logDebugMessage("Do nothing: " + str(self.intervalCounter))


        return True

    def getStatus(self, ipAddress):

        protocol = "http"
        port     = "80"
        url = protocol + "://" + ipAddress + ":" + port + "/status.json"
        logDebugMessage('Retrieve Roomba data from ' + url)

        try:
            req = urllib.request.Request(url)
            jsonData = urllib.request.urlopen(req).read()
            jsonObject = json.loads(jsonData.decode('utf-8'))
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logDebugMessage("Error: " + str(e) + " URL: " + url)
            return

        logDebugMessage("JSON: " + str(jsonData))

        return jsonObject

    def isRoombaActive (self, jsonObject):

        # Check what Roomba is doing

        logDebugMessage("JSON " + str(jsonObject))
        if str(jsonObject) == "None":
            logDebugMessage("No data from Roomba")
            return "Off"
        else:
            logDebugMessage("Data from Roomba ")
            s = str(jsonObject)
            if s.find('success') > 0:
              logDebugMessage("Data from Roomba " + s)
              return "Active"
            else:
              logDebugMessage("Roomba alive, but no status")
              return "Online"

    def getRoombaStatusData(self, status, jsonObject):

        if (status != "Off"):
           # Get the header data  when active or online
           self.name     = jsonObject["status"]["name"]
           self.battery  = jsonObject["status"]["battery_charge"]
           self.state    = jsonObject["status"]["cleaner_state"]
           self.cleaning = jsonObject["status"]["cleaning"]

        if (status == "Off"):
           # Use saved  data
           self.name     = self.previousName
           self.battery  = self.previousBattery
           self.state    = self.previousState
           self.cleaning = self.previousCleaning

    def logErrorCode(self, jsonObject):

        if str(jsonObject) == "None":
           code = 1
           reason = self.previousName + " is offline"

        else:
         code   = 0
         reason = jsonObject["result"]
         if (code == 0):
            reason = self.previousName + " is active, but no action"

        if (code != 0):
            logErrorMessage("Code: " + str(code) + ", reason: " + reason)

        return

    def stateBeautifier(self, state):

        status = state

        if state == "st_delayed":
            status = "Delayed%20vacuuming%20will%20start%20soon%20.."
        if state == "st_plug":
            status = "plugged%20in%20not%20charging"
        if state == "st_plug_recon":
            status = "plugged%20in%20reconditioning%20charging"
        if state == "st_plug_full":
            status = "plugged%20in%20full%20charging"
        if state == "st_plug_trickle":
            status = "plugged%20in%20trickle%20charging"
        if state == "st_plug_wait":
            status = "plugged%20in%20and%20waiting"
        if state == "st_base":
            status = "at%20home%20and%20not%20charging"
        if state == "st_remote":
            status = "remote%20waiting%20for%20command"
        if state == "st_wait":
            status = "remote%20and%20no%20command"
        if state == "st_off":
            status = "off"
        if state == "st_dock":
            status = "going%20home"
        if state == "st_cleanstop":
            status = "stopped%20vacuuming"
        if state == "st_stopped":
            status = "stopped"
        if state == "st_clean":
            status = "vacuuming%20your%20house"
        if state == "st_clean_spot":
            status = "spot%20cleaning%20your%20floor"
        if state == "st_clean_max":
            status = "max%20vacuuming%20your%20house"
        if state == "st_base_full":
            status = "at%20home%20and%20charging"
        if state == "st_base_recon":
            status = "at%20home%20and%20reconditioning%20charging"
        if state == "st_base_trickle":
            status = "at%20home%20and%20trickle%20charging"
        if state == "st_base_wait":
            status = "at%20home%20and%20waiting"
        if state == "st_picked":
            status = "beeing%20picked%20up"
        if state == "st_locate":
            status = "playing%20hide%20and%20seec"
        if state == "st_error":
            status = "in%20error.%20Waiting%20for%20you"
        if state == "st_unknown":
            status = "completely%20lost"

        return status

    def updateDeviceCurrent(self):
        # Device 1 - current status
        DOM_IP   = Parameters["Mode2"]
        DOM_PORT = Parameters["Mode3"]

        self.previousBattery = self.battery
        logDebugMessage("Current level " + str(self.battery))

        try:
         Devices[1].Update(self.battery, str(self.battery))
        except KeyError as e:
         cause = e.args[0]
         logErrorMessage("Cause " + str(cause))

        try:
         Devices[1].Update(self.battery, str(self.battery), Images["Roomba"].ID)
        except KeyError as e:
         cause = e.args[0]
         logErrorMessage("Cause " + str(cause))

        status = self.stateBeautifier(str(self.state))

        NAME = self.name + "%20is%20" + status
        DESC = status
        IDX  = 900

        # URL prep
        httpurl = "http://"+DOM_IP+":"+DOM_PORT+"/json.htm?type=setused&param=udevice&devoptions=1;%25&switchtype=General&used=true&idx="+str(IDX)+"&name="+str(NAME)+"&description="+str(DESC)
        logDebugMessage("http url " + str(httpurl))

        # Sending data to Domoticz
        r = requests.get(httpurl)
        logDebugMessage("Result " + str(r))



        return

    def updateDeviceOff(self):

        Devices[1].Update(0, "0", Images["RoombaOff"].ID)

        self.battery  = self.previousBattery
        self.state    = self.previousState
        self.cleaning = self.previousCleaning

    def onStop(self):
        logDebugMessage("onStop called")
        return True

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def logDebugMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "domoticz-thinkcleaner-plugin.log", "a")
        f.write("DEBUG - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Debug(message)

def logErrorMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "domoticz-thinkcleaner-plugin.log", "a")
        f.write("ERROR - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Error(message)
