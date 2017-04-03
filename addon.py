# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Kodi Add-on for http://avezy.tk
# Version 1.2.1
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#------------------------------------------------------------
# Changelog:
# 1.3.0
# - code refactor
# - converted text to english for better understanding
# - fixed log errors
# - bumped version to 1.3.0
# 1.2.1
# - Eliminar sopcast
# - Eliminar diferencia ace/sop
# 1.2.0
# - Nueva version plugintools 1.0.8
# - Muestra el idioma en el listado de canales
# 1.1.4
# - Gestion de errores en peticiones HTTP
# 1.1.3
# - Nueva URL para JSON
# 1.1.2
# - Colores distintos para ace/sop
# 1.1.1
# - Fix URL JSON
# 1.1.0
# - Soporte canales Sopcast
# 1.0.6
# - Cambio ubicacion repo
# 1.0.5
# - Auto actualizacion
# 1.0.4
# - Mostrar agenda completa
# - Pantalla de ajustes
# - Posibilidad elegir servidor (ToDo)
# - Iconos para categorias
# 1.0.3
# - First public release
# 1.0.2
# - Minor fixes
# 1.0.1
# - Use public URL
# 1.0.0
# - First release
#---------------------------------------------------------------------------

import os
import sys
import urllib
import urllib2
import json
from datetime import date
from datetime import time
from datetime import datetime
import plugintools
import xbmcgui
import xbmcaddon
import xbmcplugin

# Source Server
if plugintools.ADDON.getSetting('av_source_server') == "0":
  parserJsonUrl = "https://avezy.tk/json.php"
elif plugintools.ADDON.getSetting('av_source_server') == "1":
  parserJsonUrl = "http://arenavision.esy.es/json.php"
else:
  parserJsonUrl = "https://avezy.tk/json.php"

# Debug Selected Server
if plugintools.ADDON.getSetting('debug_enabled') == 'true':
  plugintools.log("arenavisionezy Servidor: " + plugintools.ADDON.getSetting('av_source_server'), xbmc.LOGDEBUG)
  plugintools.log("arenavisionezy Json: " + parserJsonUrl, xbmc.LOGDEBUG)

# Entry point
def run():

    # Get params
    params = plugintools.get_params()
    plugintools.log("arenavisionezy.run " + repr(params), xbmc.LOGDEBUG)

    if params.get("action") is None:
        plugintools.log("arenavisionezy.run: No action selected", xbmc.LOGDEBUG)
        category_list(params)
    else:
        action = params.get("action")
        plugintools.log("arenavisionezy.run Action: " + action, xbmc.LOGDEBUG)
        exec action+"(params)"
    
    plugintools.close_item_list()

# Main menu
def category_list(params):
  plugintools.log("arenavisionezy.category_list "+repr(params), xbmc.LOGDEBUG)

  # Set JSON URL
  jsonUrl = parserJsonUrl
  plugintools.log("arenavisionezy.category_list Parsing: " + jsonUrl, xbmc.LOGDEBUG)
  
  # JSON Request
  jsonSrc = makeRequest(jsonUrl)
  plugintools.log("arenavisionezy.events_list jsonSrc output: " + jsonSrc, xbmc.LOGDEBUG)

  # Validate request format
  if(is_json(jsonSrc) == False):
    errorTitle = 'No JSON output'
    errorMsg   = "Retrieved output is not JSON"
    display_error(errorTitle, errorMsg, jsonSrc)
    return

  # Load JSON request
  request = json.loads(jsonSrc)

  # Check if request retrieved an error
  if('error' in request):
    errorTitle = 'Error processing categories'
    errorMsg   = request['msg']
    display_error(errorTitle, errorMsg)
    return
  
  categories  = request['categories']
  last_update = request['last_update']
  
  # Event information
  title01 = "                    [COLOR skyblue]ArenaVision EZY[/COLOR] Version "+plugintools.ADDONVERSION+" (Wazzu)"
  title02 = "                    [COLOR deepskyblue]Ultima actualizacion: "+last_update+"[/COLOR]"
  plugintools.add_item( title = title01 , thumbnail = set_thumbnail('default'), folder = False )
  plugintools.add_item( title = title02 , thumbnail = set_thumbnail('default'), folder = False )

  # Show all events
  plugintools.add_item(
    action     = "show_schedule" ,
    title      = "[COLOR deepskyblue][VER AGENDA COMPLETA][/COLOR]",
    plot       = '' ,
    url        = "plugin://plugin.video.arenavisionezy/?action=show_schedule",
    thumbnail  = set_thumbnail('default'),
    isPlayable = True,
    folder     = True
  )

  # Categories list
  for category in categories:
      
      # Thumbnail
      category_thumb = set_thumbnail(category['categoria'])
      plugintools.log("arenavisionezy.category_thumb "+category_thumb, xbmc.LOGDEBUG)
      
      # Items
      plugintools.add_item(
        action     = "events_list" , 
        title      = "[UPPERCASE]" + category['categoria'] + "[/UPPERCASE]" + " (" +  category['items'] + " events)", 
        plot       = '' , 
        url        = "plugin://plugin.video.arenavisionezy/?action=events_list&cat="+urllib.quote(category['categoria']),
        thumbnail  = category_thumb,
        isPlayable = True, 
        folder     = True
      )

