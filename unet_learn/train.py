import sys
# sys.path.insert(0, '../segmentation_models')
sys.path.insert(0, '../segmentation_models')

import tensorflow as tf
import numpy as np
import cv2

from segmentation_models import Unet
from segmentation_models.backbones import get_preprocessing
from segmentation_models.losses import bce_jaccard_loss
from segmentation_models.metrics import iou_score

import os
def get_data(imgDir):
	img_path = imgDir + "/images"
	mask_path = imgDir + "/mask"
	img_files = [ f for f in os.listdir(img_path) if os.path.isfile(os.path.join(img_path,f)) ]
	# mask_files = [ f for f in os.listdir(mask_path) if os.path.isfile(os.path.join(mask_path,f)) ]

	# print(len(img_files))
	# print(img_files[0])
	# exit(0)

	train_data = []
	mask_data = []
	# ttt=np.array()
	print("Start load images ...")
	total_num = len(img_files)
	for idx, fn in enumerate(img_files):
		if idx > 8000:
			break
		print("load progress = [", total_num, ",", idx, "]")
		img = cv2.imread(img_path + "/" + fn)
		if img is None:
			print("Can't imread: ", img_path + "/" + fn)
			continue
		mask = cv2.imread(mask_path + "/" + fn, 0)
		if mask is None:
			print("Can't imread: ", mask_path + "/" + fn)
			continue
		mask=mask.reshape(mask.shape[0],mask.shape[1],1)

		img=cv2.resize(img, (224,224))/255.0
		mask=cv2.resize(mask, (224,224)).reshape(224,224,1)/255.0

		train_data.append(img)
		mask_data.append(mask)

	print("Load images finish")
	return np.array([i for i in train_data]), np.array([i for i in mask_data])

def main():
	# train_imgDir = "/home/xiping/mydisk2/imglib/my_imglib/coco/train2014_person"
	train_imgDir = "/coco/train2014_person"
	train_data, mask_data = get_data(train_imgDir)

	# print(train_data.shape)
	# print(mask_data.shape)
	# exit(0)

	print("================================")
	BACKBONE = 'mobilenetv2'
	# define model
	model = Unet(BACKBONE, classes=2, 
		input_shape=(None, None, 3),
		activation='softmax', 
		encoder_weights='imagenet')

	model.compile('Adam', loss=bce_jaccard_loss, metrics=[iou_score])

	
	print("================================")
	print("Start train...")
	# fit model
	# if you use data generator use model.fit_generator(...) instead of model.fit(...)
	# more about `fit_generator` here: https://keras.io/models/sequential/#fit_generator
	model.fit(
	    x=train_data,
	    y=mask_data,
	    batch_size=256,
	    epochs=100,
	    # validation_data=(x_val, y_val),
	)

if __name__ == '__main__':
	main()