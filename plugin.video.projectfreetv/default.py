import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import urlresolver
#from metautils import metahandlers, metacontainers

addon = Addon('plugin.video.projectfreetv', sys.argv)
xaddon = xbmcaddon.Addon(id='plugin.video.projectfreetv')
net = Net()

##### Queries ##########
play = addon.queries.get('play', None)
mode = addon.queries['mode']
section = addon.queries.get('section', None)
url = addon.queries.get('url', None)
video = addon.queries.get('video', None)

print 'Mode: ' + str(mode)
print 'Play: ' + str(play)
print 'URL: ' + str(url)
print 'Section: ' + str(section)
print 'Video: ' + str(video)

################### Global Constants #################################

MainUrl = 'http://www.free-tv-video-online.me/'
MovieUrl = MainUrl + "movies/"
TVUrl = MainUrl + "internet/"
AddonPath = xaddon.getAddonInfo('path')
IconPath = AddonPath + "/icons/"
#pluginhandle = int(sys.argv[1])

######################################################################

###################### Video URL's ###################################

MegaVideoUrl = 'http://www.megavideo.com/?v=%s'
MegaVideoHost = 'megavideo.com'
MegaUploadUrl = 'http://www.megaupload.com/?d=%s'
MegaUploadHost = 'megaupload.com'
NovaMovUrl = 'http://www.novamov.com/video/%s'
NovaMovHost = 'novamov.com'
PutLockerUrl = 'http://www.putlocker.com/file/%s'
PutLockerHost = 'putlocker.com'
SockShareUrl = 'http://www.sockshare.com/file/%s'
SockShareHost = 'sockshare.com'
MovShareUrl = 'http://www.movshare.net/video/%s'
MovShareHost = 'movshare.com'
DivxDenUrl = 'http://www.vidxden.com/embed-%s.html'
DivxDenHost = 'divxden.com'
VideoBBUrl = 'http://www.videobb.com/video/%s'
VideoBBHost = 'videobb.com'
VideoWeedUrl = 'http://www.videoweed.es/file/%s'
VideoWeedHost = 'videoweed.es'
YouTubeUrl = 'http://www.youtube.com/watch?v=%s'
ZShareUrl = 'http://www.zshare.net/video/%s'
ZShareHost = 'zshare'

######################################################################

### Create A-Z Menu
def AZ_Menu(type, url):
     
    addon.add_directory({'mode': type, 
                         'url': url + 'numeric.html', 'letter': '#'},'#',
                         img=IconPath + "numeric.png")
    for l in string.uppercase:
        addon.add_directory({'mode': type, 
                             'url': url + str(l.lower()) + '.html', 'letter': l}, l,
                             img=IconPath + l + ".png")
                             
### Get List of Movies from given URL
def GetMovieList(url):

    html = net.http_GET(url).content
    match = re.compile('<td width="97%" class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a>(.+?)<').findall(html)

    for link, movie, numlinks in match:
       if re.search("../",link) is not None:
          link = link.strip('\n').replace("../","")
          newUrl = MovieUrl + link
       else:
          newUrl = url + "/" + link
       addon.add_video_item(newUrl, {'title': movie}, {'section': 'movies'})
       
#Determine stream type and build URL to pass to resolver
def DetermineHostUrl(host, linkid):
    if host == MegaVideoHost:
       return MegaVideoUrl % linkid
    elif host == MegaUploadHost:
       return MegaUploadUrl % linkid
    elif host == NovaMovHost:
       return NovaMovUrl % linkid
    elif host == PutLockerHost:
       return PutLockerUrl % linkid
    elif host == SockShareHost:
       return SockShareUrl % linkid
    elif host == MovShareHost:
       return MovShareUrl % linkid
    elif host == DivxDenHost:
       return DivxDenUrl % linkid
    elif host == VideoBBHost:
       return VideoBBUrl % linkid
    elif host == VideoWeedHost:
       return VideoWeedUrl % linkid       
    elif host == ZShareHost:
       return ZShareUrl % linkid             
    else:
       return 'nothing'

