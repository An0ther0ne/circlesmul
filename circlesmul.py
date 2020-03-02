#-*- coding: utf-8 -*-

import os
import re
from math import sin, cos, pi
import numpy as np
import cv2
from PIL import Image
import PySimpleGUI 	as sg

# --- Global Constants

WIDTH  		  = 800
HEIGHT 		  = WIDTH
X0 			  = WIDTH / 2
Y0 			  = HEIGHT / 2
RADIUS 		  = (WIDTH - 10) // 2
MAXN 		  = 128
MAXcolorRANGE = 100
BTNPADX 	  = 40
SCRSHOTFNAME  = 'sshot'
SCRSHOTFTYPE  = '.png'
ANIMFNAME	  = 'anim.gif'

# --- Global Vars

Inverted 	= False
color 		= [0,220,255]
old_type  	= -1
old_N     	= -1
old_mul   	= -1
old_shift	= -1
old_color 	= -1
SSHOTCNT  	= -1
N_MIN 	    = 3
P_MIN		= 1

# --- Procedures

def GetColor(col):
	R = min(255, int(300*sin(pi*float(col)/MAXcolorRANGE)))
	G = min(255, max(0, int(300*sin(pi*float(col + MAXcolorRANGE//3)/MAXcolorRANGE))))
	B = min(255, max(0, int(300*sin(pi*float(col - MAXcolorRANGE//3)/MAXcolorRANGE))))
	return [B,G,R]

def TakeScrShot():
	global SSHOTCNT
	if SSHOTCNT <= 0:
		files = [f for f in os.listdir() if os.path.isfile(f) and re.match(SCRSHOTFNAME, f)]
		if len(files) == 0:
			SSHOTCNT = 1
		else:
			lastnum = 0
			for f in files:
				matchstr = '^' + SCRSHOTFNAME + '(\\d+)\\' + SCRSHOTFTYPE + '$'
				matchresult = re.match(matchstr, f)
				if matchresult:
					num = int(matchresult.group(1))
					if lastnum < num:
						lastnum = num
			SSHOTCNT = lastnum + 1
	else:
		SSHOTCNT += 1
	sshotfile = SCRSHOTFNAME + str(SSHOTCNT) + SCRSHOTFTYPE
	cv2.imwrite(sshotfile, frame)

def ImgDraw(img, itype, value, nmul, inverted=False, rshift=0, ashift=0):
	def mmul(i,j):
		alfa = i * 2 * pi / value + (rshift + ashift) * pi / 360
		beta = j * 2 * pi / value + rshift * pi / 360
		x1 = int(X0 + RADIUS * cos(alfa))
		y1 = int(Y0 - RADIUS * sin(alfa))
		x2 = int(X0 + RADIUS * cos(beta))
		y2 = int(Y0 - RADIUS * sin(beta))
		return (x1,y1),(x2,y2)
	frm = img.copy()
	frm = cv2.circle(frm, (WIDTH//2, HEIGHT//2), RADIUS, color, 2)
	if  itype== 1:
		for i in range(value):
			for j in range(value):
				k = (j * nmul) % value
				if i != k:
					p1,p2 = mmul(i,k)
					frm = cv2.line(frm, p1, p2, color, 1)
	elif itype == 2:
		for i in range(value):
			j = (i * (nmul + 1)) % value
			p1, p2 = mmul(i, j)
			frm = cv2.line(frm, p1, p2, color, 1)
	elif itype == 3:
		for i in range(value):
			j = (i + nmul) % value
			p1, p2 = mmul(i, j)
			frm = cv2.line(frm, p1, p2, color, 1)
	if inverted:
		frm = cv2.bitwise_not(frm)
	return frm

# --- GUI

TypeLayout = [[
		sg.Radio('1', 'radio_folders', pad=(10,2), default='1', key='-type_1-'),
	],[
		sg.Radio('2', 'radio_folders', pad=(10,2), key='-type_2-')
	],[
		sg.Radio('3', 'radio_folders', pad=(10,2), key='-type_3-')
]]

SlideLayout = [[
		sg.Text('N:', size=(6,1)),
		sg.Slider(range=(N_MIN,MAXN), disable_number_display=True, default_value=3, orientation='h', size=(54,20), key='-N_slide-')
	],[
		sg.Text('Pass:', size=(6,1)),
		sg.Slider(range=(P_MIN,MAXN), disable_number_display=True, default_value=1, orientation='h', size=(54,20), key='-P_mul-')
	],[
		sg.Text('Shift:', size=(6,1)),
		sg.Slider(range=(0, 720), disable_number_display=True, default_value=0, orientation='h', size=(54,20), key='-S_hift-')
	],[
		sg.Text('Color:', size=(6,1)),
		sg.Slider(range=(1,MAXcolorRANGE), disable_number_display=True, default_value=1, orientation='h', size=(54,20), key='-color-')
]]

MainLayout = [[
		sg.Image(filename='', key='-image-')
	],[
		sg.Frame(
			'Options:',
			SlideLayout,
			font='Any 11',
			title_color='blue',
			pad=(5,2),
			element_justification = 'left',
			title_location = sg.TITLE_LOCATION_TOP_LEFT,
		),
		sg.Frame(
			'Method:',
			TypeLayout,
			font='Any 11',
			title_color='blue',
			pad=(5,2),
			element_justification = 'left',
			title_location = sg.TITLE_LOCATION_TOP,
		),
	],[
		sg.Button('Screenshot', size=(10,1), pad=(BTNPADX,2), font='Hevletica 14', key='-scrshot-'),
		sg.Button('Animation', size=(10,1), pad=(BTNPADX,2), font='Hevletica 14', key='-animate-'),
		sg.Button('Invert', size=(10,1), pad=(BTNPADX,2), font='Hevletica 14', key='-invert-'),
		sg.Button('Exit', size=(10,1), pad=(BTNPADX,2), font='Hevletica 14')
]]

# --- Main Program

MainWindow = sg.Window('Circle of multiplications', MainLayout, no_titlebar=False, location=(0,0))
image_elem  = MainWindow['-image-']
image = np.zeros((HEIGHT, WIDTH, 3), dtype="uint8")

while True:
	event, values = MainWindow.Read(timeout=10)
	N_value = int(values['-N_slide-'])
	S_color = values['-color-']
	P_mul = int(values['-P_mul-'])
	S_hift = int(values['-S_hift-'])
	if values['-type_1-']:
		N_type = 1
	elif values['-type_2-']:
		N_type = 2
	elif values['-type_3-']:
		N_type = 3
	if event == 'Exit' or event is None:
		break
	elif event == '-invert-':
		Inverted = not Inverted
		old_type = -1
	elif event == '-scrshot-':
		TakeScrShot()
	elif event == '-animate-':

		AnimDlgLayoutL = [[
			sg.Text('From: ', size=(4,1)),
			sg.Input(str(N_value), size=(5,1), key='-a_from-'),
			],[
			sg.Text('To: ', size=(4,1)),
			sg.Input(str(MAXN), size=(5,1), key='-a_to-'),
			],[
			sg.Text('Step: ', size=(4,1)),
			sg.Input(str(1), size=(5,1), key='-a_stp-'),
		]]

		AnimDlgLayoutR = [[
			sg.Radio('N',    'animate_for', pad=(10,1), default=True, enable_events=True, key='-a_n-'),
			],[
			sg.Radio('Pass', 'animate_for', pad=(10,1),  enable_events=True, key='-a_p-'),
			],[
			sg.Radio('RotAngle', 'animate_for', pad=(10,1),  enable_events=True, key='-a_ar-'),
			],[
			sg.Radio('Shift', 'animate_for', pad=(10,1),  enable_events=True, key='-a_as-'),
			],[
			sg.Radio('color', 'animate_for', pad=(10,1),  enable_events=True, key='-a_c-'),
		]]

		AnimDialog = sg.Window(
			'Animation',
			[[
				sg.Text('Save to:'),
				sg.Input(ANIMFNAME, size=(27,1), key='-afname-'),
			],[
				sg.Checkbox('Half Size', default=True, size=(16,1), key='-half-'),
				sg.FileSaveAs(file_types=(('GIF','*.gif'),('ALL Files', '*.*'),), size=(10,1)),
			],[
				sg.Frame(
					' Frames: ',
					AnimDlgLayoutL,
					font='Any 11',
					title_color='yellow',
					pad=(5,5),
					element_justification = 'left',
					title_location = sg.TITLE_LOCATION_TOP,
				),
				sg.Frame(
					' Animation Type: ',
					AnimDlgLayoutR,
					font='Any 11',
					title_color='yellow',
					pad=(5,5),
					element_justification = 'left',
					title_location = sg.TITLE_LOCATION_TOP,
				),
			],[
				sg.Ok(pad=(30,10), size=(10,1)),
				sg.Cancel(pad=(5,1), size=(10,1))
			]]
		)

		AnimDialogFromVal = AnimDialog['-a_from-']
		AnimDialogToVal = AnimDialog['-a_to-']
		AnimDialogStpVal = AnimDialog['-a_stp-']

		while True:
			aevnt, ares = AnimDialog.Read()
			if aevnt == 'Ok' or aevnt == 'Cancel' or aevnt is None:
				break
			elif aevnt == '-a_n-':
				AnimDialogFromVal.update(N_value)
				AnimDialogToVal.update(MAXN)
				AnimDialogStpVal.update(1)
			elif aevnt == '-a_p-':
				AnimDialogFromVal.update(P_mul)
				AnimDialogToVal.update(MAXN)
				AnimDialogStpVal.update(1)
			elif aevnt == '-a_ar-':
				AnimDialogFromVal.update(0)
				AnimDialogToVal.update(720)
				AnimDialogStpVal.update(1)
			elif aevnt == '-a_as-':
				AnimDialogFromVal.update(S_hift)
				AnimDialogToVal.update(720)
				AnimDialogStpVal.update(1)
			elif aevnt == '-a_c-':
				AnimDialogFromVal.update(1)
				AnimDialogToVal.update(MAXcolorRANGE)
				AnimDialogStpVal.update(MAXcolorRANGE // 20 )
		AnimDialog.close()

		if aevnt == 'Ok':
			afrom  = int(ares['-a_from-'])
			ato    = int(ares['-a_to-'])
			astep  = int(ares['-a_stp-'])
			afname = ares['-afname-']
			if afrom >= ato:
				sg.PopupError("'From' value must be lower then 'To'!")
			elif astep > (ato - afrom):
				sg.PopupError("Step value too big!")
			else:
				if ares['-a_n-']:
					if afrom < N_MIN:
						afrom = N_MIN
				elif ares['-a_p-']:
					if afrom < P_MIN:
						afrom = P_MIN

				AnimProgressLayout = [[
					sg.Text('Progress:'),
					sg.Text('', size=(4,1), key='-a_value-')
				],[
					sg.ProgressBar(ato - afrom, orientation='h', size=(20, 20), key='-animprogress-')
				],[
					sg.Cancel()
				]]

				AnimProgressWnd = sg.Window('Create animation', AnimProgressLayout)

				AnimProgressBar = AnimProgressWnd['-animprogress-']
				AnimProgressVal = AnimProgressWnd['-a_value-']

				frames = []

				for i in range(afrom, ato+1, astep):
					eprogress, vprogress = AnimProgressWnd.read(timeout=5)
					if eprogress == 'Cancel':
						break
					AnimProgressBar.UpdateBar(i-afrom)
					AnimProgressVal.update(str(i))
					if ares['-a_ar-']:
						frame = ImgDraw(image, N_type, N_value, P_mul, inverted=Inverted, ashift=S_hift, rshift=i)
					elif ares['-a_as-']:
						S_hift = i
						frame = ImgDraw(image, N_type, N_value, P_mul, inverted=Inverted, ashift=i)
					else:
						if ares['-a_n-']:
							N_value = i
						elif ares['-a_p-']:
							P_mul = i
						elif ares['-a_c-']:
							S_color = i
							color = GetColor(i)
						frame = ImgDraw(image, N_type, N_value, P_mul, inverted=Inverted, ashift=S_hift)
					imgbytes = cv2.imencode('.png', frame)[1].tobytes()
					image_elem.update(data=imgbytes)
					if ares['-half-']:
						aheight, awidth = frame.shape[:2]
						# interpolation: INTER_LINEAR, INTER_NEAREST, INTER_AREA, INTER_CUBIC, INTER_LANCZOS4
						frame = cv2.resize(frame, (awidth//2, aheight//2), interpolation = cv2.INTER_LINEAR)
					pilimg = Image.fromarray(frame, mode='RGB')
					frames.append(pilimg)

				AnimProgressWnd.close()

				frames[0].save(
					afname,
					save_all=True,
					append_images=frames[1:],
					optimize=True,
					duration=40,
					loop=0)
				del frames[:]
				del frames

	if (N_value != old_N) or (old_color != S_color) or (old_mul != P_mul) or (N_type != old_type) or (old_shift != S_hift):
		if S_color != old_color:
			old_color = S_color
			color = GetColor(S_color)
		elif old_N != N_value:
			old_N = N_value
		elif old_mul != P_mul:
			old_mul = P_mul
		elif old_type != N_type:
			old_type = N_type
		elif old_shift != S_hift:
			old_shift = S_hift
		frame = ImgDraw(image, N_type, N_value, P_mul, inverted=Inverted, ashift=S_hift)
		imgbytes = cv2.imencode('.png', frame)[1].tobytes()
		image_elem.update(data=imgbytes)
