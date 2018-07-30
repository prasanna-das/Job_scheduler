from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

def upload_location(instance, filename):
    return "%s/%s/%s" %( "userprofile/userphoto" , instance.id, filename)
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user')
    photo = models.ImageField(upload_to = upload_location,
                             default = 'userprofile/userphoto/no-image-icon-hi.png', help_text = 'Profile photo')

    firstname = models.CharField(max_length=140,null=True, blank=True)
    lastname = models.CharField(max_length=140,null=True, blank=True)

class Meta:
        db_table = "userprofile"





def create_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)