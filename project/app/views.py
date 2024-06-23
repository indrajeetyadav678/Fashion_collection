from django.shortcuts import render,redirect,get_object_or_404
from .models import *
# from .models import Product, AddItem,Registration
from django.conf import settings
from project.settings import *
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import FileResponse
from django.template.loader import render_to_string
import pdfkit
import logging


# Create your views here.
def Index(request):
    # del request.session['user_data']
    try:
        logindetails=request.session['user_data']
        print("--------------->",logindetails)
        addtocart = request.session.get('addtocart')
        leng = 0
        if addtocart:
            leng=len(addtocart)
        return render(request,'index.html',{'leng':leng,'logindetails':logindetails,'adminDetails':adminDetails})
    except:
        return render(request,'index.html')
    
def About(request):
    addtocart = request.session.get('addtocart')
    logindetails=request.session['user_data']
    leng = 0
    if addtocart:
       leng=len(addtocart)
    return render(request,'about.html',{'leng':leng,'logindetails':logindetails,'adminDetails':adminDetails})

def AddProduct(request):
    addtocart = request.session.get('addtocart')
    leng = 0
    if addtocart:
       leng=len(addtocart)
    return render(request,'Additem.html',{'leng':leng,'adminDetails':adminDetails})


def Productdata(request):
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('img')

        AddItem.objects.create(Name = name,
                                 Price = price,
                                  Image = image)
        
        addtocart = request.session.get('addtocart')
        leng = 0
        if addtocart:
           leng=len(addtocart)
        return render(request,'AddItem.html',{'leng':leng})

def allProduct(request):
    item = AddItem.objects.all()
    addtocart = request.session.get('addtocart')
    logindetails=request.session['user_data']
    leng = 0
    if addtocart:
       leng=len(addtocart)
   
    return render(request,'Products.html',{'item':item, 'media_url':settings.MEDIA_URL,'leng':leng,'logindetails':logindetails,'adminDetails':adminDetails})


def AddToCart(request,pk):
    if request.method == "POST":
        addtocart = request.session.get('addtocart',[])
        addtocart.append(pk)
        request.session['addtocart'] = addtocart   # for again put change value in session
        # return redirect('Product')
        item = AddItem.objects.all()
        logindetails=request.session['user_data']
        leng = 0
        if addtocart:
           leng=len(addtocart)
        return render(request,'Products.html',{'item':item,'media_url':settings.MEDIA_URL,'leng':leng,'logindetails':logindetails})
    
def Cart(request):
    addtocart = request.session.get('addtocart')
    logindetails=request.session['user_data']
    print("------------------>",logindetails)
    Cartdetails = []
    TotalAmount = 0
    leng = 0
    if addtocart:
       leng=len(addtocart)
    
    for i in addtocart:
        data = AddItem.objects.get(id=i)
        context={
            'id':data.id,
            'Nm':data.Name,
            'Pr':data.Price,
            'Img':data.Image,
        }
        TotalAmount+=data.Price
        Cartdetails.append(context)
    return render(request,'Cart.html',{'Cartdetails':Cartdetails,'media_url':MEDIA_URL,'TotalAmount':TotalAmount,'leng':leng,'logindetails':logindetails})


def Delete(request,pk):
    addtocart = request.session.get('addtocart')
    addtocart.remove(pk)
    request.session['addtocart'] = addtocart
    
    Cartdetails = []
    TotalAmount = 0
    leng = 0
    logindetails=request.session['user_data']
    if addtocart:
       leng=len(addtocart)
    
    for i in addtocart:
        data = AddItem.objects.get(id=i)
        context={
            'id':data.id,
            'Nm':data.Name,
            'Pr':data.Price,
            'Img':data.Image,
        }
        TotalAmount+=data.Price
        Cartdetails.append(context)
    return render(request,'Cart.html',{'Cartdetails':Cartdetails,'media_url':MEDIA_URL,'TotalAmount':TotalAmount,'leng':leng,'logindetails':logindetails})



