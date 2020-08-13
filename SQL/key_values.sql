INSERT INTO `Test-TVM-DB`.key_values (`key`,info,comments) VALUES 
('def_dl','piratebay','The default downloader to assign to newly followed shows')
,('email','dickkluis@gmail.com','your gmail email address')
,('emailpas','iu4exCvsNKbzTNDQyGYcutQs','your gmail password')
,('minput_x','11','Line where the menu input is displayed:  Calc is mtop + minput_x')
,('mmenu_2y','65','Second Column of Menu items')
,('mmenu_3y','110','Third Column of Menu items')
,('mmenu_y','10','First Column of Menu items')
,('mstatus_x','2','Line where the Status is displayed:  Calc is minput_x + mstatus_x')
,('mstatus_y','18','Column where the status messasges are displayed')
,('msub_screen_x','2','Number of line to skip for sub_screen processing')
;
INSERT INTO `Test-TVM-DB`.key_values (`key`,info,comments) VALUES 
('mtop','2','Top line where the Menu starts')
,('plexdonotmove','sample.mkv,sample.mp4,sample.avi,sample.wmv,rarbg.mp4,rarbg.mkv,rarbg.avi,rarbg.wmv',NULL)
,('plexexts','mkv,mp4,mv4,avi,wmv,srt','Media extension to process')
,('plexmovd','/Volumes/HD-Data-CA-Server/PlexMedia/Movies/','Movies Main Directory')
,('plexmovstr','720p,1080p,dvdscr,web-dl,web-,bluray,x264,dts-hd,acc-rarbg,solar,h264,hdtv,rarbg,-sparks,-lucidtv','Eliminate these string from the movie name')
,('plexprefs','www.torrenting.org  -  ,www.torrenting.org - ,www.Torrenting.org       ,www.torrenting.org.,from [ www.torrenting.me ] -,[ www.torrenting.com ] -,www.Torrenting.com  -  ,www.torrenting.com -,www.torrenting.com,www.torrenting.me -,www.torrenting.me,www.scenetime.com  -,www.scenetime.com - ,www.scenetime.com -,www.scenetime.com,www.speed.cd - ,www.speed.cd,xxxxxxxxx','Prefixes to ignore for show or movies names')
,('plexprocessed','/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/TransmissionFiles/Processed/',NULL)
,('plexsd','/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/TransmissionFiles/','Download Source Directory')
,('plextrash','/Users/dick/.Trash/',NULL)
,('plextvd1','/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows/','TV Shows Main Direcotory')
;
INSERT INTO `Test-TVM-DB`.key_values (`key`,info,comments) VALUES 
('plextvd2','/Volumes/HD-Data-CA-Server/PlexMedia/Kids/TV Shows/','Second directory to store tv shows (for the grandkids)')
,('plextvd2selections','Doc Mcstuffins,Elena Of Avalor,Mickey And The Roadster Racers,Sofia The First,Tangled The Series,Star Wars Resistance,Avengers Assemble,Star Wars The Clone Wars','The different shows to store separate for the grandkids')
,('sms','8138189195@tmomail.net','You cell phone providers email adress to get you text messages')
,('tvmheader','{''Authorization'': ''Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH''}','tvmaze private key:  Use Dashboard to pick up password and use Premiun API testing to login in and get authorization key')
;