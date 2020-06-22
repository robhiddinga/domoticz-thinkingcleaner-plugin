# domoticz thinkingcleaner plugin for your Roomba
 domoticz thinking cleaner plugin, python

The script creates a device with status info of your ThinkingCleaner.  
Create yourself a dummy device with on and off action to control your Roomba:  
<ipadress>/command.json?command=clean and  
<ipadress>/command.json?command=dock

 install

 goto your plugins folder
 ```bash
  git clone https://github.com/robhiddinga/domoticz-thinkingcleaner-plugin
```
update

```bash
git pull
```
Restart your Domoticz service with:

```bash
sudo service domoticz.sh restart
```

Now go to **Setup**, **Hardware** in Domoticz.
There you add **ThinkingCleaner**.

Fill in the IP address of your ThinkingCleaner.  
And the adress and port of your Domoticz server.  

Have fun!

