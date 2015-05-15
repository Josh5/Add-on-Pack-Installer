##Run Add-On Pack Installer
import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,os,sys,downloader,extract,time,shutil,subprocess
from resources.modules import main
addon_id='script.pack.installer'; AddonTitle='Add-on Pack Installer'; 
wizardUrl='https://raw.githubusercontent.com/Josh5/addon-packs/master/'; #wizardUrl='http://tribeca.xbmchub.com/tools/wizard/'
SiteDomain='TinyHTPC.co.nz'; #SiteDomain='XBMCHUB.com'
TeamName='Add-on Pack Installer'; #TeamName='Team XBMCHUB'
try:        from addon.common.addon import Addon
except:
    try:    from t0mm0.common.addon import Addon
    except: from t0mm0_common_addon import Addon
try:        from addon.common.net   import Net
except:
    try:    from t0mm0.common.net   import Net
    except: from t0mm0_common_net   import Net
addon=main.addon; net=Net(); settings=xbmcaddon.Addon(id=addon_id); net.set_user_agent('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'); 
#==========================Help WIZARD=====================================================================================================
def HELPCATEGORIES():
    if ((XBMCversion['Ver'] in ['','']) or (int(XBMCversion['two']) < 12)) and (settings.getSetting('bypass-xbmcversion')=='false'):
        eod(); addon.show_ok_dialog(["Compatibility Issue: Outdated Kodi Setup","Please upgrade to a newer version of XBMC first!","Visit %s for Support!"%SiteDomain],title="XBMC "+XBMCversion['Ver'],is_error=False); DoA('Back'); 
    else:
        link=OPEN_URL(wizardUrl+'packs.txt').replace('\n','').replace('\r','')
        match=re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)".+?ype="(.+?)".+?nset="(.+?)".+?estart="(.+?)"').findall(link)
        for name,url,iconimage,fanart,description,filetype,skinset,restart in match:
            #if 'status' in filetype:
                #main.addHELPDir(name,url,'wizardstatus',iconimage,fanart,description,filetype)
            #else:    
                main.addHELPDir(name,url,'helpwizard',iconimage,fanart,description,filetype,skinset,restart)
                #print [name,url]
        main.AUTO_VIEW('movies')
        #main.addHELPDir('Testing','http://www.firedrive.com/file/################','helpwizard',iconimage,fanart,description,filetype) ## For Testing to test a url with a FileHost.
        ## ### ## \/ OS Check and Button Suggestions \/ ## ### ## 
        #if   sOS.lower() in ['win32']: SuggestButton('Windows')    ## Windows.
        #elif sOS.lower() in ['linux']: SuggestButton('Linux')     ## May include android stuff as well.
        #elif sOS.lower() in ['mac','osx']: SuggestButton('MAC')   ## 
        #elif sOS.lower() in ['android']: SuggestButton('Android') ## 
        ## ### ## 