# Schedule list
def show_schedule(params):
  plugintools.log("arenavisionezy.show_schedule "+repr(params), xbmc.LOGDEBUG)

  # Parse JSON
  jsonUrl = parserJsonUrl + '?cat=all'
  plugintools.log("arenavisionezy.show_schedule Parsing: " + jsonUrl, xbmc.LOGDEBUG)
  jsonSrc     = urllib2.urlopen(jsonUrl)
  request     = json.load(jsonSrc)
  events      = request['eventos']
  last_update = request['last_update']

  # Category title
  title01 = "                [COLOR skyblue]Complete schedule[/COLOR] (last updated: "+last_update+")"
  plugintools.add_item( title = title01 , thumbnail = set_thumbnail('default'), action='', url='', isPlayable = False, folder = False )

  # For each event...
  for event in events:
    title     = "[COLOR skyblue]" + event['fecha'] + " " + event['hora'] + "[/COLOR] " + event['titulo']
    plot      = ""
    thumbnail = set_thumbnail(event['categoria'])
    url       = "plugin://plugin.video.arenavisionezy/?action=channels_list&event="+event['id']
    plugintools.add_item(
      action="channels_list" ,
      title=title ,
      plot=plot ,
      url=url ,
      thumbnail=thumbnail ,
      isPlayable=True,
      folder=True
    )

# List all category events
def events_list(params):
  plugintools.log("Python Version: " + (sys.version), xbmc.LOGDEBUG)
  plugintools.log("arenavisionezy.events_list "+repr(params), xbmc.LOGDEBUG)
  category = params['cat']
  
  # Parse json
  jsonUrl = parserJsonUrl + '?cat='+urllib.quote(category)
  plugintools.log("arenavisionezy.events_list Parsing: " + jsonUrl, xbmc.LOGDEBUG)
  jsonSrc = makeRequest(jsonUrl)
  plugintools.log("arenavisionezy.events_list jsonSrc output: " + jsonSrc, xbmc.LOGDEBUG)

  # Load JSON request
  request = json.loads(jsonSrc)

  # Check if request retrieved any error
  if('error' in request):
    errorTitle = 'Error processing events'
    errorMsg   = request['msg']
    display_error(errorTitle, errorMsg)
    return

  events     = request['eventos']
  last_update = request['last_update']

  # Category title
  title01 = "                [COLOR skyblue][UPPERCASE]"+category+"[/UPPERCASE][/COLOR] (last updated: "+last_update+")"
  plugintools.add_item( title = title01 , thumbnail = set_thumbnail('default'), action='', url='', isPlayable = False, folder = False )
  
  # For each event...
  for event in events:
    # ToDo: Past events
    #plugintools.log("Endtime: " + ending_time)
    #showDate = datetime.strptime(ending_time, "%d/%m/%y %H:%M:%S").date()
    #todayDate = datetime.today().date()
    #if(showDate < todayDate):
    #  color = 'grey'
    #else:
    #  color = 'skyblue'
    color     = 'skyblue'
    title     = "[COLOR "+color+"]" + event['fecha'] + " " + event['hora'] + "[/COLOR] " + event['titulo']
    plot      = ""
    thumbnail = set_thumbnail(category)
    url       = "plugin://plugin.video.arenavisionezy/?action=channels_list&event="+event['id']
    plugintools.add_item(
      action="channels_list" , 
      title=title , 
      plot=plot , 
      url=url ,
      thumbnail=thumbnail , 
      isPlayable=True, 
      folder=True
    )

