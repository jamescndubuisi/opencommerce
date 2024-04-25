from .forms import LoginForm, CreateUser
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart
# Create your views here.


@login_required
def homepage(request):
    title = "Home"
    message = """Hero can be anyone. Even a man knowing something as simple and reassuring as putting a coat around a young boy shoulders to let him know the world hadn’t ended.

                You fight like a younger man, there’s nothing held back. It’s admirable, but mistaken. When their enemies were at the gates the Romans would suspend democracy and appoint one man to protect the city.

            It wasn’t considered an honor, it was a public service."""
    name = request.session.get('first_name', "Anonymous")
    Cart.objects.new_or_get(request)
    print(name)
    context = {"title": title, "message": message}
    return render(request, "index.html", context)


def login_page(request):
    title = "Login"
    message = ""
    purpose = "Login"
    form = LoginForm
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request,email=email, password=password)

            if user is not None:
                login(request, user=user)
                return redirect("home")
            else:
                messages.error(request, 'username or password not correct')
                return redirect('log_in')
        else:
            print("Terrible form")
            return render(
                request, "registration/login.html", {"form": form, "message": message}
            )
    return render(
        request,
        "registration/login.html",
        {"form": form, "message": message, "title": title, "purpose": purpose},
    )


def sign_up(request):
    title = "Register"
    context = {"title": title}
    form = CreateUser(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'index.html')
    context['form'] = form
    return render(request, 'registration/register.html', context)