def Payment(request):
    logindetails=request.session['user_data']
    addtocart = request.session.get('addtocart')
    try:
        cart_no=len(addtocart)
    except:
        cart_no=0
    # ------------------------------------------
    amount=int(request.POST.get('amount'))*100
    print("---------------->amount",amount)
    client = razorpay.Client(auth=("rzp_test_8jTLUV3aVex82Q","n3PL7ZbSgnKSWJeA1s9ndhaO"))
    data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
    # print(data)
    payment = client.order.create(data=data)
    # print("Payment ----->",payment)
    global Payableamount 
    Payableamount=payment
    # print(payment['id'])
    global order_id
    order_id = payment['id']

    # ------------- get data from addtocard session ------------------
    addcart_data = request.session.get('addtocart', [])
    # print(addcartround(_data)
    total_amount = 0
    pro_data = []

    for item in addcart_data:
        # print(item)
        pro_value = AddItem.objects.get(id=item)
        print(pro_value)
        pro_data.append(pro_value)
        total_amount += pro_value.Price
        #-------------- purchase AddItem data save ------------ 
        print(logindetails)
        print(logindetails['Em'])
        pr_data={
            "Prod_Image1":pro_value.Image,
            "Prod_Price":pro_value.Price,
            "Order_id":payment['id'],
            "Email_id":logindetails['Em'],
        }
        # print("asas",logindetails["Em"])
        Purchaseproduct.objects.create(**pr_data)
    
    # ---------- Order Create data save in Paymentdatamodel ------------------
    PaymentdataModel.objects.create(
        Email=logindetails['Em'],
        Amount=payment['amount']/100,
        Amount_paid=payment['amount_paid']/100,
        Amount_due=payment['amount_due']/100,
        Currency=payment['currency'],
        Receipt =payment['receipt'],
        Status=payment['status'],
        Attempts=payment['attempts'],
        Notes=payment['notes'],
        Order_id=payment['id'],
    )

    cart_length = len(addcart_data)
    Context={
        'logindetails':logindetails,
        'addcartno': cart_no, 
        'pay_data':data, 
        'media_url': settings.MEDIA_URL,
        'payment':payment,
        'amount': total_amount,
        'prod_data': pro_data,
        'length':cart_length,
        'makepay':True
    }
    # print(payment)
    return render(request, 'Cart.html', Context)


# def Payment(request):
    # global payment
    # amount = int(request.POST.get('amount'))
    # amunts=amount*100

    # client = razorpay.Client(auth=("rzp_test_3LJ7CBlMbFfwT6","4thIATbNrfvi0N6mdFDThupO"))

    # data = { "amount": amunts, "currency": "INR", "receipt": "order_rcptid_11" }
    # payment = client.order.create(data=data)

    # Product.objects.create(amount=amount, order_id=payment['id'])

    # addtocart = request.session.get('addtocart')
    # Cartdetails = []
    # TotalAmount = 0
    # leng = 0
    # if addtocart:
    #    leng=len(addtocart)
    # for i in addtocart:
    #     data = AddItem.objects.get(id=i)
    #     context={
    #         'id':data.id,
    #         'Nm':data.Name,
    #         'Pr':data.Price,
    #         'Img':data.Image,
    #     }
    #     TotalAmount+=data.Price
    #     Cartdetails.append(context)
    # return render(request,'Cart.html',{'Cartdetails':Cartdetails,'media_url':MEDIA_URL,'TotalAmount':TotalAmount,'payment':payment,'leng':leng,'logindetails':logindetails})


from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from .models import PaymentdataModel, Invoicemodel, AddItem, Purchaseproduct
import razorpay

