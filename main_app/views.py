from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Bird
from .models import Feeding
from .forms import FeedingForm
from .models import Toy


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def birds_index(request):
    birds = Bird.objects.all()
    return render(request, 'birds/index.html', {'birds': birds})


def birds_detail(request, bird_id):
    bird = Bird.objects.get(id=bird_id)
    feeding_form = FeedingForm()
    return render(request, 'birds/detail.html', {
        'bird': bird,
        'feeding_form': feeding_form
    })


def add_feeding(request, bird_id):
    form = FeedingForm(request.POST)

    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.bird_id = bird_id
        new_feeding.save()
    return redirect('detail', bird_id=bird_id)


class BirdCreate (CreateView):
    model = Bird
    fields = '__all__'


class BirdUpdate(UpdateView):
    model = Bird
    # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']


class BirdDelete(DeleteView):
    model = Bird
    success_url = '/birds/'


def toys_index(request):
    toys = Toy.objects.all()
    return render(request, 'toys/index.html', {'toys': toys})


def toys_detail(request, toy_id):
    toy = Toy.objects.get(id=toy_id)
    return render(request, 'toys/detail.html', {'toy': toy})


class ToyCreate(CreateView):
    model = Toy
    fields = '__all__'


class ToyUpdate(UpdateView):
    model = Toy
    fields = ['color', 'description']


class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys/'