if play:

    links = {}
    html = net.http_GET(play).content
           
    if section == 'movies':
        
        #Check for trailers
        match = re.compile('<a target="_blank" style="font-size:9pt" class="mnlcategorylist" href=".+?id=(.+?)">(.+?)</a>&nbsp;&nbsp;&nbsp;').findall(html)
        for linkid, name in match:      
            link = YouTubeUrl % linkid
            links[link] = name        
     
    elif section == 'latestmovies':
        #Search within HTML to only get portion of links specific to movie name
        # TO DO - currently does not return enough of the header for the first link
        r = re.search('<div>%s</div>(.+?)(<div>(?!%s)|<p align="center">)' % (video, video), html, re.DOTALL)
        if r:
            html = r.group(0)
        else:
            html = ''
    
    elif section == 'tvshows':
        #Search within HTML to only get portion of links specific to episode requested
        r = re.search('<td class="episode"><a name=".+?"></a><b>%s</b>(.+?)(<a name=|<p align="center">)' % video, html, re.DOTALL)
        if r:
            html = r.group(1)
        else:
            html = ''   
        
    #Now Add video source links
    match = re.compile('''<a onclick=.+? href=".+?id=(.+?)" target=.+?<div>.+?(|part [0-9]* of [0-9]*)</div>.+?<span class='.+?'>(.+?)</span>.+?Host: (.+?)<br/>.+?class="report">.+?([0-9]*[0-9]%) Said Work''',re.DOTALL).findall(html)
    for linkid, name, load, host, working in match:
        link = DetermineHostUrl(host, linkid)
        if name:
           name = name.title()
        else:
           name = 'Full'
        links[link] = name + ' - ' + host + ' - ' + load + ' - ' + working
    
    #Display dialog box of available sources
    #stream_url = urlresolver.choose_source(links)
    
    #Filter out unsupported stream types
    validsources = urlresolver.filter_urls(links.keys())
    
    #Add filtered links to a list to launch a dialog box
    if validsources:
        readable = []
        for x in validsources:
            readable.append(links[x])
        
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose your stream', readable)
        
        #Resolve the final video url for the selected stream
        if index >= 0:
            stream_url = urlresolver.resolve(validsources[index])
        else:
            stream_url = False
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok('No Streams', 'No Playable Streams Found')
        addon.log_error('No Playable Streams Found')
        stream_url = False
    
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)
    
    
if mode == 'main': 
    addon.add_directory({'mode': 'movies', 'section': 'movies'}, 'Movies', img=IconPath + 'Movies.png')
    addon.add_directory({'mode': 'tv', 'section': 'tv'}, 'TV Shows')
    addon.add_directory({'mode': 'resolver_settings'}, 'Resolver Settings', is_folder=False, img=IconPath + 'Resolver_Settings.png')

elif mode == 'movies':
    addon.add_directory({'mode': 'moviesaz', 'section': 'moviesaz'}, 'A-Z', img=IconPath + "AZ.png")
    addon.add_directory({'mode': 'moviesgenre', 'section': 'moviesgenre'}, 'Genre', img=IconPath + 'Genre.png')
    addon.add_directory({'mode': 'movieslatest', 'section': 'movieslatest'}, 'Latest')
    addon.add_directory({'mode': 'moviespopular', 'section': 'moviespopular'}, 'Popular')
    addon.add_directory({'mode': 'moviesyear', 'section': 'moviesyear'}, 'Year')

elif mode == 'moviesaz':
   AZ_Menu('movieslist',MovieUrl + 'browse/')

elif mode == 'moviesgenre':
    url = MovieUrl
    html = net.http_GET(url).content
    match = re.compile('<a class ="genre" href="/(.+?)"><b>(.+?)</b></a><b>').findall(html)

    # Add each link found as a directory item
    for link, genre in match:
       addon.add_directory({'mode': 'movieslist', 'url': MainUrl + link, 'section': 'movies'}, genre)
  
elif mode == 'movieslatest':
    latestlist = []
    url = MovieUrl
    html = net.http_GET(url).content
        
    match = re.compile('''<a onclick='visited.+?' href=".+?" target=.+?<div>(.+?)</div>''',re.DOTALL).findall(html)
    for name in match:
        latestlist.append(name)

    #convert list to a set which removes duplicates, then back to a list
    latestlist = list(set(latestlist))

    for movie in latestlist:
        addon.add_video_item(MovieUrl, {'title': movie}, {'section': 'latestmovies', 'video': movie})

