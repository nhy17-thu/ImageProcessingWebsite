from urllib.request import urlretrieve

from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext

from .forms import RegisterForm, UserForm
from users import models
from django.shortcuts import render, redirect
from .forms import PicForm  # 上传图片的图表
from .models import Pic, User  # 保存上传图片相关信息的模型
from final_project.settings import MEDIA_ROOT
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
import datetime
from users.Object_Detection import func
from users.Classification18 import classify_18
from users.Classification152 import classify_152, imagenet_classes
from users.neural_style import stylize
from users.Face_Detection import face_detect
from users.Face_Clustering import face_cluster

import django.http
import json
import time
import os


def register(request):
	# get the "next" parameter from POST or GET
	# GET: "next" is passed by url -> /?next=value
	# POST: "next" is passed by form -> <input type="hidden" name="next" value="{{ next }}"/>
	# "next" will record the previous visiting page, and then redirect back after registration
	redirect_to = request.POST.get('next', request.GET.get('next', ''))

	if request.method == 'POST':
		# submit username and password
		# 實例化一個用戶註冊表單
		form = RegisterForm(request.POST)

		if form.is_valid():
			# if the form is valid, save it
			# django 自己的包
			form.save()

			if redirect_to:
				return redirect(redirect_to)
			else:
				return redirect('/')
	else:
		# if request is not POST, it indicates that the user is visiting register page.
		# so show an empty register form
		form = RegisterForm()

	return render(request, 'users/register.html', context={'form': form, 'next': redirect_to})


def index(request):
	context = {}
	form = PicForm
	context['form'] = form
	return render(request, 'index.html', context)


class UserFormLogin(object):
	pass


def login(request):
	if request.method == 'POST':
		userform = UserForm(request.POST)
		if userform.is_valid():
			# 获取表单用户密码
			username = userform.cleaned_data['username']
			password = userform.cleaned_data['password']
			# 获取的表单数据与数据库进行比较
			user = auth.authenticate(username=username, password=password)
			request.session["has_login"] = True
			if user:
				auth.login(request, user)
				response = HttpResponseRedirect('/')
				response.set_cookie('username', username)
				return response
			else:
				return HttpResponseRedirect('/users/login/')
	else:
		userform = UserForm()
	return render(request, 'users/login.html', {'userform': userform})


