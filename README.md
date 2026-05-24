# FastMacro
A fast and accurate mouse/keyboard recording and playback application.

Keypresses have a submillisecond level of accuracy during playback.
Clicks have a +-5 millisecond level of accuracy during playback.

<img width="319" height="266" alt="{8D665106-EA52-4A08-BF5B-2287B7E28FD1}" src="https://github.com/user-attachments/assets/2ab97bb9-1c8e-49d9-87b6-6e6a5777aaa9" />

## Recording
Records your mouse and keyborard inputs.

F1 Record, F2 Stop, F8 Pause, F9 Append to current loaded inputs.

<img width="319" height="101" alt="{6A46736F-9E83-4917-B645-88B3327299FA}" src="https://github.com/user-attachments/assets/be8ce79f-6492-40f2-8cbe-ead3c904a182" />

## Playback
Play your inputs back.

F3 Play, F4 Stop.
Adjust speed, Loop infinitely, or repeat a specified amount of times.
<img width="315" height="94" alt="image" src="https://github.com/user-attachments/assets/878bb8a3-d296-443a-92a1-64dad0f73f76" />




## Extra Settings
Configure to disable recording of your mouse or keyboard.
Configure to minimize when playing or recording.
Replace your clicks with the windows Touch API. (Not a 1:1 record to playback accuracy but can be used for applications that don't detect clicks for some reason)


<img width="220" height="159" alt="{7ECF5F0F-D148-46D0-9A20-590B52C24144}" src="https://github.com/user-attachments/assets/f6366470-b4fc-4f2b-b12b-6591cda3175e" />

# Download
Use either the FastMacro.exe or FastMacro.py. Both are the same application with the exception that the executable doesn't require python installed. 

If using the python version. No pip installs required. All using built in libraries. I recommend renaming .py to .pyw to not have a console.

# How to compile python to exe. (Optional)
Requirements. 
- pip install nuitka
- Desktop Developement with C++ (MSVC v143 checked) https://visualstudio.microsoft.com/downloads/?q=build+tools
```bash
nuitka --standalone --onefile --windows-console-mode=disable --msvc=latest --enable-plugin=tk-inter --lto=yes --windows-icon-from-ico=icon.png --python-flag=-O "FastMacro.py"
```

