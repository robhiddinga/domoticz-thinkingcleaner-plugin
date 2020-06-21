# python roomba thinkcleaner
 domoticz think cleaner

The script creates a device with status info of your ThinkCleaner.  
Create yourself a dummy device with on anf off action to control your Roomba:  
<ipadress>/command.json?command=clean and  
<ipadress>/command.json?command=dock

 install

 goto your plugins folder
 ```bash
  git clone https://github.com/robhiddinga/domoticz-thinkcleaner-plugin
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
There you add **ThinkCleaner**.

Fill in the IP address of your ThinkCleaner.  
And the adress and port of your Domoticz server.  

Have fun!

