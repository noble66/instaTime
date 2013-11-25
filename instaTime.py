#!/usr/bin/env python3
# Generates JSON output for timeline
import sys
sys.path.append('/home/suman/insta/')
sys.path.append('/home/suman/insta/realtime')
from flask import Flask         
app = Flask(__name__)          
import insta_utils as iu
import unicodedata
import redis_rank as rr
import datetime
import json
from flask import request
from flask import redirect
from flask import render_template
import rtanalysis as rt
import utils as ut
import topRanked as tr
import insta_users as ius
import categorize as cats



# returns json output embeddable into html 
def generate_instatime(target_cat, minusDays, debug=0):
    monthList = {'oct':['2013-11-01', 31],'sept':['2013-10-01', 30], 'aug':['2013-09-01', 31],'july':['2013-08-01', 31], 'jan': ['2013-02-01',31], 'feb': ['2013-03-01', 28], 'mar': ['2013-04-01',31], 'apr':['2013-05-01',30], 'may':['2013-06-01', 31], 'june':['2013-07-01', 30]}
    print 'Received: ', target_cat, minusDays
    if target_cat!='default':
        #print 'Going to category data..'
        topsOnDay = tr.categorize_wise_last_n_days(target_cat, minusDays)
    else:
        #print 'Going to non-category data'
	mnames = monthList.keys()
	if True in [minusDays.startswith(x1) for x1 in monthList.keys()]:
	    for x in mnames:
		if minusDays.startswith(x):
		    mname = x
		    break
	    if mname is None:
		mname  = 'jan'
	    # monthly timeline
	    #print monthList[minusDays][0], monthList[minusDays][1]
	    dates = iu.prev_n(monthList[mname][0], monthList[mname][1])
	    
	    topsOnDay = tr.get_preInstarank_data(dates)
	    #print topsOnDay
	    if '2013-10-14' in topsOnDay:
		topsOnDay['2013-10-14']='www.theguardian.com/commentisfree/2013/oct/14/independent-epitaph-establishment-journalism'
	    sys.stdout.flush()
	else: 
	    topsOnDay = tr.get_last_nDays_tops(minusDays)
	    #bad parsing
	    topsOnDay['2013-10-04']= 'www.arstechnica.com/tech-policy/2013/10/how-the-feds-took-down-the-dread-pirate-roberts/'
    if len(topsOnDay) == 0:
        return ''' <html> umm.. something went wrong :( </html> '''
    linkDetails = ius.get_urls_details(topsOnDay.values())                          # this decides the set of links {dt: link }
    links_mem = iu.nomnom('/home/suman/insta/data/embedly_data.dict')
    #print topsOnDay
    events = ''' '''
    dummy=''' '''
    debug_res = {}
    for dt in sorted(topsOnDay.keys()):
        dtsp = dt.split('-')
        yr = int(dtsp[0])
        mon = int(dtsp[1])
        day = int(dtsp[2])
        linkuri = topsOnDay[dt]
        
        if linkuri[:7]=='http://':              # remove http://
            linkuri = linkuri[7:]
        if linkuri not in links_mem:
            print 'Querying api for: ', linkuri
            try:
                res = tr.get_embed_api_query(linkuri)
            except:
                res={}
        else:
            res = links_mem[linkuri]
        if 'description' in res:
            sumar = res['description']
        else:
            sumar = ''
        if 'title' in res:
            title = res['title']
        else:
            title = ''
        if 'thumbnail_url' in res:
            imurl = res['thumbnail_url']
        else:
            imurl = ''
        if 'author_name' in res:
            aname = res['author_name']
        else:
            aname = ''
        if 'url' in res:
            url = res['url']
        else:
            url = ''
	debug_res[dt] = {'title':title, 'summary':sumar, 'link': url,'image':imurl,'author':aname}
	if len(url)==2 and len(title)<2:
	    continue
    return json.dumps(debug_res)


@app.route('/instatime/<category>')
def instatime(category, debug=0):
    cat_set = ['search', 'default','', 'gaming', 'recreation', 'business', 'computer_internet', 'culture_politics', 'science_technology', 'law_crime', 'sports', 'religion', 'weather', 'health', 'arts_entertainment']

    if '=' in category:                 # keyword search
	query = category.split('=')[1]
	res = generate_searchTime(query, debug)
	return res
    
    if '&' in category:                     # category-browsing
        minusDays = category.split('&')[1]
	target_cat= category.split('&')[0]
    else:                                   # no categories
        minusDays = '-1'
	target_cat=category
    if target_cat not in cat_set:
        target_cat = 'default'
    #print 'Received: ', target_cat, minusDays
    #sys.stdout.flush()
    res = generate_instatime(target_cat, minusDays, debug)
    return res

@app.route('/hello')                
def hello_world():              
    return 'umm.. hey .. this is ackward'       


if __name__ == '__main__':      
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0',port = 8084)
