from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

import dateutil.parser
import time
import urllib2
from xml.etree import ElementTree as ET
from django.db import models

from collections import defaultdict

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from django.conf import settings

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d








class EveUser(AbstractUser):
    """custom User class to work with django-social-auth"""

    @cached_property
    def _eve_auth(self):
        """shortcut to python-social-auth's EVE-related extra data for this user"""
        return self.social_auth.get(provider='eveonline').extra_data

    def _get_crest_tokens(self):
        """get tokens for authenticated CREST"""
        expires_in = time.mktime(
            dateutil.parser.parse(
                self._eve_auth['expires']  # expiration time string
            ).timetuple()                             # expiration timestamp
        ) - time.time()                               # seconds until expiration
        return {
            'access_token': self._eve_auth['access_token'],
            'refresh_token': self._eve_auth['refresh_token'],
            'expires_in': expires_in
        }

    @property
    def character_id(self):
        """get CharacterID from authentification data"""
        if self.eveuserprofile._character_id == 0:
            self.eveuserprofile._character_id = self._eve_auth['id']
            self.eveuserprofile.save()

        return self.eveuserprofile._character_id

    @property
    def character_name(self):
        """ get character name from public eve onlien api data """
        return self.eveuserprofile.character_name

    @property
    def alliance_name(self):
        """get Alliance Name from public eve online api data"""
        return self.eveuserprofile.alliance_name

    @property
    def corporation_name(self):
        """get Corporation Name from public eve online api data"""
        return self.eveuserprofile.corporation_name

    @property
    def alliance_id(self):
        """get Alliance ID from public eve online api data"""
        return self.eveuserprofile.alliance_id

    @property
    def corporation_id(self):
        """get Corporation ID from public eve online api data"""
        return self.eveuserprofile.corporation_id

    @property
    def is_allowed(self):
        """ check if this corp/alliance is allowed on the server """
        return self.alliance_id in settings.ALLOWED_ALLIANCE_IDS

    def get_portrait_url(self, size=128):
        """returns URL to Character portrait from EVE Image Server"""
        return "https://image.eveonline.com/Character/{0}_{1}.jpg".format(self.character_id, size)

    def get_profile(self):
        """ returns the eveuser profile associated to this """
        return EveUserProfile.objects.filter(user=self)[0]



class EveUserProfile(models.Model):
    """ The EvE Online users profile (char id, name, corp, ...) """
    user = models.OneToOneField(EveUser, on_delete=models.CASCADE)

    profile_created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    profile_updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    #other fields here
    _character_id = models.BigIntegerField(default=0)
    _character_name = models.CharField(max_length=128,default='')
    _corporation_name = models.CharField(max_length=128,default='')
    _alliance_name = models.CharField(max_length=128,default='')
    _alliance_id = models.BigIntegerField(default=0)
    _corporation_id = models.BigIntegerField(default=0)




    def update_profile_info(self):
        """ updates profile information from eve api """
        self._character_name = self._eve_characterinfo['characterName']
        self._alliance_name = self._eve_characterinfo['alliance'] if 'alliance' in self._eve_characterinfo else ""
        self._corporation_name = self._eve_characterinfo['corporation']
        self._alliance_id = self._eve_characterinfo['allianceID'] if 'allianceID' in self._eve_characterinfo else 0
        self._corporation_id = self._eve_characterinfo['corporationID']

        self.save()

    @cached_property
    def _eve_characterinfo(self):
        """access the eve online characterinfo data based on character_id"""
        # https://api.eveonline.com/Eve/CharacterInfo.xml.aspx?characterID=1352400035
        requestURL = "https://api.eveonline.com/Eve/CharacterInfo.xml.aspx?characterID=" + str(self.user.character_id)

        print "Requesting ", requestURL

        root = ET.parse(urllib2.urlopen(requestURL)).getroot()
        ddd = etree_to_dict(root)
        return ddd['eveapi']['result']

    def __str__(self):
          return "%s's profile" % self.user

    @property
    def character_name(self):
      """get character name from public eve online api data"""
      if self._character_name == "":
          self._character_name = self._eve_characterinfo['characterName']
          self.save()
      return self._character_name

    @property
    def alliance_name(self):
      """get Alliance Name from public eve online api data"""
      if self._alliance_name == "":
          self.update_profile_info()
      return self._alliance_name

    @property
    def corporation_name(self):
      """get Corporation Name from public eve online api data"""
      if self._corporation_name == "":
          self.update_profile_info()
      return self._corporation_name

    @property
    def alliance_id(self):
      """get Alliance ID from public eve online api data"""
      if self._alliance_id == 0:
          self.update_profile_info()
      return self._alliance_id

    @property
    def corporation_id(self):
      """get Corporation ID from public eve online api data"""
      if self._corporation_id == 0:
          self.update_profile_info()
      return self._corporation_id


def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = EveUserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=EveUser)
