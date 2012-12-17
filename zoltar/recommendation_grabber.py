import urllib
import json
import random
import sys

class recommendation_grabber :
  
  BASE_URL = 'http://api.zappos.com/Search?key=ea094499f485656d3e06eaf8688b94a8d1b224f8&filters='
  FILTERS  = {
    'female':    '"txAttrFacet_Gender":["Women"]',
    'male':      '"txAttrFacet_Gender":["Men"]',
    'cold':      '"personalityFacet":["Winter","Snow"]',
    'warm':      '"personalityFacet":["Summer","Beach"]',
    'fancy':     '"personalityFacet":["Dress","Fashion","Elegant","Designer","Sophisticated","Luxury","Fashionable"]',
    'casual':    '"personalityFacet":["Casual","Athleisure","Comfort","Novelty","Street","Librarian"]',
    'colourful': '"colorFacet":["Multi","Red","Pink","Orange","Yellow","Animal+Print"]',
    'drab':      '"colorFacet":["Black","Brown","Gray","Navy","Beige","Tan","Taupe","Olive","Khaki"]',
    'expensive': '"priceFacet":["$200.00+and+Over"]',
    'cheap':     '"priceFacet":["$100.00+and+Under"]'
  }
  CATEGORIES = [
    '"categoryFacet":["Tops"]',
    '"categoryFacet":["Bottoms"]',
    '"productType":["footwear"]'
  ]
  
  def __init__(self):
    "Iniitialize"
    
  def get_image( self, url, sku ):
    image = urllib.URLopener()
    filename, result = image.retrieve( url, 'temp/' + sku + ".jpg" )
    print filename
    return filename

  def get_recommendations( self, answers ):
    outfit = []
    filters = []
    for answer in answers:
      filters.append( self.FILTERS[ answer ] )
    for category in self.CATEGORIES:
      url = self.BASE_URL + '{' + ",".join( filters + [ category ] ) + '}'
      u = urllib.urlopen( url )
      response = u.read()
      data = json.loads( response )
      try:
        pick = random.choice( data['results'] )
        outfit.append({
          'image': 'http://zodiac.production.zappos-expo.com/pi/thermal/style_id/' + pick['styleId'] + '/angle/PAIR',
          'price': pick['price'],
          'sku':   pick['productId'],
          'name':  pick['productName']
        })
      except IndexError:
        print "Error: " + url
    return outfit