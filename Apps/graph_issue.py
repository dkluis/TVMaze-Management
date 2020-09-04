from dearpygui.dearpygui import *

#from tvm_lib import execute_sql
#sql = f'select statepoch, tvmshows from statistics where statrecind = "TVMaze"'
#result = execute_sql(sqltype='Fetch', sql=sql)
#print(result)

plot_data = [(1593449278, 46977), (1593449510, 46980), (1593450932, 46980), (1593454812, 46981), (1593469533, 46981), (1593479738, 46982), (1593490538, 46982), (1593494134, 46983), (1593504937, 46985), (1593510345, 46987), (1593512136, 46988), (1593514716, 46990), (1593519350, 46991), (1593521138, 46991), (1593522943, 46992), (1593526557, 46993), (1593530162, 46994), (1593531932, 46994), (1593533831, 46999), (1593535537, 46999), (1593537342, 47002), (1593540948, 47003), (1593542741, 47003), (1593548140, 47006), (1593549945, 47006), (1593550085, 47006), (1593558948, 47007), (1593564357, 47007), (1593565759, 47007), (1593571541, 47007), (1593575119, 47007), (1593576938, 47007), (1593593154, 47007), (1593596743, 47007), (1593598553, 47008), (1593605743, 47010), (1593609344, 47010), (1593623748, 47010), (1593625550, 47010), (1593629152, 47010), (1593630982, 47011), (1593638170, 47015), (1593654345, 47015), (1593656158, 47018), (1593663363, 47018), (1593668753, 47018), (1593675954, 47018), (1593681351, 47018), (1593683143, 47018), (1593686753, 47018), (1593688568, 47019), (1593693947, 47020), (1593695778, 47024), (1593706569, 47025), (1593710152, 47026), (1593711951, 47026), (1593717341, 47028), (1593720958, 47029), (1593749748, 47029), (1593756961, 47029), (1593774938, 47029), (1593800158, 47031), (1593803794, 47032), (1593809153, 47032), (1593810999, 47040), (1593814552, 47041), (1593819944, 47041), (1593821858, 47041), (1593827145, 47041), (1593834348, 47041), (1593836147, 47041), (1593841549, 47041), (1593843362, 47042), (1593844064, 47042), (1593844151, 47042), (1593845142, 47042), (1593852333, 47042), (1593872136, 47042), (1593879340, 47043), (1593881129, 47043), (1593888332, 47043), (1593895549, 47047), (1593897333, 47048), (1593900944, 47049), (1593904528, 47052), (1593908241, 47053), (1593922541, 47054), (1593943272, 47054), (1593945949, 47054), (1593947750, 47054), (1593949546, 47054), (1593956738, 47054), (1593958543, 47057), (1593962139, 47062), (1593965743, 47063), (1593976621, 47067), (1593980143, 47067), (1593985531, 47067), (1593994641, 47067), (1594001750, 47070), (1594003535, 47070), (1594008932, 47070), (1594010735, 47070), (1594012537, 47070), (1594023342, 47070), (1594034152, 47071), (1594041345, 47071), (1594044954, 47071), (1594048358, 47071), (1594052133, 47072), (1594062492, 47073), (1594062988, 47074), (1594066529, 47075), (1594070122, 47076), (1594071919, 47076), (1594081052, 47082), (1594084526, 47082), (1594091757, 47082), (1594095342, 47082), (1594107931, 47082), (1594115125, 47082), (1594116941, 47084), (1594120534, 47085), (1594129520, 47085), (1594138567, 47086), (1594140340, 47086), (1594145739, 47087), (1594152948, 47096), (1594156536, 47096), (1594165520, 47096), (1594169124, 47096), (1594178139, 47096), (1594181721, 47096), (1594188950, 47097), (1594194326, 47098), (1594196141, 47098), (1594199730, 47098), (1594210547, 47099), (1594221356, 47100), (1594227369, 47100), (1594232147, 47107), (1594232776, 47107), (1594235736, 47108), (1594239329, 47109), (1594250136, 47109), (1594255516, 47109), (1594266320, 47109), (1594268118, 47109), (1594275352, 47109), (1594280729, 47109), (1594282521, 47109), (1594286122, 47110), (1594293339, 47110), (1594300520, 47111), (1594311341, 47112), (1594317112, 47112), (1594321459, 47112), (1594322197, 47115), (1594329362, 47124), (1594331133, 47124), (1594340229, 47125), (1594341938, 47125), (1594345545, 47128), (1594347342, 47130), (1594372523, 47130), (1594383346, 47131), (1594390569, 47132), (1594397755, 47135), (1594401346, 47136), (1594419336, 47138), (1594431920, 47138), (1594433736, 47140), (1594459480, 47141), (1594460729, 47141), (1594462540, 47141), (1594464411, 47141), (1594464893, 47141), (1594465235, 47141), (1594465356, 47141), (1594466153, 47141), (1594468677, 47141), (1594468895, 47141), (1594469059, 47141), (1594469744, 47142), (1594473358, 47144), (1594475132, 47144), (1594480547, 47145), (1594487724, 47147), (1594491332, 47148), (1594494935, 47149), (1594498549, 47157), (1594502137, 47158), (1594507531, 47158), (1594509336, 47158), (1594514717, 47158), (1594520143, 47159), (1594520369, 47159), (1594523723, 47159), (1594525527, 47159), (1594527329, 47159), (1594541737, 47161), (1594545354, 47163), (1594548922, 47164), (1594550722, 47164), (1594552536, 47165), (1594561532, 47165), (1594563570, 47165), (1594563828, 47165), (1594565173, 47165), (1594565788, 47165), (1594581346, 47173), (1594584929, 47174), (1594590342, 47174), (1594592148, 47174), (1594593930, 47174), (1594604718, 47174), (1594606544, 47174), (1594610143, 47175), (1594613740, 47175), (1594615517, 47175), (1594626339, 47175), (1594635342, 47175), (1594637158, 47175), (1594638941, 47175), (1594646147, 47176), (1594655152, 47176), (1594656991, 47177), (1594660611, 47179), (1594665954, 47179), (1594683929, 47179), (1594691158, 47180), (1594700132, 47180), (1594710928, 47180), (1594718167, 47180), (1594719917, 47180), (1594723526, 47180), (1594730742, 47183), (1594737992, 47183), (1594741570, 47185), (1594748761, 47186), (1594752341, 47190), (1594755945, 47191), (1594763131, 47192), (1594766750, 47193), (1594773931, 47193), (1594779337, 47193), (1594781147, 47194), (1594784734, 47195), (1594786531, 47195), (1594790142, 47195), (1594797337, 47195), (1594802752, 47196), (1594806349, 47197), (1594809973, 47198), (1594813553, 47198), (1594814147, 47198), (1594815323, 47198), (1594820730, 47199), (1594824402, 47200), (1594828030, 47205), (1594829742, 47205), (1594831584, 47209), (1594842336, 47211), (1594844116, 47211), (1594851326, 47211), (1594862132, 47211), (1594865733, 47211), (1594867547, 47212), (1594871131, 47213), (1594872926, 47213), (1594878359, 47213), (1594885561, 47213), (1594887347, 47213), (1594894522, 47213), (1594898112, 47213), (1594916115, 47213), (1594917938, 47214), (1594921534, 47216), (1594925141, 47220), (1594926931, 47220), (1594932342, 47223), (1594939537, 47224), (1594941323, 47224), (1594947633, 47225), (1594950335, 47225), (1594953924, 47226), (1594959344, 47226), (1594961146, 47226), (1594962929, 47226), (1594986331, 47226), (1594989025, 47226), (1595000734, 47227), (1595004362, 47228), (1595007967, 47230), (1595011561, 47232), (1595015155, 47234), (1595018763, 47240), (1595022336, 47244), (1595025934, 47245), (1595033128, 47245), (1595036725, 47245), (1595040344, 47247), (1595043924, 47248), (1595045715, 47248), (1595054746, 47249), (1595072739, 47249), (1595079957, 47250), (1595085337, 47250), (1595087140, 47250), (1595094343, 47253), (1595097950, 47255), (1595103331, 47255), (1595112340, 47255), (1595119538, 47255), (1595121335, 47255), (1595126737, 47256), (1595132124, 47256), (1595144747, 47257), (1595155536, 47257), (1595160921, 47257), (1595162752, 47258), (1595166394, 47261), (1595169950, 47263), (1595193337, 47263), (1595195129, 47264), (1595196943, 47264), (1595198727, 47265), (1595205949, 47266), (1595211323, 47266), (1595218525, 47266), (1595220341, 47267), (1595222142, 47267), (1595232919, 47267), (1595234743, 47267), (1595238331, 47267), (1595240130, 47267), (1595245541, 47268), (1595247320, 47268), (1595252760, 47269), (1595263553, 47271), (1595265348, 47271), (1595267178, 47272), (1595268930, 47272), (1595272545, 47272), (1595274382, 47274), (1595281538, 47275), (1595283338, 47275), (1595286931, 47275), (1595288751, 47275), (1595294122, 47275), (1595297729, 47275), (1595299556, 47275), (1595304917, 47275), (1595321145, 47275), (1595328317, 47275), (1595333300, 47275), (1595339187, 47279), (1595342781, 47279), (1595349975, 47282), (1595351778, 47282), (1595363618, 47283), (1595367976, 47284), (1595369771, 47284), (1595371573, 47285), (1595375169, 47285), (1595376967, 47285), (1595378788, 47285), (1595385989, 47291), (1595389567, 47292), (1595391363, 47292), (1595393173, 47293), (1595396758, 47293), (1595400360, 47294), (1595407571, 47294), (1595411199, 47296), (1595412986, 47296), (1595418389, 47296), (1595423871, 47296), (1595425619, 47301), (1595432817, 47302), (1595436411, 47303), (1595438208, 47303), (1595443617, 47305), (1595450833, 47305), (1595452618, 47305), (1595458008, 47306), (1595465215, 47308), (1595467016, 47308), (1595474180, 47308), (1595477759, 47308), (1595479565, 47308), (1595490370, 47310), (1595493977, 47312), (1595497583, 47313), (1595501185, 47313), (1595504772, 47313), (1595508396, 47314), (1595510177, 47314), (1595511957, 47314), (1595515556, 47318), (1595519174, 47318), (1595520974, 47318), (1595522754, 47318), (1595524621, 47318), (1595528163, 47318), (1595533566, 47322), (1595537162, 47324), (1595549760, 47326), (1595553362, 47326), (1595558760, 47326), (1595573152, 47327), (1595580364, 47328), (1595583961, 47330), (1595591151, 47330), (1595601958, 47331), (1595603758, 47331), (1595605562, 47331), (1595607357, 47331), (1595616359, 47331), (1595623558, 47333), (1595625353, 47333), (1595627165, 47333), (1595628962, 47333), (1595632559, 47333), (1595634357, 47333), (1595637965, 47333), (1595641564, 47333), (1595650580, 47333), (1595659570, 47333), (1595663160, 47334), (1595670367, 47334), (1595672166, 47334), (1595673962, 47335), (1595684810, 47336), (1595695561, 47336), (1595699183, 47341), (1595702787, 47349), (1595704565, 47349), (1595708167, 47349), (1595709974, 47351), (1595711769, 47351), (1595713576, 47352), (1595717179, 47353), (1595720781, 47354), (1595724381, 47355), (1595727985, 47357), (1595736998, 47357), (1595738796, 47357), (1595746006, 47359), (1595760406, 47362), (1595767633, 47362), (1595769395, 47362), (1595771214, 47363), (1595773005, 47363), (1595785613, 47364), (1595789212, 47365), (1595791009, 47365), (1595794608, 47365), (1595796408, 47366), (1595800003, 47367), (1595803610, 47367), (1595805395, 47367), (1595812608, 47367), (1595814426, 47367), (1595816207, 47367), (1595818041, 47367), (1595819792, 47367), (1595823378, 47367), (1595825188, 47367), (1595837763, 47367), (1595853970, 47368), (1595854063, 47368), (1595857572, 47370), (1595861183, 47371), (1595864772, 47372), (1595870171, 47372), (1595871975, 47372), (1595877361, 47372), (1595880976, 47372), (1595882789, 47374), (1595889973, 47377), (1595893587, 47377), (1595895384, 47377), (1595898972, 47377), (1595904375, 47378), (1595909757, 47378), (1595911571, 47379), (1595922366, 47379), (1595940387, 47380), (1595956592, 47382), (1595960175, 47382), (1595963779, 47387), (1595972763, 47387), (1595978159, 47387), (1595983571, 47387), (1595987169, 47387), (1595996170, 47387), (1596010562, 47389), (1596014157, 47389), (1596039369, 47396), (1596042979, 47397), (1596044768, 47397), (1596055280, 47402), (1596059170, 47402), (1596064579, 47402), (1596068168, 47402), (1596082595, 47402), (1596093385, 47402), (1596095180, 47402), (1596096985, 47402), (1596109575, 47402), (1596122191, 47402), (1596125792, 47402), (1596129376, 47403), (1596132979, 47408), (1596140183, 47411), (1596143780, 47414), (1596145572, 47414), (1596147382, 47415), (1596150979, 47416), (1596154580, 47416), (1596168975, 47416), (1596176186, 47417), (1596190576, 47417), (1596192368, 47417), (1596194180, 47420), (1596197773, 47421), (1596206777, 47421), (1596218096, 47424), (1596222991, 47432), (1596231974, 47432), (1596233773, 47432), (1596237393, 47439), (1596240970, 47439), (1596244584, 47439), (1596246388, 47439), (1596251778, 47440), (1596255377, 47440), (1596257163, 47440), (1596258960, 47441), (1596266163, 47441), (1596276971, 47442), (1596280566, 47442), (1596282360, 47442), (1596284164, 47443), (1596291369, 47447), (1596294971, 47448), (1596298570, 47450), (1596302184, 47456), (1596303967, 47456), (1596305763, 47457), (1596316575, 47459), (1596318365, 47459), (1596323761, 47459), (1596327363, 47460), (1596330971, 47461), (1596334566, 47462), (1596338159, 47462), (1596341758, 47462), (1596365170, 47462), (1596379553, 47462), (1596384954, 47462), (1596388571, 47463), (1596394638, 47471), (1596395779, 47472), (1596406577, 47473), (1596408367, 47473), (1596411982, 47473), (1596413767, 47473), (1596417373, 47473), (1596420973, 47473), (1596428202, 47473), (1596429994, 47473), (1596440788, 47473), (1596442586, 47473), (1596449767, 47473), (1596456973, 47473), (1596471384, 47474), (1596473189, 47474), (1596474990, 47479), (1596485776, 47479), (1596492980, 47483), (1596494768, 47483), (1596503768, 47483), (1596505826, 47483), (1596514575, 47483), (1596516367, 47483), (1596525368, 47484), (1596527180, 47484), (1596528968, 47485), (1596532558, 47485), (1596536170, 47487), (1596537972, 47487), (1596546974, 47488), (1596550577, 47489), (1596554186, 47490), (1596557774, 47491), (1596561376, 47492), (1596564983, 47496), (1596568578, 47502), (1596572169, 47504), (1596573971, 47504), (1596579368, 47504), (1596582963, 47505), (1596586568, 47505), (1596590161, 47505), (1596593775, 47506), (1596600967, 47506), (1596608210, 47507), (1596615399, 47507), (1596622604, 47508), (1596629801, 47509), (1596637007, 47513), (1596644201, 47515), (1596647798, 47518), (1596649604, 47518), (1596651408, 47526), (1596654998, 47526), (1596656777, 47526), (1596658587, 47527), (1596662184, 47527), (1596669380, 47533), (1596672975, 47533), (1596678388, 47536), (1596680180, 47536), (1596687381, 47536), (1596689163, 47536), (1596692769, 47536), (1596694581, 47537), (1596701781, 47537), (1596707178, 47537), (1596716176, 47537), (1596723369, 47538), (1596726969, 47539), (1596730577, 47540), (1596737785, 47543), (1596741377, 47544), (1596744985, 47545), (1596797668, 47553), (1596798956, 47553), (1596800761, 47553), (1596809760, 47554), (1596813363, 47557), (1596816956, 47558), (1596820556, 47559), (1596824176, 47560), (1596827771, 47562), (1596834973, 47562), (1596843974, 47567), (1596845763, 47567), (1596847565, 47567), (1596849366, 47568), (1596851174, 47568), (1596860185, 47568), (1596861975, 47568), (1596867386, 47569), (1596876364, 47569), (1596878175, 47569), (1596880002, 47569), (1596883576, 47569), (1596899779, 47570), (1596903410, 47578), (1596906994, 47581), (1596910653, 47582), (1596917962, 47585), (1596919589, 47585), (1596932304, 47587), (1596935905, 47587), (1596939502, 47587), (1596978966, 47587), (1596982565, 47587), (1596984353, 47587), (1596991565, 47587), (1596993372, 47590), (1596996984, 47590), (1597000585, 47594), (1597007782, 47595), (1597011384, 47596), (1597020370, 47596), (1597022173, 47598), (1597023973, 47598), (1597033037, 47598), (1597034791, 47598), (1597043801, 47600), (1597047385, 47601), (1597054600, 47601), (1597058188, 47601), (1597074590, 47607), (1597076190, 47607), (1597078010, 47607), (1597079798, 47608), (1597083415, 47615), (1597087019, 47615), (1597097807, 47620), (1597101402, 47621), (1597103255, 47621), (1597105028, 47621), (1597108673, 47621), (1597114029, 47621), (1597119389, 47621), (1597130165, 47621), (1597140969, 47622), (1597142779, 47622), (1597144574, 47627), (1597148225, 47633), (1597151769, 47634), (1597155371, 47636), (1597159001, 47640), (1597166173, 47642), (1597167982, 47642), (1597169779, 47643), (1597173406, 47648), (1597178780, 47648), (1597191375, 47649), (1597205804, 47649), (1597207572, 47649), (1597223773, 47650), (1597225565, 47650), (1597227369, 47650), (1597238194, 47652), (1597241792, 47654), (1597245424, 47662), (1597247193, 47662), (1597256192, 47662), (1597259795, 47663), (1597263394, 47665), (1597265206, 47665), (1597266997, 47666), (1597274188, 47669), (1597275996, 47669), (1597283194, 47670), (1597292200, 47670), (1597297614, 47670), (1597301175, 47670), (1597313811, 47670), (1597317449, 47670), (1597333614, 47670), (1597337221, 47672), (1597339025, 47678), (1597342582, 47683), (1597344382, 47683), (1597346192, 47685), (1597348061, 47685), (1597349834, 47685), (1597356992, 47685), (1597365985, 47685), (1597367817, 47691), (1597378628, 47691), (1597380394, 47691), (1597389374, 47691), (1597392988, 47691), (1597402070, 47691), (1597412839, 47691), (1597423610, 47695), (1597427223, 47702), (1597438034, 47703), (1597441641, 47707), (1597445208, 47708), (1597448819, 47709), (1597457929, 47709), (1597464982, 47709), (1597477618, 47712), (1597495620, 47712), (1597497461, 47712), (1597506476, 47722), (1597510080, 47725), (1597513717, 47726), (1597515465, 47726), (1597517219, 47729), (1597524398, 47730), (1597527996, 47733), (1597531590, 47735), (1597533378, 47735), (1597534449, 47736), (1597536998, 47737), (1597542400, 47737), (1597544209, 47737), (1597547835, 47737), (1597551413, 47737), (1597564005, 47738), (1597571186, 47739), (1597574808, 47740), (1597578392, 47741), (1597582034, 47742), (1597592800, 47745), (1597596419, 47746), (1597601861, 47746), (1597614403, 47746), (1597619818, 47746), (1597621629, 47748), (1597627032, 47748), (1597634207, 47748), (1597637930, 47748), (1597639584, 47748), (1597652283, 47748), (1597655820, 47748), (1597659415, 47748), (1597663040, 47748), (1597670179, 47748), (1597672010, 47749), (1598023833, 47817)]


def graph_refresh(sender, data):
    add_line_series(f'graph issue##plot', 'minimal code', plot_data)


window = 'Graphs Issue'
add_window(window)
add_button(f'Refresh##graph', callback='graph_refresh')
add_plot(f'graph issue##plot')
end_window()
set_style_window_title_align(0.5, 0.5)
# the original code creates the window separately from graph data
# it does a refresh
graph_refresh(None, None)


start_dearpygui()