def show_pic(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic = Pic.objects.get(pk=pic_id)
			pic_path = os.path.join('media', str(pic.picture))

			with open(pic_path, 'rb') as image:
				image_data = image.read()
			# 使用文件流，从服务器后台发送图片（二进制数据）到网页
			return django.http.HttpResponse(image_data, content_type='image/png')
		except Exception as e:
			print(e)
			return django.http.HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


def show_face_pic(request, folder_id, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic_path = os.path.join('media', 'faces', str(folder_id), f'face_{pic_id}.jpg')

			with open(pic_path, 'rb') as image:
				image_data = image.read()
			# 使用文件流，从服务器后台发送图片（二进制数据）到网页
			return django.http.HttpResponse(image_data, content_type='image/png')
		except Exception as e:
			print(e)
			return django.http.HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


# 展示id对应图片的Detection处理结果
def show_result(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic = Pic.objects.get(pk=pic_id)
			res_path = os.path.join('media', str(pic.res))

			while not os.path.exists(res_path):
				# 每隔0.1秒检查一次输出文件是否存在，若已输出则返回相应结果
				time.sleep(0.1)

			with open(res_path, 'rb') as image:
				image_data = image.read()

			# 使用文件流，从服务器后台发送处理结果（二进制数据）到网页
			return HttpResponse(image_data, content_type='image/png')
		except Exception as e:
			print(e)
			return HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


# 展示id对应图片的风格迁移结果
def show_result_transfer(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic = Pic.objects.get(pk=pic_id)
			res_path = os.path.join('media', str(pic.transfer))

			while not os.path.exists(res_path):
				# 每隔0.1秒检查一次输出文件是否存在，若已输出则返回相应结果
				time.sleep(0.1)

			with open(res_path, 'rb') as image:
				image_data = image.read()

			# 使用文件流，从服务器后台发送处理结果（二进制数据）到网页
			return HttpResponse(image_data, content_type='image/png')
		except Exception as e:
			print(e)
			return HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


# 展示id对应图片的人脸识别结果，一张图中所有人脸
def show_result_faces(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic = Pic.objects.get(pk=pic_id)
			res_path = os.path.join('media', str(pic.faces))

			while not os.path.exists(res_path):
				# 每隔0.1秒检查一次输出文件是否存在，若已输出则返回相应结果
				time.sleep(0.1)

			with open(res_path, 'rb') as image:
				image_data = image.read()

			# 使用文件流，从服务器后台发送处理结果（二进制数据）到网页
			return HttpResponse(image_data, content_type='image/png')
		except Exception as e:
			print(e)
			return HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


def show_result_res18(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			while not Pic.objects.get(pk=pic_id).classification18:
				# 每隔0.1秒检查一次输出结果是否存在，若已输出则返回相应结果
				time.sleep(0.1)

			return HttpResponse(Pic.objects.get(pk=pic_id).classification18)
		except Exception as e:
			print(e)
			return HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


def show_result_res152(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			while not Pic.objects.get(pk=pic_id).classification152:
				time.sleep(0.1)

			return HttpResponse(Pic.objects.get(pk=pic_id).classification152)
		except Exception as e:
			print(e)
			return HttpResponse(str(e))
	else:
		return HttpResponse("please login with your own session")


# 使用AJAX动态返回表单
def check_records(request, page):
	if request.session.get("has_login", False):
		record_list = []
		user = request.user
		for record in Pic.objects.all():
			if record.username == user.username:
				record_list.append({
					'user': record.username,
					'record_id': record.id,
					'input_picture': os.path.join('media', str(record.picture)),
					'output_picture': os.path.join('media', str(record.res)),
					'upload_time': record.timestamp
				})

		# 规定每页10条数据，进行分割
		paginator = Paginator(record_list, 10)

		if request.method == 'GET':
			try:
				records = paginator.page(page)
			except PageNotAnInteger:
				# 如果请求的页数不是整数，返回第一页
				records = paginator.page(1)
			except EmptyPage:
				# 如果页数不在合法范围内，返回结果最后一页
				records = paginator.page(paginator.num_pages)
			except InvalidPage:
				# 如果请求的页数不存在，重定向页面
				return HttpResponse('找不到页面内容')

			template_view = 'users/check_record.html'

			return render(request, template_view, {'records': records})
	else:
		return HttpResponse("please login with your own session")


# 按照日期范围查询记录
def search(request, page):
	if request.session.get("has_login", False):
		start_date_str = request.GET.get('start_date')
		end_date_str = request.GET.get('end_date')
		start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
		end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

		record_list = []
		user = request.user
		for record in Pic.objects.all():
			if record.username == user.username:
				update_date = datetime.datetime.strptime(record.timestamp, '%Y-%m-%d %H:%M:%S').date()
				if start_date <= update_date <= end_date:
					record_list.append({
						'user': record.username,
						'record_id': record.id,
						'input_picture': os.path.join('media', str(record.picture)),
						'output_picture': os.path.join('media', str(record.res)),
						'upload_time': record.timestamp
					})

		# 规定每页10条数据，进行分割
		paginator = Paginator(record_list, 10)

		try:
			records = paginator.page(page)
		except PageNotAnInteger:
			# 如果请求的页数不是整数，返回第一页
			records = paginator.page(1)
		except EmptyPage:
			# 如果页数不在合法范围内，返回结果最后一页
			records = paginator.page(paginator.num_pages)
		except InvalidPage:
			# 如果请求的页数不存在，重定向页面
			return HttpResponse('找不到页面内容')

		return render(request, 'users/check_record.html',
		              {'records': records, 'searched': True, 'start_date': start_date_str, 'end_date': end_date_str})
	else:
		return HttpResponse("please login with your own session")


# empty file and url will make it buggy
def upload_and_view(request):
	if request.session.get("has_login", False):
		if request.method == "POST":
			form = PicForm(request.POST, request.FILES)

			if form.is_valid():
				try:
					pic = form.cleaned_data["picture"]
					url = form.cleaned_data["url"]

					current_user = request.user
					username = current_user.username

					time_now = int(time.time())
					time_local = time.localtime(time_now)
					timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
					nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
					context = {}
					form = PicForm
					context['form'] = form

					if pic:
						picture = pic

					elif url:
						path = "./media/pictures/"
						pic_name = str(nowTime) + ".jpg"
						urlretrieve(url, path + pic_name)
						picture = os.path.join('pictures', pic_name)
					# print(picture)

					pic_content = models.Pic.objects.create(timestamp=timestamp, username=username, picture=picture)

					# 在前端网页渲染以后再进行图片处理，这里先指定路径
					temp_path = str(str(picture).split('.')[0])
					res = os.path.join('pictures', temp_path.split("/")[-1]) + '_res.jpg'
					transfer = os.path.join('pictures', temp_path.split("/")[-1]) + '_transfer.jpg'
					faces = os.path.join('pictures', temp_path.split("/")[-1]) + '_faces.jpg'
					pic_content.res = res
					pic_content.transfer = transfer
					pic_content.faces = faces
					pic_content.classification18 = ''
					pic_content.classification152 = ''
					pic_content.save()
					context['pic_id'] = pic_content.id
					context['uploaded'] = True

				except Exception as e:
					print(e)
					return render(request, 'index.html')  # 如果没有上传照片，返回首页

			else:
				return render(request, 'index.html')  # 如果没有上传照片，返回首页

		else:
			context = {}
			form = PicForm
			context['form'] = form
	else:
		return HttpResponse("please login with your own session")
	return render(request, 'users/upload_and_view.html', context)


# 响应前端网页的结果，开始处理并生成结果
def process_images(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic = Pic.objects.get(id=pic_id)
			pic_path = os.path.join('media', str(pic.picture))
			# 对象检测Detection处理
			func(pic_path)

			# Style Transfer处理
			stylize(pic_path)

			# 小图分类ResNet-18处理
			pic.classification18 = classify_18(pic_path)

			# ResNet-152 1000类分类
			pic.classification152 = classify_152(pic_path)

			# dlib实现正面人脸检测
			face_detect(pic_path)

			pic.save()  # 处理完了记得保存到数据库
			return HttpResponse()

		except ObjectDoesNotExist as e:
			return HttpResponse(e)
	else:
		return HttpResponse("please login with your own session")


def delete(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request deletion for your own pictures ONLY!')
		try:
			# 不保存关联的图像文件，将其一起删除
			Pic.objects.get(id=pic_id).delete()
			return check_records(request, 1)

		except ObjectDoesNotExist as e:
			return HttpResponse(e)
	else:
		return HttpResponse("please login with your own session")


def delete_batch(request):
	if request.session.get("has_login", False):
		start_date_str = request.POST.get('start_date')
		end_date_str = request.POST.get('end_date')
		start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
		end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

		user = request.user
		for record in Pic.objects.all():
			if record.username == user.username:
				update_date = datetime.datetime.strptime(record.timestamp, '%Y-%m-%d %H:%M:%S').date()
				if start_date <= update_date <= end_date:
					record.delete()
		return HttpResponse('批量删除成功！')
	else:
		return HttpResponse("please login with your own session")


# 渲染新页面以查看所有处理结果
def review_result(request, pic_id):
	if request.session.get("has_login", False):
		if request.user.username != Pic.objects.get(id=pic_id).username:
			return HttpResponse('Please request results for your own pictures ONLY!')
		try:
			pic = Pic.objects.get(id=pic_id)
			context = {
				'pic_id': pic_id,
				'classification18': pic.classification18,
				'classification152': pic.classification152
			}
			return render(request, 'users/review_result.html', context)
		except ObjectDoesNotExist as e:
			return HttpResponse(e)
		except Exception as e:
			return HttpResponse(e)
	else:
		return HttpResponse("please login with your own session")


# 根据ResNet-152分类的结果返回图片id
def check_records_byclass(request):
	if request.session.get("has_login", False):
		try:
			content = {}
			for num, value in imagenet_classes.items():
				content[value] = []
				for pic in Pic.objects.filter(classification152__contains=value):
					if pic.username == request.user.username:
						content[value].append(pic.id)

			return render(request, 'users/check_record_byclass.html', {'content': content})
		except ObjectDoesNotExist as e:
			return HttpResponse(e)
		except Exception as e:
			return HttpResponse(e)
	else:
		return HttpResponse("please login with your own session")


# 利用dlib实现人脸聚类功能，输出不同人脸的对应图片
def check_records_byface(request):
	if request.session.get("has_login", False):
		pic_list = []
		for pic in Pic.objects.all():
			if pic.username == request.user.username:
				pic_list.append({
					'path': os.path.join('media', str(pic.picture)),
					'id': pic.id
				})

		# 执行人脸聚类操作并返回所有输出图片路径
		# 字典键为文件夹编号，值为输出图片信息组成的数组（详见Face_Clustering.py）
		faces_path = face_cluster(pic_list)
		# 受sqlite3特性限制，在数据表中存储数组/字典型数据将有较大困难
		# 因此选择在每一次打开人脸聚类页面时都即时演算所有图片，并将结果即时传送给前端页面

		# 在模版页面上展示所有不同人脸的结果
		return render(request, 'users/face_clustering_result.html', {'faces_path': faces_path})
	else:
		return HttpResponse("please login with your own session")
