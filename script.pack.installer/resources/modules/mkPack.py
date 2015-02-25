#!/usr/bin/env python

import os
import zipfile
import shutil
import time
import errno

import xbmc
import xbmcgui
from xbmcaddon import Addon
# Plugin Info
ID         = 'script.pack.installer'
ADDON      = Addon( ID )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

class PackGenerator:

    def __init__(self):
        self.xbmcDialog = xbmcgui.Dialog()
        self.TIME_STAMP = self.timestamp()
        #Folder Locations settings
        self.OS_HOME    = os.path.expanduser('~/')
        if (self.checkVersion() == "kodi"):
            self.KODI_HOME     = self.OS_HOME+"/.kodi"
        elif (self.checkVersion() == "xbmc"):
            self.KODI_HOME     = self.OS_HOME+"/.xbmc"
        self.WORKING_DIR        = self.OS_HOME+"/Generated_Add-On_Packs/"
        self.BACKUP_DIR         = self.WORKING_DIR+self.TIME_STAMP
        self.SRC_ADDON_FOLDER   = self.KODI_HOME+"/addons"
        self.DEST_ADDON_FOLDER  = self.BACKUP_DIR+"/addons"
        self.ADDON_PACKAGES     = self.BACKUP_DIR+"/addons/packages"
        self.SRC_UDAT_FOLDER    = self.KODI_HOME+"/userdata/addon_data"
        self.DEST_UDAT_FOLDER   = self.BACKUP_DIR+"/userdata/addon_data"
        self.SRC_DBASE_FOLDER   = self.KODI_HOME+"/userdata/Database"
        self.DEST_DBASE_FOLDER  = self.BACKUP_DIR+"/userdata/Database"
        self.SRC_THUMB_FOLDER   = self.KODI_HOME+"/userdata/Thumbnails"
        self.DEST_THUMB_FOLDER  = self.BACKUP_DIR+"/userdata/Thumbnails"
        self.SRC_XML            = self.KODI_HOME+"/userdata"
        self.DEST_XML           = self.BACKUP_DIR+"/userdata"
        self.ZIP_ADDONS         = "addons"
        self.ZIP_USERDATA       = "userdata"

    def do_generator(self):
        # Select what to backup
        self.getSRC()
        # Change current working directory	
        os.chdir(self.BACKUP_DIR)
        # Remove what is older than 1980
        self.remOStamp('.')
        self.adzip()
        self.write_howto()

    def write_howto(self):
        # Create an upload form
        Pack_Name    = self.xbmcDialog.input('Name your Add-On Pack', '', type=xbmcgui.INPUT_ALPHANUM)
        self.FormIn  = ADDON_DIR+'/resources/Form.txt'
        self.FormOut = self.BACKUP_DIR+'/'+Pack_Name+'_Submission_Form.txt'
        FormOpen     = open(self.FormIn).readlines()
        FormWrite    = open(self.FormOut, 'w')
        for line in FormOpen:
            if line.startswith('#'):
                FormWrite.write(line)
            elif line.startswith('name='):
                FormWrite.write('\nname="'+Pack_Name+'"\n')
                FormWrite.write('%s\n%s\n%s\n%s\n' % ('url=""', 'img=""', 'fanart=""', 'description=""'))
        FormWrite.close()
        self.Fin  = self.xbmcDialog.ok('Add-On Pack Generator', "All done!", "Your Add-On Pack, [COLOR=selected][B]"+Pack_Name+"[/B][/COLOR], has been saved to: ", self.BACKUP_DIR)

    def timestamp(self):
        self.now = time.time()
        localtime = time.localtime(self.now)
        return time.strftime('%Y%m%d%H%M%S', localtime)
        #return time.strftime('%d-%b-%Y_%H%M-%S', localtime)

    def checkVersion(self):
        if os.path.isdir(self.OS_HOME+"/.kodi"):
            return "kodi"
        elif os.path.isdir(self.OS_HOME+"/.xbmc"):
            return "xbmc"

    def zipdir(self, path, zip):
        for root, dirs, files in os.walk(path):
            for file in files:
                zip.write(os.path.join(root, file))

    def adzip(self):
        self.zipf = zipfile.ZipFile("Addon_Pack.zip", 'w')
        self.zipdir(self.ZIP_ADDONS , self.zipf)
        self.zipdir(self.ZIP_USERDATA, self.zipf)
        self.zipf.close()

    def copyrecursively(self, src, dest):
        try:
            shutil.copytree(src, dest)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                print('Directory not copied. Error: %s' % e)

    def create_dir(self, dirname):
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

    def remOStamp(self, path):
        # Change stamp as zip wont allow older than 1980
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                f = os.path.join(root, name)
                old_time = os.stat(f).st_mtime #old access time
                new_mtime = time.time() #new modification time
                os.utime(f,(old_time,new_mtime)) #modify the file timestamp
            for name in dirs:
                f = os.path.join(root, name)
                old_time = os.stat(f).st_mtime #old access time
                new_mtime = time.time() #new modification time
                os.utime(f,(old_time,new_mtime)) #modify the file timestamp

    def getSRC(self):
        # Select what to backup
        self.answer     = self.xbmcDialog.ok('Add-On Pack Generator', "Before we begin, let's decide what we're including...", "", "Be carefull not to include folders containing sensitive data such as usernames or passwords.")
        self.addon_data = self.xbmcDialog.yesno("Add-On Pack Generator", "Would you like to include your [COLOR=selected][B]Add-On's Data Folder[/B][/COLOR]?", "", "This folder contains the settings of all your installed add-ons and may contain sensitive information if they're configured.")
        self.database   = self.xbmcDialog.yesno("Add-On Pack Generator", "Would you like to include your [COLOR=selected][B]Kodi Library Database[/B][/COLOR] and associated sources + images?", "", "This contains a list of your library's current media sources.")
        self.create_dir(self.BACKUP_DIR)
        self.copyrecursively(self.SRC_ADDON_FOLDER, self.DEST_ADDON_FOLDER)
        shutil.rmtree(self.ADDON_PACKAGES)
        if self.addon_data:
            self.copyrecursively(self.SRC_UDAT_FOLDER, self.DEST_UDAT_FOLDER)
        if self.database:
            self.copyrecursively(self.SRC_DBASE_FOLDER, self.DEST_DBASE_FOLDER)
            self.copyrecursively(self.SRC_THUMB_FOLDER, self.DEST_THUMB_FOLDER)
            self.copyrecursively(self.SRC_XML+'/RssFeeds.xml', self.DEST_XML+'/RssFeeds.xml')
            self.copyrecursively(self.SRC_XML+'/sources.xml', self.DEST_XML+'/sources.xml')

    def get_folders(self):
        pass


if __name__ == '__main__':
    packgenerator = PackGenerator()
    packgenerator.do_generator()