@csrf_exempt
def payment_status(request):
    logindetails = request.session.get('user_data', {})
    addcart = request.session.get('addtocart', [])
    cart_no = len(addcart)
    
    if request.method == "POST":
        response = request.POST
        razorpay_data = {
            'razorpay_order_id': response.get('razorpay_order_id'),
            'razorpay_payment_id': response.get('razorpay_payment_id'),
            'razorpay_signature': response.get('razorpay_signature')
        } 
        fname = request.POST.get('firstname')
        email = request.POST.get('email')
        billing_address = request.POST.get('address')
        contact_number = request.POST.get('number')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')
        shipping_address = billing_address
        
    try:
            payment_data = PaymentdataModel.objects.get(Order_id=razorpay_data['razorpay_order_id'])
            payment_data.Payment_Id = razorpay_data['razorpay_payment_id']
            payment_data.Signature = razorpay_data['razorpay_signature']
            payment_data.save(update_fields=['Payment_Id', 'Signature', 'Datetime'])
    except PaymentdataModel.DoesNotExist:
            print("Payment data not found for order ID:", razorpay_data['razorpay_order_id'])
            return render(request, 'payment_error.html')

    pro_list = []
    client = razorpay.Client(auth=("rzp_test_8jTLUV3aVex82Q", "n3PL7ZbSgnKSWJeA1s9ndhaO"))

    for item in addcart:
            try:
                pro_value = AddItem.objects.get(id=item)
                item_data = {
                    'id': pro_value.id,
                    'unit_amount': pro_value.Price,
                    'currency': 'INR',
                }
                pro_list.append(item_data)
            except AddItem.DoesNotExist:
                print("Product not found for id:", item)
                continue

    customer = {
            "name": fname,
            "contact": contact_number,
            "email": email,
            "billing_address": {
                "line1": billing_address,
                "zipcode": zip_code,
                "city": city,
                "state": state,
                "country": "india"
            },
            "shipping_address": {
                "line1": billing_address,
                "zipcode": zip_code,
                "city": city,
                "state": state,
                "country": "india"
            }
        }
    customers = client.customer.all()
    print(customers)
    if customers['count'] > 0:
        for key in customers['items']:
            print(key)
            print("==========================================================================",'\n')
            if key['email']==email:
                customer_data=key['id']
                break
    else:
            customers=client.customer.create(customer)
            customer_data=customers['id']
            print(customer_data)
    
    invoice = client.invoice.create({
        "type": "invoice",
        "customer_id": customer_data,
        "line_items": pro_list
        })
    print(invoice)
        

        
    Invoicemodel.objects.create(
                Invoice_id=invoice['id'],
                Order_id=razorpay_data['razorpay_order_id'],
                Payment_id=razorpay_data['razorpay_payment_id'],
                Amount=invoice['amount'],
                Amount_paid=invoice['amount_due'],
                Amount_due=invoice['amount_paid'],
                Currency=invoice['currency'],
                Billing_address=billing_address,
                Shipping_address=billing_address,
                Email_id=logindetails('Em'),
                Status="Paid"
    )
        

    if 'addtocart' in request.session:
            del request.session['addtocart']

    payment_data = PaymentdataModel.objects.get(Order_id=razorpay_data['razorpay_order_id'])
    invoice_data = Invoicemodel.objects.get(Order_id=razorpay_data['razorpay_order_id'])
    purchase_data = Purchaseproduct.objects.filter(Order_id=razorpay_data['razorpay_order_id'])

    context = {
            'logindetails': logindetails,
            'addcartno': cart_no,
            'media_url': settings.MEDIA_URL,
            'invoice': invoice,
            'payment_data': payment_data,
            "invoice_data": invoice_data,
            "purchase_data": purchase_data
    }

    return render(request, 'invoice.html', context)



    # except Exception as e:
    #     print(e)
    #     try:
    #         payment_data = PaymentdataModel.objects.get(Order_id=razorpay_data['razorpay_order_id'])
    #         payment_data.Status = "Fail"
    #         payment_data.save(update_fields=['Status'])
    #     except PaymentdataModel.DoesNotExist:
    #         pass
        
    #     context = {
    #         'logindetails': logindetails,
    #         'addcartno': cart_no,
    #         'media_url': settings.MEDIA_URL,
    #         "payment_fail": True,
    #     }
    #     return render(request, 'Cart.html', context)

