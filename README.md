# freestylehero
rate your freestyles. rap away
Remember to edit the code in Notepad to add your api keys. You should obtain a google api key for ai and a replicate api key
after obtaining the keys, paste them in the apropriate place in the code between the "" signs.(obtain the free libs required first, tutorial down bellow)
record your freestyle beforehand and select the pre recorded freestyle option or record on the fly by selecting a beat first and then clicking start and freestyling away
your freestyles will be saved as well as the rating and feedback

REQUIRES PYTHON 3.10. THIS CAN BE OBTAINED VIA MICROSOFT STORE. REMEMBER THAT YOU WILL GET ERROR MESSAGES IF YOU DONT PIP INSTALL THE FOLLOWING LIBS
import tkinter as tk
from tkinter import filedialog
import pygame
import speech_recognition as sr
import random
import os
import time
import threading
import google.generativeai as genai
import replicate
import http.server
import socketserver
import threading
import base64
import requests
ALL YOU NEED TO DO IS RUN IN A CMD  : pip install <libname>
for example pip install requests
pip install google-generativeai
