from django.contrib import admin
from django.contrib.auth.models import Group
from .models import BankAccountType, User, UserAddress, UserBankAccount

admin.site.register(BankAccountType)
admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(UserBankAccount)
admin.site.unregister(Group)