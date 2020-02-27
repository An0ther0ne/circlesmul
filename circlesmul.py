#-*- coding: utf-8 -*-

import os
import numpy as np
import cv2
import PySimpleGUI 	as sg
from math import sin, cos, pi

width  = 800
height = width
x0 = width / 2
y0 = height / 2
Radius = (width - 10) // 2

def viewImage(image, name_of_window):
	cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
	cv2.imshow(name_of_window, image)
	
color = [0,220,255]
maxcolorrange = 100

typelayout = [[
		sg.Radio('1', 'radio_folders', pad=(10,3), default='1', key='-type_1-'),
	],[
		sg.Radio('2', 'radio_folders', pad=(10,3), key='-type_2-')
	],[
		sg.Radio('3', 'radio_folders', pad=(10,3), key='-type_3-')		
	]]
	
slidelayout = [[
		sg.Text('N:', size=(6,1)), 
		sg.Slider(range=(3,64), disable_number_display=True, default_value=3, orientation='h', size=(54,20), key='-N_slide-')
	],[
		sg.Text('Pass:', size=(6,1)), 
		sg.Slider(range=(1,64), disable_number_display=True, default_value=1, orientation='h', size=(54,20), key='-N_mul-')
	],[
		sg.Text('Color:', size=(6,1)),
		sg.Slider(range=(1,maxcolorrange), disable_number_display=True, default_value=1, orientation='h', size=(54,20), key='-color-')
	]]

layout = [[
		sg.Image(filename='', key='-image-')
	],[
		sg.Frame(
			'Options:', 
			slidelayout, 
			font='Any 11', 
			title_color='blue', 
			pad=(5,10),
			element_justification = 'left',
			title_location = sg.TITLE_LOCATION_TOP_LEFT,
		),
		sg.Frame(
			'Type:', 
			typelayout, 
			font='Any 11', 
			title_color='blue', 
			pad=(5,10),
			element_justification = 'left',
			title_location = sg.TITLE_LOCATION_TOP,
		),	
	],[
		sg.Button('Exit', size=(7,1), font='Hevletica 14')
	],]

window = sg.Window('Circle of multiplications', layout, no_titlebar=False, location=(0,0))
image = np.zeros((height, width, 3), dtype="uint8")
image_elem  = window['-image-']

old_N     = -1
old_color = -1
old_mul   = -1
old_type  = -1

def mmul(i,j):
	x1 = int(x0 + Radius * cos(i * 2 * pi / N_value))
	y1 = int(y0 - Radius * sin(i * 2 * pi / N_value))
	x2 = int(x0 + Radius * cos(j * 2 * pi / N_value))
	y2 = int(y0 - Radius * sin(j * 2 * pi / N_value))
	return (x1,y1),(x2,y2)

while True:
	event, values = window.read(timeout=50)
	if event == 'Exit' or event == None:
		break
	N_value = int(values['-N_slide-'])
	S_color = values['-color-']
	N_mul = int(values['-N_mul-'])
	if values['-type_1-']:
		N_type = 1
	elif values['-type_2-']:
		N_type = 2
	elif values['-type_3-']:
		N_type = 3
	print(values)
	if (N_value != old_N) or (old_color != S_color) or (old_mul != N_mul) or (N_type != old_type):
		if S_color != old_color:
			old_color = S_color
			R = min(255, int(300*sin(pi*float(S_color)/maxcolorrange)))
			G = min(255, max(0, int(300*sin(pi*float(S_color + maxcolorrange//3)/maxcolorrange))))
			B = min(255, max(0, int(300*sin(pi*float(S_color - maxcolorrange//3)/maxcolorrange))))
			color = [B,G,R]
		elif old_N != N_value:
			old_N = N_value
		elif old_mul != N_mul:
			old_mul = N_mul
		elif old_type != N_type:
			old_type = N_type
		frame = image.copy()
		frame = cv2.circle(frame, (width//2, height//2), Radius, color, 2)
		if N_type == 1:
			for i in range(N_value):
				for j in range(N_value):
					k = (j * N_mul) % N_value
					if i != k:
						p1,p2 = mmul(i,k)
						frame = cv2.line(frame, p1, p2, color, 1)
		elif N_type == 2:
			for i in range(N_value):
				j = i * (N_mul + 1) % N_value
				p1,p2 = mmul(i,j)
				frame = cv2.line(frame, p1, p2, color, 1)
		imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
		image_elem.update(data=imgbytes)
