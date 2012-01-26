import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import urlresolver

addon = Addon('plugin.video.projectfreetv', sys.argv)
xaddon = xbmcaddon.Addon(id='plugin.video.projectfreetv')
net = Net()

##### Queries ##########
play = addon.queries.get('play', None)
mode = addon.queries['mode']
section = addon.queries.get('section', None)
url = addon.queries.get('url', None)
video = addon.queries.get('video', None)
imdb_id = addon.queries.get('imdb_id', None)
season = addon.queries.get('season', None)

print 'Mode: ' + str(mode)
print 'Play: ' + str(play)
print 'URL: ' + str(url)
print 'Section: ' + str(section)
print 'Video: ' + str(video)
print 'IMDB: ' + str(imdb_id)
print 'Season: ' + str(season)

################### Global Constants #################################

MainUrl = 'http://www.free-tv-video-online.me/'
MovieUrl = MainUrl + "movies/"
TVUrl = MainUrl + "internet/"
AddonPath = xaddon.getAddonInfo('path')
IconPath = AddonPath + "/icons/"

######################################################################

# Create A-Z Menu
def AZ_Menu(type, url):
     
    addon.add_directory({'mode': type, 
                         'url': url + 'numeric.html', 'letter': '#'},{'title': '#'},
                         img=IconPath + "numeric.png")
    for l in string.uppercase:
        addon.add_directory({'mode': type, 
                             'url': url + str(l.lower()) + '.html', 'letter': l}, {'title': l},
                             img=IconPath + l + ".png")

                            
# Get List of Movies from given URL
def GetMovieList(url):

    html = net.http_GET(url).content
    match = re.compile('<td width="97%" class="mnlcategorylist"><a href="(.+?)"><b>(.+?) [(]*([0-9]{4})[)]*</b></a>(.+?)<').findall(html)

    for link, movie, year, numlinks in match:
       if re.search("../",link) is not None:
          link = link.strip('\n').replace("../","")
          newUrl = MovieUrl + link
       else:
          newUrl = url + "/" + link
       addon.add_video_item({'url': newUrl, 'section': 'movies'}, {'title': movie}, total_items=len(match))
       
if play:

    sources = []
    html = net.http_GET(url).content
           
    if section == 'movies':
        
        #Check for trailers
        match = re.compile('<a target="_blank" style="font-size:9pt" class="mnlcategorylist" href=".+?id=(.+?)">(.+?)</a>&nbsp;&nbsp;&nbsp;').findall(html)
        for linkid, name in match:      
            media = urlresolver.HostedMediaFile(host='youtube', media_id=linkid, title=name)
            sources.append(media)        
     
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
        if name:
           name = name.title()
        else:
           name = 'Full'
        media = urlresolver.HostedMediaFile(host=host, media_id=linkid, title=name + ' - ' + host + ' - ' + load + ' - ' + working)
        sources.append(media)
    
    source = urlresolver.choose_source(sources)
    if source:
        stream_url = source.resolve()
    else:
        stream_url = False
      
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)
       
if mode == 'main': 
    addon.add_directory({'mode': 'movies', 'section': 'movies'}, {'title':  'Movies'}, img=IconPath + 'Movies.png')
    addon.add_directory({'mode': 'tv', 'section': 'tv'}, {'title': 'TV Shows'})
    addon.add_directory({'mode': 'resolver_settings'}, {'title':  'Resolver Settings'}, is_folder=False, img=IconPath + 'Resolver_Settings.png')

elif mode == 'movies':
    addon.add_directory({'mode': 'moviesaz', 'section': 'moviesaz'}, {'title': 'A-Z'}, img=IconPath + "AZ.png")
    addon.add_directory({'mode': 'moviesgenre', 'section': 'moviesgenre'}, {'title': 'Genre'}, img=IconPath + 'Genre.png')
    addon.add_directory({'mode': 'movieslatest', 'section': 'movieslatest'}, {'title': 'Latest'})
    addon.add_directory({'mode': 'moviespopular', 'section': 'moviespopular'}, {'title': 'Popular'})
    addon.add_directory({'mode': 'moviesyear', 'section': 'moviesyear'}, {'title': 'Year'})

elif mode == 'moviesaz':
   AZ_Menu('movieslist',MovieUrl + 'browse/')

