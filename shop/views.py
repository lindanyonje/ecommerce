from django.db.models.fields import Field
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from .models import Category, Delivery, Seller, Product, Offer, Voucher, Order, Payment,Customer,Review, Wishlist, Feedback,Cart,Checkout
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse
from django.http import JsonResponse
from django .contrib.auth.decorators import login_required
from .forms import FeedbackForm
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail


#html email required stuff

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.

def home(request):

    context = {}

    category = Category.objects.get(name="Electronics")




    context['products'] = Product.objects.all()[:3]
    context['categories'] = Category.objects.all()
    context['wishlist'] = Wishlist.objects.all()
    context['cart'] = Cart.objects.all()
    # context['classified_products'] = Product.objects.filter(category_id=category)[:1]
    

    return render(request, 'shop/frontend/home.html', context)



def adminDashboard(request):

    ##Declaring a dictionary used to package the data we shall
    ##send to the frontend html template for display.

    context = {}

    context['product_count'] =  Product.objects.all().count()
    context['order_count'] =  Order.objects.all().count()
    context['payment_count'] =  Payment.objects.all().count()
    context['payments'] =  Payment.objects.all()[:10]
    context['pending_orders'] =  Order.objects.filter(status ="Pending")



    return render(request, 'shop/admin/dashboard.html', context)

def getCategoryProducts(request, id):

    c_id = id
    context = {}
    context['products'] = Product.objects.filter(category_id = c_id)

    return render(request, 'shop/frontend/category_products.html', context)

def getProduct(request, id):

    product = Product.objects.get(pk = id)
    commentForm = FeedbackForm()
    

    context = {
        'product' : product,
        'related_products' : Product.objects.filter(category_id = product.id),
        # 'reviews' : Review.objects.filter(product_id = product.id),
        'form' : commentForm,
        'rating': range(product.rating)
    }

    return render(request, 'shop/frontend/detail_product.html', context)

def get_cart(request):
    cart_items = Cart.objects.filter(order_id__isnull = True)
    
    return render(request, 'shop/frontend/cart.html', {'cart': cart_items})    


def get_wishlist(request):
    wishlist = Wishlist.objects.all()

    return render(request, 'shop/frontend/wishlist.html', {'wishlist': wishlist})



def checkoutDetails(request, total):

    context = {
            'total' : total,
        }
    return render(request, 'shop/frontend/checkout.html', context)


def finalizeCheckout(request):
    if request.method == "GET":

        return render(request, 'shop/frontend/cart.html', context={})

    else:
        name=request.POST.get('name')
        email=request.POST.get('email')
        total=request.POST.get('total')
        order_number= "BURA_123_56"
        address=request.POST.get('address')
        delivery_method = request.POST.get("delivery_method")
        payment_mode = request.POST.get("paymentMode")
        
        customer = Customer.objects.filter(email= email).first()
        if customer is None:
            customer = Customer.objects.create(
                name = name,
                email = email,
                password = email,
            )
        order = Order.objects.create(
            total = total,
            order_number = order_number,
            status = "Pending",
            customer_id = customer

        )

        cart_items = Cart.objects.filter(order_id__isnull = True).update(order_id = order.id)

        context = {
            'order' : order.id,
        }

        return JsonResponse(context)

# def orderSummary(request, id):

#     order = Order.objects.get(id = id)
#     # cart = Cart.objects.filter(order_id = order)

#     try:
        
#         send_mail(

#             'Bura Order Success',
#             'Your order has been made successfully.' 
            # 'You can use the order number '+ order.order_number+" to track it's progress"
#             'Thank you for choosing Bura',
#             'admin@gmail.com',
#             [order.customer_id.email],
#             fail_silently= False,
            

#         )

    #   datatuple = (
    #     ('Subject', 'Message.', 'from@example.com', ['john@example.com']),
    #     ('Subject', 'Message.', 'from@example.com', ['jane@example.com']),
    #   )
      
    #   send_mass_mail(datatuple)


    # except:
    #     print("Email sending failed.")

    # return render(request, 'shop/frontend/receipt.html',  { 'order' : order})


