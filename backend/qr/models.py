from django.db import models

# Create your models here.

class Files(models.Model):
    session_id = models.CharField(max_length=64, db_index=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
   
    user_id = models.IntegerField(null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.session_id} - {self.uploaded_at}"