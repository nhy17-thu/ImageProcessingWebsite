import torch
import torchvision
import torch.nn.functional
import torchvision.transforms as transforms
from torch.autograd import Variable
from users.resnet18 import ResNet18
from PIL import Image

device = torch.device('cpu')

# cifar-10的标签
classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

tran = transforms.Compose([
	transforms.Resize((32, 32)),
	transforms.ToTensor(),
	transforms.Normalize(mean=[0.4914, 0.4822, 0.4465],
	                     std=[0.2023, 0.1994, 0.2010])
])


def classify_image(image):
	# 加载训练好的ResNet-18模型
	net = ResNet18()
	net.load_state_dict(torch.load('users/config/resnet18.pth', map_location=device))
	net.eval()

	img = Image.open(image)
	img = tran(img)   # 这里经过转换后输出的input格式是[C,H,W],网络输入还需要增加一维批量大小B
	img = img.unsqueeze(0)  # 增加一维，输出的img格式为[1,C,H,W]

	outputs = net(Variable(img))    # 将图片输入网络得到输出
	# 取得分最高的类 (outputs.data的索引号)
	_, predicted = torch.max(outputs.data, 1)

	return f'Predicted: {classes[predicted[0]]}'