def sendanemail(request):
    
    # order = Order.objects.get(id = note_id)

    if request.method == "POST":
        to= request.POST.get=('toemail')
        content= request.POST.get=('content')

        html_content = render_to_string("shop/frontend/email_template.html", {'title':'test email', 'content':content})
        
        text_content= strip_tags(html_content)

        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])

        email= EmailMultiAlternatives(
            #subject
            'Bura Order Success',
            
            #context
            text_content,
        
            #from email
            settings.EMAIL_HOST_USER,

            #recepients list
             ['lindaatieno@gmail.com']
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        return render(
            request,
            'shop/frontend/email.html',
            {
                'title': 'send an email'
            }
        )
    else:
        return render(
            request,
            'shop/frontend/email.html',
            {
                'title': 'send an email'
            }

        )    



def get_Order(request, order_id):

    order = Order.objects.get(id =order_id)
    # order = get_object_or_404(Order, pk=Order.id)
    shipping_cost=request.POST.get('shipping_cost'),
    total=request.POST.get('total'),
    order_number= "BURA_123_56",
    

    return render(request, 'shop/frontend/receipt.html',  { 'order' : order.id})


def createFeedback(request):    
    form=FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form. is_valid():
            form.save()

    context= {'form':form}
    return render(request, 'shop/frontend/feedback_form.html',   context)

def ordercomplete(request, id):
    
    order = Order.objects.get(id = id)
    cart = Cart.objects.filter(order_id = order)
   
    



class SearchResult(ListView):
    model = Product
    template_name = 'shop/frontend/layouts/search_results.html'

    def get_queryset(self):
        query =self.request.GET.get('search_data')
        object_list = Product.objects.filter(Q(name__icontains=query))
        # object_list = Product.objects.filter(
        #     Q(name__icontains=query | Q(state__icontains=query))
            
        # )
        return object_list



class FeedbackFormView(FormView):
    login_required= True
    model = Feedback
    template_name= "shop/admin/feedback.html"


class CategoryList(ListView):
    
    login_required= True
    model = Category
    template_name= "shop/admin/category_list.html"

class CategoryDetail(DetailView):

    model = Category

class CategoryCreate(CreateView):  

    login_required= True
    model = Category
    template_name= "shop/admin/category_form.html"

    #specify the fields to be displayed

    fields = '__all__'

    #function to redirect user

    def get_success_url(self):
        return reverse('Category_List') #uses the path name

class CategoryUpdate(UpdateView):

    login_required= True
    model = Category
    fields = '__all__'
    template_name= "shop/admin/category_form.html"
    success_url = '/categories' #this uses the path url

class CategoryDelete(DeleteView):

    login_required= True
    model = Category
    success_url = '/categories'

    

class ProductList(ListView):

    login_required= True
    model =Product
    template_name= "shop/admin/product_list.html"

class ProductDetail(DetailView):

    login_required= True
    model = Product
    template_name= "shop/admin/product_detail.html"


class ProductCreate(CreateView): 

    login_required= True 
    model = Product
    template_name= "shop/admin/product_form.html"
    success_url = '/categories'

    #specify the fields to be displayed

    fields = '__all__'

    #function to ridirect user

    def get_success_url(self):
        return reverse('Product')

class ProductUpdate(UpdateView):

    login_required= True
    model = Product
    fields = '__all__'
    success_url = '/products'
    template_name= "shop/admin/product_form.html"


class ProductDelete(DeleteView):

    login_required= True
    model = Product
    success_url = '/products'
    template_name= "shop/admin/product_confirm_delete.html"



class  SellerList(ListView):

    login_required= True
    model =  Seller
    template_name= "shop/admin/seller_list.html"

class  SellerDetail(DetailView):

    login_required= True
    model =  Seller
    template_name= "shop/admin/seller_details.html"

class  SellerCreate(CreateView): 

    login_required= True 
    model =  Seller
    template_name= "shop/admin/seller_form.html"
    success_url = '/sellers'

    #specify the fields to be displayed

    fields ='__all__'

    #function to ridirect user

    def get_success_url(self):
        return reverse('seller_list')

class SellerUpdate(UpdateView):

    login_required= True
    model = Seller
    fields = '__all__' 
    template_name= "shop/admin/seller_form.html"
    success_url = '/sellers'

class  SellerDelete(DeleteView):

    login_required= True
    model =  Seller
    template_name= "shop/admin/seller_confirm_delete.html"
    success_url = '/sellers'

    

class OfferList(ListView):

    login_required= True
    model = Offer
    template_name= "shop/admin/offer_list.html"

class OfferDetail(DetailView):

    login_required= True
    model = Offer
    template_name= "shop/admin/offer_details.html"

class OfferCreate(CreateView):  

    login_required= True
    model = Offer
    template_name= "shop/admin/offer_form.html"

    #specify the fields to be displayed

    fields = '__all__'

    #function to ridirect user

    def get_success_url(self):
        return reverse('offer_list')

class OfferUpdate(UpdateView):

    login_required= True
    model = Offer
    fields = '__all__'
    template_name= "shop/admin/offer_form.html"
    success_url = '/offers'

class OfferDelete(DeleteView):

    login_required= True
    model = Offer
    template_name="shop/admin/offer_confirm_delete.html"
    success_url = '/offers'  



class VoucherList(ListView):

    login_required= True
    model = Voucher
    template_name= "shop/admin/voucher_list.html"

class VoucherDetail(DetailView):

    login_required= True
    model = Voucher

class VoucherCreate(CreateView):

    login_required= True  
    model = Voucher
    template_name= "shop/admin/voucher_form.html"
    success_url = 'vouchers/'

    #specify the fields to be displayed

    fields = '__all__'

    #function to ridirect user

    def get_success_url(self):
        return reverse('voucher_list')

class VoucherUpdate(UpdateView):

    
    login_required= True
    model = Voucher
    fields = '__all__' 
    template_name= "shop/admin/voucher_form.html"
    success_url = 'vouchers/'

class VoucherDelete(DeleteView):

    login_required= True
    model = Voucher
    success_url = '/vouchers'  




class OrderList(ListView):

    login_required= True
    model =Order
    template_name= "shop/admin/order_list.html"

class OrderDetail(DetailView):

    login_required= True
    model = Order
    template_name= "shop/admin/order_form.html"

class OrderCreate(CreateView): 

    login_required= True 
    model = Order
    template_name= "shop/admin/order_form.html"
    success_url = '/orders'


    #specify the fields to be displayed

    fields = '__all__'

    #function to ridirect user

    def get_success_url(self):
        return reverse('order_list')

class OrderUpdate(UpdateView):

    login_required= True
    model = Order
    fields = '__all__'
    template_name= "shop/admin/order_form.html"
    success_url = '/orders'

class OrderDelete(DeleteView):

    login_required= True
    model = Order
    template_name= "shop/admin/order_confirm_delete.html"
    success_url = '/orders'  



class PaymentList(ListView):

    login_required= True
    model =Payment
    template_name= "shop/admin/payment_list.html"

class PaymentDetail(DetailView):

    login_required= True
    model = Payment

class PaymentCreate(CreateView):

    login_required= True  
    model = Payment
    template_name= "shop/admin/payment_form.html"
    success_url = '/payments'


    #specify the fields to be displayed

    fields = ['order_id', 'amount', 'description', 'invoice_number']

    #function to ridirect user

    def get_success_url(self):
        return reverse('payment_list')

class PaymentUpdate(UpdateView):

    login_required= True
    model = Payment
    fields = '__all__'
    template_name= "shop/admin/payment_form.html"
    success_url = '/payments'

class PaymentDelete(DeleteView):

    login_required= True
    model =Payment
    template_name= "shop/admin/payment_confirm_delete.html"
    success_url = '/payments'  



class CustomerList(ListView):

    login_required= True
    model = Customer
    template_name= "shop/admin/customer_list.html"

class CustomerDetail(DetailView):

    login_required= True
    model =  Customer
    template_name= "shop/admin/customer_details.html"


class  CustomerCreate(CreateView):  

    login_required= True
    model =  Customer
    fields='__all__'
    template_name= "shop/admin/customer_form.html"

    #specify the fields to be displayed

    #function to ridirect user

    def get_success_url(self):
        return reverse('customer_list')

class CustomerUpdate(UpdateView):

    login_required= True
    model =  Customer
    fields = '__all__'
    template_name= "shop/admin/customer_form.html"
    success_url = '/customers'

class CustomerDelete(DeleteView):

    login_required= True
    model =Customer
    template_name= "shop/admin/customer_confirm_delete.html"
    success_url = '/customers'


class Review(FormView):
        model = Review
        fields = ['rating',]
        template_name= "'shop/frontend/review.html'"
        success_url = '/rating'


# class ReviewList(ListView):

#     login_required= True
#     model =Review
#     template_name= "shop/admin/review_list.html"

# class ReviewDetail(DetailView):

#     login_required= True
#     model = Review
#     template_name= "shop/admin/review_form.html"

# class ReviewCreate(CreateView): 

#     login_required= True 
#     model = Review
#     template_name= "shop/admin/review_form.html"
#     success_url = '/reviews'


#     #specify the fields to be displayed

#     fields = '__all__'

#     #function to ridirect user

#     def get_success_url(self):
#         return reverse('review_list')

# class ReviewUpdate(UpdateView):

#     login_required= True
#     model = Review
#     fields = '__all__'
#     template_name= "shop/admin/review_form.html"
#     success_url = '/reviews'

# class ReviewDelete(DeleteView):

#     login_required= True
#     model = Review
#     template_name= "shop/admin/review_confirm_delete.html"
#     success_url = '/reviews'  


class CartList(ListView):

    login_required= True
    model = Cart
    template_name= "shop/admin/cart_list.html"

class CartDetail(DetailView):

    login_required= True
    model =  Cart
    template_name= "shop/admin/cart_details.html"


class  CartCreate(CreateView):  

    login_required= True
    model =  Cart
    fields='__all__'
    template_name= "shop/admin/cart_form.html"

    #specify the fields to be displayed

    #function to ridirect user

    def get_success_url(self):
        return reverse('cart_list')

class CartUpdate(UpdateView):

    login_required= True
    model =  Cart
    fields = '__all__'
    template_name= "shop/admin/cart_form.html"
    success_url = '/cart'

class CartDelete(DeleteView):

    login_required= True
    model =Cart
    template_name= "shop/admin/cart_confirm_delete.html"
    success_url = '/cart'



class WishlistList(ListView):

    login_required= True
    model = Wishlist
    template_name= "shop/admin/wishlist_list.html"

class WishlistDetail(DetailView):

    login_required= True
    model = Wishlist

class WishlistCreate(CreateView):

    login_required= True  
    model = Wishlist
    template_name= "shop/admin/wishlist_form.html"
    success_url = 'wishlists/'

    #specify the fields to be displayed

    fields = '__all__'

    #function to ridirect user

    def get_success_url(self):
        return reverse('wishlist_list')

class WishlistUpdate(UpdateView):

    
    login_required= Truemodel = Wishlist
    fields = '__all__' 
    template_name= "shop/admin/wishlist_form.html"
    success_url = 'wishlists/'

class WishlistDelete(DeleteView):

    login_required= True
    model = Voucher
    success_url = '/wishlists'  



@login_required

def deleteCategory(request):
    Category_id= request.POST.get('id',None)
    category=Category.objects.get(id= Category_id)
    category.delete()
    data= {
        'deleted':True
    }
    return JsonResponse(data)


def deleteSeller(request):
    Seller_id= request.POST.get('id',None)
    seller=Seller.objects.get(id= Seller_id)
    seller.delete()
    data= {
        'deleted':True
    }

    return  JsonResponse(data)

def deleteProduct(request):

    Product_id= request.POST.get('id',None)
    product=Product.objects.get(id=Product_id)
    product.delete()
    data= {
        'deleted':True
    }

    return JsonResponse(data)

def deleteReview(request):

    customer_id= request.POST.get('id',None)

    product_id= request.POST.get('id',None)

    Review= Review.objects.get(id=Review_id)

    Review.delete()
    
    data= {
        'deleted':True
    }

    return JsonResponse(data)    



def deleteCart(request):

    cart_id = request.POST.get('cart_id')
    cart_item= Cart.objects.get(pk = cart_id)
    cart_item.delete()
    

    data ={}

    return JsonResponse(data)






def addToCart(request):

    product_id = request.POST.get("product_id", None)

    quantity = request.POST.get("quantity", None)

    product = Product.objects.get(id = product_id)

    # Cart.objects.create(product_id = product, quantity = quantity)

    cart_product = Cart.objects.filter(product_id = product.id)
    print(cart_product)
    if not cart_product:
   
        Cart.objects.create(product_id = product, quantity= quantity)
        data ={
            'message' : "Product added to cart"
        }
    else:
        data = {
            'message' : "Product is already in cart"
        }

    return JsonResponse(data)


    





def deleteWishlist(request):

    product_id = request.POST.get("product_id", None)
   
    print(product_id)
    
    wishlist_object = Wishlist.objects.get(id = product_id)
    print(wishlist_object)
    wishlist_object.delete()

    data ={}

    return JsonResponse(data)



def addToWishlist(request):

    product_id = request.POST.get("product_id", None)
   
    product = Product.objects.get(pk =product_id) 

    wishlist_product = Wishlist.objects.filter(product_id = product.id)
    print(wishlist_product)
    if not wishlist_product:
   
        Wishlist.objects.create(product_id = product)
        data ={
            'message' : "Product added to wishlist"
        }
    else:
        data = {
            'message' : "Product is already in wishlist"
        }

    return JsonResponse(data)



def wishlistToCart(request):

    id = request.POST.get("id", None)
    
    quantity = 1

    wishlist_item = Wishlist.objects.get(pk = id)

    product =  wishlist_item.product_id

    Cart.objects.create(product_id = product, quantity = quantity)

    wishlist_item.delete()

    data ={}

    return JsonResponse(data)


def cartToWishlist(request):

    id = request.POST.get("id", None)

    # quantity = 1

    cart_item = Cart.objects.get(pk = id)

    product =  cart_item.product_id

    Wishlist.objects.create(product_id = product)

    # Cart.objects.create(product_id = product, quantity = quantity)

    cart_item.delete()

    data ={}

    return JsonResponse(data)



def review(request, id): # view for displaying and storing the form
    product = get_object_or_404(Product, id=Product.id)

    review= Review.objects.all()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit = False)
            review.product = Product
            review.save()
            Product.has_review = True
            Product.save()
            if Product.review==0:
                Product.rating = review.rating
            else:
                Product.rating = (Product.rating*Product.review + review.rating)/(Product.review + 1)
            Product.review += 1
            Product.save()
            review.success(request, 'your review has been sent correctly !')
            return redirect(Product)
    else:
        form = ReviewForm()

    return render(request, 'shop/frontend/review.html', {'review': review})

def review(request, id): # view for recording the rating
    review = get_object_or_404(Review, id=id)
    rating = request.POST.get('rating')
    review.rating= rating
    review.save()
    review.success(request, 'your review has been sent correctly!')
    return redirect(Product)  
  

def markAsComplete(request):

    order_id = request.POST.get('order_id')
    print(order_id)

    order = Order.objects.get(pk = order_id)
    order.status = "Completed"
    order.save()

    data = {
        'success' : True
        }

    return JsonResponse(data)