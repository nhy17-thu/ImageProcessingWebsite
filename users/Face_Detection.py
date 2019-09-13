import dlib
import numpy as np
import cv2


def face_detect(image):
	# dlib 检测器
	detector = dlib.get_frontal_face_detector()
	# 读取图像
	img = cv2.imread(image)
	# dlib 检测
	faces = detector(img, 1)
	# print(f'Faces in all: {len(faces)} \n')

	# 记录人脸矩阵大小
	height_max = 0
	width_sum = 0

	# 计算要生成的图像 img_blank 大小
	for face in faces:
		# 计算矩形框大小
		height = face.bottom()-face.top()
		width = face.right()-face.left()

		# 处理宽度
		width_sum += width

		# 处理高度
		if height > height_max:
			height_max = height
		else:
			height_max = height_max

	# 生成用来显示的结果图像
	img_blank = np.zeros((height_max, width_sum, 3), np.uint8)

	# 记录每次开始写入人脸像素的宽度位置
	blank_start = 0

	# 将人脸填充到 img_blank
	for face in faces:

		height = face.bottom()-face.top()
		width = face.right()-face.left()

		# 填充
		for i in range(height):
			for j in range(width):
				img_blank[i][blank_start+j] = img[face.top()+i][face.left()+j]
		# 调整图像
		blank_start += width

	# 保存图像
	output_path = image.split('.')[0] + '_faces.jpg'
	cv2.imwrite(output_path, img_blank)
