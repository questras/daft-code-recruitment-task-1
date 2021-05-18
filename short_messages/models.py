from django.db import models


class ShortMessage(models.Model):
    body = models.CharField(max_length=160, blank=False)
    views_counter = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def reset_views(self):
        self.views_counter = 0
        self.save()

    def increment_views(self) -> int:
        self.views_counter += 1
        self.save()

        return self.views_counter

    def __str__(self):
        return f'"{self.body}" - {self.views_counter} views.'
