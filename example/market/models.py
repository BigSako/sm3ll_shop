from __future__ import unicode_literals

from django.db import models


def none_or_int(str):
    if str == 'None':
        return None
    else:
        return int(str)

def none_or_double(str):
    if str == 'None':
        return 0.0
    else:
        return float(str)


class ItemGroup(models.Model):
    """ EVE Online Inventory Groups
    Uses InvGroups.csv with the following model:
    groupID,categoryID,groupName,iconID,useBasePrice,anchored,anchorable,fittableNonSingleton,published
    """
    class Meta:
        verbose_name = 'Item Group'
        verbose_name_plural = 'Item Groups'

    groupID = models.IntegerField(primary_key=True)
    categoryID = models.IntegerField()
    groupName = models.CharField(max_length=128)
    iconID = models.IntegerField(null=True)
    useBasePrice = models.SmallIntegerField()
    anchored = models.SmallIntegerField()
    anchorable = models.SmallIntegerField()
    fittableNonSingleton = models.SmallIntegerField()
    published = models.SmallIntegerField()


    def is_published(self):
        return "Yes" if self.published == 1 else "No"

    def __str__(self):
        return self.groupName

    def __unicode__(self):
        return self.groupName

    @staticmethod
    def from_csv(dict):
        item = ItemGroup()
        item.groupID = int(dict['groupID'])
        item.categoryID = int(dict['categoryID'])
        item.groupName = dict['groupName']
        item.iconID = none_or_int(dict['iconID'])
        item.useBasePrice = int(dict['useBasePrice'])
        item.anchored = none_or_int(dict['anchored'])
        item.anchorable = none_or_int(dict['anchorable'])
        item.fittableNonSingleton = none_or_int(dict['fittableNonSingleton'])
        item.published = int(dict['published'])

        return item

    @staticmethod
    def parse(csvfile):
        """ Helper: parses the invGroups csv file and updates the appropriate
        table in database """
        ItemGroup.objects.all().delete()
        for row in csvfile:
            item = ItemGroup.from_csv(row)
            item.save()



class ItemMarketGroup(models.Model):
    """ EVE Online Market Groups
    Uses InvMarketGroups.csv with the following model:
    marketGroupID,parentGroupID,marketGroupName,description,iconID,hasTypes
    """
    class Meta:
        verbose_name = 'Market Group'
        verbose_name_plural = 'Market Groups'

    marketGroupID = models.IntegerField(primary_key=True)
    parentGroupID = models.IntegerField(verbose_name='Parent market group id',
                                        null=True, blank=True)
    #models.ForeignKey('self', verbose_name='Parent market group', null=True, blank=True, db_constraint=False)
    marketGroupName = models.CharField(max_length=128)
    description = models.TextField()
    iconID = models.IntegerField(null=True)
    hasTypes = models.SmallIntegerField()

    @property
    def parent(self):
        if self.parentGroupID == 0 or self.parentGroupID == None:
            return None
        else:
            return ItemMarketGroup.objects.get(marketGroupID=self.parentGroupID)

    @property
    def parent_group_name(self):
        if self.parentGroupID == 0 or self.parentGroupID == None:
            return "None"
        else:
            return self.parent().marketGroupName

    def get_parents_as_list(self):
        """ returns a list of parents in direct order """
        parents = []

        parent_id = self.parentGroupID

        while parent_id != 0 and parent_id != None:
            parent = ItemMarketGroup.objects.get(marketGroupID=parent_id)
            name = parent.marketGroupName
            parents.append({'id': parent_id, 'name': name})

            parent_id = parent.parentGroupID

        return parents

    def get_parents_as_breadcrumb_list(self, include_self=False):
        marketgroups = self.get_parents_as_list()

        if include_self:
            marketgroups = [{'id': self.marketGroupID, 'name': self.marketGroupName}] + marketgroups

        breadcrumbs = []

        for gr in marketgroups:
            breadcrumbs.append({'link': "/market/group/" + str(gr['id']), 'name': gr['name']})

        return reversed(breadcrumbs)

    def __str__(self):
        return self.marketGroupName

    def __unicode__(self):
        return self.marketGroupName

    @staticmethod
    def from_csv(dict):
        item = ItemMarketGroup()
        item.marketGroupID = int(dict['marketGroupID'])
        item.parentGroupID = none_or_int(dict['parentGroupID'])
        item.marketGroupName = dict['marketGroupName']
        item.description = dict['description']
        item.iconID = none_or_int(dict['iconID'])
        item.hasTypes = none_or_int(dict['hasTypes'])

        return item

    @staticmethod
    def parse(csvfile):
        """ Helper: parses the invMarketGroups csv file and updates the
        appropriate table in database """
        #ItemMarketGroup.objects.all().delete()
        for row in csvfile:
            item = ItemMarketGroup.from_csv(row)
            item.save()




