This project is designed to be a choose your own adventure style app that was made as part of an Intro to Programming Logic course. There are two versions, one that uses a simple text based system (made with input from the students) and one that uses pygame for the combat portion (made by me with help from ChatGPT based on the simple version).
Simple_rpg.py is a standalone text based combat program that has you pick a character and fight a random enemy.
Advanced_rpg.py is a standalone graphical combat program made with pygame that has you pick a character and fight a random enemy, but also has a couple added elements to enhance the combat, such as individual inventory and special abillities for each character.
Branching_paths and branching_paths_advanced are the choose your own adventure elements that utilize the simple and advanced rpg combat programs respectively for combat.

For the full experience it is recommended to use branching_paths_advanced to play.

This program, works best on Windows. Other opperating systems may not be supported.

To start, make sure you have Python installed. Python version 3.12.10 was used for development, but I don't think that specific version is required for use.
Download the source code by clicking on the green Code button and download as a zip file. Extract the zip file where you want it.

In command prompt (or terminal), navigate to the location you unzipped the python files, and run the following command:  
  pip install requirements.txt  
followed by this command:  
  python [file name you want to run]  
so if you wanted to run branching_paths_advanced.py it would look like this:  
  python branching_paths_advanced.py
