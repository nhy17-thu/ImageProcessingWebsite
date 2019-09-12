import re

import torch
from torchvision import transforms

import users.neural_transfer.utils as utils
from users.neural_transfer.transformer_net import TransformerNet
from users.neural_transfer.vgg import Vgg16


def stylize(image):
	device = torch.device('cpu')

	content_image = utils.load_image(image)
	content_transform = transforms.Compose([
		transforms.ToTensor(),
		transforms.Lambda(lambda x: x.mul(255))
	])
	content_image = content_transform(content_image)
	content_image = content_image.unsqueeze(0).to(device)

	with torch.no_grad():
		style_model = TransformerNet()
		# 更改此处模型文件可以更改不同风格
		state_dict = torch.load('users/config/mosaic.pth')
		# remove saved deprecated running_* keys in InstanceNorm from the checkpoint
		for k in list(state_dict.keys()):
			if re.search(r'in\d+\.running_(mean|var)$', k):
				del state_dict[k]
		style_model.load_state_dict(state_dict)
		style_model.to(device)
		output = style_model(content_image).cpu()

	output_path = image.split('.')[0] + '_transfer.jpg'
	utils.save_image(output_path, output[0])
