# HelloDisplay
Display tool for hello system
A work in progress.
PR-s are welcome.


![alt text](https://github.com/PreyK/HelloDisplay/blob/main/display.png?raw=true)

### Modules&Files:

Randr.py - communicates with Randr trough the command line and exposes an api to do randr stuff.

Display.py - the frontend written in PyQt. Communicates with Randr.py to display the settings.

Edid.csv - EDID lookup repository for pyedid.

Layout.UI - QT designer layout for the UI.

Res.QRC - icons (qt resource)

Other files in the repo considered scratch/prototyping, will be cleaned up.


### running:
1. Install pyedid https://pypi.org/project/pyedid/
2. run Display.py
3. You should be able to select display resolutions, rotations and set a screen as primary.

### ToDo:
* Get display placement (randr position X, Y) working. The UI shows it but it doesn't yet have an effect on apply.
* Get PyEdid as one file .py like Randr.py so we don't need pip dependencies.
* BUG: When a display is selected as primary, the UI doesn't correctly show the display's current rotation. (It always shows landscape even if it's portrait)
* Find a way to properly reinitialize the UI after applied settings without needing to close and restart the whole UI.
* Prompt that ask you to keep screen settings or restore prevorious after the selected settings applied. (the standard stuff on every OS, recovery)
* Make display settings persist after reboot. (when Randr.py applies the settings it builds a shell command and executes it. Possibly we'd just need to write it to a startup path so it executes the last selected display layout on boot, haven't tested yet.)
* Add multi-monitor options for "mirror screen, turn-off, extend" and show it on the UI.
* Add advanced options (refresh rate, color space, etc..)


### acknowledgements:
@cakturk for pyrandr: https://github.com/cakturk/pyrandr

@dd4e for pyedid: https://github.com/dd4e/pyedid