class InvType(models.Model):
    """ EVE Online Inventory Types
    Uses InvTypes.csv with the following model:
    typeID,groupID,typeName,description,mass,volume,capacity,portionSize,raceID,basePrice,published,marketGroupID,iconID,soundID,graphicID
    """
    class Meta:
        verbose_name = 'Item Type'
        verbose_name_plural = 'Item Types'


    typeID = models.BigIntegerField(primary_key=True)
    typeName = models.CharField(max_length=128)
    description = models.TextField()
    mass = models.FloatField()
    itemgroup =  models.ForeignKey(ItemGroup, on_delete=models.CASCADE,
                                 verbose_name="Related Item Group (groupID)")
    volume = models.FloatField()
    capacity = models.FloatField()
    portionSize = models.FloatField() # what is this?
    raceID = models.IntegerField(null=True, blank=True) # probably not needed
    basePrice = models.FloatField() # probably not filled?
    published = models.SmallIntegerField("Whether or not this item has been published")
    itemmarketgroup = models.ForeignKey(ItemMarketGroup, on_delete=models.CASCADE,
                                      verbose_name="Related market Group (marketGroupID)",
                                      null=True, blank=True)
    iconID = models.FloatField(null=True) # what is this for?
    soundID = models.IntegerField(null=True) # what is this for?
    graphicID = models.IntegerField(null=True) # what is this for


    def is_published(self):
        return "Yes" if self.published == 1 else "No"


    def get_img(self, width=64):
        return "https://image.eveonline.com/Type/" + str(self.typeID) + "_" + str(width) + ".png"

    def get_img_64(self):
        return self.get_img(64)

    def get_img_32(self):
        return self.get_img(32)

    def get_img_128(self):
        return self.get_img(128)


    @staticmethod
    def from_csv(dict):
        marketGroupID=none_or_int(dict['marketGroupID'])
        if marketGroupID == None:
            return None # we dont want this in our database (for performance reasons)

        item = InvType()
        item.typeID = int(dict['typeID'])
        item.typeName = dict['typeName']
        item.description = dict['description']
        item.mass = float(dict['mass'])
        item.itemgroup = ItemGroup.objects.get(groupID=int(dict['groupID']))
        item.volume = float(dict['volume'])
        item.capacity = float(dict['capacity'])
        item.portionSize = float(dict['portionSize'])
        item.raceID = none_or_int(dict['raceID'])
        item.basePrice = none_or_double(dict['basePrice'])
        item.published = int(dict['published'])
        print("marketGroupID=", marketGroupID)
        item.itemmarketgroup = ItemMarketGroup.objects.get(marketGroupID=marketGroupID)
        item.iconID = none_or_int(dict['iconID'])
        item.graphicID = none_or_int(dict['graphicID'])


        return item

    @staticmethod
    def parse(csvfile):
        """ Helper: parses the invTypes csv file and updates the
        appropriate table in database """
        InvType.objects.all().delete()
        for row in csvfile:
            item = InvType.from_csv(row)
            if item != None:
                item.save()


class CartItem(models.Model):
    """ Stores an item in a shopping cart and relates it to a user """
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    invtype = models.ForeignKey(InvType, on_delete=None,
                                verbose_name="Related Item Type")
    eveuser = models.ForeignKey("crest_app.EveUserProfile",
                                verbose_name="Related EVE User Profile")
    amount = models.IntegerField("How many of that item")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)


    @staticmethod
    def remove_from_cart(eveuser, invtype):
        existing = CartItem.objects.filter(eveuser=eveuser, invtype=invtype)
        if len(existing) > 0:
            existing[0].delete()

    @staticmethod
    def add_to_cart(eveuser, invtype, amount):
        """ Adds an item to the cart """
        # first, see if this item is in the current cart already
        existing = CartItem.objects.filter(eveuser=eveuser, invtype=invtype)

        if len(existing) == 0:
            item = CartItem.objects.create(
                eveuser=eveuser, invtype=invtype, amount=amount)
            print("adding item to cart: eveuser=", eveuser, ", invtype=", invtype)
            return item
        else:
            item = existing[0]
            item.amount += amount
            item.save()

            return item
