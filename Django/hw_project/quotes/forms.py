from django.forms import ModelForm, CharField, TextInput, ModelChoiceField
from .models import Tag, Quote, Author

class TagForm(ModelForm):

    name = CharField(min_length=3, max_length=25, required=True, widget=TextInput())
    
    class Meta:
        model = Tag
        fields = ['name']

class QuoteForm(ModelForm):

    author = ModelChoiceField(queryset=Author.objects.all(), required=True)
    quote = CharField(min_length=10, max_length=500, required=True, widget=TextInput())

    class Meta:
        model = Quote
        fields = ['author', 'quote']
        exclude = ['tags']

class AuthorForm(ModelForm):

    fullname = CharField(min_length=5, max_length=50, required=True, widget=TextInput())
    born_date = CharField(max_length=50, required=True, widget=TextInput())
    born_location = CharField(max_length=150, required=True, widget=TextInput())
    description = CharField(required=True, widget=TextInput())

    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location','description']

