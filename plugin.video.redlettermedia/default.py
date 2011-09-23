import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from elementtree.ElementTree import parse

addon = Addon('plugin.video.redlettermedia', sys.argv)
xaddon = xbmcaddon.Addon(id='plugin.video.redlettermedia')
net = Net()

##### Queries ##########
play = addon.queries.get('play', None)
mode = addon.queries['mode']
url = addon.queries.get('url', None)

print 'Mode: ' + str(mode)
print 'Play: ' + str(play)
print 'URL: ' + str(url)


################### Global Constants #################################

MainUrl = 'http://www.redlettermedia.com/'
APIPath = 'http://blip.tv/players/episode/%s?skin=api'
AddonPath = xaddon.getAddonInfo('path')
IconPath = AddonPath + "/icons/"

######################################################################


# Temporary function to grab html even when encountering an error
# Some pages on the site return 404 even though the html is there
def get_http_error(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', net._user_agent)
    try:
        response = urllib2.urlopen(req)
        html = response.read()
    except urllib2.HTTPError, error:
        html = error.read()
    
    return html
                           
if play:

    html = get_http_error(url)
      
    #First check if there are multiple video parts on the page
    parts = re.compile('>([PARTart]* [1-9]):<br />').findall(html)
    
    #Page has multiple video parts
    if len(parts) > 1:
        partlist = []
        for part in parts:
            partlist.append(part)    
        
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose the video', partlist)
        
        #Take only selected part portion of the html
        if index >= 0:          
            html = re.search('>%s:<br />(.+?)</p>' % partlist[index],html,re.DOTALL).group(1)
        else:
            html = False
    
    if html:                 
    
        #Check for youtube video first
        youtube = re.search('src="(http://www.youtube.com/[v|embed]*/[0-9A-Za-z_\-]+).+?"',html)      
        
        if youtube:
            stream_url = urlresolver.HostedMediaFile(url=youtube.group(1)).resolve()
        else:
        
            video = re.search('<embed.+?src="http://[a.]{0,2}blip.tv/[^#/]*[#/]{1}([^"]*)"',html, re.DOTALL).group(1)
            api_url = APIPath % video
           
            links = []
            roles = []
                
            tree = parse(urllib.urlopen(api_url))
            for media in tree.getiterator('media'):
                for link in media.getiterator('link'):
                    links.append(link.get('href'))
                    roles.append(media.findtext('role'))
                
            dialog = xbmcgui.Dialog()
            index = dialog.select('Choose a video source', roles)          
            if index >= 0:
                stream_url = links[index]
            else:
                stream_url = False
    else:
        stream_url = False
    
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)  
       
    
if mode == 'main': 
    addon.add_directory({'mode': 'plinkett', 'url': MainUrl}, 'Plinkett Reviews', img=IconPath + 'plinkett.jpg')
    addon.add_directory({'mode': 'halfbag', 'url': MainUrl + 'half-in-the-bag/'}, 'Half in the Bag', img=IconPath + 'halfbag.jpg')
    addon.add_directory({'mode': 'featurefilms', 'url': MainUrl + 'films/'}, 'Feature Films')    
    addon.add_directory({'mode': 'shortfilms', 'url': MainUrl + 'shorts/'}, 'Short Films')        

elif mode == 'plinkett':
    url = addon.queries['url']
    html = get_http_error(url)
    
    r = re.search('Plinkett Reviews</a>.+?<ul class="sub-menu">(.+?)</ul>', html, re.DOTALL)
    if r:
        match = re.compile('<li.+?><a href="(.+?)">(.+?)</a></li>').findall(r.group(1))
    else:
        match = None

    # Add each link found as a directory item
    for link, name in match:
       addon.add_directory({'mode': 'plinkettreviews', 'url': link}, name)

elif mode == 'plinkettreviews':
    url = addon.queries['url']
    html = get_http_error(url)

    match = re.compile('<td.+?<a href="(.+?)".+?img src="(.+?)"').findall(html)
    for link, thumb in match:
        name = re.search("[http://]*[a-z./-]*/(.+?)/",'/' + link).group(1).replace('-',' ').replace('/',' ').title()
        
        if re.search('http',link):
            newlink = link
        else:
            newlink = url + link
        addon.add_video_item({'url': newlink},{'title':name},img=thumb)

elif mode == 'halfbag':
    url = addon.queries['url']
    html = get_http_error(url)

    match = re.compile('<td width=270><a href="(.+?)" ><img src="(.+?)"></a></td>').findall(html)
    
    episodenum = 1
    for link, thumb in match:
        addon.add_video_item({'url': link},{'title':'Episode ' + str(episodenum)},img=thumb)
        episodenum += 1
    
elif mode == 'featurefilms':
    url = addon.queries['url']
    html = get_http_error(url)
    
    r = re.search('Feature Films</a>.+?<ul class="sub-menu">(.+?)</ul>', html, re.DOTALL)
    if r:
        match = re.compile('<li.+?<a href="(.+?)">(.+?)</a></li>').findall(r.group(1))
    else:
        match = None
           
    thumb = re.compile('<td><a href=".+?"><img src="(.+?)" ></a></td>').findall(html)

    #Add each link found as a directory item
    i = 0
    for link, name in match:
        addon.add_directory({'mode': 'film', 'url': link}, name, img=thumb[i])
        i += 1

elif mode == 'film':
    url = addon.queries['url']
    html = get_http_error(url)

    match = re.compile('<td><a href="(.+?)".*><img src="(.+?)".*>').findall(html)
    for link, thumb in match:
        link = url + link.replace(url,'')
        name = link.replace(url,'').replace('-',' ').replace('/',' ').title()
        addon.add_video_item({'url': link},{'title': name}, img=thumb)
   
elif mode == 'shortfilms':
    url = addon.queries['url']
    html = get_http_error(url)

    r = re.search('''Short Films</a>.+?<ul class="sub-menu">(.+?)</ul>''', html, re.DOTALL)
    if r:
        match = re.compile('<a href="(.+?)">(.+?)</a></li>').findall(r.group(1))
            
    # Add each link found as a directory item
    for link, name in match:
       addon.add_directory({'mode': 'shortseason', 'url': link}, name)  

elif mode == 'shortseason':
    url = addon.queries['url']
    html = get_http_error(url)
    
    #Check if there are any videos embedded on the page
    if re.search('[<embed src=|youtube.com/embed]',html):
        addon.add_video_item({'url': url},{'title': 'Video'})
    else:
        match = re.compile('<td><a href="(.+?)".*><img src="(.+?)".*></a></td>').findall(html)
        
        # Add each link found as a video item
        for link, thumb in match:
            name = link.replace(url,'').replace('-',' ').replace('/',' ').title()
            link = url + link.replace(url,'')
            addon.add_video_item({'url': link},{'title': name},img=thumb)

if not play:
    addon.end_of_directory()