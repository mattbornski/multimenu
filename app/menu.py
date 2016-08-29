#!/usr/bin/env python

import datetime

class Item():
    def __init__(self):
        self.resource = None
        self.name = None
        self.description = None
        self.cuisine = None
        self.photo = None
        self.price = None
        self.available = None

    def __repr__(self):
        return '\t' + self.name

    @classmethod
    def from_gobble(cls, data):
        instance = cls()
        instance.resource = 'gobble://' + ('sides/' if data['is_side'] else 'meals/') + str(data['id'])
        instance.name = data['name'].strip()
        instance.description = data['description'].strip()
        instance.cuisine = data['cuisine_name'].strip()
        instance.photo = data['photo']
        instance.price = data['price']
        instance.available = not data['is_sold_out']
        return instance

class Side(Item):
    pass

class Meal(Item):
    pass

class Menu:
    def __init__(self):
        self.resource = None
        self.date = None
        self.meals = []
        self.sides = []
        self.available = None

    def __repr__(self):
        return '\n'.join([
            self.resource,
            'Week of ' + str(self.date),
        ] + (['still unlocked' if self.available else 'LOCKED']) + [unicode(meal) for meal in self.meals] + [unicode(side) for side in self.sides])

    @classmethod
    def from_gobble(cls, data):
        instance = cls()
        instance.resource = 'gobble://menus/' + str(data['id'])
        instance.date = datetime.datetime.strptime(data['week_of'], '%Y-%m-%d').date()
        for item in data['entrees']:
            instance.meals.append(Meal.from_gobble(item))
        for item in data['sides']:
            instance.sides.append(Side.from_gobble(item))
        instance.available = (data['state'] == 'open')
        return instance
