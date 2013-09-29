from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import urllib2
import re
import sets
import sys
import cookielib
import datetime


from urllib import urlencode
import cgi
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.api import users

class  Registration(db.Model):
  code = db.StringProperty()
  name = db.StringProperty()
  mobno = db.StringProperty()
  pwd = db.StringProperty()
  pro = db.StringProperty()
  #count = db.StringProperty()
class Code(db.Model):
  current = db.StringProperty()
  
def registration_key():
  return db.Key.from_path('RegistrationTable', 'registration_record')

def code_key():
  return db.Key.from_path('CodeTable', 'lastcode')

name = None  #user name
mobno = None #user mobile no
pro = None  #provider eg 160by2,site2sms
pswd = None #provider password
key = None  # send s or regiser r
code = None  #user registerd unique code
msg = None
urltosend = None
tono = None
TOTAL = 260

CONNECTION_ERROR = -1
SUCCESS = 1
class MainPage(webapp.RequestHandler): 
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    message=self.request.get_all('message')
    self.response.out.write("<html><body>")  
    if message is None:
      sys.exit(1)    
    data=[]
    data=message[-1].split(None,1) 
    if data[0] == 'cet' :
      atdata = data[1].split(' ')
      uid =atdata[0]
      psw = atdata[1]
      cj = cookielib.CookieJar()
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
      url = 'http://117.211.100.44:8080/index.php'
      url_data = urlencode({'userid':uid,'password':psw,'Submit':'Submit'})
      usock = opener.open(url, url_data) 
      url = 'http://117.211.100.44:8080/index.php'
      url_data = urlencode({'module':'com_views','task':'student_attendance_view'})
      atand = opener.open(url, url_data)
      page=atand.read()
      line=page.split('\n')
      new=set([])
      for i in range (len(line)) :    
	mat2=re.match(r'.*Logged in as.*',line[i],re.M)
	if mat2: 
	  i = i+2
	  nam=re.match(r'.*<td>(.*?)</td>.*',line[i])
	  if nam:
	    str0= nam.group(1)
	    self.response.out.write("Name : "+str0)
	mat1=re.match(r'.*Attendance till date :.*',line[i],re.M)
	if mat1:	
	  self.response.out.write("</br>"+line[i])       
    elif data[0] == 'send' and len(data)==2:
      self.response.out.write("Received" )
      smsdata = data[1].split('>',1)  #contain all message exclude 'send'
      key = smsdata[0]
      if key == 'a' :  #admit new user
	secondparse = smsdata[1].split('>',3)
	name = secondparse[0]
	mobno = secondparse[1]
	pro = secondparse[2]
	pswd =secondparse[3]
	
	deleteContact = db.GqlQuery("SELECT * FROM Registration WHERE ANCESTOR IS :1 AND mobno =:2 and pro =:3", registration_key(),mobno,pro).get()
	if deleteContact is not None:
	  code = deleteContact.code
	  if code == '0':
	    sys.exit(1)
	  db.delete(deleteContact)
	cd = db.GqlQuery("SELECT * FROM Code WHERE ANCESTOR IS :1 ", code_key()).get() 
	if cd is not None:
	  tcode = cd.current
	  code = str(int(tcode)+1)
	else:
	  code = '1'
	deletecode = db.GqlQuery("SELECT * FROM Code WHERE ANCESTOR IS :1 ", code_key())
	if deletecode is not None:
	  db.delete(deletecode)	
	codedata = Code(parent = code_key())
	codedata.current = code
	codedata.put()
	usrdata = Registration(parent=registration_key())			
	usrdata.code = code
	usrdata.mobno = mobno
	usrdata.name = name
	usrdata.pro = pro
	usrdata.pwd = pswd
	usrdata.put()
	tono =mobno
	msg="Application activated, |"+pro+"|"+code+"|"
	urltosend = name+">"+mobno+">"+pswd+">"+pro+">"+tono+">"+msg    #url to send
	if pro == 'u': #ultoo.com
	  now = datetime.datetime.now()
	  if mobno == '9037755659':
	    msg=msg
	  else:
	    msg2= name+'('+mobno+'):'+msg
	    msg=msg2
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url = 'http://ultoo.in/login.php'
	  url_data = urlencode({'LoginMobile':'9037755659','LoginPassword':'47951','RememberMe':'1','submit2':'LOGIN HERE'})
	  usock = opener.open(url, url_data)
	  day=now.day
	  day2=str(day)
	  if len(day2) == 1 :
	    day2='0'+str(day)
	  mon=now.month
	  mon2=str(mon)
	  if len(mon2) == 1 :
	    mon2='0'+str(mon)   
	  send_sms_url = 'http://ultoo.in/home.php'
	  send_sms_data = urlencode({'MessageLength':'140','MobileNos':tono,'Message': msg,'SendNow': 'Send Now','SendNowBtn':'Send Now','Day':day2,'Month':mon2,'Year':now.year,'TimeInterval':'09:00 - 09:59','CCode':''})
		    
	  opener.addheaders = [('Referer','http://ultoo.com/home.php')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)		  
	elif pro =='s':  #sitetosms.com
	  msg2= '('+name+'):'+msg
	  msg=msg2	  
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url = 'http://www.site2sms.com/auth.asp'
	  url_data = urlencode({'txtCCode':'91','userid':mobno,'Password':pswd,'Submit':'Login'})	    	    
	  usock = opener.open(url, url_data)
	  send_sms_url = 'http://www.site2sms.com/user/send_sms_next.asp'
	  send_sms_data = urlencode({'txtCategory':'40','txtGroup':'0','txtLeft': len(msg) - TOTAL,'txtMessage': msg, 'txtMobileNo': tono,'txtUsed':len(msg)})      
	  opener.addheaders = [('Referer','http://www.site2sms.com/user/send_sms.asp')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)		  
	elif pro == 'w': #way2sms.com
	  msg2= '('+name+'):'+msg
	  msg=msg2	  
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url='http://site4.way2sms.com/Login1.action'
	  url_data = urlencode({'username':mobno,'password':pswd,'button':'Login'})
	  usock = opener.open(url, url_data)
	    ###############3
	  send_sms_url = 'http://site4.way2sms.com/quicksms.action'
	  send_sms_data = urlencode({'HiddenAction':'instantsms','catnamedis':'Birthday','Action': 'sa65sdf656fdfd','chkall': 'on','MobNo':tono,'textArea':msg})
	  opener.addheaders = [('Referer','http://site4.way2sms.com/jsp/InstantSMS.jsp')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)
	elif pro == 'b': #160by2.com
	  msg2= '('+name+'):'+msg
	  msg=msg2	  
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url='http://160by2.com/re-login'
	  opener.addheaders = [('Referer','Http://160by2.com/')]  
	  url_data = urlencode({'username':mobno,'password':pswd,'button':'Login'})
	  usock = opener.open(url, url_data)
	  self.response.out.write("login :"+mobno+pswd)
	  send_sms_url = 'http://160by2.com/SendSMSAction'
	  send_sms_data = urlencode({'hid_exists':'no','action1':'sf55sa5655sdf5','mobile1':tono,'msg1':msg,'sel_month':0,'sel_day':0,'sel_year':0,'sel_hour':'hh','sel_minute':'mm','sel_cat':0,'messid_0':'','messid_1':'','messid_2':'','messid_3':''})
	  opener.addheaders = [('Referer','http://160by2.com/SendSMS?id=9AEF17EFFA4653F27EEFEC3CA5F4BA30.05')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)			
	#end else if  
	msg="New user registerd ."+"Name :"+name +",   Mob : "+mobno+",  In :"+pro
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	url = 'http://www.site2sms.com/auth.asp'
	url_data = urlencode({'txtCCode':'91','userid':'9037755659','Password':'9054687','Submit':'Login'})	    	    
	usock = opener.open(url, url_data)
	send_sms_url = 'http://www.site2sms.com/user/send_sms_next.asp'
	send_sms_data = urlencode({'txtCategory':'40','txtGroup':'0','txtLeft': len(msg) - TOTAL,'txtMessage': msg, 'txtMobileNo': '9037755659','txtUsed':len(msg)})      
	opener.addheaders = [('Referer','http://www.site2sms.com/user/send_sms.asp')]  
	sms_sent_page = opener.open(send_sms_url,send_sms_data)	  
	  
	#usock = opener.open(url, url_data)	#must add new url that i new user registerd to me
				      		
      elif key == 'm':  #mailing to request
	secondparse2 = smsdata[1].split('>',2)
	code = secondparse2[0]
	tono = secondparse2[1]
	msg = secondparse2[2]
	my_text = msg.replace('_', ' ')
	msg=my_text
	#
	
	#
	rslt = db.GqlQuery("SELECT * FROM Registration WHERE ANCESTOR IS :1 AND code =:2",registration_key(),code).get()			    
	if rslt is not None:
	  mobno = rslt.mobno
	  pswd = rslt.pwd  
	  pro = rslt.pro
	  name = rslt.name
	else:
	  sys.exit(1)
	urltosend = name+">"+mobno+">"+pswd+">"+pro+">"+tono+">"+msg  
	if pro == 'u': #ultoo.com
	  
	  
	  #Logging into the SMS Site
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  
	  # To fool the website as if a Web browser is visiting the site
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  
	  #	  
	  url = 'http://ultoo.in/login.php'
	  url_data = urlencode({'LoginMobile':'9037755659','LoginPassword':'47951','RememberMe':'1','submit2':'LOGIN HERE'})
	  #try:
	  usock = opener.open(url, url_data)
	  now = datetime.datetime.now()
	  day=now.day
	  day2=str(day)
	  if len(day2) == 1 :
	    day2='0'+str(day)
	   
	  mon=now.month
	  mon2=str(mon)
	  if len(mon2) == 1 :
	    mon2='0'+str(mon)   
	  send_sms_url = 'http://ultoo.in/home.php'
	  send_sms_data = urlencode({'MessageLength':'140','MobileNos':tono,'Message': msg,'SendNow': 'Send Now','SendNowBtn':'Send Now','Day':day2,'Month':mon2,'Year':now.year,'TimeInterval':'09:00 - 09:59','CCode':''})
	  opener.addheaders = [('Referer','http://ultoo.com/home.php')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)
	  
	  
	elif pro =='s':  #sitetosms.com
	  #self.response.out.write("Site 2 sms  > "+urltosend)
	  msg2= '('+name+'):'+msg
	  msg=msg2	  
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url = 'http://www.site2sms.com/auth.asp'
	  url_data = urlencode({'txtCCode':'91','userid':mobno,'Password':pswd,'Submit':'Login'})	    	    
	  usock = opener.open(url, url_data)
	  send_sms_url = 'http://www.site2sms.com/user/send_sms_next.asp'
	  send_sms_data = urlencode({'txtCategory':'40','txtGroup':'0','txtLeft': len(msg) - TOTAL,'txtMessage': msg, 'txtMobileNo': tono,'txtUsed':len(msg)})      
	  opener.addheaders = [('Referer','http://www.site2sms.com/user/send_sms.asp')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)		  
	elif pro == 'w': #way2sms.com
	  msg2= '('+name+'):'+msg
	  msg=msg2	  
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url='http://site4.way2sms.com/Login1.action'
	  url_data = urlencode({'username':mobno,'password':pswd,'button':'Login'})
	  usock = opener.open(url, url_data)
	  send_sms_url = 'http://site4.way2sms.com/quicksms.action'
	  send_sms_data = urlencode({'HiddenAction':'instantsms','catnamedis':'Birthday','Action': 'sa65sdf656fdfd','chkall': 'on','MobNo':tono,'textArea':msg})
	  opener.addheaders = [('Referer','http://site4.way2sms.com/jsp/InstantSMS.jsp')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)
	elif pro == 'b': #160by2.com
	  self.response.out.write("enter")
	  msg2= '('+name+'):'+msg
	  msg=msg2	  
	  cj = cookielib.CookieJar()
	  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	  opener.addheaders = [('User-Agent','Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0')]
	  url='http://160by2.com/re-login'
	  opener.addheaders = [('Referer','Http://160by2.com/')]  
	  url_data = urlencode({'username':mobno,'password':pswd,'button':'Login'})
	  usock = opener.open(url, url_data)
	  self.response.out.write("login :"+mobno+pswd)
	  send_sms_url = 'http://160by2.com/SendSMSAction'
	  send_sms_data = urlencode({'hid_exists':'no','action1':'sf55sa5655sdf5','mobile1':tono,'msg1':msg,'sel_month':0,'sel_day':0,'sel_year':0,'sel_hour':'hh','sel_minute':'mm','sel_cat':0,'messid_0':'','messid_1':'','messid_2':'','messid_3':''})
	  opener.addheaders = [('Referer','http://160by2.com/SendSMS?id=9AEF17EFFA4653F27EEFEC3CA5F4BA30.05')]  
	  sms_sent_page = opener.open(send_sms_url,send_sms_data)	  
	
	
      #if else end here
      elif key == 'x':
	self.response.out.write("<br>" )
	commands =smsdata[1].split('>')
	c1 = commands[0]
	c2 = commands[1]
	if c1 == "all" :
	  if c2 == "disp":
	    self.response.out.write("<br>" )
	    self.response.out.write("<Table>")
	    self.response.out.write("<tr>")
	    self.response.out.write("<td>No</td><td>Code</td><td>Name</td><td>Moblie Number</td><td>Password</td><td>Provider</td>")
	    self.response.out.write("</tr>")
	    members = db.GqlQuery("SELECT * FROM Registration WHERE ANCESTOR IS :1 ", registration_key())
	    count = 1
	    for member in members:
	      self.response.out.write("<tr>")
	      self.response.out.write("<td>"+str(count)+"</td><td>"+member.code +"</td><td>"+member.name+"</td><td>"+member.mobno+"</td><td>"+member.pwd+"</td><td>"+member.pro  )
	      self.response.out.write("</tr>" )	
	      count =count +1
	    self.response.out.write("</Table>")
	  elif c2 == "del":
	    deleteallreg = db.GqlQuery("SELECT * FROM Registration WHERE ANCESTOR IS :1 ", registration_key())
	    if deleteallreg is not None:
	      db.delete(deleteallreg)	    
	    deleteall = db.GqlQuery("SELECT * FROM Code WHERE ANCESTOR IS :1 ", code_key())
	    if deleteall is not None:
	      db.delete(deleteall)
	    self.response.out.write("Database cleared successfully" )
	elif c1 == "block":
	  blkuser = db.GqlQuery("SELECT * FROM Registration WHERE ANCESTOR IS :1 and code=:2 ", registration_key(),c2).get()
	  if blkuser is not None:
	    name = blkuser.name
	    mobno =blkuser.mobno
	    pswd = blkuser.pwd
	    pro =blkuser.pro
	    db.delete(blkuser)
	  usrdata = Registration(parent=registration_key())			
	  usrdata.code = '0'
	  usrdata.mobno = mobno
	  usrdata.name = name
	  usrdata.pro = pro
	  usrdata.pwd = pswd
	  usrdata.put()	
	  self.response.out.write("User Blocked :"+name+"  "+mobno )
	elif c1=="unblock":
	  ublkuser = db.GqlQuery("SELECT * FROM Registration WHERE ANCESTOR IS :1 and mobno=:2 ", registration_key(),c2).get()
	  if ublkuser is not None:
	    self.response.out.write("User Unblocked :"+ublkuser.name+"  "+ublkuser.mobno )
	    db.delete(ublkuser)	  
	    
      
          
    else:
                  op = urllib2.build_opener()
		  url='http://thesaurus.com/browse/'		  
		  #self.response.out.write("<html><body>")
		  l=[]
		  l.append(url)
		  l.append(data[0])
		  url=''.join(l)
		  intake=op.open(url)
		  page=intake.read()
		  line=page.split('\n')
		  new=set([])
		  for i in range (len(line)) :
			mat1=re.match(r'.*Antonyms:.*',line[i],re.M)
			if mat1:
			      i=i+2
			      self.response.out.write(" <br/> " + "Opposite of " + data[0] + " : ")
			      while 1 :
				    mat2=re.match(r'</span></td>',line[i])
				    if mat2 :
					  break
				    mat2=re.match(r'.*>(.*?)<.*>(.*?)',line[i])
				    mat3=re.match(r'(.*)<.*>(.*?)<.*',line[i])
				    if mat2:
					  new.add(mat2.group(1))
					  new.add(mat2.group(2))
				    if mat3:
					  new.add(mat3.group(1))
					  new.add(mat3.group(2))
				    i=i+1            			
			      break
		  for i in new:  
			self.response.out.write(i)
    
    self.response.out.write("</body></html>")
	    
	    	    
application = webapp.WSGIApplication(
    [('/', MainPage)],
    debug=True)

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
	main()		                       
                        
