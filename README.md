# room_mixer (Spelunky 2)

A script for mixing all the room templates from all levels, into every single level file.

## Instructions
- Create a folder named "Original" and move the level files, except camp files to preven't running out of short tilecodes

- Execute solveTileCodes.py, it will make all the levels to have the same tilecodes and save those to "Created".

- Execute getRoomTemplates.py, the room templates included in `toChangeTemplates` in the script will be replaced with all the room templates from all the level files, the levels will be saved in "mixed" folder
