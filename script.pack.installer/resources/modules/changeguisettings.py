#!/usr/bin/env python
##
#
#    Author Josh Sunnex  https://github.com/josh5
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
###########################################################################

import os
import xbmc
import xbmcgui
from xbmcaddon import Addon

# Plugin Info of EmbER System Settings
ID               = 'script.system.settings'
ADDON            = Addon( ID )
ADDON_ID         = ADDON.getAddonInfo('id')
ADDON_NAME       = ADDON.getAddonInfo('name')
ADDON_ICON       = ADDON.getAddonInfo('icon')
ADDON_VERSION    = ADDON.getAddonInfo('version')
ADDON_DATA       = xbmc.translatePath( "special://profile/addon_data/%s/" % ID )
ADDON_DIR        = ADDON.getAddonInfo( "path" )

gui_xml = os.path.join(xbmc.translatePath("special://userdata"),"guisettings.xml")
ch_file = os.path.join(xbmc.translatePath("special://userdata"), "addon_data", "script.system.settings",".guisettings_set")

# Global definitions
def read_xml_entry(XML,element,entry):
    import xml.etree.ElementTree as ET
    if os.path.isfile(XML):
        print "looking at: "+element+" > "+entry
        tree = ET.parse(XML)
        root = tree.getroot()
        for child in root:
            if child.tag == element:
                for subchild in child:
                    if subchild.tag == entry:
                        return subchild.text

def write_xml_entry(XML,element,entry,value):
    import xml.etree.ElementTree as ET
    if os.path.isfile(XML):
        print "Writing: "+element+" > "+entry+" > "+value
        tree = ET.parse(XML)
        root = tree.getroot()
        for child in root:
            if child.tag == element:
                for subchild in child:
                    if subchild.tag == entry:
                        if subchild.attrib and ("default" in subchild.attrib):
                            if subchild.attrib["default"] == "true":
                                subchild.attrib["default"] = "false"
                        subchild.text = value
        tree.write(XML)

def write_to_chfile(parent, sub, setting):
    try:
        chfile = open(ch_file, 'a')
        chfile.write("%s %s %s\n" % (parent, sub, setting))
        chfile.close()
        return True
    except Exception, e:
        xbmc.log('Changeguisettings: Exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
        return False

def reload_kodi():
    import subprocess
    cmd = 'pkill -9 kodi && python '+xbmc.translatePath(os.path.join( ADDON_DIR, 'resources', 'scripts', 'setguisettings.py'))
    xbmc.log("shut down Kodi so the choosen guisettings will take effect")
    xbmc.sleep(1000)
    subprocess.Popen(cmd, shell=True, close_fds=True)

def set_setting(parent, sub, setting):
    try:
        setting_current = read_xml_entry(gui_xml,parent,sub)
    except Exception, e:
        xbmc.log('Changeguisettings: Exception occurred', level=xbmc.LOGERROR)
        xbmc.log(str(e), level=xbmc.LOGERROR)
        setting_current = "Somthing went wrong reading file"
    if setting != setting_current:
        try:
            write_xml_entry(gui_xml,parent,sub,setting)
            return True
        except Exception, e:
            xbmc.log('Changeguisettings: Exception occurred', level=xbmc.LOGERROR)
            xbmc.log(str(e), level=xbmc.LOGERROR)
            return False
    else:
        return False


##########
### Change Skin ###
### 
def get_skin_list():
    list = []
    path1 = xbmc.translatePath( "special://xbmc/addons/")
    path2 = xbmc.translatePath( "special://home/addons/")
    for dirname in os.listdir(path1):
        xbmc.log(dirname)
        if len(dirname) >0 and dirname.startswith("skin."):
            xbmc.log('Path1 - found skin: '+dirname)
            list.append(dirname)
    for dirname in os.listdir(path2):
        xbmc.log(dirname)
        if len(dirname) >0 and dirname.startswith("skin."):
            xbmc.log('Path2 - found skin: '+dirname)
            list.append(dirname)
    list.sort()
    return list
    
def get_skin_name(skin_list):
    list = []
    gui_xml=os.path.join(xbmc.translatePath("special://userdata"),"guisettings.xml")
    skin_current = read_xml_entry(gui_xml,"lookandfeel","skin")
    for ID in skin_list:
        skinname = Addon( ID ).getAddonInfo('name')
        if ID == skin_current:
            skinname = "[COLOR=selected]"+skinname+"     [B](SELECTED)[/B][/COLOR]"
        list.append(skinname)
    return list

def set_skin(skin):
    gui_xml=os.path.join(xbmc.translatePath("special://userdata"),"guisettings.xml")
    skin_current = read_xml_entry(gui_xml,"lookandfeel","skin")
    if skin != skin_current:
        xbmc.log("I will try to set the skin to "+skin)
        write_xml_entry(gui_xml,"lookandfeel","skin",skin)
        xbmc.log("skin: "+read_xml_entry(gui_xml,"lookandfeel","skin"))
        return True
    else:
        return False

def select_skin():
    try:
        parent  = "lookandfeel"
        sub     = "skin"
        skn_list = get_skin_list()
        name_list = get_skin_name(skn_list)
        get_more = "Get More..."
        name_list.append(get_more)
        skn_list.append("more")
        if len(skn_list) > 0:
            dialog = xbmcgui.Dialog()
            answer = dialog.select('Select a Skin', name_list)
            xbmc.log("answer "+str(answer))
            xbmc.log("choice: "+skn_list[answer])
        if answer != -1:
            skin = skn_list[answer]
            xbmc.log("choice: "+skin)
            if skin == "more":
                xbmc.executebuiltin("ActivateWindow(addonbrowser,addons://all/xbmc.gui.skin,return)")
            elif set_skin(skin) == True:
                write_to_chfile(parent, sub, skin)
            else:
                pass
    except:
        xbmc.log('An Error Cccured While Getting Skin Information.')
