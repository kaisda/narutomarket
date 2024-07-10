from django.shortcuts import render, redirect
from django.http import HttpResponse
from myapp.models import ProductModel, OrderModel, DetailModel
from smtplib import SMTP
from email.mime.text import MIMEText

# Create your views here.

def index(request):
    # return HttpResponse('這裡是index')

    # 設立變數並存放從資料庫撈出來的所有資料, 透過locals()送去指定網頁
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
            # 全域變數
            cartlist.append(templist)
        request.session['cartlist'] = cartlist
        # print(request.session['cartlist']) # 把session 資料列印到終端機顯示
        # return HttpResponse('使用者已選購商品') # 在頁面顯示加入成功資訊
        return redirect('/cart/')
    elif type == 'empty':
        cartlist = []                          # 清空購物車資訊
        request.session['cartlist']=cartlist   # 重設session
        return redirect('/cart/')              # 重新導回購物車頁面
    elif type == 'update':
        if request.method == 'POST':
            n = 1
            for unit in cartlist:
                unit[2] = request.POST.get('quantity'+str(n), '1')
                unit[3] = str(int(unit[1])*int(unit[2]))
                n = n+1
            request.session['cartlist'] = cartlist
            # return HttpResponse('POST成功')
            return redirect('/cart/')
    elif type == 'remove':
         del cartlist[int(id)]      # 這個id是cartlist的索引值
         request.session['cartlist']=cartlist   # 重設session
         return redirect('/cart/')              # 重新導回購物車頁面
         

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

def cartorder(request):
    global cartlist
    global shipping 
    localcartlist = cartlist
    localshipping = shipping
    total = 0
    for unit in cartlist:
         total = total + int(unit[3])
    grandtotal = total + localshipping
    return render(request, 'cartorder.html', locals())

def cartok(request):
    global cartlist
    global shipping
    if request.method == 'POST':
        customername = request.POST['customername']
        customerphone = request.POST['customerphone']
        customeremail= request.POST['customeremail']
        customeraddress = request.POST['customeraddress']
        paytype = request.POST['paytype']
        # print(customername + " " + customerphone + " " + customeremail + " " + customeraddress + " " + paytype)
        total = 0
        for unit in cartlist:
            total = total + int(unit[3])
        grandtotal = total + shipping

    #-- 將訂購人資訊寫入OrderModel表單 ---
    productOrder = OrderModel.objects.create(customername = customername, customerphone = customerphone, customeremail = customeremail, customeraddress = customeraddress, paytype = paytype, grandtotal = grandtotal, shipping = shipping, subtotal = total)
    productOrder.save()

    #-- 將該筆訂單寫入DetailModel表單 ---
    #-- 預判商品不會只有一筆, 用 for 迴圈逐筆寫入資料庫
    dtotal = 0
    for unit in cartlist:
        dtotal = int(unit[1]) * int(unit[2])
        unitDetail = DetailModel.objects.create(pname = unit[0], unitprice = int(unit[1]), quantity = int(unit[2]), dtotal = dtotal, dorder = productOrder)
        unitDetail.save()
    
    #-- 訂單送出後清空購物車 ---
    cartlist = []


    #-- 郵件寄送
    mailfrom = 'ftcyang@gmail.com'
    mailpw = 'mkwmbiigidlsmkju'
    mailto = customeremail
    mailsubject = '木葉商城訂單通知'
    mailcontent = customername + ', 您所選取的商品已訂購成功, 我們會盡速且祕密的送至您指定的地點, 感謝您的支持, 歡迎隨時回來 !'
    send_message(mailfrom, mailpw, mailto, mailsubject, mailcontent)

    return render(request, 'cartok.html', locals())
    
def send_message(mailfrom, mailpw, mailto, mailsubject, mailcontent):
    strSmtp = 'smtp.gmail.com:587'
    strAccount = mailfrom
    strPassword = mailpw
    msg = MIMEText(mailcontent)
    msg['Subject'] = mailsubject
    mailto1 = mailto
    server = SMTP(strSmtp)
    server.ehlo()       # 與主機溝通
    server.starttls()   # TTLS安全認證
    server.login(strAccount, strPassword)
    server.sendmail(strAccount, mailto1, msg.as_string())