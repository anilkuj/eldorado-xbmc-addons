import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import urlresolver

addon = Addon('plugin.video.quicksilverscreen', sys.argv)
xaddon = xbmcaddon.Addon(id='plugin.video.quicksilverscreen')
net = Net()

##### Queries ##########
play = addon.queries.get('play', None)
mode = addon.queries['mode']
section = addon.queries.get('section', None)
url = addon.queries.get('url', None)

print 'Mode: ' + str(mode)
print 'Play: ' + str(play)
print 'URL: ' + str(url)
print 'Section: ' + str(section)

################### Global Constants #################################

main_url = 'http://www.quicksilverscreen.ch/'
episode_url = main_url + 'episodes.php?e=%s&c=%s'
addon_path = xaddon.getAddonInfo('path')
icon_path = addon_path + "/icons/"

######################################################################


### Create A-Z Menu
def AZ_Menu(type, url):
     
    addon.add_directory({'mode': type,
                         'url': main_url + url % 'etc',
                         'section': section,
                         'letter': 'etc'},'#',
                         img='')
    for l in string.uppercase:
        addon.add_directory({'mode': type,
                             'url': main_url + url % l,
                             'section': section,
                             'letter': l}, l,
                             img='')


def get_video_quick_list(url):
    html = net.http_GET(url).content
    
    match = re.compile('<div id="avatar">.+?<a href="(.+?)" >.+?<img class="browse_avatar" src="(.+?)" alt=".+?" title="(.+?)" />',re.DOTALL).findall(html)
    total = len(match)
    for link, thumb, title in match:
        if section == 'tv':
            addon.add_directory({'mode': 'tvseasons', 'url': link, 'section': 'tv'}, title, img=main_url + thumb, total_items=total)
        else:       
            addon.add_video_item({'url': link}, {'title': title}, img=main_url + thumb, total_items=total)                                          
                             
def get_video_list(url):

    html = net.http_GET(url).content
    match = re.compile('<td class="bullet.+?">.+?<a href="(.+?)" title=".+?" >(.+?)</a>',re.DOTALL).findall(html)
    total = len(match)
    for link, title in match:
        if section == 'tv':
            addon.add_directory({'mode': 'tvseasons', 'url': link, 'section': 'tv'}, title, img='', total_items=total)
        else:
            addon.add_video_item({'url': link}, {'title': title.strip()}, img='', total_items=total)     
       
if play:

    links = []
    hosts = []
    hostses = []
    html = net.http_GET(url).content

    match = re.compile('<td class="link_type">.+?<a target="_blank" href=".+?">(.+?)</a>.+?<td class="submitted_text"><a target="_blank" href="(.+?)">.+? Watch online on: <b>(.+?)</b></a></td>',re.DOTALL).findall(html)
    for video_type, link, host in match:
        links.append(link)
        hosts.append(host + ' - ' + video_type)

    #Display dialog box of sources
    dialog = xbmcgui.Dialog()
    index = dialog.select('Choose a video source', hosts)
    if index >= 0:
        url = links[index]
        
        html = net.http_GET(url).content
        media_id = re.search('<input type="hidden" value="(.+?)" id="vid" />', html, re.DOTALL).group(1)
        host = re.search('<input type="hidden" value="(.+?)" id="vhost" />', html, re.DOTALL).group(1)
       
        stream_url = urlresolver.HostedMediaFile(host=host, media_id=media_id).resolve()     
    else:
        stream_url = False
  
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)
    
    
if mode == 'main': 
    addon.add_directory({'mode': 'movies', 'section': 'movies'}, 'Movies', img=icon_path + 'Movies.jpg')
    addon.add_directory({'mode': 'tv', 'section': 'tv'}, 'TV Shows', img='')
    addon.add_directory({'mode': 'cartoons', 'section': 'cartoons', 'url': main_url + 'videos?g=4&mt=1'}, 'Cartoons', img='')
    addon.add_directory({'mode': 'documentary', 'section': 'documentary', 'url': main_url + 'videos?g=5&mt=1'}, 'Documentaries', img='')
    addon.add_directory({'mode': 'musicvid', 'section': 'musicvid', 'url': main_url + 'videos?g=17&mt=1'}, 'Music Videos', img='')
    addon.add_directory({'mode': 'resolver_settings'}, 'Resolver Settings', is_folder=False, img='')

elif mode == 'movies':
    addon.add_directory({'mode': 'moviestop', 'url': main_url, 'section': 'movie'}, 'Top Movies', img='')
    addon.add_directory({'mode': 'moviesaz', 'section': 'movie'}, 'A-Z', img='')
    addon.add_directory({'mode': 'moviesgenre', 'url': main_url + 'videos?mt=1', 'section': 'movie'}, 'Genre', img='')
    addon.add_directory({'mode': 'moviesrecent', 'url': main_url + 'videos?a=dr&mt=1', 'section': 'movie'}, 'Recently Released', img='')
    addon.add_directory({'mode': 'moviesadded', 'url': main_url + 'videos?a=da&mt=1', 'section': 'movie'}, 'Recently Added', img='')
    addon.add_directory({'mode': 'moviespopular', 'url': main_url + 'videos?a=m&mt=1', 'section': 'movie'}, 'Most Popular', img='')
    addon.add_directory({'mode': 'moviesyear', 'url': main_url + 'videos?mt=1', 'section': 'movie'}, 'Year', img='')

