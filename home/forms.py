from django.forms import ModelForm
# from matplotlib import widgets
from home.models import Register


class UpdateForm(ModelForm):
     class Meta:
          model = Register
          fields = ('bio','location')
          