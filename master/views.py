from rest_framework import viewsets
from .models import*
from .serializers import*



class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    
class CostCategoryViewSet(viewsets.ModelViewSet):
    queryset = CostCategory.objects.all()
    serializer_class = CostCategorySerializer

    
class SourceCategoryViewSet(viewsets.ModelViewSet):
    queryset = SourceCategory.objects.all()
    serializer_class = SourceCategorySerializer

    
class PaymentModeViewSet(viewsets.ModelViewSet):
    queryset = PaymentMode.objects.all()
    serializer_class = PaymentModeSerializer



class DivisionMasterViewSet(viewsets.ModelViewSet):
    queryset = DivisionMaster.objects.all()
    serializer_class = DivisionMasterSerializer


class DistrictMasterViewSet(viewsets.ModelViewSet):
    queryset = DistrictMaster.objects.all()
    serializer_class = DistrictMasterSerializer


class CountryMasterViewSet(viewsets.ModelViewSet):
    queryset = CountryMaster.objects.all()
    serializer_class = CountryMasterSerializer


class SupplierTypeMasterViewSet(viewsets.ModelViewSet):
    queryset = SupplierTypeMaster.objects.all()
    serializer_class = SupplierTypeMasterSerializer



class BankCategoryMasterViewSet(viewsets.ModelViewSet):
    queryset = BankCategoryMaster.objects.all()
    serializer_class = BankCategoryMasterSerializer
    

class BankMasterViewSet(viewsets.ModelViewSet):
    queryset = BankMaster.objects.all()
    serializer_class = BankMasterSerializer



class AccountCategoryViewSet(viewsets.ModelViewSet):
    queryset = AccountCategory.objects.all()
    serializer_class = AccountCategorySerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer