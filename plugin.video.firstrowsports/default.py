import xbmc, xbmcgui, urllib2, urllib, re, xbmcplugin, random


####### Global Constants
MainUrl = 'http://www.firstrowsports.eu'       
pluginhandle = int(sys.argv[1])
_Unknown = "UNKNOWN"

###########################################################
####### Some stream types need hardcoded values

# Seeon.tv streams
SeeonStreamType = "directembed"
SeeonRTMP = "rtmp://live#.seeon.tv/edge"
SeeonSWF = "http://www.seeon.tv/jwplayer/player.swf"

# Zonein streams
ZoneinStreamType = "zonein"
ZoneRTMP = "rtmp://68.68.31.98:1935/"
ZoneSWF = "http://cdncdn.zonein1.com/kikikili.swf"
ZonePlayPath = "zonein"

# Ustream.tv streams
UstreamType = "ustream"
UstreamSWF = "http://cdn1.ustream.tv/swf/4/viewer.rsl.606.swf"
UstreamAMF = "http://cgw.ustream.tv/Viewer/getStream/1/#.amf"

# Jimey.tv streams
JimeyStreamType = "jimey"
JimeyRTMP = "rtmpe://174.37.65.216/edge"
JimeySWF = "http://jimey.tv/player/fresh.swf"

# CastAmp streams
CastAmpStreamType = "castamp"
CastAmpRTMP = "rtmp://68.68.29.113/live"
CastAmpSWF = "http://live.castamp.com/player.swf"
CastAmpPageURL = "http://castamp.com/embed.php?c=#&vwidth=640&vheight=440&domain=www.firstrowsports.eu"

# Wii-Cast streams
WiiCastStreamType = "wii-cast"
WiiCastRTMP = ""

# MIPS.tv streams
MipsStreamType="mips"
MipsSWF="http://www.mips.tv/player/eplayer.swf"
MipsRTMP="rtmp://50.23.239.11/live"
MipsPlayPath="gfhffd?id=#"



###########################################################


### Standard function - add a directory
def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok

### Standard function - retrieve the html for a given url    
def getURL(url):
    try:
        txdata = None
        txheaders = {'Referer': MainUrl,
            'X-Forwarded-For': '12.13.14.15',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',  
        }
        req = urllib2.Request(url, txdata, txheaders)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        error = 'Error code: '+ str(e.code)
        xbmcgui.Dialog().ok(error,error)
        print 'Error code: ', e.code
        return False
    else:
        return link

### Create the main page listing
def MainPage():
    
    # Add main sport directories manually - scripting was a pain in the ass
    
    addDir("American Football",MainUrl + "/sport/american-football.html",1,MainUrl+"/images/sports/3.png")
    addDir("Aussie Rules",MainUrl + "/sport/aussie-rules.html",1,MainUrl+"/images/sports/17.png")    
    addDir("Baseball",MainUrl + "/sport/baseball.html",1,MainUrl+"/images/sports/5.png")
    addDir("Basketball",MainUrl + "/sport/basketball.html",1,MainUrl+"/images/sports/2.png")
    addDir("Boxing / WWE / UFC",MainUrl + "/sport/boxing-wwe-ufc.html",1,MainUrl+"/images/sports/7.png")
    addDir("Darts",MainUrl + "/sport/darts.html",1,MainUrl+"/images/sports/11.png")    
    addDir("Football",MainUrl + "/sport/football.html",1,MainUrl+"/images/sports/1.png")
    addDir("Golf",MainUrl + "/sport/golf.html",1,MainUrl+"/images/sports/13.png")
    addDir("Handball",MainUrl + "/sport/handball.html",1,MainUrl+"/images/sports/18.png")
    addDir("Hockey",MainUrl + "/sport/ice-hockey.html",1,MainUrl+"/images/sports/4.png")
    addDir("Motosport",MainUrl + "/sport/motosport.html",1,MainUrl+"/images/sports/10.png")
    addDir("Other",MainUrl + "/sport/others.html",1,MainUrl+"/images/sports/14.png")    
    addDir("Rugby",MainUrl + "/sport/rugby.html",1,MainUrl+"/images/sports/8.png")    
    addDir("Snooker",MainUrl + "/sport/snooker.html",1,MainUrl+"/images/sports/12.png")        
    addDir("Tennis",MainUrl + "/sport/tennis.html",1,MainUrl+"/images/sports/6.png")
    addDir("TV",MainUrl + "/sport/tv-box.html",1,MainUrl+"/images/sports/16.png")
    xbmcplugin.endOfDirectory(pluginhandle)

