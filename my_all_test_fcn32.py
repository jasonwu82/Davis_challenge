#!/usr/bin/env python

import os
import scipy as scp
import scipy.misc

import numpy as np
import tensorflow as tf

import nets.fcn32_vgg as fcn32_vgg
import utils
from settings import settings
#from imagenet_classes import class_names
from pascal.pascal_classes import class_names
from tensorflow.python.framework import ops
def show_top5_class(img):
    unique, counts = np.unique(img, return_counts=True)
    preds = (np.argsort(counts)[::-1])[0:5]
    for p in preds:
        print class_names[unique[p]], counts[p]
#img1 = scp.misc.imread("./test_data/tabby_cat.png")
dir_path = "/home/hungwei/cv542/CV_semanticSegmentation/data/TrainVal/VOCdevkit/VOC2011/JPEGImages/"

with open("train_pascal.txt") as f:
    contents = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip()+'.jpg' for x in contents] 
img_filename = "2007_000121.jpg"
img_filename_without_extension = os.path.splitext(img_filename)[0] 
img1 = scp.misc.imread(os.path.join(dir_path,img_filename))
#img1 = scp.misc.imread("./test_data/bus1.jpg")
#np.set_printoptions(threshold=np.nan,edgeitems=100)
np.set_printoptions(threshold=np.nan)
with tf.Session() as sess:
    images = tf.placeholder("float")
    feed_dict = {images: img1}
    batch_images = tf.expand_dims(images, 0)

    vgg_fcn = fcn32_vgg.FCN32VGG(vgg16_npy_path='./tmp/vgg16.npy')
    with tf.name_scope("content_vgg"):
        vgg_fcn.build(batch_images,num_classes=21, debug=True)

    print('Finished building Network.')

    #init = tf.global_variables_initializer()
    ckpt = tf.train.get_checkpoint_state('checkpoints/')
    saver = tf.train.Saver()
    saver.restore(sess,ckpt.model_checkpoint_path)
    #sess.run(init)

    print('Running the Network')
    tensors = [vgg_fcn.pred, vgg_fcn.pred_up,vgg_fcn.score_fr]

    for i in range(30):
        print("reading img: " + content[i])
        img_filename = content[i]
        img_filename_without_extension = os.path.splitext(img_filename)[0] 
        img1 = scp.misc.imread(os.path.join(dir_path,img_filename))
        feed_dict = {images: img1}
        down, up, down_score = sess.run(tensors, feed_dict=feed_dict)
        
        max_scores = np.argmax(down_score,axis=3)

        print('down: ')
        print(down[0])
        #show_top5_class(down[0])
        show_top5_class(down[0])
        print('up: ')
        show_top5_class(up[0])
        down_color = utils.color_image(down[0])
        up_color = utils.color_image(up[0])
        scp.misc.imsave(os.path.join(settings.img_result,img_filename_without_extension+'_original.png'),img1)
        scp.misc.imsave(os.path.join(settings.img_result,img_filename_without_extension+'_fcn32_downsampled.png'), down_color)
        scp.misc.imsave(os.path.join(settings.img_result,img_filename_without_extension+'_fcn32_upsampled.png'), up_color)