# List event channels
def channels_list(params):
  plugintools.log("arenavisionezy.channels_list "+repr(params), xbmc.LOGDEBUG)
  event = params['event']
  
  # Parse json
  jsonUrl = parserJsonUrl + '?evento='+event
  plugintools.log("arenavisionezy.channels_list Parsing: " + jsonUrl, xbmc.LOGDEBUG)
  jsonSrc = makeRequest(jsonUrl)
  plugintools.log("arenavisionezy.events_list jsonSrc output: " + jsonSrc, xbmc.LOGDEBUG)

  # Load JSON request
  event = json.loads(jsonSrc)

  # Check if response retrieved any error
  if('error' in event):
    errorTitle = 'Error processing channels'
    errorMsg   = event['msg']
    display_error(errorTitle, errorMsg)
    return
  
  # Event info
  category = event['categoria']
  title    = event['titulo']
  endtime  = event['fecha']
  channels = event['canales']

  # Event information
  title01 = "[COLOR skyblue] " + category + " - " + endtime + "[/COLOR]"
  plugintools.add_item( title = title01 , thumbnail = set_thumbnail('default'), isPlayable = True, folder = True )
  title01 = "[COLOR skyblue] " + title + "[/COLOR]"
  plugintools.add_item( title = title01 , thumbnail = set_thumbnail('default'), isPlayable = True, folder = True )

  # Event channels
  for channel in channels:
    channel_name = channel['canal']
    channel_url  = channel['enlace']
    channel_lang = channel['idioma']
    channel_mode = channel['mode']
	
    label = "["+channel_lang+"] [COLOR red]" + channel_name + "[/COLOR]" + " "

    label = label + "  " + title
    url   = "plugin://program.plexus/?url=" + channel_url + "&mode="+channel_mode+"&name=" + title
    plugintools.add_item( 
      title      = label , 
      url        = url , 
      thumbnail  = set_thumbnail(category) ,
      isPlayable = True, 
      folder     = False 
    )

# Thumbnail source
def set_thumbnail(category):
  thumb = category.lower().replace(" ", "_")
  thumb_path = os.path.dirname(__file__) + "/resources/media/" + thumb + ".png"
  if(os.path.isfile(thumb_path)):
    # Category thumbnail
    category_thumb = "special://home/addons/" + plugintools.ADDONID + "/resources/media/" + thumb + ".png"
  else:
    # Default thumbnail
    category_thumb = "special://home/addons/" + plugintools.ADDONID + "/resources/media/default.png"
  return category_thumb

# Display errors as Notification
def display_error(title, message, debug=""):
    plugintools.log("ERROR: " + title, xbmc.LOGERROR)

    errTitle = "[COLOR red][UPPERCASE]ERROR: " + title + "[/UPPERCASE][/COLOR]"
    errMsg   = message + "[CR]For more information, please check your logs."
    
    plugintools.add_item( title = errTitle, thumbnail = set_thumbnail('default'), action='', url='', isPlayable = False, folder = False )
    plugintools.add_item( title = errMsg, thumbnail = set_thumbnail('default'), action='', url='', isPlayable = False, folder = False )
    return

# Make HTTP request
def makeRequest(url):
  plugintools.log("makeRequest: " + url, xbmc.LOGDEBUG)

  try:
    req      = urllib2.Request(url)
    response = urllib2.urlopen(req)
    data     = response.read()
    response.close()
    return data
  except urllib2.URLError, e:
    errorMsg = str(e)
    plugintools.log(errorMsg, xbmc.LOGERROR);
    xbmc.executebuiltin("Notification(ArenavisionEzy,"+errorMsg+")")
    data_err = []
    data_err.append(['error', True])
    data_err.append(['msg', errorMsg])
    data_err = json.dumps(data_err)
    data_err = "{\"error\":\"true\", \"msg\":\""+errorMsg+"\"}"
    return data_err

# Check if output is in JSON format
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True

# Main loop
run()