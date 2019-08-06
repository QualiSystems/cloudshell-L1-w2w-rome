import os
import re
from collections import deque
from unittest import TestCase

from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from mock import MagicMock

from w2w_rome.driver_commands import DriverCommands

RUNTIME_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    'test_runtime_config.yaml',
)
DEFAULT_PROMPT = 'ROME[OPER]#'
SHOW_BOARD = '''ROME[OPER]# show board 
CURR SW VERSION  creationDate(Feb 21 2019, 19:51:00)
ROME STATUS      adminStatus(enabled) operStatus(enabled) alarmState(Cleared)
ROME STATE       OPER
ROME NAME        ROME
ACTIVE UNITS     1
ROME TYPE        ROME500
RTOS             VxWorks (6.8) 
BOARD            ver(LCU-100) rev(3) S/N(9727-4733-2222)
MATRIX SIZE:
                 Matrix A: Male/West 1..132, Female/East 1..130
                 Matrix B: Male/West 1..132, Female/East 1..130

IP               IP addr(192.168.1.2) subnet(255.255.255.0/0xffffff00)
                 gateway(192.168.1.1) dns(192.168.1.1)
VERSIONS         nonTffsDbVer(0) nextLoadImage(active)
ACTIVE SW DESC   active image was created at 02-21-2019 19:51
ACTIVE SW BANK   1 
ACTIVE SW VER    1.10.2.10
STANDBY SW DESC  standby image was created at 02-21-2019 19:51
STANDBY SW VER   1.10.2.10
UP TIME          0 days,5 hours,2 minutes and 44 seconds (total 12 seconds)
Recovery         recovery was done
CONNECTIONS      connection execution is enabled
OPERATION COUNT  7766
FPGA VER         proj6_fpga_2019Feb11_a.rbf
TIME SOURCE      MANUAL
AUTHENTICATION   local
CONNECTION TYPE  ssh and telnet
ROME[OPER]#'''
PORT_SHOW_MATRIX_A = '''ROME[OPER]# port show                 
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
E1[1AE1]         Unlocked     Enabled     Disconnected  2       W2[1AW2]       A1      
E2[1AE2]         Unlocked     Enabled     Disconnected  0                      A2      
E3[1AE3]         Unlocked     Enabled     Disconnected  0                      A3      
E4[1AE4]         Unlocked     Enabled     Disconnected  0                      A4      
E5[1AE5]         Unlocked     Enabled     Disconnected  0                      A5      
E6[1AE6]         Unlocked     Enabled     Disconnected  0                      A6      
E7[1AE7]         Unlocked     Enabled     Disconnected  0                      A7      
E8[1AE8]         Unlocked     Enabled     Disconnected  0                      A8      
E9[1AE9]         Unlocked     Enabled     Disconnected  0                      A9      
E10[1AE10]       Unlocked     Enabled     Disconnected  0                      A10     
E11[1AE11]       Unlocked     Enabled     Disconnected  2                      A11     
E12[1AE12]       Unlocked     Enabled     Disconnected  0                      A12     
E13[1AE13]       Unlocked     Enabled     Disconnected  0                      A13     
E14[1AE14]       Unlocked     Enabled     Disconnected  0                      A14     
E15[1AE15]       Unlocked     Enabled     Disconnected  2                      A15     
E16[1AE16]       Unlocked     Enabled     Disconnected  0                      A16     
E17[1AE17]       Unlocked     Enabled     Disconnected  0                      A17     
E18[1AE18]       Unlocked     Enabled     Disconnected  2                      A18     
E19[1AE19]       Unlocked     Enabled     Disconnected  0                      A19     
E20[1AE20]       Unlocked     Enabled     Disconnected  0                      A20     
E21[1AE21]       Unlocked     Enabled     Disconnected  2                      A21     
E22[1AE22]       Unlocked     Enabled     Disconnected  0                      A22     
E23[1AE23]       Unlocked     Enabled     Disconnected  0                      A23     
E24[1AE24]       Unlocked     Enabled     Disconnected  2                      A24     
E25[1AE25]       Unlocked     Enabled     Disconnected  0                      A25     
E26[1AE26]       Unlocked     Enabled     Disconnected  0                      A26     
E27[1AE27]       Unlocked     Enabled     Disconnected  0                      A27     
E28[1AE28]       Unlocked     Enabled     Disconnected  0                      A28     
E29[1AE29]       Unlocked     Enabled     Disconnected  0                      A29     
E30[1AE30]       Unlocked     Enabled     Disconnected  0                      A30     
E31[1AE31]       Unlocked     Enabled     Disconnected  0                      A31     
E32[1AE32]       Unlocked     Enabled     Disconnected  0                      A32     
E33[1AE33]       Unlocked     Enabled     Disconnected  0                      A33     
E34[1AE34]       Unlocked     Enabled     Disconnected  0                      A34     
E35[1AE35]       Unlocked     Enabled     Disconnected  0                      A35     
E36[1AE36]       Unlocked     Enabled     Disconnected  0                      A36     
E37[1AE37]       Unlocked     Enabled     Disconnected  0                      A37     
E38[1AE38]       Unlocked     Enabled     Disconnected  0                      A38     
E39[1AE39]       Unlocked     Enabled     Disconnected  0                      A39     
E40[1AE40]       Unlocked     Enabled     Disconnected  0                      A40     
E41[1AE41]       Unlocked     Enabled     Disconnected  0                      A41     
E42[1AE42]       Unlocked     Enabled     Disconnected  0                      A42     
E43[1AE43]       Unlocked     Enabled     Disconnected  0                      A43     
E44[1AE44]       Unlocked     Enabled     Disconnected  0                      A44     
E45[1AE45]       Unlocked     Enabled     Disconnected  0                      A45     
E46[1AE46]       Unlocked     Enabled     Disconnected  0                      A46     
E47[1AE47]       Unlocked     Enabled     Disconnected  0                      A47     
E48[1AE48]       Unlocked     Enabled     Disconnected  0                      A48     
E49[1AE49]       Unlocked     Enabled     Disconnected  0                      A49     
E50[1AE50]       Unlocked     Enabled     Disconnected  0                      A50     
E51[1AE51]       Unlocked     Enabled     Disconnected  0                      A51     
E52[1AE52]       Unlocked     Enabled     Disconnected  0                      A52     
E53[1AE53]       Unlocked     Enabled     Disconnected  0                      A53     
E54[1AE54]       Unlocked     Enabled     Disconnected  0                      A54     
E55[1AE55]       Unlocked     Enabled     Disconnected  0                      A55     
E56[1AE56]       Unlocked     Enabled     Disconnected  0                      A56     
E57[1AE57]       Unlocked     Enabled     Disconnected  0                      A57     
E58[1AE58]       Unlocked     Enabled     Disconnected  0                      A58     
E59[1AE59]       Unlocked     Enabled     Disconnected  0                      A59     
E60[1AE60]       Unlocked     Enabled     Disconnected  0                      A60     
E61[1AE61]       Unlocked     Enabled     Disconnected  0                      A61     
E62[1AE62]       Unlocked     Enabled     Disconnected  0                      A62     
E63[1AE63]       Unlocked     Enabled     Disconnected  0                      A63     
E64[1AE64]       Unlocked     Enabled     Disconnected  0                      A64     
E65[1AE65]       Unlocked     Enabled     Disconnected  0                      A65     
E66[1AE66]       Unlocked     Enabled     Disconnected  0                      A66     
E67[1AE67]       Unlocked     Enabled     Disconnected  0                      A67     
E68[1AE68]       Unlocked     Enabled     Disconnected  0                      A68     
E69[1AE69]       Unlocked     Enabled     Disconnected  0                      A69     
E70[1AE70]       Unlocked     Enabled     Disconnected  0                      A70     
E71[1AE71]       Unlocked     Enabled     Disconnected  0                      A71     
E72[1AE72]       Unlocked     Enabled     Disconnected  0                      A72     
E73[1AE73]       Unlocked     Enabled     Disconnected  0                      A73     
E74[1AE74]       Unlocked     Enabled     Disconnected  0                      A74     
E75[1AE75]       Unlocked     Enabled     Disconnected  0                      A75     
E76[1AE76]       Unlocked     Enabled     Disconnected  0                      A76     
E77[1AE77]       Unlocked     Enabled     Disconnected  0                      A77     
E78[1AE78]       Unlocked     Enabled     Disconnected  0                      A78     
E79[1AE79]       Unlocked     Enabled     Disconnected  0                      A79     
E80[1AE80]       Unlocked     Enabled     Disconnected  0                      A80     
E81[1AE81]       Unlocked     Enabled     Disconnected  0                      A81     
E82[1AE82]       Unlocked     Enabled     Disconnected  0                      A82     
E83[1AE83]       Unlocked     Enabled     Disconnected  0                      A83     
E84[1AE84]       Unlocked     Enabled     Disconnected  0                      A84     
E85[1AE85]       Unlocked     Enabled     Disconnected  0                      A85     
E86[1AE86]       Unlocked     Enabled     Disconnected  0                      A86     
E87[1AE87]       Unlocked     Enabled     Disconnected  0                      A87     
E88[1AE88]       Unlocked     Enabled     Disconnected  0                      A88     
E89[1AE89]       Unlocked     Enabled     Disconnected  0                      A89     
E90[1AE90]       Unlocked     Enabled     Disconnected  0                      A90     
E91[1AE91]       Unlocked     Enabled     Disconnected  0                      A91     
E92[1AE92]       Unlocked     Enabled     Disconnected  0                      A92     
E93[1AE93]       Unlocked     Enabled     Disconnected  0                      A93     
E94[1AE94]       Unlocked     Enabled     Disconnected  0                      A94     
E95[1AE95]       Unlocked     Enabled     Disconnected  0                      A95     
E96[1AE96]       Unlocked     Enabled     Disconnected  0                      A96     
E97[1AE97]       Unlocked     Enabled     Disconnected  0                      A97     
E98[1AE98]       Unlocked     Enabled     Disconnected  0                      A98     
E99[1AE99]       Unlocked     Enabled     Disconnected  0                      A99     
E100[1AE100]     Unlocked     Enabled     Disconnected  0                      A100    
E101[1AE101]     Unlocked     Enabled     Disconnected  0                      A101    
E102[1AE102]     Unlocked     Enabled     Disconnected  0                      A102    
E103[1AE103]     Unlocked     Enabled     Disconnected  0                      A103    
E104[1AE104]     Unlocked     Enabled     Disconnected  0                      A104    
E105[1AE105]     Unlocked     Enabled     Disconnected  0                      A105    
E106[1AE106]     Unlocked     Enabled     Disconnected  0                      A106    
E107[1AE107]     Unlocked     Enabled     Disconnected  0                      A107    
E108[1AE108]     Unlocked     Enabled     Disconnected  0                      A108    
E109[1AE109]     Unlocked     Enabled     Disconnected  0                      A109    
E110[1AE110]     Unlocked     Enabled     Disconnected  0                      A110    
E111[1AE111]     Unlocked     Enabled     Disconnected  0                      A111    
E112[1AE112]     Unlocked     Enabled     Disconnected  0                      A112    
E113[1AE113]     Unlocked     Enabled     Disconnected  0                      A113    
E114[1AE114]     Unlocked     Enabled     Disconnected  0                      A114    
E115[1AE115]     Unlocked     Enabled     Disconnected  0                      A115    
E116[1AE116]     Unlocked     Enabled     Disconnected  0                      A116    
E117[1AE117]     Unlocked     Enabled     Disconnected  0                      A117    
E118[1AE118]     Unlocked     Enabled     Disconnected  0                      A118    
E119[1AE119]     Unlocked     Enabled     Disconnected  0                      A119    
E120[1AE120]     Unlocked     Enabled     Disconnected  0                      A120    
E121[1AE121]     Unlocked     Enabled     Disconnected  0                      A121    
E122[1AE122]     Unlocked     Enabled     Disconnected  0                      A122    
E123[1AE123]     Unlocked     Enabled     Disconnected  0                      A123    
E124[1AE124]     Unlocked     Enabled     Disconnected  0                      A124    
E125[1AE125]     Unlocked     Enabled     Disconnected  0                      A125    
E126[1AE126]     Unlocked     Enabled     Disconnected  0                      A126    
E127[1AE127]     Unlocked     Enabled     Disconnected  0                      A127    
E128[1AE128]     Unlocked     Enabled     Disconnected  0                      A128    
1AE129           Unlocked     Enabled     Disconnected  0                              
1AE130           Unlocked     Enabled     Disconnected  0                              
E129[1BE1]       Unlocked     Enabled     Disconnected  0                      B129    
E130[1BE2]       Unlocked     Enabled     Disconnected  0                      B130    
E131[1BE3]       Unlocked     Enabled     Disconnected  0                      B131    
E132[1BE4]       Unlocked     Enabled     Disconnected  0                      B132    
E133[1BE5]       Unlocked     Enabled     Disconnected  0                      B133    
E134[1BE6]       Unlocked     Enabled     Disconnected  0                      B134    
E135[1BE7]       Unlocked     Enabled     Disconnected  0                      B135    
E136[1BE8]       Unlocked     Enabled     Disconnected  0                      B136    
E137[1BE9]       Unlocked     Enabled     Disconnected  0                      B137    
E138[1BE10]      Unlocked     Enabled     Disconnected  0                      B138    
E139[1BE11]      Unlocked     Enabled     Disconnected  0                      B139    
E140[1BE12]      Unlocked     Enabled     Disconnected  0                      B140    
E141[1BE13]      Unlocked     Enabled     Disconnected  2                      B141    
E142[1BE14]      Unlocked     Enabled     Disconnected  0                      B142    
E143[1BE15]      Unlocked     Enabled     Disconnected  2                      B143    
E144[1BE16]      Unlocked     Enabled     Disconnected  0                      B144    
E145[1BE17]      Unlocked     Enabled     Disconnected  0                      B145    
E146[1BE18]      Unlocked     Enabled     Disconnected  0                      B146    
E147[1BE19]      Unlocked     Enabled     Disconnected  0                      B147    
E148[1BE20]      Unlocked     Enabled     Disconnected  0                      B148    
E149[1BE21]      Unlocked     Enabled     Disconnected  0                      B149    
E150[1BE22]      Unlocked     Enabled     Disconnected  0                      B150    
E151[1BE23]      Unlocked     Enabled     Disconnected  0                      B151    
E152[1BE24]      Unlocked     Enabled     Disconnected  0                      B152    
E153[1BE25]      Unlocked     Enabled     Disconnected  0                      B153    
E154[1BE26]      Unlocked     Enabled     Disconnected  0                      B154    
E155[1BE27]      Unlocked     Enabled     Disconnected  0                      B155    
E156[1BE28]      Unlocked     Enabled     Disconnected  0                      B156    
E157[1BE29]      Unlocked     Enabled     Disconnected  0                      B157    
E158[1BE30]      Unlocked     Enabled     Disconnected  0                      B158    
E159[1BE31]      Unlocked     Enabled     Disconnected  0                      B159    
E160[1BE32]      Unlocked     Enabled     Disconnected  0                      B160    
E161[1BE33]      Unlocked     Enabled     Disconnected  0                      B161    
E162[1BE34]      Unlocked     Enabled     Disconnected  0                      B162    
E163[1BE35]      Unlocked     Enabled     Disconnected  0                      B163    
E164[1BE36]      Unlocked     Enabled     Disconnected  0                      B164    
E165[1BE37]      Unlocked     Enabled     Disconnected  0                      B165    
E166[1BE38]      Unlocked     Enabled     Disconnected  0                      B166    
E167[1BE39]      Unlocked     Enabled     Disconnected  0                      B167    
E168[1BE40]      Unlocked     Enabled     Disconnected  0                      B168    
E169[1BE41]      Unlocked     Enabled     Disconnected  0                      B169    
E170[1BE42]      Unlocked     Enabled     Disconnected  0                      B170    
E171[1BE43]      Unlocked     Enabled     Disconnected  0                      B171    
E172[1BE44]      Unlocked     Enabled     Disconnected  0                      B172    
E173[1BE45]      Unlocked     Enabled     Disconnected  0                      B173    
E174[1BE46]      Unlocked     Enabled     Disconnected  0                      B174    
E175[1BE47]      Unlocked     Enabled     Disconnected  0                      B175    
E176[1BE48]      Unlocked     Enabled     Disconnected  0                      B176    
E177[1BE49]      Unlocked     Enabled     Disconnected  0                      B177    
E178[1BE50]      Unlocked     Enabled     Disconnected  0                      B178    
E179[1BE51]      Unlocked     Enabled     Disconnected  0                      B179    
E180[1BE52]      Unlocked     Enabled     Disconnected  0                      B180    
E181[1BE53]      Unlocked     Enabled     Disconnected  0                      B181    
E182[1BE54]      Unlocked     Enabled     Disconnected  0                      B182    
E183[1BE55]      Unlocked     Enabled     Disconnected  0                      B183    
E184[1BE56]      Unlocked     Enabled     Disconnected  0                      B184    
E185[1BE57]      Unlocked     Enabled     Disconnected  0                      B185    
E186[1BE58]      Unlocked     Enabled     Disconnected  0                      B186    
E187[1BE59]      Unlocked     Enabled     Disconnected  0                      B187    
E188[1BE60]      Unlocked     Enabled     Disconnected  0                      B188    
E189[1BE61]      Unlocked     Enabled     Disconnected  0                      B189    
E190[1BE62]      Unlocked     Enabled     Disconnected  0                      B190    
E191[1BE63]      Unlocked     Enabled     Disconnected  0                      B191    
E192[1BE64]      Unlocked     Enabled     Disconnected  0                      B192    
E193[1BE65]      Unlocked     Enabled     Disconnected  0                      B193    
E194[1BE66]      Unlocked     Enabled     Disconnected  0                      B194    
E195[1BE67]      Unlocked     Enabled     Disconnected  0                      B195    
E196[1BE68]      Unlocked     Enabled     Disconnected  0                      B196    
E197[1BE69]      Unlocked     Enabled     Disconnected  0                      B197    
E198[1BE70]      Unlocked     Enabled     Disconnected  0                      B198    
E199[1BE71]      Unlocked     Enabled     Disconnected  0                      B199    
E200[1BE72]      Unlocked     Enabled     Disconnected  0                      B200    
E201[1BE73]      Unlocked     Enabled     Disconnected  0                      B201    
E202[1BE74]      Unlocked     Enabled     Disconnected  0                      B202    
E203[1BE75]      Unlocked     Enabled     Disconnected  0                      B203    
E204[1BE76]      Unlocked     Enabled     Disconnected  0                      B204    
E205[1BE77]      Unlocked     Enabled     Disconnected  0                      B205    
E206[1BE78]      Unlocked     Enabled     Disconnected  0                      B206    
E207[1BE79]      Unlocked     Enabled     Disconnected  0                      B207    
E208[1BE80]      Unlocked     Enabled     Disconnected  0                      B208    
E209[1BE81]      Unlocked     Enabled     Disconnected  0                      B209    
E210[1BE82]      Unlocked     Enabled     Disconnected  0                      B210    
E211[1BE83]      Unlocked     Enabled     Disconnected  0                      B211    
E212[1BE84]      Unlocked     Enabled     Disconnected  0                      B212    
E213[1BE85]      Unlocked     Enabled     Disconnected  0                      B213    
E214[1BE86]      Unlocked     Enabled     Disconnected  0                      B214    
E215[1BE87]      Unlocked     Enabled     Disconnected  0                      B215    
E216[1BE88]      Unlocked     Enabled     Disconnected  0                      B216    
E217[1BE89]      Unlocked     Enabled     Disconnected  0                      B217    
E218[1BE90]      Unlocked     Enabled     Disconnected  0                      B218    
E219[1BE91]      Unlocked     Enabled     Disconnected  0                      B219    
E220[1BE92]      Unlocked     Enabled     Disconnected  0                      B220    
E221[1BE93]      Unlocked     Enabled     Disconnected  0                      B221    
E222[1BE94]      Unlocked     Enabled     Disconnected  0                      B222    
E223[1BE95]      Unlocked     Enabled     Disconnected  0                      B223    
E224[1BE96]      Unlocked     Enabled     Disconnected  0                      B224    
E225[1BE97]      Unlocked     Enabled     Disconnected  0                      B225    
E226[1BE98]      Unlocked     Enabled     Disconnected  0                      B226    
E227[1BE99]      Unlocked     Enabled     Disconnected  0                      B227    
E228[1BE100]     Unlocked     Enabled     Disconnected  0                      B228    
E229[1BE101]     Unlocked     Enabled     Disconnected  0                      B229    
E230[1BE102]     Unlocked     Enabled     Disconnected  0                      B230    
E231[1BE103]     Unlocked     Enabled     Disconnected  0                      B231    
E232[1BE104]     Unlocked     Enabled     Disconnected  0                      B232    
E233[1BE105]     Unlocked     Enabled     Disconnected  0                      B233    
E234[1BE106]     Unlocked     Enabled     Disconnected  0                      B234    
E235[1BE107]     Unlocked     Enabled     Disconnected  2                      B235    
E236[1BE108]     Unlocked     Enabled     Disconnected  0                      B236    
E237[1BE109]     Unlocked     Enabled     Disconnected  2                      B237    
E238[1BE110]     Unlocked     Enabled     Disconnected  0                      B238    
E239[1BE111]     Unlocked     Enabled     Disconnected  0                      B239    
E240[1BE112]     Unlocked     Enabled     Disconnected  0                      B240    
E241[1BE113]     Unlocked     Enabled     Disconnected  0                      B241    
E242[1BE114]     Unlocked     Enabled     Disconnected  0                      B242    
E243[1BE115]     Unlocked     Enabled     Disconnected  0                      B243    
E244[1BE116]     Unlocked     Enabled     Disconnected  0                      B244    
E245[1BE117]     Unlocked     Enabled     Disconnected  0                      B245    
E246[1BE118]     Unlocked     Enabled     Disconnected  0                      B246    
E247[1BE119]     Unlocked     Enabled     Disconnected  0                      B247    
E248[1BE120]     Unlocked     Enabled     Disconnected  0                      B248    
E249[1BE121]     Unlocked     Enabled     Connected     13      W253[1BW125]   B249    
E250[1BE122]     Unlocked     Enabled     Disconnected  0                      B250    
E251[1BE123]     Unlocked     Enabled     Disconnected  0                      B251    
E252[1BE124]     Unlocked     Enabled     Disconnected  0                      B252    
E253[1BE125]     Unlocked     Enabled     Connected     13      W249[1BW121]   B253    
E254[1BE126]     Unlocked     Enabled     Disconnected  0                      B254    
E255[1BE127]     Unlocked     Enabled     Disconnected  0                      B255    
E256[1BE128]     Unlocked     Enabled     Disconnected  0                      B256    
1BE129           Unlocked     Enabled     Disconnected  0                              
1BE130           Unlocked     Enabled     Disconnected  0                              
W1[1AW1]         Unlocked     Enabled     Disconnected  0                      A1      
W2[1AW2]         Unlocked     Enabled     Disconnected  0       E1[1AE1]       A2      
W3[1AW3]         Unlocked     Enabled     Disconnected  0                      A3      
W4[1AW4]         Unlocked     Enabled     Disconnected  0                      A4      
W5[1AW5]         Unlocked     Enabled     Disconnected  0                      A5      
W6[1AW6]         Unlocked     Enabled     Disconnected  0                      A6      
W7[1AW7]         Unlocked     Enabled     Disconnected  0                      A7      
W8[1AW8]         Unlocked     Enabled     Disconnected  0                      A8      
W9[1AW9]         Unlocked     Enabled     Disconnected  0                      A9      
W10[1AW10]       Unlocked     Enabled     Disconnected  2                      A10     
W11[1AW11]       Unlocked     Enabled     Disconnected  0                      A11     
W12[1AW12]       Unlocked     Enabled     Disconnected  0                      A12     
W13[1AW13]       Unlocked     Enabled     Disconnected  0                      A13     
W14[1AW14]       Unlocked     Enabled     Disconnected  0                      A14     
W15[1AW15]       Unlocked     Enabled     Disconnected  0                      A15     
W16[1AW16]       Unlocked     Enabled     Disconnected  0                      A16     
W17[1AW17]       Unlocked     Enabled     Disconnected  0                      A17     
W18[1AW18]       Unlocked     Enabled     Disconnected  0                      A18     
W19[1AW19]       Unlocked     Enabled     Disconnected  0                      A19     
W20[1AW20]       Unlocked     Enabled     Disconnected  0                      A20     
W21[1AW21]       Unlocked     Enabled     Disconnected  0                      A21     
W22[1AW22]       Unlocked     Enabled     Disconnected  0                      A22     
W23[1AW23]       Unlocked     Enabled     Disconnected  0                      A23     
W24[1AW24]       Unlocked     Enabled     Disconnected  0                      A24     
W25[1AW25]       Unlocked     Enabled     Disconnected  2                      A25     
W26[1AW26]       Unlocked     Enabled     Disconnected  0                      A26     
W27[1AW27]       Unlocked     Enabled     Disconnected  0                      A27     
W28[1AW28]       Unlocked     Enabled     Disconnected  0                      A28     
W29[1AW29]       Unlocked     Enabled     Disconnected  0                      A29     
W30[1AW30]       Unlocked     Enabled     Disconnected  0                      A30     
W31[1AW31]       Unlocked     Enabled     Disconnected  0                      A31     
W32[1AW32]       Unlocked     Enabled     Disconnected  0                      A32     
W33[1AW33]       Unlocked     Enabled     Disconnected  0                      A33     
W34[1AW34]       Unlocked     Enabled     Disconnected  0                      A34     
W35[1AW35]       Unlocked     Enabled     Disconnected  0                      A35     
W36[1AW36]       Unlocked     Enabled     Disconnected  0                      A36     
W37[1AW37]       Unlocked     Enabled     Disconnected  0                      A37     
W38[1AW38]       Unlocked     Enabled     Disconnected  0                      A38     
W39[1AW39]       Unlocked     Enabled     Disconnected  0                      A39     
W40[1AW40]       Unlocked     Enabled     Disconnected  0                      A40     
W41[1AW41]       Unlocked     Enabled     Disconnected  0                      A41     
W42[1AW42]       Unlocked     Enabled     Disconnected  0                      A42     
W43[1AW43]       Unlocked     Enabled     Disconnected  0                      A43     
W44[1AW44]       Unlocked     Enabled     Disconnected  0                      A44     
W45[1AW45]       Unlocked     Enabled     Disconnected  0                      A45     
W46[1AW46]       Unlocked     Enabled     Disconnected  0                      A46     
W47[1AW47]       Unlocked     Enabled     Disconnected  0                      A47     
W48[1AW48]       Unlocked     Enabled     Disconnected  0                      A48     
W49[1AW49]       Unlocked     Enabled     Disconnected  0                      A49     
W50[1AW50]       Unlocked     Enabled     Disconnected  2                      A50     
W51[1AW51]       Unlocked     Enabled     Disconnected  0                      A51     
W52[1AW52]       Unlocked     Enabled     Disconnected  0                      A52     
W53[1AW53]       Unlocked     Enabled     Disconnected  0                      A53     
W54[1AW54]       Unlocked     Enabled     Disconnected  0                      A54     
W55[1AW55]       Unlocked     Enabled     Disconnected  0                      A55     
W56[1AW56]       Unlocked     Enabled     Disconnected  0                      A56     
W57[1AW57]       Unlocked     Enabled     Disconnected  0                      A57     
W58[1AW58]       Unlocked     Enabled     Disconnected  0                      A58     
W59[1AW59]       Unlocked     Enabled     Disconnected  0                      A59     
W60[1AW60]       Unlocked     Enabled     Disconnected  2                      A60     
W61[1AW61]       Unlocked     Enabled     Disconnected  0                      A61     
W62[1AW62]       Unlocked     Enabled     Disconnected  0                      A62     
W63[1AW63]       Unlocked     Enabled     Disconnected  0                      A63     
W64[1AW64]       Unlocked     Enabled     Disconnected  0                      A64     
W65[1AW65]       Unlocked     Enabled     Disconnected  0                      A65     
W66[1AW66]       Unlocked     Enabled     Disconnected  0                      A66     
W67[1AW67]       Unlocked     Enabled     Disconnected  0                      A67     
W68[1AW68]       Unlocked     Enabled     Disconnected  0                      A68     
W69[1AW69]       Unlocked     Enabled     Disconnected  0                      A69     
W70[1AW70]       Unlocked     Enabled     Disconnected  0                      A70     
W71[1AW71]       Unlocked     Enabled     Disconnected  0                      A71     
W72[1AW72]       Unlocked     Enabled     Disconnected  0                      A72     
W73[1AW73]       Unlocked     Enabled     Disconnected  0                      A73     
W74[1AW74]       Unlocked     Enabled     Disconnected  0                      A74     
W75[1AW75]       Unlocked     Enabled     Disconnected  0                      A75     
W76[1AW76]       Unlocked     Enabled     Disconnected  0                      A76     
W77[1AW77]       Unlocked     Enabled     Disconnected  0                      A77     
W78[1AW78]       Unlocked     Enabled     Disconnected  0                      A78     
W79[1AW79]       Unlocked     Enabled     Disconnected  0                      A79     
W80[1AW80]       Unlocked     Enabled     Disconnected  0                      A80     
W81[1AW81]       Unlocked     Enabled     Disconnected  0                      A81     
W82[1AW82]       Unlocked     Enabled     Disconnected  0                      A82     
W83[1AW83]       Unlocked     Enabled     Disconnected  0                      A83     
W84[1AW84]       Unlocked     Enabled     Disconnected  0                      A84     
W85[1AW85]       Unlocked     Enabled     Disconnected  0                      A85     
W86[1AW86]       Unlocked     Enabled     Disconnected  0                      A86     
W87[1AW87]       Unlocked     Enabled     Disconnected  0                      A87     
W88[1AW88]       Unlocked     Enabled     Disconnected  0                      A88     
W89[1AW89]       Unlocked     Enabled     Disconnected  0                      A89     
W90[1AW90]       Unlocked     Enabled     Disconnected  0                      A90     
W91[1AW91]       Unlocked     Enabled     Disconnected  0                      A91     
W92[1AW92]       Unlocked     Enabled     Disconnected  0                      A92     
W93[1AW93]       Unlocked     Enabled     Disconnected  0                      A93     
W94[1AW94]       Unlocked     Enabled     Disconnected  0                      A94     
W95[1AW95]       Unlocked     Enabled     Disconnected  0                      A95     
W96[1AW96]       Unlocked     Enabled     Disconnected  0                      A96     
W97[1AW97]       Unlocked     Enabled     Disconnected  0                      A97     
W98[1AW98]       Unlocked     Enabled     Disconnected  0                      A98     
W99[1AW99]       Unlocked     Enabled     Disconnected  0                      A99     
W100[1AW100]     Unlocked     Enabled     Disconnected  2                      A100    
W101[1AW101]     Unlocked     Enabled     Disconnected  0                      A101    
W102[1AW102]     Unlocked     Enabled     Disconnected  0                      A102    
W103[1AW103]     Unlocked     Enabled     Disconnected  0                      A103    
W104[1AW104]     Unlocked     Enabled     Disconnected  0                      A104    
W105[1AW105]     Unlocked     Enabled     Disconnected  0                      A105    
W106[1AW106]     Unlocked     Enabled     Disconnected  0                      A106    
W107[1AW107]     Unlocked     Enabled     Disconnected  0                      A107    
W108[1AW108]     Unlocked     Enabled     Disconnected  0                      A108    
W109[1AW109]     Unlocked     Enabled     Disconnected  0                      A109    
W110[1AW110]     Unlocked     Enabled     Disconnected  0                      A110    
W111[1AW111]     Unlocked     Enabled     Disconnected  0                      A111    
W112[1AW112]     Unlocked     Enabled     Disconnected  0                      A112    
W113[1AW113]     Unlocked     Enabled     Disconnected  0                      A113    
W114[1AW114]     Unlocked     Enabled     Disconnected  0                      A114    
W115[1AW115]     Unlocked     Enabled     Disconnected  0                      A115    
W116[1AW116]     Unlocked     Enabled     Disconnected  0                      A116    
W117[1AW117]     Unlocked     Enabled     Disconnected  0                      A117    
W118[1AW118]     Unlocked     Enabled     Disconnected  0                      A118    
W119[1AW119]     Unlocked     Enabled     Disconnected  2                      A119    
W120[1AW120]     Unlocked     Enabled     Disconnected  0                      A120    
W121[1AW121]     Unlocked     Enabled     Disconnected  0                      A121    
W122[1AW122]     Unlocked     Enabled     Disconnected  0                      A122    
W123[1AW123]     Unlocked     Enabled     Disconnected  0                      A123    
W124[1AW124]     Unlocked     Enabled     Disconnected  0                      A124    
W125[1AW125]     Unlocked     Enabled     Disconnected  0                      A125    
W126[1AW126]     Unlocked     Enabled     Disconnected  0                      A126    
W127[1AW127]     Unlocked     Enabled     Disconnected  0                      A127    
W128[1AW128]     Unlocked     Enabled     Disconnected  0                      A128    
1AW129           Unlocked     Enabled     Disconnected  0                              
1AW130           Unlocked     Enabled     Disconnected  0                              
1AW131           Unlocked     Enabled     Disconnected  0                              
1AW132           Unlocked     Enabled     Disconnected  0                              
W129[1BW1]       Unlocked     Enabled     Disconnected  0                      B129    
W130[1BW2]       Unlocked     Enabled     Disconnected  0                      B130    
W131[1BW3]       Unlocked     Enabled     Disconnected  0                      B131    
W132[1BW4]       Unlocked     Enabled     Disconnected  0                      B132    
W133[1BW5]       Unlocked     Enabled     Disconnected  0                      B133    
W134[1BW6]       Unlocked     Enabled     Disconnected  0                      B134    
W135[1BW7]       Unlocked     Enabled     Disconnected  0                      B135    
W136[1BW8]       Unlocked     Enabled     Disconnected  0                      B136    
W137[1BW9]       Unlocked     Enabled     Disconnected  0                      B137    
W138[1BW10]      Unlocked     Enabled     Disconnected  0                      B138    
W139[1BW11]      Unlocked     Enabled     Disconnected  0                      B139    
W140[1BW12]      Unlocked     Enabled     Disconnected  0                      B140    
W141[1BW13]      Unlocked     Enabled     Disconnected  2                      B141    
W142[1BW14]      Unlocked     Enabled     Disconnected  0                      B142    
W143[1BW15]      Unlocked     Enabled     Disconnected  2                      B143    
W144[1BW16]      Unlocked     Enabled     Disconnected  0                      B144    
W145[1BW17]      Unlocked     Enabled     Disconnected  0                      B145    
W146[1BW18]      Unlocked     Enabled     Disconnected  0                      B146    
W147[1BW19]      Unlocked     Enabled     Disconnected  0                      B147    
W148[1BW20]      Unlocked     Enabled     Disconnected  0                      B148    
W149[1BW21]      Unlocked     Enabled     Disconnected  0                      B149    
W150[1BW22]      Unlocked     Enabled     Disconnected  0                      B150    
W151[1BW23]      Unlocked     Enabled     Disconnected  0                      B151    
W152[1BW24]      Unlocked     Enabled     Disconnected  0                      B152    
W153[1BW25]      Unlocked     Enabled     Disconnected  0                      B153    
W154[1BW26]      Unlocked     Enabled     Disconnected  0                      B154    
W155[1BW27]      Unlocked     Enabled     Disconnected  0                      B155    
W156[1BW28]      Unlocked     Enabled     Disconnected  0                      B156    
W157[1BW29]      Unlocked     Enabled     Disconnected  0                      B157    
W158[1BW30]      Unlocked     Enabled     Disconnected  0                      B158    
W159[1BW31]      Unlocked     Enabled     Disconnected  0                      B159    
W160[1BW32]      Unlocked     Enabled     Disconnected  0                      B160    
W161[1BW33]      Unlocked     Enabled     Disconnected  0                      B161    
W162[1BW34]      Unlocked     Enabled     Disconnected  0                      B162    
W163[1BW35]      Unlocked     Enabled     Disconnected  0                      B163    
W164[1BW36]      Unlocked     Enabled     Disconnected  0                      B164    
W165[1BW37]      Unlocked     Enabled     Disconnected  0                      B165    
W166[1BW38]      Unlocked     Enabled     Disconnected  0                      B166    
W167[1BW39]      Unlocked     Enabled     Disconnected  0                      B167    
W168[1BW40]      Unlocked     Enabled     Disconnected  0                      B168    
W169[1BW41]      Unlocked     Enabled     Disconnected  0                      B169    
W170[1BW42]      Unlocked     Enabled     Disconnected  0                      B170    
W171[1BW43]      Unlocked     Enabled     Disconnected  0                      B171    
W172[1BW44]      Unlocked     Enabled     Disconnected  0                      B172    
W173[1BW45]      Unlocked     Enabled     Disconnected  0                      B173    
W174[1BW46]      Unlocked     Enabled     Disconnected  0                      B174    
W175[1BW47]      Unlocked     Enabled     Disconnected  0                      B175    
W176[1BW48]      Unlocked     Enabled     Disconnected  0                      B176    
W177[1BW49]      Unlocked     Enabled     Disconnected  0                      B177    
W178[1BW50]      Unlocked     Enabled     Disconnected  0                      B178    
W179[1BW51]      Unlocked     Enabled     Disconnected  0                      B179    
W180[1BW52]      Unlocked     Enabled     Disconnected  0                      B180    
W181[1BW53]      Unlocked     Enabled     Disconnected  0                      B181    
W182[1BW54]      Unlocked     Enabled     Disconnected  0                      B182    
W183[1BW55]      Unlocked     Enabled     Disconnected  0                      B183    
W184[1BW56]      Unlocked     Enabled     Disconnected  0                      B184    
W185[1BW57]      Unlocked     Enabled     Disconnected  0                      B185    
W186[1BW58]      Unlocked     Enabled     Disconnected  0                      B186    
W187[1BW59]      Unlocked     Enabled     Disconnected  0                      B187    
W188[1BW60]      Unlocked     Enabled     Disconnected  0                      B188    
W189[1BW61]      Unlocked     Enabled     Disconnected  0                      B189    
W190[1BW62]      Unlocked     Enabled     Disconnected  0                      B190    
W191[1BW63]      Unlocked     Enabled     Disconnected  0                      B191    
W192[1BW64]      Unlocked     Enabled     Disconnected  0                      B192    
W193[1BW65]      Unlocked     Enabled     Disconnected  0                      B193    
W194[1BW66]      Unlocked     Enabled     Disconnected  0                      B194    
W195[1BW67]      Unlocked     Enabled     Disconnected  0                      B195    
W196[1BW68]      Unlocked     Enabled     Disconnected  0                      B196    
W197[1BW69]      Unlocked     Enabled     Disconnected  0                      B197    
W198[1BW70]      Unlocked     Enabled     Disconnected  0                      B198    
W199[1BW71]      Unlocked     Enabled     Disconnected  0                      B199    
W200[1BW72]      Unlocked     Enabled     Disconnected  0                      B200    
W201[1BW73]      Unlocked     Enabled     Disconnected  0                      B201    
W202[1BW74]      Unlocked     Enabled     Disconnected  0                      B202    
W203[1BW75]      Unlocked     Enabled     Disconnected  0                      B203    
W204[1BW76]      Unlocked     Enabled     Disconnected  0                      B204    
W205[1BW77]      Unlocked     Enabled     Disconnected  0                      B205    
W206[1BW78]      Unlocked     Enabled     Disconnected  0                      B206    
W207[1BW79]      Unlocked     Enabled     Disconnected  0                      B207    
W208[1BW80]      Unlocked     Enabled     Disconnected  0                      B208    
W209[1BW81]      Unlocked     Enabled     Disconnected  0                      B209    
W210[1BW82]      Unlocked     Enabled     Disconnected  0                      B210    
W211[1BW83]      Unlocked     Enabled     Disconnected  0                      B211    
W212[1BW84]      Unlocked     Enabled     Disconnected  0                      B212    
W213[1BW85]      Unlocked     Enabled     Disconnected  0                      B213    
W214[1BW86]      Unlocked     Enabled     Disconnected  0                      B214    
W215[1BW87]      Unlocked     Enabled     Disconnected  0                      B215    
W216[1BW88]      Unlocked     Enabled     Disconnected  0                      B216    
W217[1BW89]      Unlocked     Enabled     Disconnected  0                      B217    
W218[1BW90]      Unlocked     Enabled     Disconnected  0                      B218    
W219[1BW91]      Unlocked     Enabled     Disconnected  0                      B219    
W220[1BW92]      Unlocked     Enabled     Disconnected  0                      B220    
W221[1BW93]      Unlocked     Enabled     Disconnected  0                      B221    
W222[1BW94]      Unlocked     Enabled     Disconnected  0                      B222    
W223[1BW95]      Unlocked     Enabled     Disconnected  0                      B223    
W224[1BW96]      Unlocked     Enabled     Disconnected  0                      B224    
W225[1BW97]      Unlocked     Enabled     Disconnected  0                      B225    
W226[1BW98]      Unlocked     Enabled     Disconnected  0                      B226    
W227[1BW99]      Unlocked     Enabled     Disconnected  0                      B227    
W228[1BW100]     Unlocked     Enabled     Disconnected  0                      B228    
W229[1BW101]     Unlocked     Enabled     Disconnected  0                      B229    
W230[1BW102]     Unlocked     Enabled     Disconnected  0                      B230    
W231[1BW103]     Unlocked     Enabled     Disconnected  0                      B231    
W232[1BW104]     Unlocked     Enabled     Disconnected  0                      B232    
W233[1BW105]     Unlocked     Enabled     Disconnected  0                      B233    
W234[1BW106]     Unlocked     Enabled     Disconnected  0                      B234    
W235[1BW107]     Unlocked     Enabled     Disconnected  2                      B235    
W236[1BW108]     Unlocked     Enabled     Disconnected  0                      B236    
W237[1BW109]     Unlocked     Enabled     Disconnected  2                      B237    
W238[1BW110]     Unlocked     Enabled     Disconnected  0                      B238    
W239[1BW111]     Unlocked     Enabled     Disconnected  0                      B239    
W240[1BW112]     Unlocked     Enabled     Disconnected  0                      B240    
W241[1BW113]     Unlocked     Enabled     Disconnected  0                      B241    
W242[1BW114]     Unlocked     Enabled     Disconnected  0                      B242    
W243[1BW115]     Unlocked     Enabled     Disconnected  0                      B243    
W244[1BW116]     Unlocked     Enabled     Disconnected  0                      B244    
W245[1BW117]     Unlocked     Enabled     Disconnected  0                      B245    
W246[1BW118]     Unlocked     Enabled     Disconnected  0                      B246    
W247[1BW119]     Unlocked     Enabled     Disconnected  0                      B247    
W248[1BW120]     Unlocked     Enabled     Disconnected  0                      B248    
W249[1BW121]     Unlocked     Enabled     Connected     13      E253[1BE125]   B249    
W250[1BW122]     Unlocked     Enabled     Disconnected  0                      B250    
W251[1BW123]     Unlocked     Enabled     Disconnected  0                      B251    
W252[1BW124]     Unlocked     Enabled     Disconnected  0                      B252    
W253[1BW125]     Unlocked     Enabled     Connected     13      E249[1BE121]   B253    
W254[1BW126]     Unlocked     Enabled     Disconnected  0                      B254    
W255[1BW127]     Unlocked     Enabled     Disconnected  0                      B255    
W256[1BW128]     Unlocked     Enabled     Disconnected  0                      B256    
1BW129           Unlocked     Enabled     Disconnected  0                              
1BW130           Unlocked     Enabled     Disconnected  0                              
1BW131           Unlocked     Enabled     Disconnected  0                              
1BW132           Unlocked     Enabled     Disconnected  0                              

ROME[OPER]# '''
PORT_SHOW_MATRIX_B = '''ROME[OPER]# port show                 
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
E1[1AE1]         Unlocked     Enabled     Disconnected  2                      A1      
E2[1AE2]         Unlocked     Enabled     Disconnected  0                      A2      
E3[1AE3]         Unlocked     Enabled     Disconnected  0                      A3      
E4[1AE4]         Unlocked     Enabled     Disconnected  0                      A4      
E5[1AE5]         Unlocked     Enabled     Disconnected  0                      A5      
E6[1AE6]         Unlocked     Enabled     Disconnected  0                      A6      
E7[1AE7]         Unlocked     Enabled     Disconnected  0                      A7      
E8[1AE8]         Unlocked     Enabled     Disconnected  0                      A8      
E9[1AE9]         Unlocked     Enabled     Disconnected  0                      A9      
E10[1AE10]       Unlocked     Enabled     Disconnected  0                      A10     
E11[1AE11]       Unlocked     Enabled     Disconnected  2                      A11     
E12[1AE12]       Unlocked     Enabled     Disconnected  0                      A12     
E13[1AE13]       Unlocked     Enabled     Disconnected  0                      A13     
E14[1AE14]       Unlocked     Enabled     Disconnected  0                      A14     
E15[1AE15]       Unlocked     Enabled     Disconnected  2                      A15     
E16[1AE16]       Unlocked     Enabled     Disconnected  0                      A16     
E17[1AE17]       Unlocked     Enabled     Disconnected  0                      A17     
E18[1AE18]       Unlocked     Enabled     Disconnected  2                      A18     
E19[1AE19]       Unlocked     Enabled     Disconnected  0                      A19     
E20[1AE20]       Unlocked     Enabled     Disconnected  0                      A20     
E21[1AE21]       Unlocked     Enabled     Disconnected  2                      A21     
E22[1AE22]       Unlocked     Enabled     Disconnected  0                      A22     
E23[1AE23]       Unlocked     Enabled     Disconnected  0                      A23     
E24[1AE24]       Unlocked     Enabled     Disconnected  2                      A24     
E25[1AE25]       Unlocked     Enabled     Disconnected  0                      A25     
E26[1AE26]       Unlocked     Enabled     Disconnected  0                      A26     
E27[1AE27]       Unlocked     Enabled     Disconnected  0                      A27     
E28[1AE28]       Unlocked     Enabled     Disconnected  0                      A28     
E29[1AE29]       Unlocked     Enabled     Disconnected  0                      A29     
E30[1AE30]       Unlocked     Enabled     Disconnected  0                      A30     
E31[1AE31]       Unlocked     Enabled     Disconnected  0                      A31     
E32[1AE32]       Unlocked     Enabled     Disconnected  0                      A32     
E33[1AE33]       Unlocked     Enabled     Disconnected  0                      A33     
E34[1AE34]       Unlocked     Enabled     Disconnected  0                      A34     
E35[1AE35]       Unlocked     Enabled     Disconnected  0                      A35     
E36[1AE36]       Unlocked     Enabled     Disconnected  0                      A36     
E37[1AE37]       Unlocked     Enabled     Disconnected  0                      A37     
E38[1AE38]       Unlocked     Enabled     Disconnected  0                      A38     
E39[1AE39]       Unlocked     Enabled     Disconnected  0                      A39     
E40[1AE40]       Unlocked     Enabled     Disconnected  0                      A40     
E41[1AE41]       Unlocked     Enabled     Disconnected  0                      A41     
E42[1AE42]       Unlocked     Enabled     Disconnected  0                      A42     
E43[1AE43]       Unlocked     Enabled     Disconnected  0                      A43     
E44[1AE44]       Unlocked     Enabled     Disconnected  0                      A44     
E45[1AE45]       Unlocked     Enabled     Disconnected  0                      A45     
E46[1AE46]       Unlocked     Enabled     Disconnected  0                      A46     
E47[1AE47]       Unlocked     Enabled     Disconnected  0                      A47     
E48[1AE48]       Unlocked     Enabled     Disconnected  0                      A48     
E49[1AE49]       Unlocked     Enabled     Disconnected  0                      A49     
E50[1AE50]       Unlocked     Enabled     Disconnected  0                      A50     
E51[1AE51]       Unlocked     Enabled     Disconnected  0                      A51     
E52[1AE52]       Unlocked     Enabled     Disconnected  0                      A52     
E53[1AE53]       Unlocked     Enabled     Disconnected  0                      A53     
E54[1AE54]       Unlocked     Enabled     Disconnected  0                      A54     
E55[1AE55]       Unlocked     Enabled     Disconnected  0                      A55     
E56[1AE56]       Unlocked     Enabled     Disconnected  0                      A56     
E57[1AE57]       Unlocked     Enabled     Disconnected  0                      A57     
E58[1AE58]       Unlocked     Enabled     Disconnected  0                      A58     
E59[1AE59]       Unlocked     Enabled     Disconnected  0                      A59     
E60[1AE60]       Unlocked     Enabled     Disconnected  0                      A60     
E61[1AE61]       Unlocked     Enabled     Disconnected  0                      A61     
E62[1AE62]       Unlocked     Enabled     Disconnected  0                      A62     
E63[1AE63]       Unlocked     Enabled     Disconnected  0                      A63     
E64[1AE64]       Unlocked     Enabled     Disconnected  0                      A64     
E65[1AE65]       Unlocked     Enabled     Disconnected  0                      A65     
E66[1AE66]       Unlocked     Enabled     Disconnected  0                      A66     
E67[1AE67]       Unlocked     Enabled     Disconnected  0                      A67     
E68[1AE68]       Unlocked     Enabled     Disconnected  0                      A68     
E69[1AE69]       Unlocked     Enabled     Disconnected  0                      A69     
E70[1AE70]       Unlocked     Enabled     Disconnected  0                      A70     
E71[1AE71]       Unlocked     Enabled     Disconnected  0                      A71     
E72[1AE72]       Unlocked     Enabled     Disconnected  0                      A72     
E73[1AE73]       Unlocked     Enabled     Disconnected  0                      A73     
E74[1AE74]       Unlocked     Enabled     Disconnected  0                      A74     
E75[1AE75]       Unlocked     Enabled     Disconnected  0                      A75     
E76[1AE76]       Unlocked     Enabled     Disconnected  0                      A76     
E77[1AE77]       Unlocked     Enabled     Disconnected  0                      A77     
E78[1AE78]       Unlocked     Enabled     Disconnected  0                      A78     
E79[1AE79]       Unlocked     Enabled     Disconnected  0                      A79     
E80[1AE80]       Unlocked     Enabled     Disconnected  0                      A80     
E81[1AE81]       Unlocked     Enabled     Disconnected  0                      A81     
E82[1AE82]       Unlocked     Enabled     Disconnected  0                      A82     
E83[1AE83]       Unlocked     Enabled     Disconnected  0                      A83     
E84[1AE84]       Unlocked     Enabled     Disconnected  0                      A84     
E85[1AE85]       Unlocked     Enabled     Disconnected  0                      A85     
E86[1AE86]       Unlocked     Enabled     Disconnected  0                      A86     
E87[1AE87]       Unlocked     Enabled     Disconnected  0                      A87     
E88[1AE88]       Unlocked     Enabled     Disconnected  0                      A88     
E89[1AE89]       Unlocked     Enabled     Disconnected  0                      A89     
E90[1AE90]       Unlocked     Enabled     Disconnected  0                      A90     
E91[1AE91]       Unlocked     Enabled     Disconnected  0                      A91     
E92[1AE92]       Unlocked     Enabled     Disconnected  0                      A92     
E93[1AE93]       Unlocked     Enabled     Disconnected  0                      A93     
E94[1AE94]       Unlocked     Enabled     Disconnected  0                      A94     
E95[1AE95]       Unlocked     Enabled     Disconnected  0                      A95     
E96[1AE96]       Unlocked     Enabled     Disconnected  0                      A96     
E97[1AE97]       Unlocked     Enabled     Disconnected  0                      A97     
E98[1AE98]       Unlocked     Enabled     Disconnected  0                      A98     
E99[1AE99]       Unlocked     Enabled     Disconnected  0                      A99     
E100[1AE100]     Unlocked     Enabled     Disconnected  0                      A100    
E101[1AE101]     Unlocked     Enabled     Disconnected  0                      A101    
E102[1AE102]     Unlocked     Enabled     Disconnected  0                      A102    
E103[1AE103]     Unlocked     Enabled     Disconnected  0                      A103    
E104[1AE104]     Unlocked     Enabled     Disconnected  0                      A104    
E105[1AE105]     Unlocked     Enabled     Disconnected  0                      A105    
E106[1AE106]     Unlocked     Enabled     Disconnected  0                      A106    
E107[1AE107]     Unlocked     Enabled     Disconnected  0                      A107    
E108[1AE108]     Unlocked     Enabled     Disconnected  0                      A108    
E109[1AE109]     Unlocked     Enabled     Disconnected  0                      A109    
E110[1AE110]     Unlocked     Enabled     Disconnected  0                      A110    
E111[1AE111]     Unlocked     Enabled     Disconnected  0                      A111    
E112[1AE112]     Unlocked     Enabled     Disconnected  0                      A112    
E113[1AE113]     Unlocked     Enabled     Disconnected  0                      A113    
E114[1AE114]     Unlocked     Enabled     Disconnected  0                      A114    
E115[1AE115]     Unlocked     Enabled     Disconnected  0                      A115    
E116[1AE116]     Unlocked     Enabled     Disconnected  0                      A116    
E117[1AE117]     Unlocked     Enabled     Disconnected  0                      A117    
E118[1AE118]     Unlocked     Enabled     Disconnected  0                      A118    
E119[1AE119]     Unlocked     Enabled     Disconnected  0                      A119    
E120[1AE120]     Unlocked     Enabled     Disconnected  0                      A120    
E121[1AE121]     Unlocked     Enabled     Disconnected  0                      A121    
E122[1AE122]     Unlocked     Enabled     Disconnected  0                      A122    
E123[1AE123]     Unlocked     Enabled     Disconnected  0                      A123    
E124[1AE124]     Unlocked     Enabled     Disconnected  0                      A124    
E125[1AE125]     Unlocked     Enabled     Disconnected  0                      A125    
E126[1AE126]     Unlocked     Enabled     Disconnected  0                      A126    
E127[1AE127]     Unlocked     Enabled     Disconnected  0                      A127    
E128[1AE128]     Unlocked     Enabled     Disconnected  0                      A128    
1AE129           Unlocked     Enabled     Disconnected  0                              
1AE130           Unlocked     Enabled     Disconnected  0                              
E129[1BE1]       Unlocked     Enabled     Disconnected  0                      B129    
E130[1BE2]       Unlocked     Enabled     Disconnected  0                      B130    
E131[1BE3]       Unlocked     Enabled     Disconnected  0                      B131    
E132[1BE4]       Unlocked     Enabled     Disconnected  0                      B132    
E133[1BE5]       Unlocked     Enabled     Disconnected  0                      B133    
E134[1BE6]       Unlocked     Enabled     Disconnected  0                      B134    
E135[1BE7]       Unlocked     Enabled     Disconnected  0                      B135    
E136[1BE8]       Unlocked     Enabled     Disconnected  0                      B136    
E137[1BE9]       Unlocked     Enabled     Disconnected  0                      B137    
E138[1BE10]      Unlocked     Enabled     Disconnected  0                      B138    
E139[1BE11]      Unlocked     Enabled     Disconnected  0                      B139    
E140[1BE12]      Unlocked     Enabled     Disconnected  0                      B140    
E141[1BE13]      Unlocked     Enabled     Disconnected  2                      B141    
E142[1BE14]      Unlocked     Enabled     Disconnected  0                      B142    
E143[1BE15]      Unlocked     Enabled     Disconnected  2                      B143    
E144[1BE16]      Unlocked     Enabled     Disconnected  0                      B144    
E145[1BE17]      Unlocked     Enabled     Disconnected  0                      B145    
E146[1BE18]      Unlocked     Enabled     Disconnected  0                      B146    
E147[1BE19]      Unlocked     Enabled     Disconnected  0                      B147    
E148[1BE20]      Unlocked     Enabled     Disconnected  0                      B148    
E149[1BE21]      Unlocked     Enabled     Disconnected  0                      B149    
E150[1BE22]      Unlocked     Enabled     Disconnected  0                      B150    
E151[1BE23]      Unlocked     Enabled     Disconnected  0                      B151    
E152[1BE24]      Unlocked     Enabled     Disconnected  0                      B152    
E153[1BE25]      Unlocked     Enabled     Disconnected  0                      B153    
E154[1BE26]      Unlocked     Enabled     Disconnected  0                      B154    
E155[1BE27]      Unlocked     Enabled     Disconnected  0                      B155    
E156[1BE28]      Unlocked     Enabled     Disconnected  0                      B156    
E157[1BE29]      Unlocked     Enabled     Disconnected  0                      B157    
E158[1BE30]      Unlocked     Enabled     Disconnected  0                      B158    
E159[1BE31]      Unlocked     Enabled     Disconnected  0                      B159    
E160[1BE32]      Unlocked     Enabled     Disconnected  0                      B160    
E161[1BE33]      Unlocked     Enabled     Disconnected  0                      B161    
E162[1BE34]      Unlocked     Enabled     Disconnected  0                      B162    
E163[1BE35]      Unlocked     Enabled     Disconnected  0                      B163    
E164[1BE36]      Unlocked     Enabled     Disconnected  0                      B164    
E165[1BE37]      Unlocked     Enabled     Disconnected  0                      B165    
E166[1BE38]      Unlocked     Enabled     Disconnected  0                      B166    
E167[1BE39]      Unlocked     Enabled     Disconnected  0                      B167    
E168[1BE40]      Unlocked     Enabled     Disconnected  0                      B168    
E169[1BE41]      Unlocked     Enabled     Disconnected  0                      B169    
E170[1BE42]      Unlocked     Enabled     Disconnected  0                      B170    
E171[1BE43]      Unlocked     Enabled     Disconnected  0                      B171    
E172[1BE44]      Unlocked     Enabled     Disconnected  0                      B172    
E173[1BE45]      Unlocked     Enabled     Disconnected  0                      B173    
E174[1BE46]      Unlocked     Enabled     Disconnected  0                      B174    
E175[1BE47]      Unlocked     Enabled     Disconnected  0                      B175    
E176[1BE48]      Unlocked     Enabled     Disconnected  0                      B176    
E177[1BE49]      Unlocked     Enabled     Disconnected  0                      B177    
E178[1BE50]      Unlocked     Enabled     Disconnected  0                      B178    
E179[1BE51]      Unlocked     Enabled     Disconnected  0                      B179    
E180[1BE52]      Unlocked     Enabled     Disconnected  0                      B180    
E181[1BE53]      Unlocked     Enabled     Disconnected  0                      B181    
E182[1BE54]      Unlocked     Enabled     Disconnected  0                      B182    
E183[1BE55]      Unlocked     Enabled     Disconnected  0                      B183    
E184[1BE56]      Unlocked     Enabled     Disconnected  0                      B184    
E185[1BE57]      Unlocked     Enabled     Disconnected  0                      B185    
E186[1BE58]      Unlocked     Enabled     Disconnected  0                      B186    
E187[1BE59]      Unlocked     Enabled     Disconnected  0                      B187    
E188[1BE60]      Unlocked     Enabled     Disconnected  0                      B188    
E189[1BE61]      Unlocked     Enabled     Disconnected  0                      B189    
E190[1BE62]      Unlocked     Enabled     Disconnected  0                      B190    
E191[1BE63]      Unlocked     Enabled     Disconnected  0                      B191    
E192[1BE64]      Unlocked     Enabled     Disconnected  0                      B192    
E193[1BE65]      Unlocked     Enabled     Disconnected  0                      B193    
E194[1BE66]      Unlocked     Enabled     Disconnected  0                      B194    
E195[1BE67]      Unlocked     Enabled     Disconnected  0                      B195    
E196[1BE68]      Unlocked     Enabled     Disconnected  0                      B196    
E197[1BE69]      Unlocked     Enabled     Disconnected  0                      B197    
E198[1BE70]      Unlocked     Enabled     Disconnected  0                      B198    
E199[1BE71]      Unlocked     Enabled     Disconnected  0                      B199    
E200[1BE72]      Unlocked     Enabled     Disconnected  0                      B200    
E201[1BE73]      Unlocked     Enabled     Disconnected  0                      B201    
E202[1BE74]      Unlocked     Enabled     Disconnected  0                      B202    
E203[1BE75]      Unlocked     Enabled     Disconnected  0                      B203    
E204[1BE76]      Unlocked     Enabled     Disconnected  0                      B204    
E205[1BE77]      Unlocked     Enabled     Disconnected  0                      B205    
E206[1BE78]      Unlocked     Enabled     Disconnected  0                      B206    
E207[1BE79]      Unlocked     Enabled     Disconnected  0                      B207    
E208[1BE80]      Unlocked     Enabled     Disconnected  0                      B208    
E209[1BE81]      Unlocked     Enabled     Disconnected  0                      B209    
E210[1BE82]      Unlocked     Enabled     Disconnected  0                      B210    
E211[1BE83]      Unlocked     Enabled     Disconnected  0                      B211    
E212[1BE84]      Unlocked     Enabled     Disconnected  0                      B212    
E213[1BE85]      Unlocked     Enabled     Disconnected  0                      B213    
E214[1BE86]      Unlocked     Enabled     Disconnected  0                      B214    
E215[1BE87]      Unlocked     Enabled     Disconnected  0                      B215    
E216[1BE88]      Unlocked     Enabled     Disconnected  0                      B216    
E217[1BE89]      Unlocked     Enabled     Disconnected  0                      B217    
E218[1BE90]      Unlocked     Enabled     Disconnected  0                      B218    
E219[1BE91]      Unlocked     Enabled     Disconnected  0                      B219    
E220[1BE92]      Unlocked     Enabled     Disconnected  0                      B220    
E221[1BE93]      Unlocked     Enabled     Disconnected  0                      B221    
E222[1BE94]      Unlocked     Enabled     Disconnected  0                      B222    
E223[1BE95]      Unlocked     Enabled     Disconnected  0                      B223    
E224[1BE96]      Unlocked     Enabled     Disconnected  0                      B224    
E225[1BE97]      Unlocked     Enabled     Disconnected  0                      B225    
E226[1BE98]      Unlocked     Enabled     Disconnected  0                      B226    
E227[1BE99]      Unlocked     Enabled     Disconnected  0                      B227    
E228[1BE100]     Unlocked     Enabled     Disconnected  0                      B228    
E229[1BE101]     Unlocked     Enabled     Disconnected  0                      B229    
E230[1BE102]     Unlocked     Enabled     Disconnected  0                      B230    
E231[1BE103]     Unlocked     Enabled     Disconnected  0                      B231    
E232[1BE104]     Unlocked     Enabled     Disconnected  0                      B232    
E233[1BE105]     Unlocked     Enabled     Disconnected  0                      B233    
E234[1BE106]     Unlocked     Enabled     Disconnected  0                      B234    
E235[1BE107]     Unlocked     Enabled     Disconnected  2                      B235    
E236[1BE108]     Unlocked     Enabled     Disconnected  0                      B236    
E237[1BE109]     Unlocked     Enabled     Disconnected  2                      B237    
E238[1BE110]     Unlocked     Enabled     Disconnected  0                      B238    
E239[1BE111]     Unlocked     Enabled     Disconnected  0                      B239    
E240[1BE112]     Unlocked     Enabled     Disconnected  0                      B240    
E241[1BE113]     Unlocked     Enabled     Disconnected  0                      B241    
E242[1BE114]     Unlocked     Enabled     Disconnected  0                      B242    
E243[1BE115]     Unlocked     Enabled     Disconnected  0                      B243    
E244[1BE116]     Unlocked     Enabled     Disconnected  0                      B244    
E245[1BE117]     Unlocked     Enabled     Disconnected  0                      B245    
E246[1BE118]     Unlocked     Enabled     Disconnected  0       W247[1BW247]   B246    
E247[1BE119]     Unlocked     Enabled     Disconnected  0                      B247    
E248[1BE120]     Unlocked     Enabled     Disconnected  0                      B248    
E249[1BE121]     Unlocked     Enabled     Connected     13      W253[1BW125]   B249    
E250[1BE122]     Unlocked     Enabled     Disconnected  0                      B250    
E251[1BE123]     Unlocked     Enabled     Disconnected  0                      B251    
E252[1BE124]     Unlocked     Enabled     Disconnected  0                      B252    
E253[1BE125]     Unlocked     Enabled     Connected     13      W249[1BW121]   B253    
E254[1BE126]     Unlocked     Enabled     Disconnected  0                      B254    
E255[1BE127]     Unlocked     Enabled     Disconnected  0                      B255    
E256[1BE128]     Unlocked     Enabled     Disconnected  0                      B256    
1BE129           Unlocked     Enabled     Disconnected  0                              
1BE130           Unlocked     Enabled     Disconnected  0                              
W1[1AW1]         Unlocked     Enabled     Disconnected  0                      A1      
W2[1AW2]         Unlocked     Enabled     Disconnected  0                      A2      
W3[1AW3]         Unlocked     Enabled     Disconnected  0                      A3      
W4[1AW4]         Unlocked     Enabled     Disconnected  0                      A4      
W5[1AW5]         Unlocked     Enabled     Disconnected  0                      A5      
W6[1AW6]         Unlocked     Enabled     Disconnected  0                      A6      
W7[1AW7]         Unlocked     Enabled     Disconnected  0                      A7      
W8[1AW8]         Unlocked     Enabled     Disconnected  0                      A8      
W9[1AW9]         Unlocked     Enabled     Disconnected  0                      A9      
W10[1AW10]       Unlocked     Enabled     Disconnected  2                      A10     
W11[1AW11]       Unlocked     Enabled     Disconnected  0                      A11     
W12[1AW12]       Unlocked     Enabled     Disconnected  0                      A12     
W13[1AW13]       Unlocked     Enabled     Disconnected  0                      A13     
W14[1AW14]       Unlocked     Enabled     Disconnected  0                      A14     
W15[1AW15]       Unlocked     Enabled     Disconnected  0                      A15     
W16[1AW16]       Unlocked     Enabled     Disconnected  0                      A16     
W17[1AW17]       Unlocked     Enabled     Disconnected  0                      A17     
W18[1AW18]       Unlocked     Enabled     Disconnected  0                      A18     
W19[1AW19]       Unlocked     Enabled     Disconnected  0                      A19     
W20[1AW20]       Unlocked     Enabled     Disconnected  0                      A20     
W21[1AW21]       Unlocked     Enabled     Disconnected  0                      A21     
W22[1AW22]       Unlocked     Enabled     Disconnected  0                      A22     
W23[1AW23]       Unlocked     Enabled     Disconnected  0                      A23     
W24[1AW24]       Unlocked     Enabled     Disconnected  0                      A24     
W25[1AW25]       Unlocked     Enabled     Disconnected  2                      A25     
W26[1AW26]       Unlocked     Enabled     Disconnected  0                      A26     
W27[1AW27]       Unlocked     Enabled     Disconnected  0                      A27     
W28[1AW28]       Unlocked     Enabled     Disconnected  0                      A28     
W29[1AW29]       Unlocked     Enabled     Disconnected  0                      A29     
W30[1AW30]       Unlocked     Enabled     Disconnected  0                      A30     
W31[1AW31]       Unlocked     Enabled     Disconnected  0                      A31     
W32[1AW32]       Unlocked     Enabled     Disconnected  0                      A32     
W33[1AW33]       Unlocked     Enabled     Disconnected  0                      A33     
W34[1AW34]       Unlocked     Enabled     Disconnected  0                      A34     
W35[1AW35]       Unlocked     Enabled     Disconnected  0                      A35     
W36[1AW36]       Unlocked     Enabled     Disconnected  0                      A36     
W37[1AW37]       Unlocked     Enabled     Disconnected  0                      A37     
W38[1AW38]       Unlocked     Enabled     Disconnected  0                      A38     
W39[1AW39]       Unlocked     Enabled     Disconnected  0                      A39     
W40[1AW40]       Unlocked     Enabled     Disconnected  0                      A40     
W41[1AW41]       Unlocked     Enabled     Disconnected  0                      A41     
W42[1AW42]       Unlocked     Enabled     Disconnected  0                      A42     
W43[1AW43]       Unlocked     Enabled     Disconnected  0                      A43     
W44[1AW44]       Unlocked     Enabled     Disconnected  0                      A44     
W45[1AW45]       Unlocked     Enabled     Disconnected  0                      A45     
W46[1AW46]       Unlocked     Enabled     Disconnected  0                      A46     
W47[1AW47]       Unlocked     Enabled     Disconnected  0                      A47     
W48[1AW48]       Unlocked     Enabled     Disconnected  0                      A48     
W49[1AW49]       Unlocked     Enabled     Disconnected  0                      A49     
W50[1AW50]       Unlocked     Enabled     Disconnected  2                      A50     
W51[1AW51]       Unlocked     Enabled     Disconnected  0                      A51     
W52[1AW52]       Unlocked     Enabled     Disconnected  0                      A52     
W53[1AW53]       Unlocked     Enabled     Disconnected  0                      A53     
W54[1AW54]       Unlocked     Enabled     Disconnected  0                      A54     
W55[1AW55]       Unlocked     Enabled     Disconnected  0                      A55     
W56[1AW56]       Unlocked     Enabled     Disconnected  0                      A56     
W57[1AW57]       Unlocked     Enabled     Disconnected  0                      A57     
W58[1AW58]       Unlocked     Enabled     Disconnected  0                      A58     
W59[1AW59]       Unlocked     Enabled     Disconnected  0                      A59     
W60[1AW60]       Unlocked     Enabled     Disconnected  2                      A60     
W61[1AW61]       Unlocked     Enabled     Disconnected  0                      A61     
W62[1AW62]       Unlocked     Enabled     Disconnected  0                      A62     
W63[1AW63]       Unlocked     Enabled     Disconnected  0                      A63     
W64[1AW64]       Unlocked     Enabled     Disconnected  0                      A64     
W65[1AW65]       Unlocked     Enabled     Disconnected  0                      A65     
W66[1AW66]       Unlocked     Enabled     Disconnected  0                      A66     
W67[1AW67]       Unlocked     Enabled     Disconnected  0                      A67     
W68[1AW68]       Unlocked     Enabled     Disconnected  0                      A68     
W69[1AW69]       Unlocked     Enabled     Disconnected  0                      A69     
W70[1AW70]       Unlocked     Enabled     Disconnected  0                      A70     
W71[1AW71]       Unlocked     Enabled     Disconnected  0                      A71     
W72[1AW72]       Unlocked     Enabled     Disconnected  0                      A72     
W73[1AW73]       Unlocked     Enabled     Disconnected  0                      A73     
W74[1AW74]       Unlocked     Enabled     Disconnected  0                      A74     
W75[1AW75]       Unlocked     Enabled     Disconnected  0                      A75     
W76[1AW76]       Unlocked     Enabled     Disconnected  0                      A76     
W77[1AW77]       Unlocked     Enabled     Disconnected  0                      A77     
W78[1AW78]       Unlocked     Enabled     Disconnected  0                      A78     
W79[1AW79]       Unlocked     Enabled     Disconnected  0                      A79     
W80[1AW80]       Unlocked     Enabled     Disconnected  0                      A80     
W81[1AW81]       Unlocked     Enabled     Disconnected  0                      A81     
W82[1AW82]       Unlocked     Enabled     Disconnected  0                      A82     
W83[1AW83]       Unlocked     Enabled     Disconnected  0                      A83     
W84[1AW84]       Unlocked     Enabled     Disconnected  0                      A84     
W85[1AW85]       Unlocked     Enabled     Disconnected  0                      A85     
W86[1AW86]       Unlocked     Enabled     Disconnected  0                      A86     
W87[1AW87]       Unlocked     Enabled     Disconnected  0                      A87     
W88[1AW88]       Unlocked     Enabled     Disconnected  0                      A88     
W89[1AW89]       Unlocked     Enabled     Disconnected  0                      A89     
W90[1AW90]       Unlocked     Enabled     Disconnected  0                      A90     
W91[1AW91]       Unlocked     Enabled     Disconnected  0                      A91     
W92[1AW92]       Unlocked     Enabled     Disconnected  0                      A92     
W93[1AW93]       Unlocked     Enabled     Disconnected  0                      A93     
W94[1AW94]       Unlocked     Enabled     Disconnected  0                      A94     
W95[1AW95]       Unlocked     Enabled     Disconnected  0                      A95     
W96[1AW96]       Unlocked     Enabled     Disconnected  0                      A96     
W97[1AW97]       Unlocked     Enabled     Disconnected  0                      A97     
W98[1AW98]       Unlocked     Enabled     Disconnected  0                      A98     
W99[1AW99]       Unlocked     Enabled     Disconnected  0                      A99     
W100[1AW100]     Unlocked     Enabled     Disconnected  2                      A100    
W101[1AW101]     Unlocked     Enabled     Disconnected  0                      A101    
W102[1AW102]     Unlocked     Enabled     Disconnected  0                      A102    
W103[1AW103]     Unlocked     Enabled     Disconnected  0                      A103    
W104[1AW104]     Unlocked     Enabled     Disconnected  0                      A104    
W105[1AW105]     Unlocked     Enabled     Disconnected  0                      A105    
W106[1AW106]     Unlocked     Enabled     Disconnected  0                      A106    
W107[1AW107]     Unlocked     Enabled     Disconnected  0                      A107    
W108[1AW108]     Unlocked     Enabled     Disconnected  0                      A108    
W109[1AW109]     Unlocked     Enabled     Disconnected  0                      A109    
W110[1AW110]     Unlocked     Enabled     Disconnected  0                      A110    
W111[1AW111]     Unlocked     Enabled     Disconnected  0                      A111    
W112[1AW112]     Unlocked     Enabled     Disconnected  0                      A112    
W113[1AW113]     Unlocked     Enabled     Disconnected  0                      A113    
W114[1AW114]     Unlocked     Enabled     Disconnected  0                      A114    
W115[1AW115]     Unlocked     Enabled     Disconnected  0                      A115    
W116[1AW116]     Unlocked     Enabled     Disconnected  0                      A116    
W117[1AW117]     Unlocked     Enabled     Disconnected  0                      A117    
W118[1AW118]     Unlocked     Enabled     Disconnected  0                      A118    
W119[1AW119]     Unlocked     Enabled     Disconnected  2                      A119    
W120[1AW120]     Unlocked     Enabled     Disconnected  0                      A120    
W121[1AW121]     Unlocked     Enabled     Disconnected  0                      A121    
W122[1AW122]     Unlocked     Enabled     Disconnected  0                      A122    
W123[1AW123]     Unlocked     Enabled     Disconnected  0                      A123    
W124[1AW124]     Unlocked     Enabled     Disconnected  0                      A124    
W125[1AW125]     Unlocked     Enabled     Disconnected  0                      A125    
W126[1AW126]     Unlocked     Enabled     Disconnected  0                      A126    
W127[1AW127]     Unlocked     Enabled     Disconnected  0                      A127    
W128[1AW128]     Unlocked     Enabled     Disconnected  0                      A128    
1AW129           Unlocked     Enabled     Disconnected  0                              
1AW130           Unlocked     Enabled     Disconnected  0                              
1AW131           Unlocked     Enabled     Disconnected  0                              
1AW132           Unlocked     Enabled     Disconnected  0                              
W129[1BW1]       Unlocked     Enabled     Disconnected  0                      B129    
W130[1BW2]       Unlocked     Enabled     Disconnected  0                      B130    
W131[1BW3]       Unlocked     Enabled     Disconnected  0                      B131    
W132[1BW4]       Unlocked     Enabled     Disconnected  0                      B132    
W133[1BW5]       Unlocked     Enabled     Disconnected  0                      B133    
W134[1BW6]       Unlocked     Enabled     Disconnected  0                      B134    
W135[1BW7]       Unlocked     Enabled     Disconnected  0                      B135    
W136[1BW8]       Unlocked     Enabled     Disconnected  0                      B136    
W137[1BW9]       Unlocked     Enabled     Disconnected  0                      B137    
W138[1BW10]      Unlocked     Enabled     Disconnected  0                      B138    
W139[1BW11]      Unlocked     Enabled     Disconnected  0                      B139    
W140[1BW12]      Unlocked     Enabled     Disconnected  0                      B140    
W141[1BW13]      Unlocked     Enabled     Disconnected  2                      B141    
W142[1BW14]      Unlocked     Enabled     Disconnected  0                      B142    
W143[1BW15]      Unlocked     Enabled     Disconnected  2                      B143    
W144[1BW16]      Unlocked     Enabled     Disconnected  0                      B144    
W145[1BW17]      Unlocked     Enabled     Disconnected  0                      B145    
W146[1BW18]      Unlocked     Enabled     Disconnected  0                      B146    
W147[1BW19]      Unlocked     Enabled     Disconnected  0                      B147    
W148[1BW20]      Unlocked     Enabled     Disconnected  0                      B148    
W149[1BW21]      Unlocked     Enabled     Disconnected  0                      B149    
W150[1BW22]      Unlocked     Enabled     Disconnected  0                      B150    
W151[1BW23]      Unlocked     Enabled     Disconnected  0                      B151    
W152[1BW24]      Unlocked     Enabled     Disconnected  0                      B152    
W153[1BW25]      Unlocked     Enabled     Disconnected  0                      B153    
W154[1BW26]      Unlocked     Enabled     Disconnected  0                      B154    
W155[1BW27]      Unlocked     Enabled     Disconnected  0                      B155    
W156[1BW28]      Unlocked     Enabled     Disconnected  0                      B156    
W157[1BW29]      Unlocked     Enabled     Disconnected  0                      B157    
W158[1BW30]      Unlocked     Enabled     Disconnected  0                      B158    
W159[1BW31]      Unlocked     Enabled     Disconnected  0                      B159    
W160[1BW32]      Unlocked     Enabled     Disconnected  0                      B160    
W161[1BW33]      Unlocked     Enabled     Disconnected  0                      B161    
W162[1BW34]      Unlocked     Enabled     Disconnected  0                      B162    
W163[1BW35]      Unlocked     Enabled     Disconnected  0                      B163    
W164[1BW36]      Unlocked     Enabled     Disconnected  0                      B164    
W165[1BW37]      Unlocked     Enabled     Disconnected  0                      B165    
W166[1BW38]      Unlocked     Enabled     Disconnected  0                      B166    
W167[1BW39]      Unlocked     Enabled     Disconnected  0                      B167    
W168[1BW40]      Unlocked     Enabled     Disconnected  0                      B168    
W169[1BW41]      Unlocked     Enabled     Disconnected  0                      B169    
W170[1BW42]      Unlocked     Enabled     Disconnected  0                      B170    
W171[1BW43]      Unlocked     Enabled     Disconnected  0                      B171    
W172[1BW44]      Unlocked     Enabled     Disconnected  0                      B172    
W173[1BW45]      Unlocked     Enabled     Disconnected  0                      B173    
W174[1BW46]      Unlocked     Enabled     Disconnected  0                      B174    
W175[1BW47]      Unlocked     Enabled     Disconnected  0                      B175    
W176[1BW48]      Unlocked     Enabled     Disconnected  0                      B176    
W177[1BW49]      Unlocked     Enabled     Disconnected  0                      B177    
W178[1BW50]      Unlocked     Enabled     Disconnected  0                      B178    
W179[1BW51]      Unlocked     Enabled     Disconnected  0                      B179    
W180[1BW52]      Unlocked     Enabled     Disconnected  0                      B180    
W181[1BW53]      Unlocked     Enabled     Disconnected  0                      B181    
W182[1BW54]      Unlocked     Enabled     Disconnected  0                      B182    
W183[1BW55]      Unlocked     Enabled     Disconnected  0                      B183    
W184[1BW56]      Unlocked     Enabled     Disconnected  0                      B184    
W185[1BW57]      Unlocked     Enabled     Disconnected  0                      B185    
W186[1BW58]      Unlocked     Enabled     Disconnected  0                      B186    
W187[1BW59]      Unlocked     Enabled     Disconnected  0                      B187    
W188[1BW60]      Unlocked     Enabled     Disconnected  0                      B188    
W189[1BW61]      Unlocked     Enabled     Disconnected  0                      B189    
W190[1BW62]      Unlocked     Enabled     Disconnected  0                      B190    
W191[1BW63]      Unlocked     Enabled     Disconnected  0                      B191    
W192[1BW64]      Unlocked     Enabled     Disconnected  0                      B192    
W193[1BW65]      Unlocked     Enabled     Disconnected  0                      B193    
W194[1BW66]      Unlocked     Enabled     Disconnected  0                      B194    
W195[1BW67]      Unlocked     Enabled     Disconnected  0                      B195    
W196[1BW68]      Unlocked     Enabled     Disconnected  0                      B196    
W197[1BW69]      Unlocked     Enabled     Disconnected  0                      B197    
W198[1BW70]      Unlocked     Enabled     Disconnected  0                      B198    
W199[1BW71]      Unlocked     Enabled     Disconnected  0                      B199    
W200[1BW72]      Unlocked     Enabled     Disconnected  0                      B200    
W201[1BW73]      Unlocked     Enabled     Disconnected  0                      B201    
W202[1BW74]      Unlocked     Enabled     Disconnected  0                      B202    
W203[1BW75]      Unlocked     Enabled     Disconnected  0                      B203    
W204[1BW76]      Unlocked     Enabled     Disconnected  0                      B204    
W205[1BW77]      Unlocked     Enabled     Disconnected  0                      B205    
W206[1BW78]      Unlocked     Enabled     Disconnected  0                      B206    
W207[1BW79]      Unlocked     Enabled     Disconnected  0                      B207    
W208[1BW80]      Unlocked     Enabled     Disconnected  0                      B208    
W209[1BW81]      Unlocked     Enabled     Disconnected  0                      B209    
W210[1BW82]      Unlocked     Enabled     Disconnected  0                      B210    
W211[1BW83]      Unlocked     Enabled     Disconnected  0                      B211    
W212[1BW84]      Unlocked     Enabled     Disconnected  0                      B212    
W213[1BW85]      Unlocked     Enabled     Disconnected  0                      B213    
W214[1BW86]      Unlocked     Enabled     Disconnected  0                      B214    
W215[1BW87]      Unlocked     Enabled     Disconnected  0                      B215    
W216[1BW88]      Unlocked     Enabled     Disconnected  0                      B216    
W217[1BW89]      Unlocked     Enabled     Disconnected  0                      B217    
W218[1BW90]      Unlocked     Enabled     Disconnected  0                      B218    
W219[1BW91]      Unlocked     Enabled     Disconnected  0                      B219    
W220[1BW92]      Unlocked     Enabled     Disconnected  0                      B220    
W221[1BW93]      Unlocked     Enabled     Disconnected  0                      B221    
W222[1BW94]      Unlocked     Enabled     Disconnected  0                      B222    
W223[1BW95]      Unlocked     Enabled     Disconnected  0                      B223    
W224[1BW96]      Unlocked     Enabled     Disconnected  0                      B224    
W225[1BW97]      Unlocked     Enabled     Disconnected  0                      B225    
W226[1BW98]      Unlocked     Enabled     Disconnected  0                      B226    
W227[1BW99]      Unlocked     Enabled     Disconnected  0                      B227    
W228[1BW100]     Unlocked     Enabled     Disconnected  0                      B228    
W229[1BW101]     Unlocked     Enabled     Disconnected  0                      B229    
W230[1BW102]     Unlocked     Enabled     Disconnected  0                      B230    
W231[1BW103]     Unlocked     Enabled     Disconnected  0                      B231    
W232[1BW104]     Unlocked     Enabled     Disconnected  0                      B232    
W233[1BW105]     Unlocked     Enabled     Disconnected  0                      B233    
W234[1BW106]     Unlocked     Enabled     Disconnected  0                      B234    
W235[1BW107]     Unlocked     Enabled     Disconnected  2                      B235    
W236[1BW108]     Unlocked     Enabled     Disconnected  0                      B236    
W237[1BW109]     Unlocked     Enabled     Disconnected  2                      B237    
W238[1BW110]     Unlocked     Enabled     Disconnected  0                      B238    
W239[1BW111]     Unlocked     Enabled     Disconnected  0                      B239    
W240[1BW112]     Unlocked     Enabled     Disconnected  0                      B240    
W241[1BW113]     Unlocked     Enabled     Disconnected  0                      B241    
W242[1BW114]     Unlocked     Enabled     Disconnected  0                      B242    
W243[1BW115]     Unlocked     Enabled     Disconnected  0                      B243    
W244[1BW116]     Unlocked     Enabled     Disconnected  0                      B244    
W245[1BW117]     Unlocked     Enabled     Disconnected  0                      B245    
W246[1BW118]     Unlocked     Enabled     Disconnected  0                      B246    
W247[1BW119]     Unlocked     Enabled     Disconnected  0       E246[1BW246]   B247    
W248[1BW120]     Unlocked     Enabled     Disconnected  0                      B248    
W249[1BW121]     Unlocked     Enabled     Connected     13      E253[1BE125]   B249    
W250[1BW122]     Unlocked     Enabled     Disconnected  0                      B250    
W251[1BW123]     Unlocked     Enabled     Disconnected  0                      B251    
W252[1BW124]     Unlocked     Enabled     Disconnected  0                      B252    
W253[1BW125]     Unlocked     Enabled     Connected     13      E249[1BE121]   B253    
W254[1BW126]     Unlocked     Enabled     Disconnected  0                      B254    
W255[1BW127]     Unlocked     Enabled     Disconnected  0                      B255    
W256[1BW128]     Unlocked     Enabled     Disconnected  0                      B256    
1BW129           Unlocked     Enabled     Disconnected  0                              
1BW130           Unlocked     Enabled     Disconnected  0                              
1BW131           Unlocked     Enabled     Disconnected  0                              
1BW132           Unlocked     Enabled     Disconnected  0                              

ROME[OPER]# '''
PORT_SHOW_MATRIX_Q = '''ROME[OPER]# port show                 
================ ============ =========== ============= ======= ============== ========
Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
E1[1AE1]         Unlocked     Enabled     Connected     5       W4[1AW4]       Q1      
E2[1AE2]         Unlocked     Enabled     Connected     5       W3[1AW3]       Q1      
E3[1AE3]         Unlocked     Enabled     Connected     3       W2[1AW2]       Q2      
E4[1AE4]         Unlocked     Enabled     Connected     3       W1[1AW1]       Q2      
E5[1AE5]         Unlocked     Enabled     Disconnected  0                      Q3      
E6[1AE6]         Unlocked     Enabled     Disconnected  0                      Q3      
E7[1AE7]         Unlocked     Enabled     Disconnected  0                      Q4      
E8[1AE8]         Unlocked     Enabled     Disconnected  0                      Q4      
E9[1AE9]         Unlocked     Enabled     Disconnected  0                      Q5      
E10[1AE10]       Unlocked     Enabled     Disconnected  0                      Q5      
E11[1AE11]       Unlocked     Enabled     Disconnected  0                      Q6      
E12[1AE12]       Unlocked     Enabled     Disconnected  0                      Q6      
E13[1AE13]       Unlocked     Enabled     Disconnected  0                      Q7      
E14[1AE14]       Unlocked     Enabled     Disconnected  0                      Q7      
E15[1AE15]       Unlocked     Enabled     Disconnected  0                      Q8      
E16[1AE16]       Unlocked     Enabled     Disconnected  0                      Q8      
E17[1AE17]       Unlocked     Enabled     Disconnected  0                      Q9      
E18[1AE18]       Unlocked     Enabled     Disconnected  0                      Q9      
E19[1AE19]       Unlocked     Enabled     Disconnected  2                      Q10     
E20[1AE20]       Unlocked     Enabled     Disconnected  2                      Q10     
E21[1AE21]       Unlocked     Enabled     Disconnected  0                      Q11     
E22[1AE22]       Unlocked     Enabled     Disconnected  0                      Q11     
E23[1AE23]       Unlocked     Enabled     Disconnected  0                      Q12     
E24[1AE24]       Unlocked     Enabled     Disconnected  0                      Q12     
E25[1AE25]       Unlocked     Enabled     Disconnected  0                      Q13     
E26[1AE26]       Unlocked     Enabled     Disconnected  0                      Q13     
E27[1AE27]       Unlocked     Enabled     Disconnected  0                      Q14     
E28[1AE28]       Unlocked     Enabled     Disconnected  0                      Q14     
E29[1AE29]       Unlocked     Enabled     Disconnected  0                      Q15     
E30[1AE30]       Unlocked     Enabled     Disconnected  0                      Q15     
E31[1AE31]       Unlocked     Enabled     Disconnected  0                      Q16     
E32[1AE32]       Unlocked     Enabled     Disconnected  0                      Q16     
E33[1AE33]       Unlocked     Enabled     Disconnected  0                      Q17     
E34[1AE34]       Unlocked     Enabled     Disconnected  0                      Q17     
E35[1AE35]       Unlocked     Enabled     Disconnected  0                      Q18     
E36[1AE36]       Unlocked     Enabled     Disconnected  0                      Q18     
E37[1AE37]       Unlocked     Enabled     Disconnected  0                      Q19     
E38[1AE38]       Unlocked     Enabled     Disconnected  0                      Q19     
E39[1AE39]       Unlocked     Enabled     Disconnected  0                      Q20     
E40[1AE40]       Unlocked     Enabled     Disconnected  0                      Q20     
E41[1AE41]       Unlocked     Enabled     Disconnected  0                      Q21     
E42[1AE42]       Unlocked     Enabled     Disconnected  0                      Q21     
E43[1AE43]       Unlocked     Enabled     Disconnected  0                      Q22     
E44[1AE44]       Unlocked     Enabled     Disconnected  0                      Q22     
E45[1AE45]       Unlocked     Enabled     Disconnected  0                      Q23     
E46[1AE46]       Unlocked     Enabled     Disconnected  0                      Q23     
E47[1AE47]       Unlocked     Enabled     Disconnected  0                      Q24     
E48[1AE48]       Unlocked     Enabled     Disconnected  0                      Q24     
E49[1AE49]       Unlocked     Enabled     Disconnected  0                      Q25     
E50[1AE50]       Unlocked     Enabled     Disconnected  0                      Q25     
E51[1AE51]       Unlocked     Enabled     Disconnected  0                      Q26     
E52[1AE52]       Unlocked     Enabled     Disconnected  0                      Q26     
E53[1AE53]       Unlocked     Enabled     Disconnected  0                      Q27     
E54[1AE54]       Unlocked     Enabled     Disconnected  0                      Q27     
E55[1AE55]       Unlocked     Enabled     Disconnected  0                      Q28     
E56[1AE56]       Unlocked     Enabled     Disconnected  0                      Q28     
E57[1AE57]       Unlocked     Enabled     Disconnected  0                      Q29     
E58[1AE58]       Unlocked     Enabled     Disconnected  0                      Q29     
E59[1AE59]       Unlocked     Enabled     Disconnected  2                      Q30     
E60[1AE60]       Unlocked     Enabled     Disconnected  2                      Q30     
E61[1AE61]       Unlocked     Enabled     Disconnected  2                      Q31     
E62[1AE62]       Unlocked     Enabled     Disconnected  2                      Q31     
E63[1AE63]       Unlocked     Enabled     Disconnected  0                      Q32     
E64[1AE64]       Unlocked     Enabled     Disconnected  0                      Q32     
E65[1AE65]       Unlocked     Enabled     Disconnected  0                      Q33     
E66[1AE66]       Unlocked     Enabled     Disconnected  0                      Q33     
E67[1AE67]       Unlocked     Enabled     Disconnected  0                      Q34     
E68[1AE68]       Unlocked     Enabled     Disconnected  0                      Q34     
E69[1AE69]       Unlocked     Enabled     Disconnected  0                      Q35     
E70[1AE70]       Unlocked     Enabled     Disconnected  0                      Q35     
E71[1AE71]       Unlocked     Enabled     Disconnected  0                      Q36     
E72[1AE72]       Unlocked     Enabled     Disconnected  0                      Q36     
E73[1AE73]       Unlocked     Enabled     Disconnected  0                      Q37     
E74[1AE74]       Unlocked     Enabled     Disconnected  0                      Q37     
E75[1AE75]       Unlocked     Enabled     Disconnected  0                      Q38     
E76[1AE76]       Unlocked     Enabled     Disconnected  0                      Q38     
E77[1AE77]       Unlocked     Enabled     Disconnected  0                      Q39     
E78[1AE78]       Unlocked     Enabled     Disconnected  0                      Q39     
E79[1AE79]       Unlocked     Enabled     Disconnected  0                      Q40     
E80[1AE80]       Unlocked     Enabled     Disconnected  0                      Q40     
E81[1AE81]       Unlocked     Enabled     Disconnected  0                      Q41     
E82[1AE82]       Unlocked     Enabled     Disconnected  0                      Q41     
E83[1AE83]       Unlocked     Enabled     Disconnected  0                      Q42     
E84[1AE84]       Unlocked     Enabled     Disconnected  0                      Q42     
E85[1AE85]       Unlocked     Enabled     Disconnected  0                      Q43     
E86[1AE86]       Unlocked     Enabled     Disconnected  0                      Q43     
E87[1AE87]       Unlocked     Enabled     Disconnected  0                      Q44     
E88[1AE88]       Unlocked     Enabled     Disconnected  0                      Q44     
E89[1AE89]       Unlocked     Enabled     Disconnected  0                      Q45     
E90[1AE90]       Unlocked     Enabled     Disconnected  0                      Q45     
E91[1AE91]       Unlocked     Enabled     Disconnected  0                      Q46     
E92[1AE92]       Unlocked     Enabled     Disconnected  0                      Q46     
E93[1AE93]       Unlocked     Enabled     Disconnected  0                      Q47     
E94[1AE94]       Unlocked     Enabled     Disconnected  0                      Q47     
E95[1AE95]       Unlocked     Enabled     Disconnected  0                      Q48     
E96[1AE96]       Unlocked     Enabled     Disconnected  0                      Q48     
E97[1AE97]       Unlocked     Enabled     Disconnected  0                      Q49     
E98[1AE98]       Unlocked     Enabled     Disconnected  0                      Q49     
E99[1AE99]       Unlocked     Enabled     Disconnected  0                      Q50     
E100[1AE100]     Unlocked     Enabled     Disconnected  0                      Q50     
E101[1AE101]     Unlocked     Enabled     Disconnected  0                      Q51     
E102[1AE102]     Unlocked     Enabled     Disconnected  0                      Q51     
E103[1AE103]     Unlocked     Enabled     Disconnected  0                      Q52     
E104[1AE104]     Unlocked     Enabled     Disconnected  0                      Q52     
E105[1AE105]     Unlocked     Enabled     Disconnected  0                      Q53     
E106[1AE106]     Unlocked     Enabled     Disconnected  0                      Q53     
E107[1AE107]     Unlocked     Enabled     Disconnected  0                      Q54     
E108[1AE108]     Unlocked     Enabled     Disconnected  0                      Q54     
E109[1AE109]     Unlocked     Enabled     Disconnected  0                      Q55     
E110[1AE110]     Unlocked     Enabled     Disconnected  0                      Q55     
E111[1AE111]     Unlocked     Enabled     Disconnected  0                      Q56     
E112[1AE112]     Unlocked     Enabled     Disconnected  0                      Q56     
E113[1AE113]     Unlocked     Enabled     Disconnected  0                      Q57     
E114[1AE114]     Unlocked     Enabled     Disconnected  0                      Q57     
E115[1AE115]     Unlocked     Enabled     Disconnected  0                      Q58     
E116[1AE116]     Unlocked     Enabled     Disconnected  0                      Q58     
E117[1AE117]     Unlocked     Enabled     Disconnected  0                      Q59     
E118[1AE118]     Unlocked     Enabled     Disconnected  0                      Q59     
E119[1AE119]     Unlocked     Enabled     Disconnected  0                      Q60     
E120[1AE120]     Unlocked     Enabled     Disconnected  0                      Q60     
E121[1AE121]     Unlocked     Enabled     Disconnected  0                      Q61     
E122[1AE122]     Unlocked     Enabled     Disconnected  0                      Q61     
E123[1AE123]     Unlocked     Enabled     Disconnected  0                      Q62     
E124[1AE124]     Unlocked     Enabled     Disconnected  0                      Q62     
E125[1AE125]     Unlocked     Enabled     Disconnected  0                      Q63     
E126[1AE126]     Unlocked     Enabled     Disconnected  0                      Q63     
E127[1AE127]     Unlocked     Enabled     Disconnected  0                      Q64     
E128[1AE128]     Unlocked     Enabled     Disconnected  0                      Q64     
1AE129           Unlocked     Enabled     Disconnected  0                              
1AE130           Unlocked     Enabled     Disconnected  0                              
E129[1BE1]       Unlocked     Enabled     Connected     5       W132[1BW4]     Q1      
E130[1BE2]       Unlocked     Enabled     Connected     5       W131[1BW3]     Q1      
E131[1BE3]       Unlocked     Enabled     Connected     3       W130[1BW2]     Q2      
E132[1BE4]       Unlocked     Enabled     Connected     3       W129[1BW1]     Q2      
E133[1BE5]       Unlocked     Enabled     Disconnected  0                      Q3      
E134[1BE6]       Unlocked     Enabled     Disconnected  0                      Q3      
E135[1BE7]       Unlocked     Enabled     Disconnected  0                      Q4      
E136[1BE8]       Unlocked     Enabled     Disconnected  0                      Q4      
E137[1BE9]       Unlocked     Enabled     Disconnected  0                      Q5      
E138[1BE10]      Unlocked     Enabled     Disconnected  0                      Q5      
E139[1BE11]      Unlocked     Enabled     Disconnected  0                      Q6      
E140[1BE12]      Unlocked     Enabled     Disconnected  0                      Q6      
E141[1BE13]      Unlocked     Enabled     Disconnected  0                      Q7      
E142[1BE14]      Unlocked     Enabled     Disconnected  0                      Q7      
E143[1BE15]      Unlocked     Enabled     Disconnected  0                      Q8      
E144[1BE16]      Unlocked     Enabled     Disconnected  0                      Q8      
E145[1BE17]      Unlocked     Enabled     Disconnected  0                      Q9      
E146[1BE18]      Unlocked     Enabled     Disconnected  0                      Q9      
E147[1BE19]      Unlocked     Enabled     Disconnected  2                      Q10     
E148[1BE20]      Unlocked     Enabled     Disconnected  2                      Q10     
E149[1BE21]      Unlocked     Enabled     Disconnected  0                      Q11     
E150[1BE22]      Unlocked     Enabled     Disconnected  0                      Q11     
E151[1BE23]      Unlocked     Enabled     Disconnected  0                      Q12     
E152[1BE24]      Unlocked     Enabled     Disconnected  0                      Q12     
E153[1BE25]      Unlocked     Enabled     Disconnected  0                      Q13     
E154[1BE26]      Unlocked     Enabled     Disconnected  0                      Q13     
E155[1BE27]      Unlocked     Enabled     Disconnected  0                      Q14     
E156[1BE28]      Unlocked     Enabled     Disconnected  0                      Q14     
E157[1BE29]      Unlocked     Enabled     Disconnected  0                      Q15     
E158[1BE30]      Unlocked     Enabled     Disconnected  0                      Q15     
E159[1BE31]      Unlocked     Enabled     Disconnected  0                      Q16     
E160[1BE32]      Unlocked     Enabled     Disconnected  0                      Q16     
E161[1BE33]      Unlocked     Enabled     Disconnected  0                      Q17     
E162[1BE34]      Unlocked     Enabled     Disconnected  0                      Q17     
E163[1BE35]      Unlocked     Enabled     Disconnected  0                      Q18     
E164[1BE36]      Unlocked     Enabled     Disconnected  0                      Q18     
E165[1BE37]      Unlocked     Enabled     Disconnected  0                      Q19     
E166[1BE38]      Unlocked     Enabled     Disconnected  0                      Q19     
E167[1BE39]      Unlocked     Enabled     Disconnected  0                      Q20     
E168[1BE40]      Unlocked     Enabled     Disconnected  0                      Q20     
E169[1BE41]      Unlocked     Enabled     Disconnected  0                      Q21     
E170[1BE42]      Unlocked     Enabled     Disconnected  0                      Q21     
E171[1BE43]      Unlocked     Enabled     Disconnected  0                      Q22     
E172[1BE44]      Unlocked     Enabled     Disconnected  0                      Q22     
E173[1BE45]      Unlocked     Enabled     Disconnected  0                      Q23     
E174[1BE46]      Unlocked     Enabled     Disconnected  0                      Q23     
E175[1BE47]      Unlocked     Enabled     Disconnected  0                      Q24     
E176[1BE48]      Unlocked     Enabled     Disconnected  0                      Q24     
E177[1BE49]      Unlocked     Enabled     Disconnected  0                      Q25     
E178[1BE50]      Unlocked     Enabled     Disconnected  0                      Q25     
E179[1BE51]      Unlocked     Enabled     Disconnected  0                      Q26     
E180[1BE52]      Unlocked     Enabled     Disconnected  0                      Q26     
E181[1BE53]      Unlocked     Enabled     Disconnected  0                      Q27     
E182[1BE54]      Unlocked     Enabled     Disconnected  0                      Q27     
E183[1BE55]      Unlocked     Enabled     Disconnected  0                      Q28     
E184[1BE56]      Unlocked     Enabled     Disconnected  0                      Q28     
E185[1BE57]      Unlocked     Enabled     Disconnected  0                      Q29     
E186[1BE58]      Unlocked     Enabled     Disconnected  0                      Q29     
E187[1BE59]      Unlocked     Enabled     Disconnected  2                      Q30     
E188[1BE60]      Unlocked     Enabled     Disconnected  2                      Q30     
E189[1BE61]      Unlocked     Enabled     Disconnected  2                      Q31     
E190[1BE62]      Unlocked     Enabled     Disconnected  2                      Q31     
E191[1BE63]      Unlocked     Enabled     Disconnected  0                      Q32     
E192[1BE64]      Unlocked     Enabled     Disconnected  0                      Q32     
E193[1BE65]      Unlocked     Enabled     Disconnected  0                      Q33     
E194[1BE66]      Unlocked     Enabled     Disconnected  0                      Q33     
E195[1BE67]      Unlocked     Enabled     Disconnected  0                      Q34     
E196[1BE68]      Unlocked     Enabled     Disconnected  0                      Q34     
E197[1BE69]      Unlocked     Enabled     Disconnected  0                      Q35     
E198[1BE70]      Unlocked     Enabled     Disconnected  0                      Q35     
E199[1BE71]      Unlocked     Enabled     Disconnected  0                      Q36     
E200[1BE72]      Unlocked     Enabled     Disconnected  0                      Q36     
E201[1BE73]      Unlocked     Enabled     Disconnected  0                      Q37     
E202[1BE74]      Unlocked     Enabled     Disconnected  0                      Q37     
E203[1BE75]      Unlocked     Enabled     Disconnected  0                      Q38     
E204[1BE76]      Unlocked     Enabled     Disconnected  0                      Q38     
E205[1BE77]      Unlocked     Enabled     Disconnected  0                      Q39     
E206[1BE78]      Unlocked     Enabled     Disconnected  0                      Q39     
E207[1BE79]      Unlocked     Enabled     Disconnected  0                      Q40     
E208[1BE80]      Unlocked     Enabled     Disconnected  0                      Q40     
E209[1BE81]      Unlocked     Enabled     Disconnected  0                      Q41     
E210[1BE82]      Unlocked     Enabled     Disconnected  0                      Q41     
E211[1BE83]      Unlocked     Enabled     Disconnected  0                      Q42     
E212[1BE84]      Unlocked     Enabled     Disconnected  0                      Q42     
E213[1BE85]      Unlocked     Enabled     Disconnected  0                      Q43     
E214[1BE86]      Unlocked     Enabled     Disconnected  0                      Q43     
E215[1BE87]      Unlocked     Enabled     Disconnected  0                      Q44     
E216[1BE88]      Unlocked     Enabled     Disconnected  0                      Q44     
E217[1BE89]      Unlocked     Enabled     Disconnected  0                      Q45     
E218[1BE90]      Unlocked     Enabled     Disconnected  0                      Q45     
E219[1BE91]      Unlocked     Enabled     Disconnected  0                      Q46     
E220[1BE92]      Unlocked     Enabled     Disconnected  0                      Q46     
E221[1BE93]      Unlocked     Enabled     Disconnected  0                      Q47     
E222[1BE94]      Unlocked     Enabled     Disconnected  0                      Q47     
E223[1BE95]      Unlocked     Enabled     Disconnected  0                      Q48     
E224[1BE96]      Unlocked     Enabled     Disconnected  0                      Q48     
E225[1BE97]      Unlocked     Enabled     Disconnected  0                      Q49     
E226[1BE98]      Unlocked     Enabled     Disconnected  0                      Q49     
E227[1BE99]      Unlocked     Enabled     Disconnected  0                      Q50     
E228[1BE100]     Unlocked     Enabled     Disconnected  0                      Q50     
E229[1BE101]     Unlocked     Enabled     Disconnected  0                      Q51     
E230[1BE102]     Unlocked     Enabled     Disconnected  0                      Q51     
E231[1BE103]     Unlocked     Enabled     Disconnected  0                      Q52     
E232[1BE104]     Unlocked     Enabled     Disconnected  0                      Q52     
E233[1BE105]     Unlocked     Enabled     Disconnected  0                      Q53     
E234[1BE106]     Unlocked     Enabled     Disconnected  0                      Q53     
E235[1BE107]     Unlocked     Enabled     Disconnected  0                      Q54     
E236[1BE108]     Unlocked     Enabled     Disconnected  0                      Q54     
E237[1BE109]     Unlocked     Enabled     Disconnected  0                      Q55     
E238[1BE110]     Unlocked     Enabled     Disconnected  0                      Q55     
E239[1BE111]     Unlocked     Enabled     Disconnected  0                      Q56     
E240[1BE112]     Unlocked     Enabled     Disconnected  0                      Q56     
E241[1BE113]     Unlocked     Enabled     Disconnected  0                      Q57     
E242[1BE114]     Unlocked     Enabled     Disconnected  0                      Q57     
E243[1BE115]     Unlocked     Enabled     Disconnected  0                      Q58     
E244[1BE116]     Unlocked     Enabled     Disconnected  0                      Q58     
E245[1BE117]     Unlocked     Enabled     Disconnected  0                      Q59     
E246[1BE118]     Unlocked     Enabled     Disconnected  0                      Q59     
E247[1BE119]     Unlocked     Enabled     Disconnected  0                      Q60     
E248[1BE120]     Unlocked     Enabled     Disconnected  0                      Q60     
E249[1BE121]     Unlocked     Enabled     Disconnected  0                      Q61     
E250[1BE122]     Unlocked     Enabled     Disconnected  0                      Q61     
E251[1BE123]     Unlocked     Enabled     Disconnected  0                      Q62     
E252[1BE124]     Unlocked     Enabled     Disconnected  0                      Q62     
E253[1BE125]     Unlocked     Enabled     Disconnected  0                      Q63     
E254[1BE126]     Unlocked     Enabled     Disconnected  0                      Q63     
E255[1BE127]     Unlocked     Enabled     Disconnected  0                      Q64     
E256[1BE128]     Unlocked     Enabled     Disconnected  0                      Q64     
1BE129           Unlocked     Enabled     Disconnected  0                              
1BE130           Unlocked     Enabled     Disconnected  0                              
W1[1AW1]         Unlocked     Enabled     Connected     5       E4[1AE4]       Q1      
W2[1AW2]         Unlocked     Enabled     Connected     5       E3[1AE3]       Q1      
W3[1AW3]         Unlocked     Enabled     Connected     3       E2[1AE2]       Q2      
W4[1AW4]         Unlocked     Enabled     Connected     3       E1[1AE1]       Q2      
W5[1AW5]         Unlocked     Enabled     Disconnected  0                      Q3      
W6[1AW6]         Unlocked     Enabled     Disconnected  0                      Q3      
W7[1AW7]         Unlocked     Enabled     Disconnected  0                      Q4      
W8[1AW8]         Unlocked     Enabled     Disconnected  0                      Q4      
W9[1AW9]         Unlocked     Enabled     Disconnected  0                      Q5      
W10[1AW10]       Unlocked     Enabled     Disconnected  0                      Q5      
W11[1AW11]       Unlocked     Enabled     Disconnected  0                      Q6      
W12[1AW12]       Unlocked     Enabled     Disconnected  0                      Q6      
W13[1AW13]       Unlocked     Enabled     Disconnected  0                      Q7      
W14[1AW14]       Unlocked     Enabled     Disconnected  0                      Q7      
W15[1AW15]       Unlocked     Enabled     Disconnected  0                      Q8      
W16[1AW16]       Unlocked     Enabled     Disconnected  0                      Q8      
W17[1AW17]       Unlocked     Enabled     Disconnected  0                      Q9      
W18[1AW18]       Unlocked     Enabled     Disconnected  0                      Q9      
W19[1AW19]       Unlocked     Enabled     Disconnected  2                      Q10     
W20[1AW20]       Unlocked     Enabled     Disconnected  2                      Q10     
W21[1AW21]       Unlocked     Enabled     Disconnected  0                      Q11     
W22[1AW22]       Unlocked     Enabled     Disconnected  0                      Q11     
W23[1AW23]       Unlocked     Enabled     Disconnected  0                      Q12     
W24[1AW24]       Unlocked     Enabled     Disconnected  0                      Q12     
W25[1AW25]       Unlocked     Enabled     Disconnected  0                      Q13     
W26[1AW26]       Unlocked     Enabled     Disconnected  0                      Q13     
W27[1AW27]       Unlocked     Enabled     Disconnected  0                      Q14     
W28[1AW28]       Unlocked     Enabled     Disconnected  0                      Q14     
W29[1AW29]       Unlocked     Enabled     Disconnected  0                      Q15     
W30[1AW30]       Unlocked     Enabled     Disconnected  0                      Q15     
W31[1AW31]       Unlocked     Enabled     Disconnected  0                      Q16     
W32[1AW32]       Unlocked     Enabled     Disconnected  0                      Q16     
W33[1AW33]       Unlocked     Enabled     Disconnected  0                      Q17     
W34[1AW34]       Unlocked     Enabled     Disconnected  0                      Q17     
W35[1AW35]       Unlocked     Enabled     Disconnected  0                      Q18     
W36[1AW36]       Unlocked     Enabled     Disconnected  0                      Q18     
W37[1AW37]       Unlocked     Enabled     Disconnected  0                      Q19     
W38[1AW38]       Unlocked     Enabled     Disconnected  0                      Q19     
W39[1AW39]       Unlocked     Enabled     Disconnected  0                      Q20     
W40[1AW40]       Unlocked     Enabled     Disconnected  0                      Q20     
W41[1AW41]       Unlocked     Enabled     Disconnected  0                      Q21     
W42[1AW42]       Unlocked     Enabled     Disconnected  0                      Q21     
W43[1AW43]       Unlocked     Enabled     Disconnected  0                      Q22     
W44[1AW44]       Unlocked     Enabled     Disconnected  0                      Q22     
W45[1AW45]       Unlocked     Enabled     Disconnected  0                      Q23     
W46[1AW46]       Unlocked     Enabled     Disconnected  0                      Q23     
W47[1AW47]       Unlocked     Enabled     Disconnected  0                      Q24     
W48[1AW48]       Unlocked     Enabled     Disconnected  0                      Q24     
W49[1AW49]       Unlocked     Enabled     Disconnected  0                      Q25     
W50[1AW50]       Unlocked     Enabled     Disconnected  0                      Q25     
W51[1AW51]       Unlocked     Enabled     Disconnected  0                      Q26     
W52[1AW52]       Unlocked     Enabled     Disconnected  0                      Q26     
W53[1AW53]       Unlocked     Enabled     Disconnected  0                      Q27     
W54[1AW54]       Unlocked     Enabled     Disconnected  0                      Q27     
W55[1AW55]       Unlocked     Enabled     Disconnected  0                      Q28     
W56[1AW56]       Unlocked     Enabled     Disconnected  0                      Q28     
W57[1AW57]       Unlocked     Enabled     Disconnected  0                      Q29     
W58[1AW58]       Unlocked     Enabled     Disconnected  0                      Q29     
W59[1AW59]       Unlocked     Enabled     Disconnected  2                      Q30     
W60[1AW60]       Unlocked     Enabled     Disconnected  2                      Q30     
W61[1AW61]       Unlocked     Enabled     Disconnected  2                      Q31     
W62[1AW62]       Unlocked     Enabled     Disconnected  2                      Q31     
W63[1AW63]       Unlocked     Enabled     Disconnected  0                      Q32     
W64[1AW64]       Unlocked     Enabled     Disconnected  0                      Q32     
W65[1AW65]       Unlocked     Enabled     Disconnected  0                      Q33     
W66[1AW66]       Unlocked     Enabled     Disconnected  0                      Q33     
W67[1AW67]       Unlocked     Enabled     Disconnected  0                      Q34     
W68[1AW68]       Unlocked     Enabled     Disconnected  0                      Q34     
W69[1AW69]       Unlocked     Enabled     Disconnected  0                      Q35     
W70[1AW70]       Unlocked     Enabled     Disconnected  0                      Q35     
W71[1AW71]       Unlocked     Enabled     Disconnected  0                      Q36     
W72[1AW72]       Unlocked     Enabled     Disconnected  0                      Q36     
W73[1AW73]       Unlocked     Enabled     Disconnected  0                      Q37     
W74[1AW74]       Unlocked     Enabled     Disconnected  0                      Q37     
W75[1AW75]       Unlocked     Enabled     Disconnected  0                      Q38     
W76[1AW76]       Unlocked     Enabled     Disconnected  0                      Q38     
W77[1AW77]       Unlocked     Enabled     Disconnected  0                      Q39     
W78[1AW78]       Unlocked     Enabled     Disconnected  0                      Q39     
W79[1AW79]       Unlocked     Enabled     Disconnected  0                      Q40     
W80[1AW80]       Unlocked     Enabled     Disconnected  0                      Q40     
W81[1AW81]       Unlocked     Enabled     Disconnected  0                      Q41     
W82[1AW82]       Unlocked     Enabled     Disconnected  0                      Q41     
W83[1AW83]       Unlocked     Enabled     Disconnected  0                      Q42     
W84[1AW84]       Unlocked     Enabled     Disconnected  0                      Q42     
W85[1AW85]       Unlocked     Enabled     Disconnected  0                      Q43     
W86[1AW86]       Unlocked     Enabled     Disconnected  0                      Q43     
W87[1AW87]       Unlocked     Enabled     Disconnected  0                      Q44     
W88[1AW88]       Unlocked     Enabled     Disconnected  0                      Q44     
W89[1AW89]       Unlocked     Enabled     Disconnected  0                      Q45     
W90[1AW90]       Unlocked     Enabled     Disconnected  0                      Q45     
W91[1AW91]       Unlocked     Enabled     Disconnected  0                      Q46     
W92[1AW92]       Unlocked     Enabled     Disconnected  0                      Q46     
W93[1AW93]       Unlocked     Enabled     Disconnected  0                      Q47     
W94[1AW94]       Unlocked     Enabled     Disconnected  0                      Q47     
W95[1AW95]       Unlocked     Enabled     Disconnected  0                      Q48     
W96[1AW96]       Unlocked     Enabled     Disconnected  0                      Q48     
W97[1AW97]       Unlocked     Enabled     Disconnected  0                      Q49     
W98[1AW98]       Unlocked     Enabled     Disconnected  0                      Q49     
W99[1AW99]       Unlocked     Enabled     Disconnected  0                      Q50     
W100[1AW100]     Unlocked     Enabled     Disconnected  0                      Q50     
W101[1AW101]     Unlocked     Enabled     Disconnected  0                      Q51     
W102[1AW102]     Unlocked     Enabled     Disconnected  0                      Q51     
W103[1AW103]     Unlocked     Enabled     Disconnected  0                      Q52     
W104[1AW104]     Unlocked     Enabled     Disconnected  0                      Q52     
W105[1AW105]     Unlocked     Enabled     Disconnected  0                      Q53     
W106[1AW106]     Unlocked     Enabled     Disconnected  0                      Q53     
W107[1AW107]     Unlocked     Enabled     Disconnected  0                      Q54     
W108[1AW108]     Unlocked     Enabled     Disconnected  0                      Q54     
W109[1AW109]     Unlocked     Enabled     Disconnected  0                      Q55     
W110[1AW110]     Unlocked     Enabled     Disconnected  0                      Q55     
W111[1AW111]     Unlocked     Enabled     Disconnected  0                      Q56     
W112[1AW112]     Unlocked     Enabled     Disconnected  0                      Q56     
W113[1AW113]     Unlocked     Enabled     Disconnected  0                      Q57     
W114[1AW114]     Unlocked     Enabled     Disconnected  0                      Q57     
W115[1AW115]     Unlocked     Enabled     Disconnected  0                      Q58     
W116[1AW116]     Unlocked     Enabled     Disconnected  0                      Q58     
W117[1AW117]     Unlocked     Enabled     Disconnected  0                      Q59     
W118[1AW118]     Unlocked     Enabled     Disconnected  0                      Q59     
W119[1AW119]     Unlocked     Enabled     Disconnected  0                      Q60     
W120[1AW120]     Unlocked     Enabled     Disconnected  0                      Q60     
W121[1AW121]     Unlocked     Enabled     Disconnected  0                      Q61     
W122[1AW122]     Unlocked     Enabled     Disconnected  0                      Q61     
W123[1AW123]     Unlocked     Enabled     Disconnected  0                      Q62     
W124[1AW124]     Unlocked     Enabled     Disconnected  0                      Q62     
W125[1AW125]     Unlocked     Enabled     Disconnected  0                      Q63     
W126[1AW126]     Unlocked     Enabled     Disconnected  0                      Q63     
W127[1AW127]     Unlocked     Enabled     Disconnected  0                      Q64     
W128[1AW128]     Unlocked     Enabled     Disconnected  0                      Q64     
1AW129           Unlocked     Enabled     Disconnected  0                              
1AW130           Unlocked     Enabled     Disconnected  0                              
1AW131           Unlocked     Enabled     Disconnected  0                              
1AW132           Unlocked     Enabled     Disconnected  0                              
W129[1BW1]       Unlocked     Enabled     Connected     5       E132[1BE4]     Q1      
W130[1BW2]       Unlocked     Enabled     Connected     5       E131[1BE3]     Q1      
W131[1BW3]       Unlocked     Enabled     Connected     3       E130[1BE2]     Q2      
W132[1BW4]       Unlocked     Enabled     Connected     3       E129[1BE1]     Q2      
W133[1BW5]       Unlocked     Enabled     Disconnected  0                      Q3      
W134[1BW6]       Unlocked     Enabled     Disconnected  0                      Q3      
W135[1BW7]       Unlocked     Enabled     Disconnected  0                      Q4      
W136[1BW8]       Unlocked     Enabled     Disconnected  0                      Q4      
W137[1BW9]       Unlocked     Enabled     Disconnected  0                      Q5      
W138[1BW10]      Unlocked     Enabled     Disconnected  0                      Q5      
W139[1BW11]      Unlocked     Enabled     Disconnected  0                      Q6      
W140[1BW12]      Unlocked     Enabled     Disconnected  0                      Q6      
W141[1BW13]      Unlocked     Enabled     Disconnected  0                      Q7      
W142[1BW14]      Unlocked     Enabled     Disconnected  0                      Q7      
W143[1BW15]      Unlocked     Enabled     Disconnected  0                      Q8      
W144[1BW16]      Unlocked     Enabled     Disconnected  0                      Q8      
W145[1BW17]      Unlocked     Enabled     Disconnected  0                      Q9      
W146[1BW18]      Unlocked     Enabled     Disconnected  0                      Q9      
W147[1BW19]      Unlocked     Enabled     Disconnected  2                      Q10     
W148[1BW20]      Unlocked     Enabled     Disconnected  2                      Q10     
W149[1BW21]      Unlocked     Enabled     Disconnected  0                      Q11     
W150[1BW22]      Unlocked     Enabled     Disconnected  0                      Q11     
W151[1BW23]      Unlocked     Enabled     Disconnected  0                      Q12     
W152[1BW24]      Unlocked     Enabled     Disconnected  0                      Q12     
W153[1BW25]      Unlocked     Enabled     Disconnected  0                      Q13     
W154[1BW26]      Unlocked     Enabled     Disconnected  0                      Q13     
W155[1BW27]      Unlocked     Enabled     Disconnected  0                      Q14     
W156[1BW28]      Unlocked     Enabled     Disconnected  0                      Q14     
W157[1BW29]      Unlocked     Enabled     Disconnected  0                      Q15     
W158[1BW30]      Unlocked     Enabled     Disconnected  0                      Q15     
W159[1BW31]      Unlocked     Enabled     Disconnected  0                      Q16     
W160[1BW32]      Unlocked     Enabled     Disconnected  0                      Q16     
W161[1BW33]      Unlocked     Enabled     Disconnected  0                      Q17     
W162[1BW34]      Unlocked     Enabled     Disconnected  0                      Q17     
W163[1BW35]      Unlocked     Enabled     Disconnected  0                      Q18     
W164[1BW36]      Unlocked     Enabled     Disconnected  0                      Q18     
W165[1BW37]      Unlocked     Enabled     Disconnected  0                      Q19     
W166[1BW38]      Unlocked     Enabled     Disconnected  0                      Q19     
W167[1BW39]      Unlocked     Enabled     Disconnected  0                      Q20     
W168[1BW40]      Unlocked     Enabled     Disconnected  0                      Q20     
W169[1BW41]      Unlocked     Enabled     Disconnected  0                      Q21     
W170[1BW42]      Unlocked     Enabled     Disconnected  0                      Q21     
W171[1BW43]      Unlocked     Enabled     Disconnected  0                      Q22     
W172[1BW44]      Unlocked     Enabled     Disconnected  0                      Q22     
W173[1BW45]      Unlocked     Enabled     Disconnected  0                      Q23     
W174[1BW46]      Unlocked     Enabled     Disconnected  0                      Q23     
W175[1BW47]      Unlocked     Enabled     Disconnected  0                      Q24     
W176[1BW48]      Unlocked     Enabled     Disconnected  0                      Q24     
W177[1BW49]      Unlocked     Enabled     Disconnected  0                      Q25     
W178[1BW50]      Unlocked     Enabled     Disconnected  0                      Q25     
W179[1BW51]      Unlocked     Enabled     Disconnected  0                      Q26     
W180[1BW52]      Unlocked     Enabled     Disconnected  0                      Q26     
W181[1BW53]      Unlocked     Enabled     Disconnected  0                      Q27     
W182[1BW54]      Unlocked     Enabled     Disconnected  0                      Q27     
W183[1BW55]      Unlocked     Enabled     Disconnected  0                      Q28     
W184[1BW56]      Unlocked     Enabled     Disconnected  0                      Q28     
W185[1BW57]      Unlocked     Enabled     Disconnected  0                      Q29     
W186[1BW58]      Unlocked     Enabled     Disconnected  0                      Q29     
W187[1BW59]      Unlocked     Enabled     Disconnected  2                      Q30     
W188[1BW60]      Unlocked     Enabled     Disconnected  2                      Q30     
W189[1BW61]      Unlocked     Enabled     Disconnected  2                      Q31     
W190[1BW62]      Unlocked     Enabled     Disconnected  2                      Q31     
W191[1BW63]      Unlocked     Enabled     Disconnected  0                      Q32     
W192[1BW64]      Unlocked     Enabled     Disconnected  0                      Q32     
W193[1BW65]      Unlocked     Enabled     Disconnected  0                      Q33     
W194[1BW66]      Unlocked     Enabled     Disconnected  0                      Q33     
W195[1BW67]      Unlocked     Enabled     Disconnected  0                      Q34     
W196[1BW68]      Unlocked     Enabled     Disconnected  0                      Q34     
W197[1BW69]      Unlocked     Enabled     Disconnected  0                      Q35     
W198[1BW70]      Unlocked     Enabled     Disconnected  0                      Q35     
W199[1BW71]      Unlocked     Enabled     Disconnected  0                      Q36     
W200[1BW72]      Unlocked     Enabled     Disconnected  0                      Q36     
W201[1BW73]      Unlocked     Enabled     Disconnected  0                      Q37     
W202[1BW74]      Unlocked     Enabled     Disconnected  0                      Q37     
W203[1BW75]      Unlocked     Enabled     Disconnected  0                      Q38     
W204[1BW76]      Unlocked     Enabled     Disconnected  0                      Q38     
W205[1BW77]      Unlocked     Enabled     Disconnected  0                      Q39     
W206[1BW78]      Unlocked     Enabled     Disconnected  0                      Q39     
W207[1BW79]      Unlocked     Enabled     Disconnected  0                      Q40     
W208[1BW80]      Unlocked     Enabled     Disconnected  0                      Q40     
W209[1BW81]      Unlocked     Enabled     Disconnected  0                      Q41     
W210[1BW82]      Unlocked     Enabled     Disconnected  0                      Q41     
W211[1BW83]      Unlocked     Enabled     Disconnected  0                      Q42     
W212[1BW84]      Unlocked     Enabled     Disconnected  0                      Q42     
W213[1BW85]      Unlocked     Enabled     Disconnected  0                      Q43     
W214[1BW86]      Unlocked     Enabled     Disconnected  0                      Q43     
W215[1BW87]      Unlocked     Enabled     Disconnected  0                      Q44     
W216[1BW88]      Unlocked     Enabled     Disconnected  0                      Q44     
W217[1BW89]      Unlocked     Enabled     Disconnected  0                      Q45     
W218[1BW90]      Unlocked     Enabled     Disconnected  0                      Q45     
W219[1BW91]      Unlocked     Enabled     Disconnected  0                      Q46     
W220[1BW92]      Unlocked     Enabled     Disconnected  0                      Q46     
W221[1BW93]      Unlocked     Enabled     Disconnected  0                      Q47     
W222[1BW94]      Unlocked     Enabled     Disconnected  0                      Q47     
W223[1BW95]      Unlocked     Enabled     Disconnected  0                      Q48     
W224[1BW96]      Unlocked     Enabled     Disconnected  0                      Q48     
W225[1BW97]      Unlocked     Enabled     Disconnected  0                      Q49     
W226[1BW98]      Unlocked     Enabled     Disconnected  0                      Q49     
W227[1BW99]      Unlocked     Enabled     Disconnected  0                      Q50     
W228[1BW100]     Unlocked     Enabled     Disconnected  0                      Q50     
W229[1BW101]     Unlocked     Enabled     Disconnected  0                      Q51     
W230[1BW102]     Unlocked     Enabled     Disconnected  0                      Q51     
W231[1BW103]     Unlocked     Enabled     Disconnected  0                      Q52     
W232[1BW104]     Unlocked     Enabled     Disconnected  0                      Q52     
W233[1BW105]     Unlocked     Enabled     Disconnected  0                      Q53     
W234[1BW106]     Unlocked     Enabled     Disconnected  0                      Q53     
W235[1BW107]     Unlocked     Enabled     Disconnected  0                      Q54     
W236[1BW108]     Unlocked     Enabled     Disconnected  0                      Q54     
W237[1BW109]     Unlocked     Enabled     Disconnected  0                      Q55     
W238[1BW110]     Unlocked     Enabled     Disconnected  0                      Q55     
W239[1BW111]     Unlocked     Enabled     Disconnected  0                      Q56     
W240[1BW112]     Unlocked     Enabled     Disconnected  0                      Q56     
W241[1BW113]     Unlocked     Enabled     Disconnected  0                      Q57     
W242[1BW114]     Unlocked     Enabled     Disconnected  0                      Q57     
W243[1BW115]     Unlocked     Enabled     Disconnected  0                      Q58     
W244[1BW116]     Unlocked     Enabled     Disconnected  0                      Q58     
W245[1BW117]     Unlocked     Enabled     Disconnected  0                      Q59     
W246[1BW118]     Unlocked     Enabled     Disconnected  0                      Q59     
W247[1BW119]     Unlocked     Enabled     Disconnected  0                      Q60     
W248[1BW120]     Unlocked     Enabled     Disconnected  0                      Q60     
W249[1BW121]     Unlocked     Enabled     Disconnected  0                      Q61     
W250[1BW122]     Unlocked     Enabled     Disconnected  0                      Q61     
W251[1BW123]     Unlocked     Enabled     Disconnected  0                      Q62     
W252[1BW124]     Unlocked     Enabled     Disconnected  0                      Q62     
W253[1BW125]     Unlocked     Enabled     Disconnected  0                      Q63     
W254[1BW126]     Unlocked     Enabled     Disconnected  0                      Q63     
W255[1BW127]     Unlocked     Enabled     Disconnected  0                      Q64     
W256[1BW128]     Unlocked     Enabled     Disconnected  0                      Q64     
1BW129           Unlocked     Enabled     Disconnected  0                              
1BW130           Unlocked     Enabled     Disconnected  0                              
1BW131           Unlocked     Enabled     Disconnected  0                              
1BW132           Unlocked     Enabled     Disconnected  0                              

ROME[OPER]# '''


