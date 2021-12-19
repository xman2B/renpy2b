# Copyright 2004-2019 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# The public API for sound playback from games.

# TODO: Check to see if SFX are enabled before playing sounds with play or
# queue.

from __future__ import print_function

import renpy.audio

from collections import OrderedDict
MODE_MAPPING=OrderedDict()
MODE_MAPPING["beardragon"] = "BSplit"
MODE_MAPPING["beareagle"] = "BSplit"
MODE_MAPPING["bearowl"] = "BSplit"
MODE_MAPPING["catsnakedogeagle"] = "ASplit"
MODE_MAPPING["catbear"] = "BSplit"
MODE_MAPPING["catdragon"] = "BSplit"
MODE_MAPPING["cateagle"] = "BSplit"
MODE_MAPPING["catowl"] = "BSplit"
MODE_MAPPING["catsnake"] = "BSplit"
MODE_MAPPING["dogbear"] = "BSplit"
MODE_MAPPING["dogcat"] = "BSplit"
MODE_MAPPING["dogdragon"] = "BSplit"
MODE_MAPPING["dogeagle"] = "BSplit"
MODE_MAPPING["dogowl"] = "BSplit"
MODE_MAPPING["dogsnake"] = "BSplit"
MODE_MAPPING["eagledragon"] = "ASplit"
MODE_MAPPING["owldragon"] = "ASplit"
MODE_MAPPING["owleagle"] = "ASplit"
MODE_MAPPING["snakebear"] = "BSplit"
MODE_MAPPING["snakebear"] = "BSplit"
MODE_MAPPING["snakedragon"] = "ASplit"
MODE_MAPPING["snakeeagle"] = "ASplit"
MODE_MAPPING["snakeowl"] = "ASplit"
MODE_MAPPING["bear"] = "Waterfall"
MODE_MAPPING["cat"] = "Flo"
MODE_MAPPING["dog"] = "Pulse"
MODE_MAPPING["dragon"] = "Thrust"
MODE_MAPPING["eagle"] = "Bounce"
MODE_MAPPING["owl"] = "Twist"
MODE_MAPPING["snake"] = "Cycle"
MODE_MAPPING["edge"] = "Continuous"
MODE_MAPPING["gong"] = "Throb"

print(MODE_MAPPING)

URL="http://localhost:8000/api"
MIN_C = 30
MAX_C = 70
MIN_BPM = 100
MAX_BPM = 180

last_states = {}

import re
import urllib2
import json

def get_request(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    answer = response.read()
    return json.loads(answer)
    
def post_request(url, data):
    #print(json.dumps(data))
    req = urllib2.Request(url, json.dumps(data))
    req.add_header('Content-type', 'application/json')
    response = urllib2.urlopen(req)
    answer = response.read()
    return json.loads(answer)

def twob_kill():
    temp = get_request(URL + "/kill")
    #print("Kill: %s" % temp)
    return temp
    
def twob_refresh_state():
    temp = get_request(URL + "/refresh_state")
    #print("Refresh State: %s" % temp)
    return temp

def twob_get_state():
    temp = get_request(URL + "/get_state")
    #print("Get_state: %s" % temp)
    return temp

def twob_set_state(data):
    temp = post_request(URL + "/set_state", data)
    #print("Set_state: %s" % temp)
    return temp
    
def twob_set_mode(mode):
    temp = get_request(URL + "/set_mode?mode=%s" % mode)
    #print("Set_mode: %s" % temp)
    return temp
    
def save_state():
    global last_states
    #print("Save State")
    state = twob_get_state()
    last_states[state["mode"]] = dict(state)

def current_state_equals_safed():
    global last_states
    state = twob_get_state()
    if state["mode"] in list(last_states):
        return last_states[state["mode"]] == state
    return False

def restore_state(mode):
    global last_states
    if MODE_MAPPING[mode] in last_states:
        #print("Restore State")
        # restore state
        return last_states[MODE_MAPPING[mode]]
    else:
        #print("Mode not in last_states!")
        state = twob_get_state()
        state["channel_a"] = 0
        state["channel_b"] = 0
        return state
        
def bpm_to_output(bpm, min_bpm=MIN_BPM, max_bpm=MAX_BPM, min_output=MIN_C, max_output=MAX_C, invert=False):
    bpm = min(bpm, max_bpm)
    output = float((bpm - min_bpm)) / float((max_bpm - min_bpm))
    output *= max_output - min_output
    output += min_output
    
    if invert:
        output = abs(output - (max_output + min_output))
    
    return int(min(max(round(output), min_output), max_output))

reg_expr=re.compile("^.*/([a-z]+)([0-9]+)?([a-z]+)?\..*$")
def set_mode(filename):
    match = re.search(reg_expr, filename)
    if match is None:
        return
    mode, bpm, tendency = match.group(1, 2, 3)
    
    if mode.endswith("begin"):
        #print("Begin")
        return
    
    twob_refresh_state()
    state = twob_get_state()
    if (state["channel_a"] != 0 or state["channel_b"] != 0):
        save_state()
    
    if mode.endswith("stop"):
        #print("Stop")
        twob_kill()
        return
    
    for m in list(MODE_MAPPING):
        if m in mode:
            mode = m
            break
    #print("Mode: %s, BPM: %s, Tendency: %s" % (mode, bpm, tendency))
    #print(last_states)
    if mode not in MODE_MAPPING:
        return
    
    state = restore_state(mode)

    if mode is not None:
        state["mode"] = MODE_MAPPING[mode]
    if bpm is not None:
        c = bpm_to_output(int(bpm), invert= tendency == "rising")
        state["channel_c"] = c
    twob_set_state(state)
    #print()

# This is basically a thin wrapper around music, with the default
# channel set to "sound".
def play(filename, channel="sound", fadeout=0, fadein=0, tight=False, loop=False):
    set_mode(filename)
    renpy.audio.music.play(filename,
                           channel=channel,
                           fadeout=fadeout,
                           fadein=fadein,
                           tight=tight,
                           loop=loop)


def queue(filename, channel="sound", clear_queue=True, fadein=0, tight=False, loop=False):
    renpy.audio.music.queue(filename,
                            channel=channel,
                            clear_queue=clear_queue,
                            fadein=fadein,
                            tight=tight,
                            loop=loop)


def stop(channel="sound", fadeout=0):
    renpy.audio.music.stop(channel=channel,
                           fadeout=fadeout)

set_mixer = renpy.audio.music.set_mixer
set_queue_empty_callback = renpy.audio.music.set_queue_empty_callback


def set_volume(volume, delay=0, channel="sound"):
    renpy.audio.music.set_volume(volume, delay, channel=channel)


def set_pan(pan, delay, channel="sound"):
    renpy.audio.music.set_pan(pan, delay, channel=channel)


def is_playing(channel="sound"):
    return renpy.audio.music.is_playing(channel=channel)


def get_playing(channel="sound"):
    return renpy.audio.music.get_playing(channel=channel)
