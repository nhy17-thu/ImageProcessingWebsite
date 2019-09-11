from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

# django 內置的用戶註冊表單
# class UserCreationForm(forms.ModelForm):
#    class Meta:
#        model = User   # 關聯的是 django 内置的 User 模型 auth.User
#        fields = ("username",)
#        field_classes = {'username': UsernameField}


# 繼承上面的 改成自己定義的User類
class RegisterForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User    # users.User
		fields = ("username", )


class UserForm(forms.Form):
	username = forms.CharField(label='username',max_length=100)
	password = forms.CharField(label='password',widget=forms.PasswordInput())


class PicForm(forms.Form):
	picture = forms.ImageField(label='pic:', required=False)
	url = forms.URLField(label='url: ', required=False)