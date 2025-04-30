import requests
from home.models import Register
from django.shortcuts import redirect, render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,  login, logout 
from datetime import datetime,timedelta
from home.models import Getdatetime, Bookings , Payment
from home.forms import UpdateForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings

import uuid
# Create your views here.

def index(request):

   return render(request,'index.html') 


def news(request):
    return render(request,'news.html')
    # return  HttpResponse("this is aboutpage.")



def events(request):
    return render(request,'events.html')
    # return HttpResponse("this is event page.")







#for booking page. messages, date and time validation, 

def bookings(request):
   empty = ''
   if request.method == "POST":
      date = request.POST['for_date']
      time = request.POST.get('for_time')


      if date == empty:
          messages.warning(request,"Please!choose date.") 
          return redirect('bookings')
         
      elif Getdatetime.objects.filter(date = date).exists():
        messages.warning(request,'date already taken')
        return redirect('bookings')
      
      elif time == empty:
          messages.warning(request,"Please!choose time.") 
          return redirect('bookings')

      elif Getdatetime.objects.filter(time = time).exists():
           messages.warning(request,'Time Taken')
           return redirect('bookings')
      else:   
        da = Getdatetime( date = date, time = time)
        da.save()
   
   booked_date = Getdatetime.objects.all()
   return render(request,'bookings.html',{'data':booked_date})






# For booking
# @login_required(login_url='/bookings_list')

def bookings_list(request):

    empty = ''

    if request.user.is_authenticated:
     
     username = request.user
     userId = request.user.id

    # function creating id for booking
    # uuid generates unique random string of 7 letters and no.s 

     def bookingId():
         
         booking_id = int(userId)
         booking_id = uuid.uuid4().hex[:7].upper()

         if Bookings.objects.filter(unique_booking_id = booking_id).exists():
            booking_id = uuid.uuid4().hex[5].lower()
            return booking_id

         else:   
          return booking_id
      
     Bid = bookingId()
     

     if request.method == "POST":
     
      bookingdate = request.POST['for_date']
      bookingstart = request.POST['for_start_time']
      bookingfinish = request.POST.get('for_finish_time')
      currentdate = datetime.today()
      currentdate = str(currentdate)
      currentdate = currentdate.split(" ",1)[0]
      currenttime = datetime.now().strftime('%H:%M:%S')
    
      # converting time for standard booking time 7 AM - 8 PM

      strbookingstart = str(bookingstart)
      standardstart = "06:59"
    
    #   standardstart = standardstart.split(":",1)[0]

      strbookingfinish = str(bookingfinish)
      standardfinish = "20:01"
    #   standardfinish = standardfinish.split(":",1)[0]

      #2 day window. YOu can only book for today and tomorrow.
      validity_time = datetime.now() + timedelta(days=1)
      validity_time = str(validity_time).split(" ",1)[0]
      bookingdate_input = str(bookingdate)
      
      if bookingdate == empty:
          messages.warning(request,"Please select a date.") 
          return redirect('bookings')   


      elif str(currentdate) > str(bookingdate):
           messages.warning(request,"Please select a valid date")
           return redirect('bookings')  

      # standard booking window is 2days

      elif bookingdate > validity_time:
           messages.warning(request,"Standard booking window is 2 days. Please ! Choose within 2days time frame.")
           return redirect('bookings')


      elif bookingstart == empty:
           messages.warning(request,"Please select Start Time.") 
           return redirect('bookings')


      elif bookingfinish == empty:
            messages.warning(request,"Please select End Time.") 
            return redirect('bookings')


      elif bookingfinish == bookingstart:
                messages.warning(request,"Start and End time cant be same") 
                return redirect('bookings')
    

      elif bookingfinish < bookingstart:
                messages.warning(request,"End time cant be smaller than start time") 
                return redirect('bookings')


      elif strbookingstart < standardstart:
           messages.warning(request,"Our facility opens at 7 AM . Please! choose time within opening hours.")
           return redirect('bookings') 
      

      elif strbookingfinish > standardfinish:
           messages.warning(request,"Our facility closes at 8 PM . Please! choose time within opening hours")
           return redirect('bookings') 
      
      elif bookingdate == currentdate and bookingstart < currenttime:
           messages.warning(request,"Your start time is smaller than current time.")
           return redirect('bookings')


      elif Bookings.objects.filter(bookingtime_start = bookingstart).exists():
              messages.warning(request,'Time Taken')
              return redirect('bookings')


      elif Bookings.objects.filter(bookingtime_finish = bookingfinish).exists():
                messages.warning(request,'A match is happening')
                return redirect('bookings')


        #   if booking time lies in between pre booking time.
        # for ex: database time: 7:30 am - 8:38 am .
        #  user input time: 7:00 am - 8: 30 am

      elif Bookings.objects.filter(booking_date =bookingdate_input,bookingtime_start__lte=bookingstart,bookingtime_finish__gte=bookingstart).exists():
            messages.warning(request,"Please select another booking hour. The time you are choosing is already reserved.")
            return redirect('bookings') 


        # for ex: database time: 7:30 am - 8:38 am .
        #   user input time: 7:00 am - 8: 31 am
        #  if current booking start time is smaller than database booking start time and the current booking finish time is greater than database booking ending time.

      elif Bookings.objects.filter(booking_date = bookingdate_input,bookingtime_start__lte=bookingfinish,bookingtime_finish__gte=bookingfinish).exists():
            messages.warning(request,"Please select another booking hour. The time you are choosing is already reserved.")
            return redirect('bookings') 


        # for ex: database time: 7:30 am - 8:30 am .
        #   user input time: 7:20 am - 9: 00 am
        #  if current booking start time is smaller than database booking start time and the current booking finish time is greater than database booking ending time.
      
      elif Bookings.objects.filter(booking_date = bookingdate_input,bookingtime_start__gte=bookingstart,bookingtime_finish__lte=bookingfinish).exists():
            messages.warning(request,"Please select another booking hour. The time you are choosing is already reserved.")
            return redirect('bookings') 


      else:  

              #   to calculate the time difference between the two inputs
            
              s = datetime.strptime(bookingstart,"%H:%M")
              e = datetime.strptime(bookingfinish,"%H:%M")
            
             #   time difference calculation
            
              diff = e - s
            
              # converting time into minutes
            
              min = diff.total_seconds() /60
            
              #   converting the data into integer else throws error
            
              min = int(min)

              for_pricing = min / 60
              
              
              
              #   comparing for standard time         
            
              if min < 60:
                   messages.warning(request,"Minimum Time limit is 60 minutes.")
                   return redirect('bookings') 
                 
              else:
                   da = Bookings( user=username,user_id=userId,booking_date=bookingdate,
                   bookingtime_start = bookingstart,bookingtime_finish = bookingfinish,
                   booking_duration = min,unique_booking_id = Bid )
                   da.save()

                # for pricing

                   if for_pricing != 0:
                    total_price = for_pricing * 1500
                    
                    if for_pricing == 2:
                        total_price = for_pricing * 1400
                    
                    elif for_pricing  > 2 and for_pricing < 5:
                         total_price = for_pricing * 1350
                    
                    elif for_pricing > 6:
                        total_price = for_pricing * 1300
                    pricing = Payment(user = username,user_id = userId,price= total_price,booking_duration=min,product_id = Bid,)
                    pricing.save()

                    messages.info(request,"Booking successful.")
                    return redirect("payment")
 
     return render(request,"bookings.html")        
 
    else:
      messages.info(request,"Please login to continue bookings")
      return render(request,'bookings.html')
 




