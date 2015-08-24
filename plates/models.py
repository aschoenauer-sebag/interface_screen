import os, getpass

from django.db import models

from interface_screen.settings import STATIC_ROOT

clones =tuple(zip( ['1', '4', 'A', 'B'],  ['1', '4', 'A', 'B']))
media = (('Complet', 'complet'),
         ('Exp', 'Desteroidise, sans rouge de phenol'),
         ('Indpdt', 'CO2-indpt')
         )

'''
Among the things to know : when a field of a model is added, the data base should be removed and then recreated
using python manage.py syncdb. It means it is entirely deleted and then re-created so all entries are deleted... Possibility
is to use a software for db migration.
'''

class Plate(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField('date started')
    nb_col = models.IntegerField(default = 12)
    nb_row = models.IntegerField(default = 8)
    
    def well_number(self):
        return self.nb_col*self.nb_row
    
    def height(self):
        if self.well_number()==96:
            return 466.7
        elif self.well_number()==48:
            return 600
        elif self.well_number()==384:
            return 700
        else:
            raise WellNumberDefError
        
    def width(self):
        if self.well_number()==384:
            return 1200 
        else:
            return 800

    def images(self, own_folder=True):
        #on veut une liste [{location:$location, legend_location:$legend_location}]
        result = []
        
#SO HERE we are looking for the files but we need to differenciate between the file location
#that is going to be interpreted by the template and the file location as dealt with by Python
        folder = "plots" if not own_folder else os.path.join('plots', self.cosydate())
        if not os.path.isdir(os.path.join(STATIC_ROOT, folder)):
            return [{'location':[], 'legend_location':{}}]

        for el in filter(lambda x: self.cosydate() in x and 'legend' not in x and 'W' not in x, os.listdir(os.path.join(STATIC_ROOT, folder))):
            legend= 'legend_%s'%el
            if legend in os.listdir(os.path.join(STATIC_ROOT, folder)):
                d = {'location':os.path.join(folder, el), 'legend_location':os.path.join(folder,legend)}
            else:
#TODO trouver le moyen de ne pas afficher ce dont on n'a pas besoin
                d = {'location':os.path.join(folder, el),'legend_location':''}
            result.append(d)
        result.sort()
        return result
    
    def plate_setup_location(self, own_folder=True):
        if own_folder:
            return 'plots/%s/plate--%s.png'%(self.cosydate(), self.cosydate())
        else:
            return 'plots/plate--%s.png'%self.cosydate()
    
    def cosydate(self):
        s = self.date.strftime('%d')+str(int(self.date.strftime('%m')))+self.date.strftime('%y')
        if s not in os.listdir(os.path.join(STATIC_ROOT, 'plots')):
            s = self.date.strftime('%d')+self.date.strftime('%m')+self.date.strftime('%y')
        return s#self.date.strftime('%d%m%y')
#    
#    def __unicode__(self):
#        r = '%s %s'%(str(self.name), self.date.strftime('%d%m%y'))
#        return r
    
    def __str__(self):
        r = '%s %s'%(str(self.name), self.date.strftime('%d%m%y'))
        return r
    
    def buildMap(self):
#TODO fix map problem, some wells are not clickable
        num_exp = self.well_number()
        map = {}
        if self.well_number()==96:
            x0=100; step_x = 51.3; 
            y0=58.3; step_y=46.7
        elif self.well_number()==48:
            x0=100; step_x = 77; 
            y0=60; step_y=80
        elif self.well_number()==384:
            x0=150; step_x=37.2
            y0=70; step_y=35
        else:
            raise WellNumberDefError
            
        for j in range(self.nb_row):
            for i in range(self.nb_col):
                x=x0+i*step_x; x1 =x0+(i+1)*step_x 
                y=y0+j*step_y; y1=y0+(j+1)*step_y
                map[i+j*self.nb_col+1]=[x, y, x1, y1]
        return map
    
class Cond(models.Model):
    '''
    This is the class for the experimental condition of a screen. We are not using the word 
    condition because it is already used by django
    '''
    
    medium = models.CharField(max_length =50, 
                              choices = media,
                              verbose_name = 'Cell culture medium')
    serum = models.IntegerField(max_length = 2,
                                null = True, blank=True,
                                verbose_name = '%SVF')
    other = models.CharField(max_length = 500, blank = True, default = '')
    
    def __str__(self):
        r = '%s %s'%(self.medium, self.serum)
        return r
    
class Treatment(models.Model):
    xb = models.CharField(max_length = 200,
                          default = 'TCDD')
    is_ctrl = models.BooleanField(default=False)
    ctrl = models.ForeignKey('self', blank=True, null=True,
                             limit_choices_to={'is_ctrl': True})
    dose = models.FloatField(default = 0)
    
    def __str__(self):
        r = '%s %s'%(self.xb, self.dose)
        return r

class Well(models.Model):
    #this should not be a primary key because well number is going to be the same
    #for all the wells that are at the same location on different plates
    num = models.IntegerField('well number')
    
    plate = models.ForeignKey(Plate)
    treatment = models.ForeignKey(Treatment)
    cond = models.ManyToManyField(Cond)
    clone = models.CharField(max_length=1, choices=clones, null=True, blank=True)
        
    def __str__(self):
        r = 'S%s W%s'%(self.plate.date.strftime('%d%m%y'), self.num)
        return r
    
    def images(self, own_plate_folder = True):
        #on veut une liste [{location:$location}], ici pas de legendes detachees a priori
        result = []
        folder = "plots" if not own_plate_folder else os.path.join('plots', self.plate.cosydate())
        
        for el in filter(lambda x: self.plate.cosydate() in x and "W%05i"%self.num in x, os.listdir(os.path.join(STATIC_ROOT, folder))):
            result.append({'location':os.path.join(folder, el)})
        result.sort()
        return result
    
    def movies(self, own_plate_folder = False):
        '''
        Video 1: raw images, channel H2B-mCherry
        Video 2: raw images, channels H2B-mCherry and myrPalm-GFP
        Video 3: images H2B-mCherry with classification at the 1/1/2015 mitose classifier
        '''
        folder = "movies" if not own_plate_folder else os.path.join("movies", self.plate.cosydate())
        
        names = filter(lambda x: 'P%s_W%s_'%(self.plate.cosydate(), self.num) in x, os.listdir(os.path.join(STATIC_ROOT, folder)))
        return [os.path.join(folder, name) for name in names]
    
class WellNumberDefError(Exception):
    def __init__(self):
        print "Problem related to well number definition", sys.exc_info()
        pass        
