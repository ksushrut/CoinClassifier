import torch
import torch.nn as nn
#from sklearn.preprocessing import LabelEncoder
from torchvision import models, transforms
from PIL import Image
import pandas as pd
import os
import cv2
import numpy as np
from movementz import Move, Stops
import time
import rclpy
#import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import argparse
class SimpleLabelEncoder:
    def __init__(self):  # Fix typo: should be __init__, not _init_
        self.classes_ = []
        self.class_to_index = {}

    def fit(self, y):
        unique_classes = sorted(set(y))
        self.classes_ = unique_classes
        self.class_to_index = {cls: idx for idx, cls in enumerate(unique_classes)}
        return self

    def transform(self, y):
        return [self.class_to_index[label] for label in y]

    def fit_transform(self, y):
        self.fit(y)
        return self.transform(y)

    def inverse_transform(self, indices):
        return [self.classes_[idx] for idx in indices]
def set_autofocus(device = '/dev/video0', enable = True):
	auto_value = '1' if enable else '0'
	try:
		subprocess.run(
		['v4l2-ctl', '-d', device, f' --set-ctrl=focus_auto={auto_value}'],
		check =True
		)
	except subprocess.CalledProcessError as e:
		print(f"Failed to set autofocus : {e}")


def image_preprocessor(img_path, img_size=(224, 224)):
    """
    Load, crop coin using Hough Circle detection, resize to standard size.
    """
    image = cv2.imread(img_path)
    if image is None:
        return None

    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    median_img = cv2.medianBlur(gray_img, 5)

    circles = cv2.HoughCircles(
        median_img,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=50,
        maxRadius=300
    )

    if circles is not None:
        circles = np.around(circles[0, :]).astype("int")
        x, y, r = circles[0]
        x1, y1 = max(x - r, 0), max(y - r, 0)
        x2, y2 = min(x + r, image.shape[1]), min(y + r, image.shape[0])
        coin_image = image[y1:y2, x1:x2]
    else:
        print("No coin detected in:", img_path)
        coin_image = image  # Fallback: use full image

    coin_image = cv2.cvtColor(coin_image, cv2.COLOR_BGR2RGB)
    coin_image = Image.fromarray(coin_image)
    final_image = coin_image.resize(img_size, Image.LANCZOS)
    return final_image

def save_preprocessed_image(input_path, output_path, output_size=(224, 224)):
    """
    Run preprocessing on image and save it to the mirrored output path.
    """
    coin_img = image_preprocessor(input_path, output_size)
    if coin_img is not None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        coin_img.save(output_path)
        print("Saved:", output_path)
    else:
        print("Failed:", input_path)

# ---- STEP 2: Recreate the model architecture ----
def load_model(num_classes, weights_path):
    model = models.wide_resnet50_2(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )
    model.load_state_dict(torch.load(weights_path, map_location='cpu'))
    model.to('cpu')
    model.eval()
    return model

# ---- STEP 3: Preprocess the input image ----
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def predict_image(image_path, model, class_names):
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to('cpu')
    
    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_class = predicted.item()
    #print(f"Predicted class: {predicted_class} (index: {predicted.item()})")
    return predicted_class



def main(args=None):
	le = SimpleLabelEncoder()
	df = pd.read_csv('filename.csv')
	df['encoded_class']=le.fit_transform(df['label'])
	class_names=df['encoded_class'].nunique()
	#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	weights_path = "finalmodel.pth"  
	model = load_model(num_classes=3, weights_path=weights_path)
	image_path = "/home/ubuntu/Grp V 47976586/Group V 47976586/capture_topic/saved_img/image0.jpg"
	save_preprocessed_image(image_path,image_path)
	val=predict_image(image_path, model, class_names)
	class_name=le.inverse_transform([val])
	print(class_name)
	if(class_name[0]=='10 Yen'):
		#print("In if")
		rclpy.init(args=args)
		parser = argparse.ArgumentParser(description='Machine Control')
		parser.add_argument('--linear_vel', type=float, default=0.01)
		parser.add_argument('--angular_vel', type=float, default=0.0)
		parsed_args, unknown = parser.parse_known_args()
		for i in range(20):
			mover=Move(parsed_args, 0.1, 0.0)
			rclpy.spin(mover)
			mover.destroy_node()
			rclpy.shutdown()
		"""
		time.sleep(5)
		parser = argparse.ArgumentParser(description='Machine Control')
		parser.add_argument('--linear_vel', type=float, default=0.00)
		parser.add_argument('--angular_vel', type=float, default=0.0)
		parsed_args, unknown = parser.parse_known_args()
		stopper=Stop(parsed_args)
		rlpy.spin(stopper)
		stopper.destroy_node()
		rclpy.shutdown()
		"""
	elif (class_name[0] == 'AUD 2 Dollar'):
		#print("In if")
		rclpy.init(args=args)
		parser = argparse.ArgumentParser(description='Machine Control')
		parser.add_argument('--linear_vel', type=float, default=0.01)
		parser.add_argument('--angular_vel', type=float, default=0.0)
		parsed_args, unknown = parser.parse_known_args()
		for i in range(20):
			mover=Move(parsed_args, 0.1, 0.1)
			rclpy.spin(mover)
			mover.destroy_node()
			rclpy.shutdown()
	else:
		#print("In if")
		rclpy.init(args=args)
		parser = argparse.ArgumentParser(description='Machine Control')
		parser.add_argument('--linear_vel', type=float, default=0.01)
		parser.add_argument('--angular_vel', type=float, default=0.0)
		parsed_args, unknown = parser.parse_known_args()
		for i in range(20):
			mover=Move(parsed_args, 0.1, -0.1)
			rclpy.spin(mover)
			mover.destroy_node()
			rclpy.shutdown()

	
if __name__=="__main__":
	main()