# display bookings
def showbookings(request):
    current_date = datetime.today()
    current_date = str(current_date).split(" ",1)[0]
    today = str(1)
    tomorrow = str(2)

    tomorrow_date = datetime.today() + timedelta(days = 1)
    tomorrow_date = str(tomorrow_date).split(" ",1)[0]
      
    if Bookings.objects.filter(booking_date = current_date).exists() and Bookings.objects.filter(booking_date = tomorrow_date).exists():
       cur_date = Bookings.objects.filter(booking_date = current_date)
       tom_date = Bookings.objects.filter(booking_date = tomorrow_date)
       return render(request,'bookings.html',{'tom_date':tom_date,'cur_date':cur_date,'today':today,'tomorrow':tomorrow})
    else:
      if Bookings.objects.filter(booking_date = current_date).exists():

        cur_date = Bookings.objects.filter(booking_date = current_date)
        return render(request,'bookings.html',{'cur_date':cur_date,'today':today})
      elif Bookings.objects.filter(booking_date = tomorrow_date).exists():
         tom_date = Bookings.objects.filter(booking_date = tomorrow_date)
         return render(request,'bookings.html',{'tom_date':tom_date,'tomorrow':tomorrow})
      else:
        messages.info(request,"No bookings yet.")
        return render(request,"bookings.html")







# for Payment
def payment(request):

    # booking_data = Bookings.objects.filter(user_id = userID)  
    # data = {'booking_data':booking_data}
    
    if request.user.is_authenticated:
        # gets user id of current user
        userID = request.user.id
        username = request.user.username

        # query for getting user id of current user 
        for_user_id = Payment.objects.filter(user_id = userID)    
        
        # passing multiple output by making dictionaries
        return render(request,'payment.html',
        {'userID':username,
        'user_id_data':for_user_id,
        
        
        })

    else:
        messages.success(request,'Please ! Login to continue')  
        return render(request,'payment.html')  
    #     if userID == user_id:

    #        return render(request,'payment.html',data)
    #     else:
    #         messages.warning(request,"Invalid User request!")
    #         return render(request,'index.html')
    # else:
    #  messages.warning(request,"Please login to continue bookings")
    #  return render(request,'payment.html')