### Scrape for the list of channels for a given sprot
def Channels(url):
    xbmcplugin.setContent(pluginhandle, 'Channels')
    mode=2
    html=getURL(url)

    # First find URL's with time as 00:00 since HTML is formated slightly different
    match = re.compile(
       """<a class="accordlink"  href='(.+?)' target="_blank">
                    <img class="chimg" alt="(.+?)" src="(.+?)"/>
                    <span>
                        &nbsp;
                                00:00                    </span>"""
       ).findall(html)
    for u,name,icon in match:
       icon=MainUrl + icon
       name="00:00 - " + name
       addDir(name,MainUrl+u,2,icon)

    # Now find rest of URL's that have a time next to channel
    match = re.compile(
       """<a class="accordlink"  href='(.+?)' target="_blank">
                    <img class="chimg" alt="(.+?)" src="(.+?)"/>
                    <span>
                        &nbsp;
                                <span class="matchtime">(.+?)</span>"""
       ).findall(html)
    
    # Add each link found as a directory item
    for u,name,icon,time in match:
       icon=MainUrl + icon
       name=time + " - " + name
       addDir(name,MainUrl+u,2,icon)   

    xbmcplugin.endOfDirectory(pluginhandle)

### Find all the available stream links for given channel
def Links():
    xbmcplugin.setContent(pluginhandle, 'Links')
    mode=3
    html=getURL(url) 
    match = re.compile(
       """<a style='font-size:12pt;color:limef;'  title='(.+?)'href='(.+?)'>.+?</a>"""
       ).findall(html)
    for name,u in match:
       addDir(name,MainUrl+u,3,"")       
    xbmcplugin.endOfDirectory(pluginhandle)    

### Determine which type of stream is being used and handle appropriately
def DetectStream(url):
   
    ### Search for keywords in the url to determine it's source  
    if re.search(ZoneinStreamType,url) is not None:
        return ZoneinStreamType
    elif re.search(SeeonStreamType,url) is not None:
        return SeeonStreamType
    #elif re.search(UstreamType,url) is not None:
    #    return UstreamType
    elif re.search(JimeyStreamType,url) is not None:
        return JimeyStreamType
    elif re.search(WiiCastStreamType,url) is not None:
        return WiiCastStreamType
    else:
        return _Unknown


