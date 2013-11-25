# can use this function to generate the html instead of json at endpoint for timeline
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
        #if dt == '2013-10-04':          # bad extract on this day
        #    linkuri = 'arstechnica.com/tech-policy/2013/10/how-the-feds-took-down-the-dread-pirate-roberts/'
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
	if debug==1:
	    debug_res[dt] = [title, sumar, url]
	if len(url)==2 and len(title)<2:
	    continue
	
	#print yr, mon, day
	if int(mon)==2:
	    mon='02'
	sys.stdout.flush()
	
        template = '''<li>
                                    <time>'''+str(yr)+''','''+str(mon)+''','''+str(day)+'''</time>			<!-- Event Date -->
                                    
                                    <h3><a href = \''''+url+'''\'>'''+title+'''</a></h3>		<!-- Headline -->
                                    <article>							<!-- Main Text -->
                                            <p>'''+sumar+'''</p>
                                    </article>
                                    <figure>						
                                            <img src=\"'''+imurl+'''\">			<!-- Media, can also be a link to youtube video etc (optional) -->
                                            <cite> '''+aname+'''</cite>		<!-- Credit for media (optional) -->
                                            <figcaption>'''+topsOnDay[dt]+'''...</figcaption>		<!-- Caption for media (optional) -->
                                    </figure>
                            </li>'''
        events+=template
    res = '''<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<title>Popular - TimeLine </title>
		<meta name="description" content="Template Description">
		
		<!-- Le HTML5 shim, for IE6-8 support of HTML elements -->
		<!--[if lt IE 9]>
		<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
		<![endif]-->

		<!-- CSS -->
		<link href="http://semantic.rnet.missouri.edu/scg/vizSDR/timeline.css" rel="stylesheet">
		<style>
			html, body {
				height: auto;
				padding: 0px;
				margin: 0px;
				width: 100%;
			}
		</style>
		<!-- JavaScript -->
		<style type="text/css" media="screen">
			h8 {font-size:2em}
		</style>
    
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js" type="text/javascript" charset="utf-8"></script>
		<script type="text/javascript" charset="utf-8">
			$( document ).ready( function() {
				var $body = $('body'); //Cache this for performance
				
				var setBodyScale = function() {
					var scaleFactor = 0.35,
						scaleSource = $body.width(),
						maxScale = 600,
						minScale = 30;

					var fontSize = scaleSource * scaleFactor; //Multiply the width of the body by the scaling factor:

					if (fontSize > maxScale) fontSize = maxScale;
					if (fontSize < minScale) fontSize = minScale; //Enforce the minimum and maximums

					$('body').css('font-size', fontSize + '%');
				}
			
			    $(window).resize(function(){
					setBodyScale();
				});
				
				//Fire it when the page first loads:
				setBodyScale();
			});
		</script>
		<script type="text/javascript" src="http://semantic.rnet.missouri.edu/scg/vizSDR/jquery-min.js"></script>
		<!-- <script type="text/javascript" src="jquery.mobile-1.0.min.js"></script> -->
		<script type="text/javascript" src="http://semantic.rnet.missouri.edu/scg/vizSDR/timeline-min.js"></script>
		<script>
			$(document).ready(function() {
				var timeline = new VMM.Timeline();
				timeline.init();
			});
		</script>


	</head>

	<body>


			<div id="timeline">
				
				<section>													<!-- Timeline Start Screen -->
					<time>2012,12,31</time>									<!-- Timeline Begins Date -->
					<h2>'''
    if target_cat!='default':
	    res+=target_cat.replace('_','/').title()+''' : '''
    else:
	if minusDays in monthList:
	    res += minusDays.title()+''' : '''
    
    res+='''Top-Ranked Links </h2>						<!-- Main Headline -->
					<article>												<!-- Main Text -->
						<p> Looking back at the top links from the past, as ranked by InstaRank..with brief highlights about each article</p>
					</article>
					<figure>						
						<img src="http://semantic.rnet.missouri.edu/scg/js/idata.jpg">				<!-- Media, can also be a link to youtube video etc (optional) -->
						<cite>Sorted by InstaRank </cite>			<!-- Credit for media (optional) -->
						<figcaption> Data Source: Instapaper </figcaption>			<!-- Caption for media (optional) -->
					</figure>
				</section>
				
				<ul>
					
					<!-- Event ---------------------------------------------------------------------------------------------------------->

				'''+events+'''
				
				</ul>
				
				
			</div>
		
		
	</body>
</html>
'''
    if debug==1:
	return debug_res
    #return debug_res
    return res
