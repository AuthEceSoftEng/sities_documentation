# Application development in ELSA

## 1. Introduction

This tutorial is intended for developers that aim to write ELSA applications, providing them with specifications, instructions and sample excerpts of code. The tutorial constitutes of the following parts:
- Backend development 
- Frontend development 
- Bundling the code into an app
- Uploading to the store and installing

## 2. Backend - The python files

In order to create an application in ELSA, at least one Python file **must** exist. This file must be named `app.py` and this will be the first file that will be executed once the application starts. Generally speaking, you can write whatever you want in this file (functionality-wise), but in order to use the device’s hardware you must use the r4a-api.

### 2.1. How to utilize ELSA’s hardware

ELSA has a microphone, a speaker, a touch screen and a camera. The touch screen can be handled by writing a frontend component in the application (check below), but the others can be utilized by employing the [r4a-api](https://robotics-4-all.github.io/r4a-api-docs/). This API contains both low-level calls and high level calls. 

If you want to use the low level calls, the python file should start as such:

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

from r4a_apis.robot_api import RobotAPI
from r4a_apis.utilities import *

from commlib.logger import Logger
log = Logger("testing")
log.set_debug(True)
        
rapi = RobotAPI(logger = log)
InputMessage.logger = log
OutputMessage.logger = log
TekException.logger = log
```

Then you can use the `rapi` object to use the HW as such:

```python
# Record a sound and write it to file
out = rapi.recordSound(InputMessage({
    'duration': 5,
    'name': 'testing',
    'save_file_url': expanduser("~") + "/test.wav"
}))

# Replay a sound from a file
out = rapi.replaySound(InputMessage({
    'is_file': True,
    'string': expanduser("~") + "/test.wav",
    'volume': 100 # volume may be suppressed by the ELSA's global volume
}))

# Speak
_temperature = 23
out = rapi.speak(InputMessage({
    'texts': ["The temperature is ",str(_temperature), " degrees celsius"],
    'volume': 100, # volume may be suppressed by the ELSA's global volume
    'language': Languages.EL # or Languages.EN for English
}))

# Listen using the microphone and Google API
out = rapi.listen(InputMessage({
    "language": Languages.EL,
    "duration": 5
}))
print(out.data['text']) # prints the recognized text

# Get an image from camera
out = rapi.captureImage(InputMessage({
    'width': 640,
    'height': 480,
    'save_file_url': expanduser("~") + "/test.jpg"
}))
```

In case you want to use the high level calls, the file should start as such:

```python

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging

from r4a_apis.utilities import *
from r4a_apis.tek_nodes import *

from r4a_apis.robot_api import RobotAPI
from r4a_apis.cloud_api import CloudAPI
from r4a_apis.generic_api import GenericAPI

try:
	from commlib.logger import Logger
	log = Logger("testing")
	log.set_debug(True)
	
	TekNode.logger = log
	TekNode.robot_api = RobotAPI(logger = log)
	Condition.memory = TekNode.robot_api.memory
	Condition.logger = log
	InputMessage.logger = log
	OutputMessage.logger = log
	TekException.logger = log
	NodeExecutor.logger = log
	log.debug('main', "Hey, app is starting")
# ...
```

Then you can use the following TekNodes:

```python
# Age detection (get input from camera). Will return result only if a face exists
n = DetectAgeTekNode(0)
n.setParameters(
    duration = 10
)
n.execute()
v = n.robot_api.memory.getVariable(
    variable = TekVariables.AGE_DETECTION
)
print(v)

# Barcode detection
n = DetectBarcodeTekNode(0)
n.setParameters(
    duration = 10
)
n.execute()
v = n.robot_api.memory.getVariable(
    variable = TekVariables.BARCODE_DETECTION
)

# Dominant color detection
n = DetectDominantColorTekNode(0)
n.execute()
v = n.robot_api.memory.getVariable(
    variable = TekVariables.DOMINANT_COLOR
)

# Face detection
n = DetectFaceTekNode(0)
n.setParameters(
    duration = 10
)
n.execute()
v = n.robot_api.memory.getVariable(
    variable = TekVariables.DETECT_FACE_DETECTED
)

# Gender detection
n = DetectGenderTekNode(0)
n.setParameters(
    duration = 10
)
n.execute()
v = n.robot_api.memory.getVariable(
    variable = TekVariables.GENDER_DETECTION
)

# QR detection
n = DetectQrCodeTekNode(0)
n.setParameters(
    duration = 10
)
n.execute()
v = n.robot_api.memory.getVariable(
    variable = TekVariables.QR_DETECTION
)
```
### 2.2. How to access elsa's bracelet data with the app

Elsa's bracelet is constantly streaming data about the user's activity state, health status as well as the device's battery level. In order to access this data via the app.py, one has to simply subscribe to the appropriate topic in the local redis server. 

Bellow is a list of the available topics, their payload as well as a short discription for each and every one of them:
- ```m5stickC.panic_button```, ```{"timestamp": <unix-time>}``` Receives a message when the user pressed the panic button.
- ```m5stickC.fall_detected```, ```{"timestamp": <unix-time>}``` Receives a message when the bracelet detects that the user has fallen
- ```m5stickC.activity.started```, ```{"timestamp": <unix-time>}``` Receives a message when the user starts moving for about 2 seconds.
- ```m5stickC.activity.stopped```, ```{"timestamp": <unix-time>}``` Receives a message when the user stops moving for at least 2 seconds. Requires that the user was on moving state before.
- ```m5stickC.activity.steps```, ```{"steps": int}``` Receives a message containing the number of steps the user has done, right after a stopped motion activity detection.
- ```m5stickC.battery```, ```{"timestamp": <unix-time>, "voltage": float}``` Receives a message every 20 sec in case the battery is full or when it runs out.

To correctly subscribe to one of the previously listed topics follow the code segment bellow:

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

from commlib.transports.redis import Subscriber, ConnectionParameters
import time
import json

# Topic to which we wish to subscribe
topic_to_sub = "m5stickC.panic_button"

/* 
 * Callback function which will be triggerd when we will receive a message in the specified topic
 *
 * Args:
 *		msg: The serialized msg data
 *		meta: Info & properties used for the communication
 */
def panic_button_callback(msg, meta):
    try:
    	# Deserialize the data (string -> dictionary)
        payload = json.loads(msg)
    
        print(f"Received panic button message: {payload}!")
    except Exception as e:
    	print(e)

if __name__ == "__main__":
    try:
        # Declare brokers connection parameters, for local use no credentials are required
        conn_params = ConnectionParameters()
        conn_params.host = "localhost" 
        conn_params.port = 6379
	
	/* 
	 * Create a redis subscriber by passing the connection parameters, 
	 * the topic & the callback function when we receive a message
         */
	sub = Subscriber(conn_params=conn_params,
                       topic=FitnessApp.panic_button_topic,
                       on_message=self._panic_callback)
		       
	# Activate the subscriber (Non blocking)
	sub.run_forever()
    	
	# We do other tasks or wait indefinitely for a message
	While True:
	    time.sleep(1)
    except Exception as e:
        print(e)
```

Lastly here is the typical value of the **meta** parameter in the callback function:
- ```{'timestamp': 1637278969221062, 'properties': {'content_type': 'application/json', 'content_encoding': 'utf8'}}```

### 2.3. How to access files bundled with the app

In case you have a file that you need to access via the app.py, you must bundle it with the python file. Let’s say you have bundled a .wav file and you want to replay it via the speakers. The correct way to do it follows:

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import pathlib
import sys

from r4a_apis.robot_api import RobotAPI
from r4a_apis.utilities import *

try:
    from commlib.logger import Logger
    log = Logger("testing")
    rapi = RobotAPI(logger=log)
    InputMessage.logger = log

    wav_file_path = os.path.join(os.path.dirname(sys.argv[0]), 'sound.wav')
    out = rapi.replaySound(
        InputMessage({
            "is_file": True, 
            "string": wav_file_path, 
            "volume": 50
        })
    )
except Exception as e:
    print(e)
```

### 2.4. How to handle Logger Info/Error messages

You can use the existing Logger to print information or error messages throughout your application. Some important errors, such as network or authentication failures, should also be stated in the platform. In order to do that, you have to add the special token `_sities_platform_critical_error_` inside your error message like this:

```
python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from commlib.logger import Logger
log = Logger("testing")
rapi = RobotAPI(logger=log)
InputMessage.logger = log


log.info("Everything is going well!")

log.error("Something went wrong!")

log.error("_sities_platform_critical_error_: Major error occured!!")

```

## 3. Frontend - The js files

Each application can be accompanied with a custom user interface. If you want to have a custom UI, you **must** have a folder named **`ui`** and inside at least a file called **`main.html`**. Of course you can have whatever else you need in this folder, but you must have in mind to access them (from js) as relative files!

### 3.1. The concept of communicating via Redis

Currently, the core application (the python part) is executed in a container (Docker), whereas the UI must be executed in the host, since it raises a web browser (Chromium). In order to get/send commands from both you can (or must) use Redis. Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache and message broker, which has libraries for both JS and Python. Since it is in-memory, the application which is in-container can communicate seamlessly with the Chromium which is at the host.

### 3.2. How to connect an html/js UI with app.py

Let’s say we want to create an application that shows an image and two buttons. The first button is a ping/pong toggle and the second terminates the application. The UI looks like this: 

![ui_elsa_custom](https://user-images.githubusercontent.com/5663091/97679642-3322b680-1a9e-11eb-8c31-e141c8160f8d.png)

A JS sample follows (main.html):

```html
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>Dummy app</title>
	</head>
	<body>
		<div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
			<img src="https://picsum.photos/id/1003/200/300" />
			<textarea name="the-text-area" id="the-text-area" style="margin: 15px 0"></textarea>
			<div style="display: flex; justify-content: center">
				<button type="button" onclick="func()" style="width: 100px; height: 50px; margin-right: 10px">CLICK ME!</button>
				<button type="button" onclick="done()" style="width: 100px; height: 50px">DONE!</button>
			</div>
		</div>
		<script>
			const appId = "DUMMY_APP_1";
			const textarea = document.querySelector("#the-text-area");

			fetch(`http://127.0.0.1:7379/SUBSCRIBE/${appId}_client`).then(async (res) => {
				const reader = res.body.getReader();
				while (true) {
					const { done, value } = await reader.read();
					if (done) break;
					try {
						const message = JSON.parse(new TextDecoder("utf-8").decode(value)).SUBSCRIBE[2];
						if (message === 1) {
							console.log("Websocket connected.");
						} else if (message === "done") {
							textarea.value = "Server closed!";
							break;
						} else {
							textarea.value = message;
						}
					} catch (error) {
						console.error(error);
					}
				}
			});

			const func = () => fetch(`http://127.0.0.1:7379/PUBLISH/${appId}_server/${textarea.value}`);
			const done = () => fetch(`http://127.0.0.1:7379/PUBLISH/${appId}_server/done`);
		</script>
	</body>
</html>
```

The respective Python code (app.py) is:

```python
import requests
import json
appId = "DUMMY_APP_1"

r = requests.get(f"http://localhost:7379/SUBSCRIBE/{appId}_server", stream=True)
for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
       incoming = json.loads(chunk.decode("utf8"))["SUBSCRIBE"]
       if incoming[0] == "message":
            message = incoming[2]
            if message == "ping": 
                requests.get(f"http://localhost:7379/PUBLISH/{appId}_client/pong")
            elif message == "done":
                requests.get(f"http://localhost:7379/PUBLISH/{appId}_client/done")
                break
            else:
                requests.get(f"http://localhost:7379/PUBLISH/{appId}_client/ping")
r.close()
```

## 4. How to bundle into an app

- **Required files**:
  - **app.info** The app info will list the following parameters in a yaml format:
    - name (e.g. test_app)
    - version (e.g. 1.0.0)
    - elsa version (e.g. 1.0.0)
    - description (e.g. A simple app for testing)
    - tags (e.g. [“testing”])
  - **app.py** The execution file as described above
  - **requirements.txt** The file containing all the python libraries to be imported in your app.py (e.g. requests==2.24.0). You can use the python module [pipreqs](https://pypi.org/project/pipreqs/).
- **Optional files:**
  - **ui folder containing the main.html**  The ui of the application as described above
  - **voice-commands.txt**  Optional file containing custom voice commands with which the user will be able to start this application. By default the application will start if the user says its name. Further syntax information is written below.
  - **init.conf** The init conf will list the initial parameters in a yaml format, specifying the name and type and placeholder of each parameter. (e.g. as follows)

![Screenshot 2020-10-30 105814](https://user-images.githubusercontent.com/5663091/97680102-d4aa0800-1a9e-11eb-8ade-0f0910470a86.png)

Lastly, you will need to compress the application files. To do so use the command `tar -zcvf file.tar.gz /path/to/directory`.

## 5. Voice Commands syntax

An optional “voice-commands.txt” document will be provided with the application's files that contain these commands in separate lines. The system adds the name of the application as a voice command by default, so you don't have to explicitly write it. For better app usage and user experience we advise you to create a few sentences (3-5 is a good number) that are closely related to the context of your application and don't rely only on the default case. This template language is based on Rhasspy's sentence syntax. However not all functionalities of Rhasspy's language are supported from our system and, as you might see, intents remain hidden to simplify development. So if you don't want to confuse yourself, just stick only with this guide.

### 5.1. Basic Syntax

To get started, all voice commands will be listed in separate lines across the document as below:

```
Θέλω την εφαρμογή μου
Ξεκίνα μια εφαρμογή
```


If the user says `Ξεκίνα μια εφαρμογή` your application will start. **Note** that after your application has started, all voice communications will be handled entirely from your application.

### 5.2. Optional words

You can specify optional word(s) by surrounding them with `[brackets]` like:

```
Θέλω την εφαρμογή [μου]
Ξεκίνα [τώρα] μια εφαρμογή
```

This will internally create all four next sentences:
```
Θέλω την εφαρμογή
Θέλω την εφαρμογή μου
Ξεκίνα τώρα μια εφαρμογή
Ξεκίνα μια εφαρμογή
```

**Special case**

If one of your sentences happens to start with an optional word, this can lead to an internal problem. In order to avoid that, you should use a backslash escape sequence, like:

`\[Αυτή] η πρόταση θέλει προσοχή`

### 5.3. Alternatives

A set of items where only one of is matched at a time can be specified `(like | this)`.

`Θέλω (μία | την | κάποια) εφαρμογή`

This will internally create all three next sentences:
```
Θέλω μία εφαρμογή
Θέλω την εφαρμογή
Θέλω κάποια εφαρμογή
```

### 5.4. Rules

Rules allow you to reuse parts of your sentences through many commands.

```
επιλογές = (μία | η | κάποια)
Αυτή είναι <επιλογές> εφαρμογή
<επιλογές> εφαρμογή
```

## 6. Upload in SYTIES store and test

In order to upload an application to the Syties store you must be logged in with a developer account (Role-> View as Developer). Then from the sidebar navigate to “Upload app” and fill in the form. Click upload, and then you can view your uploaded apps by selecting `My applications` from the sidebar. To test your app, switch role to `View as Owner`, navigate to `Applications` from the sidebar,  click on your application, and then select your device to install it (it might take a minute or two). 