### Create the final RTMP url
def GetRTMP(streamType, url):
    
    html=getURL(url)
    rtmp=""
    
    # Zonein stream
    if streamType==ZoneinStreamType:      
        url=re.compile('src="(.+?)"').findall(html)[0]
        
        html=getURL(url)
        swfLink=re.compile('<param name="movie" value="(.+?)"/>').findall(html)[0]
        channelID=re.compile('<param name="FlashVars" VALUE=".+?&cid=(.+?)&.+?">').findall(html)[0]
        rtmp=ZoneRTMP + channelID + "?doPlay=a/ playpath=" + ZonePlayPath + " swfurl=" + swfLink + " swfvfy=true"
    
    # Seeon.tv stream
    elif streamType==SeeonStreamType:
        url=re.compile("src='(.+?)'").findall(html)[0]
        
        html=getURL(url)
        rtmp=SeeonRTMP.strip('\n').replace("#",str(random.randint(1,28)))        
        swfLink=re.compile('<param name="movie" value="(.+?)">').findall(html)[0]
        channelID=re.compile('<param name="flashvars" .+?&file=(.+?).flv.+?>').findall(html)[0]
        rtmp=rtmp + " playpath=" + channelID + " swfurl=" + swfLink + " pageurl=" + url + " swfvfy=true"
    
    # Jimey.tv stream
    elif streamType==JimeyStreamType:
       channelID=re.compile("<param name='flashvars' value='(.+?)&").findall(html)[0]
       rtmp=JimeyRTMP + " playpath=" + channelID + " swfurl=" + JimeySWF + " pageurl=" + url + " swfvfy=true"
    
    # Wii-Cast stream
    elif streamType==WiiCastStreamType:
        url=re.compile("<iframe src='(.+?)'").findall(html)[0] 
        
        html=getURL(url)
        rtmpurl="rtmp://live.wii-cast.tv/redirect"
        print rtmp
        swf=re.compile("so.addVariable('plugins','(.+?)');").findall(html)[0]
        print swf
        playpath=re.compile("so.addVariable('file', '(.+?)');").findall(html)[0]
        print playpath
        rtmp=rtmpurl + " playpath=" + playpath + " swfurl=" + swf + " pageurl=" + url + " swfvfy=true"        
    
    # Ustream.tv stream
    elif streamType==Ustream:
       channelID=re.compile('ustream.vars.channelId=(.+?);').findall(html)[0]
       if len(channelID) == 0:
           dialog = xbmcgui.Dialog()
           ok = dialog.ok('USTREAM.tv', 'Error: Not a live feed.')
           return
       url=UstreamAMF.strip('\n').replace("#",str(channelID))
       
       html=getURL(url)
       
       playPath=re.compile('streamName\W\W\W(.+?)\x00', re.DOTALL).findall(html)[0]
       tcUrl=re.compile('cdnUrl\W\W\S(.+?)\x00', re.DOTALL).findall(html)[0]
       tcUrl2=re.compile('fmsUrl\W\W\S(.+?)\x00', re.DOTALL).findall(html)[0]
       print tcUrl
       print tcUrl2
       print playPath

       if len(tcUrl) == 0:
           if len(tcUrl2) == 0:
               dialog = xbmcgui.Dialog()
               ok = dialog.ok('USTREAM.tv', 'Error: Not a live feed.')
               return
           else:
               new = tcUrl2.replace('/ustreamVideo',':1935/ustreamVideo')
               rtmp_url = new + '/'
               #dialog = xbmcgui.Dialog()
               #ok = dialog.ok('Debug', rtmp_url+'\nplayPath: '+playPath)
       else:
           rtmp_url = tcUrl
           #dialog = xbmcgui.Dialog()
           #ok = dialog.ok('Debug', rtmp_url+'\n'+playPath)
       
       thumb = xbmc.getInfoImage( "ListItem.Thumb" )
       rtmp = tcUrl + " playpath=" + playPath + " swfurl=" + UstreamSWF + " swfvfy=true"  
        
        #cid=re.compile('<param name="flashvars" value=".+?&amp;channelid=(.+?).+?/>').findall(html)[0]
        #playPath = UstreamPlayPath.strip('\n').replace("#",str(cid))
        #rtmp=UstreamRTMP + " playpath=" + playPath + " swfurl=" + UstreamSWF + " swfvfy=true"    
    
    return rtmp

### Find the correct stream url
def FindStreamUrl(url):
    html = getURL(url)
    url = re.compile(
       """</div>
  

                                    <.+? src=(.+?)>"""
       ).findall(html)[0]

    # Clean up the url, strip double and single quotes - dirty way of doing it
    url = url.strip('\n').replace("\'","")
    url = url.strip('\n').replace('\"','')
    
    # Find the first position of a blank character and take everything before it
    # Sometimes I grab too much in the link due to shitty html on the site
    blankPos = url.find(" ")
    url = url[:blankPos]
    return url

### Play the final video URL
def PlayVideo(name,url):
  
    streamUrl=FindStreamUrl(url)
    streamType=DetectStream(streamUrl)
    
    # Play stream if it is supported
    if streamType == _Unknown:
        dialog = xbmcgui.Dialog()
        dialog.ok('Unsupported', 'The stream type is currently not supported')
        return
    else:
        rtmpUrl=GetRTMP(streamType,streamUrl)
    
    xbmc.Player( xbmc.PLAYER_CORE_DVDPLAYER ).play(rtmpUrl,name)


    #item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=rtmpUrl)
    #item.setInfo( type="Video", infoLabels={ "Title": name,
    #                                         "Plot":plot,
    #                                         "premiered":premiered,
    #                                         "Season":int(season),
    #                                         "Episode":int(episode),
    #                                         "TVShowTitle":TVShowTitle})
    #xbmcplugin.setResolvedUrl(pluginhandle, True, item)

### Grab parameters passed in from the URL
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param


### Main        
params=get_params()    
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
if mode==None or url==None or len(url)<1:
    MainPage()
elif mode==1:
    Channels(url)
elif mode==2:
    Links()
elif mode==3:
    PlayVideo(name,url)