#           Domoticz Roomba ThinkCleaner Plugin
#
#           Author:     RobH 2020.
#
"""
<plugin key="ThinkCleaner" name="Think Cleaner" author="RobH" version="0.2.1" wikilink="https://github.com/robhiddinga/domoticz-thinkcleaner-plugin.git" externallink="http://www.thinkcleaner.com">
    <params>
        <param field="Mode1" label="IP Address" required="true" width="200px" />
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
import urllib.request
import urllib.error

class BasePlugin:
    RoombaWorking       = True
    intervalCounter     = None
    heartbeat           = 30
    battery             = 0
    state               = ""
    cleaning            = ""
    previousBattery     = 0
    previousState       = ""
    previousCleaning    = ""

    def onStart(self):
        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        logDebugMessage(str(Devices))
        if (len(Devices) == 0):
            Domoticz.Device(Name="Current state",  Unit=1, TypeName="Custom", Options = { "Custom" : "1;%"}, Used=1).Create()

            logDebugMessage("Devices created.")

        Domoticz.Heartbeat(self.heartbeat)
        self.intervalCounter = 0

        if ('RoombaVacuum' not in Images): Domoticz.Image('roombaVacuum.zip').Create()
        if ('RoombaVacuumOff' not in Images): Domoticz.Image('roombaVacuum.zip').Create()

        Devices[1].Update(0, sValue=str(Devices[1].sValue), Image=Images["RoombaVacuum"].ID)

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
           self.battery  = jsonObject["status"]["battery_charge"]
           self.state    = jsonObject["status"]["cleaner_state"]
           self.cleaning = jsonObject["status"]["cleaning"]

        if (status == "Off"):
           # Use saved  data
           self.battery  = self.previousBattery
           self.state    = self.previousState
           self.cleaning = self.previousCleaning

    def logErrorCode(self, jsonObject):

        if str(jsonObject) == "None":
           code = 1
           reason = " Roomba is offline"

        else:
         code   = 0
         reason = jsonObject["result"]
         if (code == 0):
            reason = 'Roomba is active, but no action'

        if (code != 0):
            logErrorMessage("Code: " + str(code) + ", reason: " + reason)

        return


    def updateDeviceCurrent(self):
        # Device 1 - current today

        self.previousBattery = self.battery
        logDebugMessage("Current level " + str(self.battery))
        try:
         Devices[1].Update(self.battery, str(self.battery), Images["RoombaVacuum"].ID)
        except KeyError as e:
         cause = e.args[0]
         logErrorMessage("Cause " + str(cause))

        return

    def updateDeviceOff(self):

        Devices[1].Update(0, "0", Images["FroniusInverterOff"].ID)

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
        f = open(Parameters["HomeFolder"] + "domoticz-roomba-plugin.log", "a")
        f.write("DEBUG - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Debug(message)

def logErrorMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "domoticz-roomba-plugin.log", "a")
        f.write("ERROR - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Error(message)
