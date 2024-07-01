from django.db import models

class Product(models.Model):
    PartNumber = models.CharField(max_length=100)
    Description = models.TextField()
    image1 = models.ImageField(upload_to='images/', blank=True)
    image2 = models.ImageField(upload_to='images/', blank=True)

    # Add any other fields you need for your product

    def __str__(self):
        return self.PartNumber  # Return the PartNumber as the string representation of the object