# cancel/delete  booking
@login_required(login_url='login')
def cancelBookings(request,product_id):
    delete_booking = Payment.objects.filter( product_id = product_id)
    delete_booking.delete()
    messages.info(request,'Successfully deleted')
    return redirect('payment')


    

#for login page
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username = username, password = password)

        if user is not None:
            auth.login(request,user)
            messages.info(request,"You are logged in.")
            return redirect('home')

        else:
            messages.error(request, 'Invalid Email or Password .')
            return redirect('login')    

    else:
        return render(request,'login.html')
        
      





# register
def register(request):  
   if request.method == 'POST':
      username = request.POST['username'] 
      email = request.POST['email']
      password = request.POST['password']
      password2 = request.POST['password2']
      user = authenticate(request,username = username, email=email,password=password,password2=password2)
    #   try:
    #      password2 = request.POST['password2']
    #   except MultiValueDictKeyError:
    #       password2 = False

      if password == password2:
          if User.objects.filter(email = email).exists():
              messages.info(request,'Email Taken')
              return redirect('register')

          elif User.objects.filter(username=username).exists():
              messages.info(request,'Username already exists')
              return redirect(register)
          
          else:

              user = User.objects.create_user(username = username, email = email, password = password)
              messages.success(request,'Registered Successfully')
              user.save()    

              #   create profile for new user
              user_model = User.objects.get(username= username)
              new_profile = Register.objects.create(user=user_model, id_user= user_model.id)
              new_profile.save()
              return redirect('register')

      else:
          messages.error(request, 'Password Not Matching')
          return redirect('register')  
   else:
       return render(request,'register.html')






# logout
def logout(request):    
       auth.logout(request)
       messages.info(request,"You logged out.")
       return redirect('home')


# show profile
def profile(request):
    userId = request.user.id
     
    if Register.objects.filter(user_id  =  userId).exists():
         profile = Register.objects.filter(user_id = userId)
         return render(request,'profile.html',{'profile':profile})
    else:
         if User.objects.filter(is_superuser = True):
               return redirect('/admin/')
         else: 
            return redirect('login')     
            # return HttpResponse("Please Login to Continue")
      


# update profile
def updateProfile(request,id_user):
     booking = Register.objects.get(user_id = id_user)
     form = UpdateForm(request.POST or None, instance=booking)
     if form.is_valid():
        form.save()
        messages.info(request,'Profile Updated.')
        return HttpResponse("Profile updated sucessfully.")
    
     return render(request,'update_profile.html',{'form':form})



def Aboutus(request):
    return render(request,'About-us.html')


def helpcentre(request):
    return render(request,"helpcentre.html")

@login_required(login_url='login')
def khaltirequest(request,price,product_id):
    if request.user.is_authenticated:
        # gets user id of current user
        userID = request.user.id

        # query for getting user id of current user 
        for_user_id = Payment.objects.filter(user_id = userID) 
        product_id2 = Payment.objects.filter( user_id = userID and product_id == product_id and price == price)
        return render(request,"khaltirequest.html",{"user_id":for_user_id,"price":price,"product_id2":product_id2,"product_id":product_id})      
    
    
    
    return render(request,"khaltirequest.html")    

@login_required(login_url='login')
def khaltiVerify(request):
    token = request.GET.get("token")
    amount = request.GET.get("amount")
    print(token,amount)
    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
          "token":token,
          "amount": amount
                  }
    headers = {
     "Authorization": "key test_secret _key_ba960a825ee24d8f8e3bd7bb85dda40b"
      }

    response = requests.post(url, payload, headers = headers)
    print(response)
    data={
        "success":True
    }    
    
    


def vendor(request, vendor_id):
    vendor = get_object_or_404(vendor, id=vendor_id)
    return render(request, 'vendor.html', {'vendor': vendor})

def vendor(request, vendor_id):  # <== expects vendor_id
    vendor = get_object_or_404(vendor, id=vendor_id)
    return render(request, 'vendor.html', {'vendor': vendor})
    
    

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # (Optional) Send email or save to DB
        send_mail(
            subject,
            f"Message from {name} <{email}>:\n\n{message}",
            settings.DEFAULT_FROM_EMAIL,
            ['youremail@example.com'],  # Replace with your own email
            fail_silently=False,
        )

        return render(request, 'contact_us.html', {'success': True})

    return render(request, 'contact_us.html')
   
   
   
 
def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"Contact Us message from {name}"
        full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            settings.EMAIL_HOST_USER,  # From email
            [settings.EMAIL_HOST_USER],  # To email (your Gmail)
            fail_silently=False,
        )
        return render(request, 'contact_success.html')  # Or a success message

    return render(request, 'contact_us.html')

   
    return JsonResponse(data)

