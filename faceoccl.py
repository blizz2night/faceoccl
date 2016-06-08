# -*- coding: utf-8 -*-

import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')


def detectFace(frame):
	faces=[]
	result = False
	temp = []
	temp = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	cv2.equalizeHist(temp,temp)
	faces = face_cascade.detectMultiScale(temp, 1.1, 2, 0 | cv2.CASCADE_SCALE_IMAGE, (1, 1))
	if len(faces)>0:
		result=True
	return result, faces

def detectMask(frame,face):
	result = False
	# i = 0
	fmat = frame[face[1]:face[1] + face[3], face[0]:face[0] + face[2]]
	# cv2.imshow(str(i), fmat)
	dy = face[1]+fmat.shape[1] / 7 * 3
	dx = face[0]
	fmat = fmat[fmat.shape[1] / 7 * 3:fmat.shape[1] / 5 * 3]

	edges = cv2.Canny(fmat, 50, 150)

	# lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
	lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 46, minLineLength=edges.shape[1] / 5, maxLineGap=edges.shape[1] / 20)
	# print lines, edges.shape[1] / 5
	if lines is not None:
		lines += (dx, dy, dx, dy)
		result = True
	else:
		lines = []
	return result, lines
			# for line in lines:
			# 	x1, y1, x2, y2 = line[0]
			# 	cv2.line(fmat, (x1, y1), (x2, y2), (0, 255, 0), 2)
		# cv2.imshow(str(i), fmat)
		# cv2.imshow('i', edges)
		# i += 1
def detectMouth(frame,face):
	#print face
	result = False
	mouths = []
	fmat = frame[face[1]:face[1] + face[3], face[0]:face[0] + face[2]]
	dy = face[1]+fmat.shape[1]/3*2
	dx = face[0]
	fmat = fmat[fmat.shape[1]/3*2:]
	fmat = cv2.cvtColor(fmat,cv2.COLOR_BGR2GRAY)
	fmat = cv2.equalizeHist(fmat)
	#print fmat
	mouths = mouth_cascade.detectMultiScale(fmat, 1.1, 3, 0 | cv2.CASCADE_SCALE_IMAGE, (30, 30))
	if len(mouths)>0:
		mouths+=(dx,dy,0,0)
		result=True
	return result, mouths

def detectSunglass(frame,face):
	result = False
	fmat = frame[face[1]:face[1] + face[3], face[0]:face[0] + face[2]]
	dy = face[1]+fmat.shape[1] / 4
	dx = face[0]
	fmat = fmat[fmat.shape[1] / 4:fmat.shape[1] / 7 * 4]
	fmat = cv2.cvtColor(fmat, cv2.COLOR_BGR2YUV)
	y, u, v = cv2.split(fmat)
	count = np.count_nonzero((u >= 133) & (u <= 173) & (v >= 77) & (v <= 127))
	ratio = float(count) / (face[2]*face[3])
	return ratio

def detectEye(frame,face):
	fmat = frame[face[1]:face[1] + face[3], face[0]:face[0] + face[2]]
	pass

cap = cv2.VideoCapture(0)

while True:
	ret, frame = cap.read()
	fshow = frame
	if not ret:
		break
	#检测人脸
	ret, faces = detectFace(frame)
	if ret:
		for face in faces:
			cv2.rectangle(fshow, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), (0, 0, 255), 2)
			#检测口罩
			ret, lines = detectMask(frame, face)
			if ret:
				#print type(lines),lines
				for line in lines:
					x1, y1, x2, y2 = line[0]
					cv2.line(fshow, (x1, y1), (x2, y2), (0, 255, 0), 2)
			#检测嘴
			ret, mouths = detectMouth(frame, face)
			if ret:
				mouth = mouths[0]
				cv2.rectangle(fshow, (mouth[0], mouth[1]), (mouth[0]+mouth[2], mouth[1]+mouth[3]), (255, 0, 255), 2)
			#检测墨镜
			out = detectSunglass(frame, face)
			print out

	cv2.imshow('1', fshow)
	k = cv2.waitKey(5) & 0xff
	if k == 27:
		break