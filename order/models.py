from django.db import models

class PrintOrder(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=15)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ProcessedFile(models.Model):
    order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE, related_name='files')
    renamed_filename = models.CharField(max_length=255)
    page_count = models.IntegerField()
    quantity = models.IntegerField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    file_path = models.FileField(upload_to='processed/')