# @csrf_exempt
# def payment_status(request):
#     if request.method == "POST":
#         response = request.POST

#         razorpay_data = {
#             'razorpay_order_id': response['razorpay_order_id'],
#             'razorpay_payment_id': response['razorpay_payment_id'],
#             'razorpay_signature': response['razorpay_signature']
#         }

#         # client instance
#         client = razorpay.Client(auth =("rzp_test_3LJ7CBlMbFfwT" , "4thIATbNrfvi0N6mdFDThupO"))

#         try:
#             status = client.utility.verify_payment_signature(razorpay_data)
#             product = AddItem.objects.get(order_id=response['razorpay_order_id'])
#             product.razorpay_payment_id = response ['razorpay_payment_id']
#             product.paid = True
#             product.save()-

#             addtocart = request.session.get('addtocart')
#             for i in addtocart:
#                 data = AddItem.objects.get(id=i)
#                 # context={
#                 #     'id':data.id,
#                 #     'Nm':data.Name,
#                 #     'Pr':data.Price,
#                 #     'Img':data.Image,
#                 # }
#             invoice_data = {
#                 "type": "invoice",
#                 "customer": {
#                     "name": "customer name", # give name in name value
#                     "contact":"9657758586",
#                     "email":"indrajeetyadu36@gmail.com",
#                     "billing_address" :"CybromTechnology MP Nagar Zone-1, Bhopal Madhya Pradesh", 
#                     "shipping_address":"kolar road bhopal",  #change this address
#                 },
#                 "line_items": [data.id,data.Name,data.Price,data.Image], #ieme product ki list pass kar dena
#             }
#             invoice = client.invoice.create(data=invoice_data)
            
#             return render(request, 'success.html', {'status': True})
#         except:
#             return render(request, 'success.html', {'status': False})


def Contact(request):
    # if request.method == "POST":
    logindetails=request.session['user_data']
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('msg')

    addtocart = request.session.get('addtocart')
    leng = 0
    if addtocart:
       leng=len(addtocart)
    
    #  For mail    
    subject='Test_mail for Query'
    message=message
    from_email=email
    recipient_list=['arpitkhare14@gmail.com','sumitumariya11@gmail.com']
    send_mail(subject, message, from_email, recipient_list)
    
    return render(request,'Contact.Html',{'leng':leng,'logindetails':logindetails})


def Registerdata(request):
    if request.method == "POST":
        name = request.POST.get('name') 
        email = request.POST.get('email') 
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        data = Registration.objects.filter(Email = email)

        if data:
            msg = "Already Exits"
            return render(request,'Register.html',{'msg':msg})
        else:
            if password == cpassword:
                Registration.objects.create(Name = name,
                                            Email = email,
                                            Password = password)
                msg= "Successfully Register"
                return render(request,'Login.html',{'msg':msg})
            else:
                msg = "Password Does not match"
                return render(request,'Register.html',{'msg':msg})

# logindetails = {}
adminDetails = {}

