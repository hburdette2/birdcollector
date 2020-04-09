from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Bird, Feeding, Toy, Photo
from .forms import FeedingForm

import uuid
import boto3
s3 = boto3.session.Session(profile_name='birdcollector-heb').client('s3')

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'birdcollector-heb'


def signup(request):
    error_message = ''

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


@login_required
def birds_index(request):
    birds = Bird.objects.filter(user=request.user)
    return render(request, 'birds/index.html', {'birds': birds})
    user = request.user


@login_required
def birds_detail(request, bird_id):
    bird = Bird.objects.get(id=bird_id)
    feeding_form = FeedingForm()

    toys_bird_doesnt_have = Toy.objects.exclude(
        id__in=bird.toys.all().values_list('id'))

    return render(request, 'birds/detail.html', {
        'bird': bird,
        'feeding_form': feeding_form,
        'toys': toys_bird_doesnt_have
    })


@login_required
def assoc_toy(request, bird_id, toy_id):
    # Note that you can pass a toy's id instead of the whole object
    Bird.objects.get(id=bird_id).toys.add(toy_id)
    return redirect('detail', bird_id=bird_id)


def remove_toy(request, bird_id, toy_id):
    Bird.objects.get(id=bird_id).toys.remove(toy_id)
    return redirect('detail', bird_id=bird_id)


@login_required
def add_feeding(request, bird_id):
    form = FeedingForm(request.POST)

    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.bird_id = bird_id
        new_feeding.save()
    return redirect('detail', bird_id=bird_id)


class BirdCreate (LoginRequiredMixin, CreateView):
    model = Bird
    fields = ['name', 'breed', 'age', 'description']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BirdUpdate(LoginRequiredMixin, UpdateView):
    model = Bird
    # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']


class BirdDelete(LoginRequiredMixin, DeleteView):
    model = Bird
    success_url = '/birds/'


@login_required
def toys_index(request):
    toys = Toy.objects.all()
    return render(request, 'toys/index.html', {'toys': toys})


@login_required
def toys_detail(request, toy_id):
    toy = Toy.objects.get(id=toy_id)
    return render(request, 'toys/detail.html', {'toy': toy})


class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'


class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['color', 'description']


class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'


@login_required
def add_photo(request, bird_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        key = uuid.uuid4().hex[:6] + \
            photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to bird_id or bird (if you have a dog object)
            photo = Photo(url=url, bird_id=bird_id)
            photo.save()
        except Exception as e:
            print(str(e))
            print('An error occurred uploading file to S3')
    return redirect('detail', bird_id=bird_id)
