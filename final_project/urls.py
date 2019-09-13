"""final_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from users import views
from django.views.static import serve
from final_project.settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^users/', include('users.urls')),
	url(r'^users/', include('django.contrib.auth.urls')),
	url(r'^$', views.index, name='index'),
	# url(r'^save_profile/', views.save_pic, name='save_pic'),
	# url(r'^static/(?P<path>.*)', serve, {"document_root": STATIC_ROOT}),
	url(r'^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),

	url(r'^show_pic/(\d+)', views.show_pic, name='image'),
	# 获取detection结果
	url(r'^show_result/(\d+)', views.show_result, name='image_result'),
	# 获取transfer结果
	url(r'^show_result_transfer/(\d+)', views.show_result_transfer, name='image_result_transfer'),
	# 获取ResNet18十分类结果
	url(r'^show_result_res18/(\d+)', views.show_result_res18, name='image_result_res18'),
	# 获取ResNet152分类结果
	url(r'^show_result_res152/(\d+)', views.show_result_res152, name='image_result_res152'),
	# 获取人脸识别结果
	url(r'^show_result_faces/(\d+)', views.show_result_faces, name='image_result_faces'),

	url(r'^check_records/(\d+)', views.check_records, name='checkRecords'),
	url(r'^search/(\d+)', views.search, name='search'),
	url(r'^upload/', views.upload_and_view, name='upload'),
	url(r'^delete/(\d+)', views.delete, name='delete'),
	url(r'^delete_batch/', views.delete_batch, name='delete_batch'),
	url(r'^review_result/(\d+)', views.review_result, name='review_result'),
	# 响应前端指令，开始处理图片
	url(r'^request_process/(\d+)', views.process_images, name='start_processing'),
	url(r'^check_records_byclass/', views.check_records_byclass, name='checkByClass'),
	# 执行人脸聚类操作并在新页面浏览结果
	url(r'^check_records_byface/', views.check_records_byface, name='checkByFace'),
	# 返回裁剪后的脸部图片，参数依次为文件夹编号/图片编号
	url(r'show_face_pic/(\d+)/(\d+)', views.show_face_pic, name='show_face_pic'),
]
