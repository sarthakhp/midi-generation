from midiutil.MidiFile import MIDIFile
import tkinter as tk
from tkinter import ttk
import os
import re



# Define and initialize the dictionary with musical notes mapping    
key_offset_dict = {
    'G': -5, 'G#': -4, 'A': -3, 'A#': -2,
    'B': -1, 'C': 0, 'C#': 1, 'D': 2,
    'D#': 3, 'E': 4, 'F': 5, 'F#': 6
}
c_flute_notes_pitches = [43,45,47, 48, 50, 52, 53, 55, 57, 59, 60,62,64,65,67]

sargam_notation_pitch_offset_dict = {
    ".pa": -5,
    "_.dha": -4,
    ".dha": -3,
    "_.ni": -2,
    ".ni": -1,
    "sa": 0,
    "_re": 1,
    "re": 2,
    "_ga": 3,
    "ga": 4,
    "ma": 5,
    "ma_": 6, 
    "pa": 7,
    "_dha": 8,
    "dha": 9,
    "_ni": 10,
    "ni": 11,
    "sa.": 12,
    "_re.": 13,
    "re.": 14,
    "_ga.": 15,
    "ga.": 16,
    "ma.": 17,
    "ma._": 18,
    "pa.": 19
}

all_sargem_notes_list = list(sargam_notation_pitch_offset_dict.keys())
all_scale_notes_list = list(key_offset_dict.keys())


major_scale_notes = [0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24]
major_scale_root_note = 5


def create_midi_file(input_key, input_notations, smallest_beat_length):
    
    smallest_beat_length = float(smallest_beat_length)
    input_notations = input_notations.lower()
    input_key = input_key.capitalize()
    key_offset = key_offset_dict[input_key]
    
    mf = get_mf(input_notations, smallest_beat_length, key_offset)

    file_path = "output.mid"
    
    # write it to disk 
    with open(file_path, 'wb') as outf:
        mf.writeFile(outf)


    root.iconify()
    # Works on windows
    abs_path = os.path.abspath(file_path)
    os.startfile(os.path.dirname(abs_path)) 


def get_avroh_note(note):
    note_index = all_sargem_notes_list.index(note)
    higher_octave_root_note = major_scale_notes.index(all_sargem_notes_list.index("sa."))
    root_note = major_scale_notes.index(all_sargem_notes_list.index("sa"))
    root_notes_diff = higher_octave_root_note - root_note

    new_note_index = higher_octave_root_note - major_scale_notes.index(note_index) + root_note
    return all_sargem_notes_list[major_scale_notes[new_note_index]]


def get_mf(input_notations, smallest_beat_length, key_offset):

    current_scale_flute_notes_pitches = {value: (sargam_notation_pitch_offset_dict[value] + 60 + key_offset) for value in sargam_notation_pitch_offset_dict}

    input_sargam = re.sub(r'[0-9]', '', input_notations).split()
    input_note_lengths = re.sub(r'[^0-9 ]', "0", input_notations).split()
    
    # create your MIDI object
    channel = 0
    volume = 100
    beat_index = 0
    mf = MIDIFile(1)     # only 1 track
    track = 0   # the only track
    time = 0    # start at the beginning
    mf.addTrackName(track, time, "Sargam")
    mf.addTempo(track, time, 120)

    final_input_sargam = []
    final_input_note_lengths = []

    step_length = int(step_length_text_box.get("1.0", "end-1c"))

    if (radio_value.get() == radio_option_cycle):
        for cycle_index in range(0, int(cycle_repetition_text_box.get("1.0", "end-1c"))):
            for index in range(0, len(input_sargam)):

                initial_sargam_note = input_sargam[index] # eg "sa"

                initial_note_index = all_sargem_notes_list.index(initial_sargam_note)
                sargam_note = all_sargem_notes_list[major_scale_notes[major_scale_notes.index(initial_note_index) + (cycle_index*step_length)]]

                final_input_sargam.append(sargam_note)
            
            final_input_note_lengths += input_note_lengths


        avroh_sargam = [get_avroh_note(input_sargam_note_temp) for input_sargam_note_temp in input_sargam]

        for cycle_index in range(0, int(cycle_repetition_text_box.get("1.0", "end-1c"))):
            for index in range(0, len(avroh_sargam)):

                initial_sargam_note = avroh_sargam[index] # eg "sa"

                initial_note_index = all_sargem_notes_list.index(initial_sargam_note)
                sargam_note = all_sargem_notes_list[major_scale_notes[major_scale_notes.index(initial_note_index) - (cycle_index*step_length)]]

                final_input_sargam.append(sargam_note)
            
            final_input_note_lengths += input_note_lengths
            
    else:
        final_input_sargam = input_sargam
        final_input_note_lengths = input_note_lengths


    final_input_note_lengths[len(final_input_note_lengths) - 1] = smallest_beat_length * 8

    print(final_input_sargam)
    print(final_input_note_lengths)


    for index in range(0, len(final_input_sargam)):
        sargam_note = final_input_sargam[index] # eg "sa"

        duration = int(final_input_note_lengths[index])
        if (duration == 0):
            duration = 1
        duration = smallest_beat_length * duration

        if (sargam_note == "_"):
            beat_index += duration
            continue


        time = beat_index
        pitch = int(current_scale_flute_notes_pitches[sargam_note])
        mf.addNote(track, channel, pitch, time, duration, volume)
        
        beat_index += duration 

    return mf



