import os
import shutil
import dlib


cluster_size_threshold = 2  # 修改此阈值参数可更改类内最低的人脸数


detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('users/config/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('users/config/dlib_face_recognition_resnet_model_v1.dat')


# 传入所有需要聚类的图片路径
def face_cluster(input_images):
	# 初始化，防止多次打开导致重复生成
	descriptors = []
	images = []

	for image in input_images:
		# 逐个加载图片
		img = dlib.load_rgb_image(image['path'])
		# 检测人脸数量和位置
		faces = detector(img, 1)
		# print(f'{len(faces)} faces detected in', image['path'])

		# 遍历所有人脸
		for face in faces:
			# 利用68关键点模型检测人脸关键点
			shape = sp(img, face)
			# 将关键点集转化为128维特征向量
			face_descriptor = facerec.compute_face_descriptor(img, shape)
			descriptors.append(face_descriptor)
			images.append((img, shape, image['path'], image['id']))

	# CW聚类算法进行人脸聚类
	labels = dlib.chinese_whispers_clustering(descriptors, 0.5)
	num_classes = len(set(labels))
	# print(f'{num_classes} Classes Detected')

	# 根据标签构造分类字典
	clusters = [[] for _ in range(num_classes)]
	for i, pair in enumerate(images):
		clusters[labels[i]].append(pair)

	process = save_face_chip

	faces_path = {}
	for i, cluster in enumerate(clusters):
		if len(cluster) > cluster_size_threshold:
			# 输出容量大于阈值的分类，过滤部分无意义结果
			cluster_folder_path = f'media/faces/{i}'

			# 先清空文件夹再重新生成，防止结果堆叠
			if os.path.exists(cluster_folder_path):
				shutil.rmtree(cluster_folder_path)
			os.makedirs(cluster_folder_path)

			# 将每个输出路径记录在返回结果中
			faces_path[str(i)] = []
			# print(f'Output: {cluster_folder_path}')

			for j, pair in enumerate(cluster):
				img, shape, image, pic_id = pair
				process({
					'img': img,
					'shape': shape,
					'file_path': os.path.join(cluster_folder_path, f'face_{j}')
				})
				# 将每张输出人脸记录在返回结果中
				faces_path[str(i)].append({
					'number': str(j),
					'pic_id': pic_id
				})

	# print(faces_path)
	return faces_path


def save_face_chip(option):
	dlib.save_face_chip(option['img'], option['shape'], option['file_path'], size=150, padding=0.25)