def SuggestButton(msg): addon.show_ok_dialog(["By the looks of your operating system","we suggest clicking: ",""+msg],title="OS: "+sOS,is_error=False); 
def OPEN_URL(url): req=urllib2.Request(url); req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'); response=urllib2.urlopen(req); link=response.read(); response.close(); return link
def FireDrive(url):
    if ('http://m.firedrive.com/file/' not in url) and ('https://m.firedrive.com/file/' not in url) and ('http://www.firedrive.com/file/' not in url) and ('http://firedrive.com/file/' not in url) and ('https://www.firedrive.com/file/' not in url) and ('https://firedrive.com/file/' not in url): return url ## contain with current url if not a filedrive url.
    #else:
    try:
        if 'https://' in url: url=url.replace('https://','http://')
        html=net.http_GET(url).content
        if ">This file doesn't exist, or has been removed.<" in html: return "[error]  This file doesn't exist, or has been removed."
        elif ">File Does Not Exist | Firedrive<" in html: return "[error]  File Does Not Exist."
        elif "404: This file might have been moved, replaced or deleted.<" in html: return "[error]  404: This file might have been moved, replaced or deleted."
        data={}; r=re.findall(r'<input\s+type="\D+"\s+name="(.+?)"\s+value="(.+?)"\s*/>',html);
        for name,value in r: data[name]=value
        if len(data)==0: return '[error]  input data not found.'
        html=net.http_POST(url,data,headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0','Referer': url,'Host': 'www.firedrive.com'}).content
        r=re.search('<a\s+href="(.+?)"\s+target="_blank"\s+id=\'top_external_download\'\s+title=\'Download This File\'\s*>',html)
        if r: 
        	print urllib.unquote_plus(r.group(1)); 
        	return urllib.unquote_plus(r.group(1))
        else: return url+'#[error]'
    except: return url+'#[error]'

def isember():
    if os.path.isfile('/etc/os-release'):
        osrelease = open('/etc/os-release')
        file = osrelease.readlines()
        OSID = False
        for line in file:
            if 'ID=' in line and not '_ID' in line:
                OSID = line[line.find('=')+1 : line.find('\n')].rstrip('\n')
                if OSID in ['ember']:
                    return True
            else:
                pass
        if OSID in ['ember']:
            return True
        else:
            return False
        osrelease.close()
    else:
        return False

def HELPWIZARD(name,url,description,filetype,skinset,restart):
    path=xbmc.translatePath(os.path.join('special://home','addons','packages'))
    confirm=xbmcgui.Dialog()
    if confirm.yesno(TeamName,"Would you like the '%s' Add-on Pack"%name,"to customize your Kodi (XBMC) installation? "," "):
        dp=xbmcgui.DialogProgress(); dp.create(AddonTitle,"Downloading",'','Please Wait')
        lib=os.path.join(path,name+'.zip')
        try: os.remove(lib)
        except: pass
        url=FireDrive(url)
        if '[error]' in url: print url; dialog=xbmcgui.Dialog(); dialog.ok("Error!",url); return
        else: print url
        downloader.download(url,lib,dp)
        if filetype == 'home':
            addonfolder=xbmc.translatePath(os.path.expanduser('~/'))
        elif filetype == 'main':
            addonfolder=xbmc.translatePath(os.path.join('special://','home'))
        else:
            addonfolder=xbmc.translatePath(os.path.join('special://','home'))
        time.sleep(2)
        dp.update(0,"Extracting Zip",'','Please Wait')
        print '======================================='; print addonfolder; print '======================================='
        extract.all(lib,addonfolder,dp)
        # === Edit XBMC Settings ===
        isthisember = isember()
        if skinset != 'none':
            from resources.modules import changeguisettings
            print "Write guisettings: "+skinset
            link=OPEN_URL(skinset)
            shorts=re.compile('shortcut="(.+?)"').findall(link)
            for shortname in shorts: xbmc.executebuiltin("Skin.SetString(%s)" % shortname)
            bools=re.compile('setbool="(.+?)"').findall(link)
            for boolname in bools: xbmc.executebuiltin("Skin.SetBool(%s)" % boolname)
            elements=re.compile('setelement="(.+?)"').findall(link)
            isthisember = isember()
            for elementname in elements:
                settings = elementname.split(',')
                print settings
                if isthisember:
                    if changeguisettings.write_to_chfile(settings[0], settings[1], settings[2]):
                        print "Prepairing to write guisetting: "+settings[0]+' > '+settings[1]+' > '+settings[2]
                else:
                    if changeguisettings.set_setting(settings[0], settings[1], settings[2]):
                        print "Writing guisetting: "+settings[0]+' > '+settings[1]+' > '+settings[2]
        time.sleep(2)
        # === Reset Kodi to take on applied changes ===
        if restart == 'yes':
            print '======================================='; print 'Restarting Kodi...'; print '======================================='
            dialog=xbmcgui.Dialog(); dialog.ok("Success!","Click OK to restart your device","","[B]Brought To You By %s[/B]"%SiteDomain)
            if isthisember:
                changeguisettings.reload_kodi()
            else:
                subprocess.Popen('pkill -9 kodi && reboot', shell=True, close_fds=True)
        xbmc.executebuiltin( 'UpdateAddonRepos' )            
        xbmc.executebuiltin( 'UpdateLocalAddons' )
        dialog=xbmcgui.Dialog(); dialog.ok("Success!","Installation Complete","","[B]Brought To You By %s[/B]"%SiteDomain)      
        #xbmc.executebuiltin( "ReplaceWindow(home)" )
        ##

def WIZARDSTATUS(url):
    link=OPEN_URL(url).replace('\n','').replace('\r','')
    match=re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)".+?ype="(.+?)"').findall(link)
    for name,url,iconimage,fanart,description,filetype in match: header="[B][COLOR gold]"+name+"[/B][/COLOR]"; msg=(description); TextBoxes(header,msg)