elif mode == 'moviesgenre':
    url = MovieUrl
    html = net.http_GET(url).content
    match = re.compile('<a class ="genre" href="/(.+?)"><b>(.+?)</b></a><b>').findall(html)

    # Add each link found as a directory item
    for link, genre in match:
       addon.add_directory({'mode': 'movieslist', 'url': MainUrl + link, 'section': 'movies'}, {'title': genre})
  
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
        addon.add_video_item({'url': MovieUrl, 'section': 'latestmovies', 'video': movie}, {'title': movie})

elif mode == 'moviespopular':
    url = MainUrl
    html = net.http_GET(url).content
    match = re.compile('''<td align="center"><a href="(.+?)">(.+?)</a></td>''',re.DOTALL).findall(html)

    # Add each link found as a directory item
    for link, name in match:
       is_movie = re.search('/movies/', link)
       if name != "...more" and is_movie:
          addon.add_video_item({'url': link, 'section': 'movies'}, {'title': name}, total_items=len(match))

elif mode == 'moviesyear':
    url = MovieUrl
    html = net.http_GET(url).content
    match = re.compile('''<td width="97%" nowrap="true" class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a></td>''').findall(html)

    # Add each link found as a directory item
    for link, year in match:
       addon.add_directory({'mode': 'movieslist', 'url': url + urllib.quote(link), 'section': 'movies'}, {'title': year})
    
elif mode == 'movieslist':
   GetMovieList(url)

elif mode == 'movielinks':
   GetMovieLinks(url)      

elif mode == 'tv':
    addon.add_directory({'mode': 'tvaz', 'section': 'tvaz'}, {'title': 'A-Z'}, img=IconPath + "AZ.png")
    #addon.add_directory({'mode': 'tvlatest', 'section': 'tvlatest'}, 'Latest')
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv24hours', 'url': TVUrl + 'index_last.html'}, {'title': 'Last 24 Hours'})
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv3days', 'url': TVUrl + 'index_last_3_days.html'}, {'title': 'Last 3 Days'})
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv7days', 'url': TVUrl + 'index_last_7_days.html'}, {'title': 'Last 7 Days'})
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tvmonth', 'url': TVUrl + 'index_last_30_days.html'}, {'title': 'This Month'})
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv90days', 'url': TVUrl + 'index_last_365_days.html'}, {'title': 'Last 90 Days'})
    addon.add_directory({'mode': 'tvpopular', 'section': 'tvpopular'}, {'title': 'Popular'})

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
            addon.add_directory({'mode': 'tvseasons', 'url': TVUrl + link, 'section': 'tvshows'}, {'title': name}, total_items=len(match))  

elif mode == 'tvlastadded':
    html = net.http_GET(url).content
    match = re.compile('class="mnlcategorylist"><a href="(.+?)#.+?"><b>(.+?)<').findall(html)
    for link, name in match:
        addon.add_directory({'mode': 'tvepisodes', 'url': TVUrl + link, 'section': 'tvshows'}, {'title': name}, total_items=len(match))  

elif mode == 'tvpopular':
    url = MainUrl
    html = net.http_GET(url).content
    match = re.compile('<td align="center"><a href="(.+?)">(.+?)</a></td>').findall(html)
    for link, name in match:
        is_tv = re.search('/internet/', link)
        if name != "...more" and is_tv:
            addon.add_directory({'mode': 'tvseasons', 'url': link, 'section': 'tvshows'}, {'title': name}, total_items=len(match))       

elif mode == 'tvseasons':
    html = net.http_GET(url).content
    match = re.compile('class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a>(.+?)</td>').findall(html)
    seasons = re.compile('class="mnlcategorylist"><a href=".+?"><b>Season ([0-9]+)</b></a>.+?</td>').findall(html)
    num = 0
    for link, season, episodes in match:
        addon.add_directory({'mode': 'tvepisodes', 'url': url + '/' + link, 'section': 'tvshows', 'imdb_id': imdb_id, 'season': num + 1}, {'title': season + episodes}, total_items=len(match))
        num += 1

elif mode == 'tvepisodes':
    html = net.http_GET(url).content.encode('utf-8')
    match = re.compile('<td class="episode">.+?b>(.+?)</b>').findall(html)
    for name in match:
        episode_num = re.search('([0-9]{0,2}).', name).group(1)
        addon.add_video_item({'url': url, 'section': 'tvshows', 'video': name}, {'title': episode_num}, total_items=len(match))

elif mode == 'resolver_settings':
    urlresolver.display_settings()

if not play:
    addon.end_of_directory()