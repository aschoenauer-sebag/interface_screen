import os, time, pdb

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic

from models import Plate, Well, Cond, Treatment

class IndexView(generic.ListView):
    template_name = 'plates/index.html'
    context_object_name = 'experiment_list'

    def get_queryset(self):
        """Return all experiments."""
        return Plate.objects.order_by('date')

class PlateView(generic.DetailView):
    model = Plate
    template_name = 'plates/plate.html'
    
    def get_context_data(self, **kwargs):
        context = super(PlateView, self).get_context_data(**kwargs)
        plate = self.object
        context["map"] = plate.buildMap()
        context["experiment_list"]=range(plate.well_number())
        return context

class WellView(generic.DetailView):
    model = Plate
    template_name = 'plates/well.html'
    
    def get_context_data(self, **kwargs):
        context = super(WellView, self).get_context_data(**kwargs)
        #le resultat de filter est un QuerySet, pas l'objet lui-meme. Si on est sur qu'il y a un seul object on peut utiliser get
        #a la place de filter. Ici cependant on n'a pas un seul objet.
        context["well"] = Well.objects.filter(plate=self.object).filter(num= self.kwargs["well"]).get()
        context['well_aim']= self.kwargs["well"]
    #ici j'ai besoin de faire ca parce que c'est une many to many relationship
        context["condition"]=context['well'].cond.get()
        #print context
        return context