def TextBoxes(heading,anounce):
        class TextBox():
            WINDOW=10147; CONTROL_LABEL=1; CONTROL_TEXTBOX=5
            def __init__(self,*args,**kwargs):
                xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, )) # activate the text viewer window
                self.win=xbmcgui.Window(self.WINDOW) # get window
                xbmc.sleep(500) # give window time to initialize
                self.setControls()
            def setControls(self):
                self.win.getControl(self.CONTROL_LABEL).setLabel(heading) # set heading
                try: f=open(anounce); text=f.read()
                except: text=anounce
                self.win.getControl( self.CONTROL_TEXTBOX ).setText (str(text))
                return
        TextBox()
#==========
def DoA(a): xbmc.executebuiltin("Action(%s)" % a) #DoA('Back'); # to move to previous screen.
def eod(): addon.end_of_directory()
#==========OS Type & XBMC Version===========================================================================================
def get_xbmc_os():
	try: xbmc_os = str(os.environ.get('OS'))
	except:
		try: xbmc_os = str(sys.platform)
		except: xbmc_os = "unknown"
	return xbmc_os
XBMCversion={}; XBMCversion['All']=xbmc.getInfoLabel("System.BuildVersion"); XBMCversion['Ver']=XBMCversion['All']; XBMCversion['Release']=''; XBMCversion['Date']=''; 
if ('Git:' in XBMCversion['All']) and ('-' in XBMCversion['All']): XBMCversion['Date']=XBMCversion['All'].split('Git:')[1].split('-')[0]
if ' ' in XBMCversion['Ver']: XBMCversion['Ver']=XBMCversion['Ver'].split(' ')[0]
if '-' in XBMCversion['Ver']: XBMCversion['Release']=XBMCversion['Ver'].split('-')[1]; XBMCversion['Ver']=XBMCversion['Ver'].split('-')[0]
if len(XBMCversion['Ver']) > 1: XBMCversion['two']=str(XBMCversion['Ver'][0])+str(XBMCversion['Ver'][1])
else: XBMCversion['two']='00'
if len(XBMCversion['Ver']) > 3: XBMCversion['three']=str(XBMCversion['Ver'][0])+str(XBMCversion['Ver'][1])+str(XBMCversion['Ver'][3])
else: XBMCversion['three']='000'
sOS=str(get_xbmc_os()); 
print [['Version All',XBMCversion['All']],['Version Number',XBMCversion['Ver']],['Version Release Name',XBMCversion['Release']],['Version Date',XBMCversion['Date']],['OS',sOS]]
#==========END HELP WIZARD==================================================================================================
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]; cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&'); param={}
                for i in range(len(pairsofparams)):
                        splitparams={}; splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
        return param
params=get_params(); url=None; name=None; mode=None; year=None; imdb_id=None; skinset=None; restart=None
try:    fanart=urllib.unquote_plus(params["fanart"])
except: pass
try:    description=urllib.unquote_plus(params["description"])
except: pass
try:    filetype=urllib.unquote_plus(params["filetype"])
except: pass
try:		url=urllib.unquote_plus(params["url"])
except: pass
try:		name=urllib.unquote_plus(params["name"])
except: pass
try:		mode=urllib.unquote_plus(params["mode"])
except: pass
try:		year=urllib.unquote_plus(params["year"])
except: pass
try:		skinset=urllib.unquote_plus(params["skinset"])
except: pass
try:		restart=urllib.unquote_plus(params["restart"])
except: pass
print "Mode: "+str(mode); print "URL: "+str(url); print "Name: "+str(name); print "Year: "+str(year); print "restart: "+str(restart)
if mode==None or url==None or len(url)<1: HELPCATEGORIES()
elif mode=="wizardstatus": print""+url; items = WIZARDSTATUS(url)
elif mode=='helpwizard': HELPWIZARD(name,url,description,filetype,skinset,restart)
xbmcplugin.endOfDirectory(int(sys.argv[1]))        
