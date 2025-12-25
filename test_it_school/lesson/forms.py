from django import forms

from .models import Lesson


class LessonCreateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "description",
            "start_time",
            "end_time",
            "status",
        ]

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and end <= start:
            raise forms.ValidationError(
                "Время окончания должно быть позже времени начала"
            )

        return cleaned_data
