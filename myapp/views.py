from django.shortcuts import render
from django.http import HttpResponse
from myapp.models import ProductModel

# Create your views here.

def index(request):
    # return HttpResponse('這裡是index')

    # 設立變數並存放從資料庫撈出來的所有資料
    products = ProductModel.objects.all()
    productlist = []
    for i in range(1, 9):
        product =  ProductModel.objects.get(id = i)
        productlist.append(product)
    return render(request, 'index.html', locals())


def detail(request, id=None):
    product= ProductModel.objects.get(id = id)
    return render(request, 'detail.html', locals())

