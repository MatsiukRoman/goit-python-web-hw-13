from django.contrib import admin
from .models import Tag, Quote, Author

# Register your models here.
admin.site.register(Tag)
admin.site.register(Quote)
admin.site.register(Author)