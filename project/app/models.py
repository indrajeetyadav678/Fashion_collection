from django.db import models

class AddItem(models.Model):
    Image = models.ImageField(upload_to='images/')
    Name = models.CharField(max_length=50)
    Price = models.IntegerField()


class Registration(models.Model):
    Name = models.CharField(max_length=50)
    Email = models.EmailField()
    Password = models.CharField(max_length=20)

class PaymentdataModel(models.Model):
    Email=models.EmailField(null= True)
    Amount=models.IntegerField( null=True)
    Amount_paid=models.IntegerField( null=True)
    Amount_due=models.IntegerField(null=True)
    Currency=models.CharField(max_length=100, null=True)
    Receipt = models.FileField(upload_to='receipts/')
    Status=models.CharField(max_length=30, null=True)
    Attempts=models.IntegerField( null=True)
    Notes=models.TextField(null=True)
    Created_at=models.DateTimeField(auto_now=True, null=True)
    Payment_Id=models.CharField(max_length=255, null=True, blank=True)
    Order_id=models.CharField(max_length=255, null=True)
    Signature=models.CharField(max_length=255, null=True, blank=True)
    Datetime=models.DateTimeField(auto_now=True)
    Prod_Quantity=models.IntegerField( null=True)

    def __str__(self):
        return self.Order_id

# ========================== 7. PURCHASE PEODUCT DATA MODEL ==============================

class Purchaseproduct(models.Model):
    Product_Type=models.CharField(max_length=254, null=True)
    Prod_Image1=models.ImageField(null=True)
    Prod_Image2=models.ImageField(null=True)
    Prod_Image3=models.ImageField(null=True)
    Prod_Image4=models.ImageField(null=True)
    Prod_Price =models.IntegerField(null=True)
    Prod_MRP=models.IntegerField(null=True)
    Prod_Offer=models.CharField(max_length=254, null=True)
    Prod_Detail=models.TextField(null=True)
    prod_color=models.CharField(max_length=254, null=True)
    Serial_no=models.IntegerField(null=True)
    Purchase_date=models.DateTimeField(auto_now=True)
    Order_id=models.CharField(max_length=255, null=True)
    Email_id=models.EmailField(null= True)
    Prod_Quantity=models.IntegerField(null=True)

    
    def __str__(self):
        return self.Email


# ========================== 8. INVOICE DATA MODEL ==============================

class Invoicemodel(models.Model):
    Invoice_id=models.CharField(max_length=255, blank=True)
    invoice_number=models.CharField(max_length=255, blank=True)
    Customer_id=models.CharField(max_length=255, blank=True)
    Order_id=models.CharField(max_length=255, blank=True)
    Payment_id=models.CharField(max_length=255, blank=True)
    Payment_method=models.CharField(max_length=255, blank=True)
    Gross_amount=models.IntegerField(blank=True)
    Tax_amount=models.IntegerField(blank=True)
    Amount=models.IntegerField(blank=True)
    Amount_paid=models.IntegerField(blank=True)
    Amount_due=models.IntegerField(blank=True)
    Currency=models.CharField(max_length=255, blank=True)
    Billing_address=models.TextField( blank=True)
    Shipping_address=models.TextField( blank=True)
    Billingtime=models.DateTimeField(auto_now=True)
    Status=models.CharField(max_length=255, blank=True)
    Invoice_pdf=models.FileField(upload_to='../invoice_pdf/', null=True)
    Email_id=models.EmailField(null= True)

    def __str__(self):
        return self.Customer_id

