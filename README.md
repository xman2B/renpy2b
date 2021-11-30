# renpy2b
Patched sound.py file to control the 2B based on audio file names in renpy games

## Supported renpy games
### [TechnicalForms](https://milovana.com/forum/viewtopic.php?f=26&t=21898}):
For each form the 2B is set to the mapped mode. The BPM determine the value for channel C. Once you set channel A or channel B to a value different than 0, the settings for the mode are saved and restored when the mode is set again.

## Installaton
Overwrite the `renpy/audio/sound.py` file in the game directory by the patched `sound.py` file.

## Usage
Start the [http server](https://github.com/xman2B/estim2b) and start the game.