def generate_midi_file():
    try:
        input_scale = str(scale_entry_box.get())
        input_notations = str(input_notation_entry_box.get("1.0", "end-1c"))
        smallest_beat_length = str(smallest_beat_length_entry_box.get("1.0", "end-1c"))
        create_midi_file(input_scale, input_notations, smallest_beat_length)

    except ValueError:
        print(ValueError)
        pass

# Create the main window
root = tk.Tk()
root.title("Generate Sargam Midi file") 

my_font=("Arial", 14)
y_gap = 20

def handle_tab(event):
    event.widget.tk_focusNext().focus_set()
    return "break"

def handle_reverse_tab(event: tk.Event):
    event.widget.tk_focusPrev().focus_set()
    return "break"

def handle_focus(event: tk.Event):
    event.widget.tag_add("sel", "1.0", "end-1c")

def do_common_things_to_text_box(text_box: tk.Text):
    text_box.bind("<Tab>", handle_tab)
    text_box.bind("<Shift-Tab>", handle_reverse_tab)
    text_box.bind("<FocusIn>", handle_focus)

# Input field for Key
style = ttk.Style()
style.configure("TCombobox", font=("Arial", 30))  # Change text size to 14
tk.Label(root, text="Key (eg \"A#\")", font=my_font).grid(row=0, column=0, pady=(y_gap, 0))
selected_key_option = tk.StringVar(value="G")
scale_entry_box = ttk.Combobox(root, values=all_scale_notes_list)
scale_entry_box.set(all_scale_notes_list[0])
scale_entry_box.config(font=my_font)
do_common_things_to_text_box(scale_entry_box)
scale_entry_box.grid(row=1, column=0)

tk.Label(root, text="Notation (eg: \"sa re1 _.ni _ sa4\")", font=my_font).grid(row=2, column=0, pady=(y_gap, 0))
input_notation_entry_box = tk.Text(root, font=my_font, height=5, undo=True)
input_notation_entry_box.focus()
do_common_things_to_text_box(input_notation_entry_box)
input_notation_entry_box.grid(row=3, column=0, padx = 30)

tk.Label(root, text="Smallest Beat length (eg: \"3\")", font=my_font).grid(row=4, column=0, pady=(y_gap, 0))
smallest_beat_length_entry_box = tk.Text(root, height=1, font=my_font, undo=True)
smallest_beat_length_entry_box.insert("1.0", "1")
do_common_things_to_text_box(smallest_beat_length_entry_box)
smallest_beat_length_entry_box.grid(row=5, column=0)

radio_option_normal = "Normal"
radio_option_cycle = "Cycle"
radio_value = tk.StringVar(value=radio_option_cycle)

# Create two radio buttons
def radio_button_switched():
    if (radio_value.get() == radio_option_cycle):
        cycle_repeatition_label.grid(row=9, column=0, pady=(y_gap, 0))
        cycle_repetition_text_box.grid(row=10, column=0, pady=(y_gap, 0))
        step_length_label.grid(step_length_label_argss)
        step_length_text_box.grid(step_length_text_box_argss)

    else:
        cycle_repeatition_label.grid_forget()
        cycle_repetition_text_box.grid_forget()
        step_length_label.grid_forget()
        step_length_text_box.grid_forget()


radio1 = tk.Radiobutton(root, text=radio_option_normal, variable=radio_value, value=radio_option_normal, command=radio_button_switched, font=my_font)
radio2 = tk.Radiobutton(root, text=radio_option_cycle, variable=radio_value, value=radio_option_cycle, command=radio_button_switched, font=my_font)

# Pack the radio buttons
radio1.grid(row=7, column=0, pady=(y_gap, 0))  # Align to the left
radio2.grid(row=8, column=0)

cycle_repeatition_label = tk.Label(root, text="Number of cycles (eg: \"5\")", font=my_font)
cycle_repeatition_label.grid(row=9, column=0, pady=(y_gap, 0))
cycle_repetition_text_box = tk.Text(root, height=1, font=my_font, undo=True)
cycle_repetition_text_box.insert("1.0", "8")
do_common_things_to_text_box(cycle_repetition_text_box)
cycle_repetition_text_box.grid(row=10, column=0, pady=(y_gap, 0))

rn = 11

step_length_label = tk.Label(root, text="Step length", font=my_font)
step_length_label.grid(row=rn, column=0, pady=(y_gap, 0))

def getargss(**kwargs):
    return kwargs 

step_length_label_argss = getargss(row=rn, column=0, pady=(y_gap, 0))

rn+=1
step_length_text_box = tk.Text(root, height=1, font=my_font, undo=True)
step_length_text_box.insert("1.0", "1")
do_common_things_to_text_box(step_length_text_box)
step_length_text_box.grid(row=rn, column=0, pady=(y_gap, 0))
step_length_text_box_argss = getargss(row=rn, column=0, pady=(y_gap, 0))
rn+=1

# Button to generate midi
subtract_button = tk.Button(root, text="Generate", command=generate_midi_file, font=my_font, pady=10)
subtract_button.grid(row=rn, column=0, pady = 15)
rn+=1

# Run the application
root.mainloop()

