import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib2
import re, string
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import urlresolver
import elementtree.ElementTree as ET
from BeautifulSoup import BeautifulSoup as BS, BeautifulStoneSoup as BSS
try:
    import json
except:
    import simplejson as json

addon = Addon('plugin.video.livetvcafe', sys.argv)
xaddon = xbmcaddon.Addon(id='plugin.video.livetvcafe')
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

main_url = 'http://www.livetvcafe.net/'
rss_watching = main_url + 'rss/watching'
rss_rating = main_url + 'rss/rating'
rss_views = main_url + 'rss/views'
rss_recent = main_url + 'rss/recent'
addon_path = xaddon.getAddonInfo('path')
icon_path = addon_path + "/icons/"

######################################################################


def parse_xml():
    #html = urllib2.urlopen(url)
    html = net.http_GET(url).content
    soup = BSS(html, convertEntities=BSS.XML_ENTITIES)
    items = soup('item')
    for i in items:
        enclosure_url = i.enclosure['url']
        link = i.link.string
        title = i.title.string
        tags = i('media:category')[0].string
        thumb = i('media:thumbnail')[0]['url']
        category = i.category.string
        cdata = i.description.contents[1]
        #print(enclosure_url,link,title,category,tags,thumb)
        newSoup = BS(cdata)
        newUrl = newSoup('a')[0]['href']
        addon.add_video_item({'mode': 'channel', 'url': newUrl}, {'title': title}, img=thumb)
    
    #tree = ET.parse(html.strip())
    #for media in tree.getiterator('item'):
    #    addon.add_directory({'mode': 'channel', 'url': media.findtext('link')}, media.findtext('title'), img='')


def getSwfUrl(channel_name):
        """Helper method to grab the swf url, resolving HTTP 301/302 along the way"""
        base_url = 'http://www.justin.tv/widgets/live_embed_player.swf?channel=%s' % channel_name
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
                   'Referer' : 'http://www.justin.tv/'+channel_name}
        req = urllib2.Request(base_url, None, headers)
        response = urllib2.urlopen(req)
        return response.geturl()


def justintv(embedcode):

    channel = re.search('data="(.+?)"', embedcode, re.DOTALL).group(1)  
    channel_name = re.search('http://www.justin.tv/widgets/.+?\?channel=(.+)', channel).group(1)
    
    api_url = 'http://usher.justin.tv/find/%s.json?type=live' % channel_name
    html = net.http_GET(api_url).content
    
    data = json.loads(html)
    jtv_token = ' jtv='+data[0]['token'].replace('\\','\\5c').replace(' ','\\20').replace('"','\\22')
    rtmp = data[0]['connect']+'/'+data[0]['play']
    swf = ' swfUrl=%s swfVfy=1' % getSwfUrl(channel_name)
    page_url = ' Pageurl=http://www.justin.tv/' + channel_name
    final_url = rtmp + jtv_token + swf + page_url
    return final_url


def get_blogspot(embedcode):
    print 'blogspot'
    return ''


if play:

    html = net.http_GET(url).content
    html = html.replace('\\','')
    embedcode = re.search('var EmbedCode=(.+?);', html, re.DOTALL).group(1)
    
    if re.search('justin.tv', embedcode):
        stream_url = justintv(embedcode)
    elif re.search('mms:', embedcode):
        stream_url = re.search('"(mms:.+?)"', embedcode).group(1)
    elif re.search('rtsp://', embedcode):
        stream_url = re.search('"(rtsp://.+?)"', embedcode).group(1)
    elif re.search('blogspot.com', embedcode):
        stream_url = get_blogspot(embedcode)
    elif re.search('bitgravity', embedcode):
        stream_url = re.search('<param name="flashvars" value="File=(.+?)\?', embedcode).group(1)
                
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)


if mode == 'main': 
    addon.add_directory({'mode': 'channels', 'url': main_url + 'videos'}, {'title': 'Channels'}, img='')
    addon.add_directory({'mode': 'parsexml', 'url': rss_recent}, {'title': 'Recently Added'}, img='')
    addon.add_directory({'mode': 'parsexml', 'url': rss_views}, {'title': 'Most Viewed'}, img='')
    addon.add_directory({'mode': 'parsexml','url': rss_rating}, {'title': 'Top Rated'}, img='')
    addon.add_directory({'mode': 'parsexml', 'url': rss_watching}, {'title': 'Being Watched'}, img='')


elif mode == 'channels':
    html = net.http_GET(url).content
    
    r = re.search('<div class="categories">(.+?)</div>',html,re.DOTALL).group(1)
    match = re.compile('<li.+?><a href="(.+?)">(.+?)</a></li>').findall(r)
    for link, name in match:
        addon.add_directory({'mode': 'channellist', 'url': link}, {'title': name}, img='')


elif mode == 'channellist':
    html = net.http_GET(url).content
    
    #First grab individual video code blocks
    videoboxes = re.compile('<!-- Video Box -->(.+?)<!--VID_WRAP END-->.+?<!-- Video Box -->', re.DOTALL).findall(html)
    for videobox in videoboxes:
        
        #Now grab link and details inside each video code block
        video = re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)"  /></a>.+?<p id="desc" class="vid_info">(.+?)</p>', re.DOTALL).findall(videobox)
        for link, thumb, name, desc in video:
            print link, thumb, name, desc
            addon.add_video_item({'mode': 'channel', 'url': link}, {'title': name, 'plot': desc}, img=thumb)

    #Set pagination
    pageblock = re.search('<div class="pagination" align="center">(.+?)</div> <!--CONTENT END-->', html, re.DOTALL).group(1)
    pages = re.compile('<a href="[0-9]+">([0-9]+)</a>').findall(pageblock)
    for page in pages:
        #newurl = url[:-1] + page
        newurl = url + page
        addon.add_directory({'mode': 'channellist', 'url': newurl}, {'title': page}, img='')
 

elif mode == 'parsexml':
    parse_xml()


elif mode == 'resolver_settings':
    urlresolver.display_settings()


if not play:
    addon.end_of_directory()