def LoginData(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    role = request.POST.get('role')

    if role == "admin":
        if email == 'admin@gmail.com' and password == '1234':
            request.session['email'] = email
            request.session['password'] = password

            global adminDetails
            adminDetails={
                'AE':request.session.get('email'),
                'AP':request.session.get('password')
            }
            print('arpit',adminDetails)
            return render(request,'Index.html',{'adminDetails':adminDetails})
        else: 
            msg = "Invalid Email or password"
            return render(request,"Login.html",{'msg':msg})
    else:     
        user = Registration.objects.filter(Email = email)

        if user:
            data = Registration.objects.get(Email = email)
            passs = data.Password

            if passs == password:
                request.session['user_data']={
                    'Nm':data.Name,
                    'Em':data.Email,
                    'Ps': data.Password
                }
                logindetails=request.session['user_data']
                print("----------->",logindetails)
                return render(request,'Index.html',{'logindetails':logindetails})
            else:
                msg = "Password does not match"
                return render(request,'Login.html',{'msg':msg})
        else:
            msg = "Enter valid Email"
            return render(request,'Login.html',{'msg':msg})
    
    
def Login(request):
    addtocart = request.session.get('addtocart')
    leng = 0
    if addtocart:
       leng=len(addtocart)
    return render(request,'Login.html',{'leng':leng})

def Register(request):
    return render(request,'Register.html')

def Logout(request):
    del request.session['user_data']
    return render(request,'Login.html')



import os

def invoice_load(request, pk):
    payment_data = get_object_or_404(PaymentdataModel, Order_id=pk)
    print(payment_data)
    invoice_data = get_object_or_404(Invoicemodel, Order_id=pk)

    print(invoice_data)
    purchase_data = Purchaseproduct.objects.filter(Order_id=pk)
    print(purchase_data.values())

    logindetails=request.session['user_data']
    context = {
        'logindetails':logindetails,
        'media_url': settings.MEDIA_URL,
        'payment_data': payment_data,
        "invoice_data": invoice_data,
        "purchase_data": purchase_data,
    }

    html_file_path1 = os.path.join(settings.BASE_DIR,'app', 'templates', 'paymentdone.html')
    html_file_path2 = os.path.join(settings.BASE_DIR,'app', 'templates', 'invoice.html')
    lis=[]
    with open(html_file_path2, 'r', encoding='utf-8') as f:
        invoice_html_content=f.read()

    with open(html_file_path1, 'w', encoding='utf-8') as g:
        g.write(invoice_html_content)

    html_string = render_to_string('paymentdone.html', context)
    with open(html_file_path1, 'w', encoding='utf-8') as h:
        h.write(html_string)
    


    path_to_wkhtmltopdf = r'D:\\Django\\PROJECT\\invoice_pdf\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'  # Update this to your path

    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    try:
        pdf_file_path = os.path.join(settings.BASE_DIR,'invoice_pdf',f'{invoice_data.Invoice_id}.pdf')
        pdfkit.from_file(html_file_path1, pdf_file_path, configuration=config, options={'enable-local-file-access': ""})

        # print(output)
        invoice_data1 = get_object_or_404(Invoicemodel, Order_id=pk)
        invoice_data1.Invoice_pdf= pdf_file_path
        invoice_data1.save(update_fields=['Invoice_pdf'])
    except OSError as e:
        print(f"Error generating PDF: {e}")
        return render(request, 'error_page.html', {'message': 'Error generating PDF'})

    return FileResponse(open(pdf_file_path, 'rb'), as_attachment=True, filename='invoice.pdf')


def myorder(request):
    User_id=request.session.get('User_id')
    user_info=get_object_or_404(Registration, id=User_id)
    addcart = request.session.get('addtocart')
    try:
        cart_no=len(addcart)
    except:
        cart_no=0
    invoice_data = Invoicemodel.objects.filter(Email_id= user_info.Email)
    print(type(invoice_data))
    if len(invoice_data)==0:
        Order_list = PaymentdataModel.objects.filter(Email=user_info.Email)
        invoice_data=[]
        for i in Order_list:
            try:
                data = Invoicemodel.objects.get(Order_id=i.Order_id)
                # print(data)
                invoice_data.append(data)
                # print(invoice_data)
            except:
                continue
        # print('---------------------------------------->3')
    logindetails=request.session['user_data']
    Context={
        'logindetails':logindetails,
        'addcartno': cart_no,
        'media_url': settings.MEDIA_URL,
        'invoice_data':invoice_data
    }
    print('==================== ==============  ============')
    return render(request, 'myorder.html', Context )

