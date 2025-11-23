from django.db import models
from django.utils import timezone


class Company(models.Model):
    company_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    def __str__(self):
        return self.company_name
    

    
class CostCategory(models.Model):
    category_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.category_name


class SourceCategory(models.Model):
    category_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.category_name

class PaymentMode(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name



class DivisionMaster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DistrictMaster(models.Model):
    division = models.ForeignKey(DivisionMaster, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CountryMaster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SupplierTypeMaster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BankCategoryMaster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BankMaster(models.Model):
    name = models.CharField(max_length=100)
    bank_category = models.ForeignKey(BankCategoryMaster, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    


class AccountCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class BankAccount(models.Model):
    accountCategory = models.CharField(max_length=100)
    accountName = models.CharField(max_length=255)
    bankName = models.CharField(max_length=255)
    accountNo = models.CharField(max_length=50)
    bankAddress = models.TextField()
    bankContact = models.CharField(max_length=20)
    bankMail = models.EmailField()
    previousBalance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.bankName} - {self.accountName}"