elif mode == 'moviestop':
    html = net.http_GET(url).content
    r = re.search('<p>Top Movies</p>(.+?)</div>',html,re.DOTALL).group(1)
    if r:
        match = re.compile('<a id="big_pic[0-9]" href="(.+?)"><img src=".+?" alt=".+?" title="(.+?)"/></a>').findall(r)
        for link, title in match:
            addon.add_video_item({'url': link}, {'title': title}, img='')
            
elif mode == 'moviesaz':
   AZ_Menu('movieslist', 'videos?mt=1&l=%s')

elif mode == 'moviesgenre':
    html = net.http_GET(url).content
    
    #Grab only portion of html that has genre
    r = re.search('Choose a Genre</option>(.+?)</select>',html, re.DOTALL) 
    
    if r:
        match = re.compile('<option label=".+?" value="(.+?)">(.+?)</option>').findall(r.group(1))

    # Add each link found as a directory item
    for link, genre in match:
       if genre != 'Browse by A to Z':
           addon.add_directory({'mode': 'movieslist', 'url': main_url + link[1:].replace('&amp;','&'), 'section': 'movies'}, genre)
  
elif mode == 'moviesrecent':
    get_video_quick_list(url)

elif mode == 'moviesadded':
    get_video_quick_list(url)

elif mode == 'moviespopular':
    get_video_quick_list(url)

elif mode == 'moviesyear':
    html = net.http_GET(url).content
    
    #Grab only portion of html that has genre
    r = re.search('Choose a Year</option>(.+?)</select>',html, re.DOTALL) 
    
    if r:
        match = re.compile('<option label=".+?" value="(.+?)">(.+?)</option>').findall(r.group(1))

    # Add each link found as a directory item
    for link, year in match:
        addon.add_directory({'mode': 'movieslist', 'url': main_url + link[1:].replace('&amp;','&'), 'section': 'movies'}, year)
    
elif mode == 'movieslist':
    get_video_list(url)   

elif mode == 'cartoons':
    get_video_list(url)

elif mode == 'documentary':
    get_video_list(url)
   
elif mode == 'musicvid':
    get_video_list(url)
   
elif mode == 'tv':
    addon.add_directory({'mode': 'tvtop', 'url': main_url, 'section': 'tv'}, 'Top TV Shows')
    addon.add_directory({'mode': 'tvaz', 'section': 'tv'}, 'A-Z', img='')
    addon.add_directory({'mode': 'tvrecent', 'url': main_url + 'videos?a=dr&mt=0', 'section': 'tv'}, 'Recently Aired')
    addon.add_directory({'mode': 'tvadded', 'url': main_url + 'videos?a=da&mt=0', 'section': 'tv'}, 'Recently Added')
    addon.add_directory({'mode': 'tvpopular', 'url': main_url + 'videos?a=m&mt=0', 'section': 'tv'}, 'Most Popular')

elif mode == 'tvtop':
    html = net.http_GET(url).content
    r = re.search('<p>Top TV Shows</p>(.+?)</div>',html,re.DOTALL).group(1)
    if r:
        match = re.compile('<a id="big_pic[0-9]" href="(.+?)"><img src=".+?" alt=".+?" title="(.+?)"/></a>').findall(r)
        for link, title in match:
            addon.add_directory({'mode': 'tvseasons', 'url': link, 'section': 'tv'}, title, img='')

elif mode == 'tvaz':
    AZ_Menu('tvseriesaz','videos?mt=0&l=%s')

elif mode == 'tvseriesaz':
    get_video_list(url)

elif mode == 'tvrecent':
    get_video_quick_list(url)
  
elif mode == 'tvadded': 
    get_video_quick_list(url)

elif mode == 'tvpopular':
    get_video_quick_list(url)

elif mode == 'tvseasons':
    url = addon.queries['url']
    html = net.http_GET(url).content

    r = re.search('<p id="seasons_info_links">(.+?)</p>',html, re.DOTALL)
    match = re.compile('<a href="(.+?)".+?>(.+?)</a>',re.DOTALL).findall(r.group(1))
    for link, season in match:
        addon.add_directory({'mode': 'tvepisodes', 'url': link}, season)

elif mode == 'tvepisodes':
    url = addon.queries['url']
    html = net.http_GET(url).content
    
    cat_id = re.search('<input type="hidden" value="(.+?)" id="cat_id" name="cat_id" />',html).group(1)
    match = re.compile(' <a class="season_link" id="(.+?)" href=".+?" >(.+?)</a>',re.DOTALL).findall(html)
    for episode, name in match:
        url = episode_url % (episode, cat_id)
        addon.add_video_item({'url': url} ,{'title':name})

elif mode == 'resolver_settings':
    urlresolver.display_settings()

if not play:
    addon.end_of_directory()