elif mode == 'moviespopular':
    url = MainUrl
    html = net.http_GET(url).content
    match = re.compile('''<tr>.+?<div align="center"><a.+?href="(.+?)">(.+?)</a></div></td>''',re.DOTALL).findall(html)

    # Add each link found as a directory item
    for link, name in match:
       if name != "...more":
          addon.add_video_item(link, {'title': name}, {'section': 'movies'})

elif mode == 'moviesyear':
    url = MovieUrl
    html = net.http_GET(url).content
    match = re.compile('''<td width="97%" nowrap="true" class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a></td>''').findall(html)

    # Add each link found as a directory item
    for link, year in match:
       addon.add_directory({'mode': 'movieslist', 'url': url + urllib.quote(link), 'section': 'movies'}, year) 
    
elif mode == 'movieslist':
   url = addon.queries['url']
   GetMovieList(url)

elif mode == 'movielinks':
   url = addon.queries['url']
   GetMovieLinks(url)      

elif mode == 'tv':
    addon.add_directory({'mode': 'tvaz', 'section': 'tvaz'}, 'A-Z', img=IconPath + "AZ.png")
    #addon.add_directory({'mode': 'tvlatest', 'section': 'tvlatest'}, 'Latest')
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv24hours', 'url': 'index_last.html'}, 'Last 24 Hours')
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv3days', 'url': 'index_last_3_days.html'}, 'Last 3 Days')
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv7days', 'url': 'index_last_7_days.html'}, 'Last 7 Days')
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tvmonth', 'url': 'index_last_30_days.html'}, 'This Month')
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv90days', 'url': 'index_last_365_days.html'}, 'Last 90 Days')
    addon.add_directory({'mode': 'tvpopular', 'section': 'tvpopular'}, 'Popular')

elif mode == 'tvaz':
    AZ_Menu('tvseries-az',TVUrl)

elif mode == 'tvseries-az':
    url = TVUrl
    letter = addon.queries['letter']
    
    html = net.http_GET(url).content
    r = re.search('<a name="%s">(.+?)(<a name=|</table>)' % letter, html, re.DOTALL)
    
    if r:
        match = re.compile('class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b>').findall(r.group(1))
        for link, name in match:
            addon.add_directory({'mode': 'tvseasons', 'url': TVUrl + link, 'section': 'tvshows'}, name)  

elif mode == 'tvlastadded':
    url = TVUrl + addon.queries['url']
    html = net.http_GET(url).content
    match = re.compile('class="mnlcategorylist"><a href="(.+?)#.+?"><b>(.+?)<').findall(html)
    for link, name in match:
        addon.add_directory({'mode': 'tvepisodes', 'url': TVUrl + link, 'section': 'tvshows'}, name)  

elif mode == 'tvpopular':
    url = MainUrl
    html = net.http_GET(url).content
    match = re.compile('href="(.+?)">(.+?)</a></div></td>\s\s.+?</tr>').findall(html)
    for link, name in match:
        if name != "...more":
            addon.add_directory({'mode': 'tvseasons', 'url': link, 'section': 'tvshows'}, name)
    
elif mode == 'tvseries':
    url = TVUrl  
    html = net.http_GET(url).content
    match = re.compile('class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a> </td>').findall(html)
    for link, name in match:
        addon.add_directory({'mode': 'tvseasons', 'url': TVUrl + link, 'section': 'tvshows'}, name)       

elif mode == 'tvseasons':
    url = addon.queries['url']
    html = net.http_GET(url).content
    match = re.compile('class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a>(.+?)</td>').findall(html)
    for link, season, episodes in match:
        addon.add_directory({'mode': 'tvepisodes', 'url': url + '/' + link, 'section': 'tvshows'}, season + episodes)

elif mode == 'tvepisodes':
    url = addon.queries['url']
    html = net.http_GET(url).content
    match = re.compile('<td class="episode">.+?b>(.+?)</b>').findall(html)
    for name in match:
        addon.add_video_item(url,{'title':name},{'section': 'tvshows', 'video': name})

elif mode == 'resolver_settings':
    urlresolver.display_settings()

if not play:
    addon.end_of_directory()