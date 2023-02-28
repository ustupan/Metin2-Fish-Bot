# Fishbot

**This project was build for educational and learning purposes only to refresh knowledge of python language.**  
The project is an extension of https://github.com/Midorina/Metin2-Fish-Bot 

### GUI

![Configuration tab](https://postimg.cc/hQ7yvWwK)
![Options tab](https://postimg.cc/N9xTxNHR)
![Logs tab](https://postimg.cc/2L6q7Cmf)

### Installation

 1. Clone repository and enter the directory
`git clone https://github.com/ustupan/Metin2-Fish-Bot.git`
`cd Metin2-Fish-Bot`
 2. Install libraries
 `python -m pip install -r requirements.txt`
 3. Run the code
 `python run.py`

### Settings
In order to detect fishes modify 

> /settings/fishing.csv

to contain fishes names in your language.


### Pointers Configuration

How to find those configuration addresses pointers and offsets? 
Depending on the launcher client and server, the search method may differ.
I was searching for it using this strategies


|                Action                          |Method of searching                         |
|-----------------------------------------------|-----------------------------|
|Pole is thrown|When the float is not in the water, the value of the variable is 0xFFFFFFFF, when it is submerged, it increases every second             |
|Fish is caught|When an image with a fish appears, the variable is set to 1, otherwise 0            |
|New message|The variable takes the value of the last chat message|
