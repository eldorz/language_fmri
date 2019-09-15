import json
from psychopy import gui, core, visual, event
import random

class TriggerCounter:
    counter = 0
    
    def increment(self, number = 1):
        self.counter += number

    def __str__(self):
        return str(self.counter)

def showChoiceDialogue():
    dlg = gui.Dlg(title="fMRI Paradigm Choice")
    dlg.addField('Paradigm:', choices = [
        "Verb Generation 1",
        "Verb Generation 2",
        "Verb Generation 3",
        "Single Letter",
        "Tap"])
    response = dlg.show()  # show dialog and wait for OK or Cancel
    return response

def get_actives(choice):
    if choice == 'Verb Generation 1':
        words = ["cake", "rabbit", "child", "artist", "pig", "bird", "wolf", 
            "fire", "fish", "knife", "rose", "cat", "ball", "wheel", "key",
            "ship", "plant", "lion", "horse", "wind", "door", "clock", "mouse",
            "hair", "frog", "emu", "top"]
        random.shuffle(words)
        return words
    elif choice == 'Verb Generation 2':
        words = ["dog", "bell", "baby", "train", "torch", "light", "kite",
            "bee", "radio", "pencil", "shirt", "broom", "chair", "eagle",
            "water", "paper", "hammer", "apple", "bicycle", "block", "spoon",
            "bottle", "cup", "bed", "shoe", "wasp", "car"]
        random.shuffle(words)
        return words
    elif choice == 'Verb Generation 3':
        words = ["pear", "bus", "rain", "soap", "lamb", "doll",
            "tiger", "bomb", "shark", "movie", "gift", "phone", "pen", "rope",
            "lock", "boat", "chain", "bear", "pony", "cup", "music", "nose",
            "diary", "eye", "sun", "music", "cards"]
        random.shuffle(words)
        return(words)
    elif choice == 'Single Letter':
        letters = ["t", "o", "a", "w", "b", "c", "d", "s", "f"]
        random.shuffle(letters)
        return letters
    elif choice == 'Tap':
        return ["tap", "TAP"] * 6
    else:
        return []

def get_passives(choice):
    return []

def display_intro(win, shapeObj, options, counter):
    print("intro")
    display_null(win, shapeObj)
    wait_for_triggers(options["trigger_key"], options["trs_in_intro"] + 1,
        counter)

def display_null(win, shapeObj):
    shapeObj.draw()
    win.flip()

def log_trig(counter):
    print("Triggers captured:", counter)

def wait_for_trigger(key, counter):
    wait_for_triggers(key, 1, counter)

def wait_for_triggers(key, reps, counter):
    triggers = 0
    while (triggers < reps):
        keys = event.getKeys(keyList = [key])
        if len(keys) != 0:
            triggers += len(keys)
            counter.increment(len(keys))
            log_trig(counter)

def display_active(win, textObj, actives, n_per_block, options, counter):
    print("active")
    if len(actives) == 0:
        raise RuntimeError('Active paradigm empty')
    my_triggers = 0
    change_flag = True
    triggers_per_change = options["trs_per_block"] / n_per_block
    change_point = 0
    while my_triggers < options["trs_per_block"]:
        if my_triggers >= change_point and change_flag == True:
            word = actives.pop(0)
            textObj.text = word
            textObj.draw()
            win.flip()
            change_flag = False
            change_point += triggers_per_change
        keys = event.getKeys(keyList = [options["trigger_key"]])
        if len(keys) != 0:
            counter.increment(len(keys))
            my_triggers += len(keys)
            change_flag = True
            log_trig(counter)

def display_passive(win, shapeObj, passives, n_per_block, options, counter):
    print("passive")
    if len(passives) == 0:
        display_null(win, shapeObj)
        wait_for_triggers(options['trigger_key'], options['trs_per_block'],
            counter)
        return
    else:
        raise RuntimeError('No code to display words during passive phase')

def display_end(win, shapeObj):
    display_null(win, shapeObj)
    core.wait(2)

def runChoice(choice, options):
    # intro _ (passive _ active) * active_blocks_per_study
    actives = get_actives(choice)
    passives = get_passives(choice)

    # define window
    win = visual.Window(size=(800, 600), pos=None, color=(41, 36, 14), 
        colorSpace='rgb255', rgb=None, dkl=None, lms=None, 
        fullscr=True, allowGUI=None, monitor=None, 
        bitsMode=None, winType=None, units=None, 
        gamma=None, blendMode='avg', screen=1, 
        viewScale=None, viewPos=None, viewOri=0.0, 
        waitBlanking=True, allowStencil=False, multiSample=False, 
        numSamples=2, stereo=False, name='window1', checkTiming=True, 
        useFBO=False, useRetina=True, autoLog=True, 
        gammaErrorPolicy='raise')

    # define text
    textObj = visual.TextStim(win, text="", font='', pos=(0, 0), 
            depth=0, rgb=None, color=(255,247,207), colorSpace='rgb255', 
            opacity=1.0, contrast=1.0, units='norm', ori=0.0, height=0.5, 
            antialias=True, bold=False, italic=False, alignHoriz='center', 
            alignVert='center', fontFiles=(), wrapWidth=None, flipHoriz=False, 
            flipVert=False, languageStyle='LTR', name=None, autoLog=None)

    # define resting cross
    cross = visual.ShapeStim(win, units='', lineWidth=1.5, 
        lineColor=(255,247,207), lineColorSpace='rgb255', fillColor=None, 
        fillColorSpace='rgb', 
        vertices=((-0.5, 0), (0.5, 0), (0, 0), (0, 0.5), (0, -0.5)),
        windingRule=None, closeShape=False, pos=(0, 0), size=1, ori=0.0, 
        opacity=1.0, contrast=1.0, depth=0, interpolate=True, 
        name=None, autoLog=None, autoDraw=False)

    # get counter
    counter = TriggerCounter()

    # display during warmup
    display_intro(win, cross, options, counter)

    # display active and passive blocks
    active_n_per_block = len(actives) // options["active_blocks_per_study"]
    passive_n_per_block = len(passives) // options["active_blocks_per_study"]
    for i in range(options["active_blocks_per_study"]):
        display_passive(win, cross, passives, passive_n_per_block, options,
            counter)
        display_active(win, textObj, actives, active_n_per_block, options,
            counter)
    if options['final_passive']:
        display_passive(win, cross, passives, passive_n_per_block, options,
            counter)

    # cooldown image
    display_end(win, cross)

    # remove window
    win.close()

def loadOptions():
    with open('options.json', 'r') as f:
        options = json.load(f)
    return options

def main():
    options = loadOptions()
    choice = showChoiceDialogue()
    while choice:
        runChoice(choice[0], options)
        choice = showChoiceDialogue()

if __name__ == '__main__':
    main()