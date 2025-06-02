from apps.accounts.models import *
from apps.accounts.serializers import *



def create_user(email, phone, name, agent):
    user_exists = User.objects.filter(email=email).exists()
    creator = User.objects.get(uid=agent)
    if not user_exists:
        user = User.objects.create(
            email=email,
            phone=phone,
            fullname=name,
            role="Client",
            created_by=creator,
        )
        user.save()
        return user
    else:
        return User.objects.get(email=email)


