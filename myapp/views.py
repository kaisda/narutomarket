from django.shortcuts import render, redirect
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


# def set_cookie(request, key=None, value=None):
#     response = HttpResponse('cookie儲存完畢')
#     response.set_cookie(key, value)
#     return response 

# def set_session(request, key=None, value=None):
#     response = HttpResponse('session儲存完畢')
#     request.session[key] = value
#     return response 

# 定義全域變數
cartlist = []
shipping = 100

def addtocart(request, type=None, id=None): # type指定購物車的四種行為
    # 使用全域變數
    global cartlist

    # 新增add 更新update 清空empty 刪除delete
    if type == 'add':
        product = ProductModel.objects.get(id = id)
        
        # 購物車裡有沒有已經存在的商品?
        # 如果有, 就更新 session 裡面的商品, 數量, 金額
        # 如果沒有, 就把商品放進 session裡
        # 用 True False 來判斷有沒有存在商品
        noCartSession = True
        for unit in cartlist:
                if product.pname == unit[0]:
                     unit[2] = str(int(unit[2]) + 1)
                     unit[3] = str(int(unit[3])+product.pprice*1)
                     noCartSession = False
        if noCartSession:
            templist = []
            
            # (pname, pprice, 1, 1*pprice)
            templist.append(product.pname)
            templist.append(str(product.pprice))
            templist.append(str(1))
            templist.append(str(product.pprice*1))
            
            cartlist.append(templist)
        request.session['cartlist']=cartlist
        # print(request.session['cartlist']) # 把session 資料列印到終端機顯示
        # return HttpResponse('使用者已選購商品') # 在頁面顯示加入成功資訊
        return redirect('/cart/')
    
def cart(request):
    #  return HttpResponse('這是購物車...')
    global cartlist             # 購物車的 session購物車的 session 全域變數
    global shipping             # 運費 shipping 全域變數
    localcartlist = cartlist    # 將全域變數改為區域變數, 會被locals() 傳送到網頁
    localshipping = shipping    # 將全域變數改為區域變數, 會被locals() 傳送到網頁
    
    total = 0                           # 金額小計, 會被locals()傳送到網頁
    for unit in cartlist:
         total = total + int(unit[3])

    grandtotal = total + localshipping  # 總價(金額+運費), 會被locals()傳送到網頁

    # print(cartlist) # 把 cartlist 的資料列印到終端機顯示
    return render(request, 'cart.html', locals())