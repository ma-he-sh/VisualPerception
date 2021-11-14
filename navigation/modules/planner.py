import cv2
import os
import config as ENV
from modules.errors import Error

class SrcImageNotFound(Error):
	pass

class SrcImage:
	def __init__(self, file_name):
		self.file_name = file_name

	def get_image_path(self):
		return os.path.join( ENV.UPLOAD_FOLDER, self.file_name )

	def get_image(self):
		imagePath = self.get_image_path()
		if os.path.isfile( imagePath ):
			return cv2.imread( imagePath, 0 )
		return False

class Planner(SrcImage):
	def __init__(self, file_name, real_width, real_height ):
		self.file_name = file_name
		self.real_width = real_width
		self.real_height= real_height

	def process_image(self):
		image = self.get_image()
		print(image)