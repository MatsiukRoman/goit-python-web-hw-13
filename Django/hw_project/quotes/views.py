from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .forms import QuoteForm, TagForm, AuthorForm
from .models import Tag, Quote, Author
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('hw_project') 

def main(request, page=1):
    quotes = Quote.objects.all()
    per_page = 10 
    paginator = Paginator(list(quotes), per_page)
    quotes_on_page = paginator.page(page)
    return render(request, 'quotes/index.html', context={'quotes': quotes_on_page})

@login_required
def add_quote(request):
    tags = Tag.objects.all()

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            new_quote = form.save(commit=False)
            new_quote.save()

            choice_tags = Tag.objects.filter(name__in=request.POST.getlist('tags'))
            for tag in choice_tags.iterator():
                new_quote.tags.add(tag)


            return redirect(to='quotes:root')
        else:
            return render(request, 'quotes/add_quote.html', {"tags": tags, 'form': form})

    return render(request, 'quotes/add_quote.html', {"tags": tags, 'form': QuoteForm()})

@login_required
def tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)

        if form.is_valid():
            tag = form.save(commit=False)
            tag.save()
            return redirect(to='quotes:root')
        else:
            return render(request, 'quotes/tag.html', {'form': form})

    return render(request, 'quotes/tag.html', {'form': TagForm()})

@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            new_author = form.save(commit=False)
            new_author.save()

            return redirect(to='quotes:root')
        else:
            return render(request, 'quotes/add_author.html')

    return render(request, 'quotes/add_author.html', {'form': AuthorForm()})

def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    return render(request, 'quotes/author_detail.html', {'author': author})