class Command(object):
    def __init__(self, request, response, regexp=False):
        self.request = request
        self.response = response
        self.regexp = regexp

    def is_equal_to_request(self, request):
        return (not self.regexp and self.request == request
                or self.regexp and re.search(self.request, request))

    def __repr__(self):
        return 'Command({!r}, {!r}, {!r})'.format(self.request, self.response, self.regexp)


class CliEmulator(object):
    def __init__(self, commands=None):
        self.request = None

        self.commands = deque([
            Command(None, DEFAULT_PROMPT),
            Command('', DEFAULT_PROMPT),
            Command('show board', SHOW_BOARD),
        ])

        if commands:
            self.commands.extend(commands)

    def _get_response(self):
        try:
            command = self.commands.popleft()
        except IndexError:
            raise IndexError('Not expected request "{}"'.format(self.request))

        if not command.is_equal_to_request(self.request):
            raise KeyError('Unexpected request - "{}"\n'
                           'Expected - "{}"'.format(self.request, command.request))

        if isinstance(command.response, Exception):
            raise command.response
        else:
            return command.response

    def receive_all(self, timeout, logger):
        return self._get_response()

    def send_line(self, command, logger):
        self.request = command

    def check_calls(self):
        if self.commands:
            commands = '\n'.join('\t\t- {}'.format(command.request) for command in self.commands)
            raise ValueError('Not executed commands: \n{}'.format(commands))


class BaseRomeTestCase(TestCase):
    def setUp(self):
        self.runtime_config = RuntimeConfiguration(RUNTIME_CONFIG_PATH)
        self.logger = MagicMock()
        self.driver_commands = DriverCommands(self.logger, self.runtime_config)
        self.cli_handler = self.driver_commands._cli_handler

    def tearDown(self):
        self.driver_commands._cli_handler._cli._session_pool._session_manager._existing_sessions = []
