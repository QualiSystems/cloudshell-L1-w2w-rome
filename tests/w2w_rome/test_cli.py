from mock import patch, MagicMock

from tests.w2w_rome.base import BaseRomeTestCase
from w2w_rome.cli.template_executor import RomeTemplateExecutor
from w2w_rome.helpers.port_entity import PortTable

PORT_SHOW_WITH_LOG = '''ROME[TECH]# port show

Port             Admin Status Oper Status Port Status   Counter ConnectedTo    Logical
================ ============ =========== ============= ======= ============== ========
E1[1AE1]         Unlocked     Enabled     Connected     93      W2[1AW2]       P1      
E2[1AE2]         Unlocked     Enabled     Connected     88      W1[1AW1]       P2      
E3[1AE3]         Unlocked     Enabled     Disconnected  31                     P3      
E4[1AE4]         Unlocked     Enabled     Disconnected  32                     P4      
E5[1AE5]         Unlocked     Enabled     Disconnected  26                     P5      
E6[1AE6]         Unlocked     Enabled     Disconnected  40                     P6      
E7[1AE7]         Unlocked     Enabled     Disconnected  16                     P7      
E8[1AE8]         Unlocked     Enabled     Disconnected  16                     P8      
E9[1AE9]         Unlocked     Enabled     Disconnected  4                      P9      
E10[1AE10]       Unlocked     Enabled     Disconnected  6                      P10     
E11[1AE11]       Unlocked     Enabled     Disconnected  4                      P11     
E12[1AE12]       Unlocked     Enabled     Connected     3       W128[1AW128]   P12     
E13[1AE13]       Unlocked     Enabled     Disconnected  2                      P13     
E14[1AE14]       Unlocked     Enabled     Disconnected  4                      P14     
E15[1AE15]       Unlocked     Enabled     Disconnected  2                      P15     
E16[1AE16]       Unlocked     Enabled     Disconnected  4                      P16     
E17[1AE17]       Unlocked     Enabled     Disconnected  2                      P17     
E18[1AE18]       Unlocked     Enabled     Disconnected  2                      P18     
E19[1AE19]       Unlocked     Enabled     Disconnected  6                      P19     
E20[1AE20]       Unlocked     Enabled     Disconnected  6                      P20     
E21[1AE21]       Unlocked     Enabled     Disconnected  2                      P21     
E22[1AE22]       Unlocked     Enabled     Disconnected  2                      P22     
E23[1AE23]       Unlocked     Enabled     Disconnected  4                      P23     
E24[1AE24]       Unlocked     Enabled     Disconnected  4                      P24     
E25[1AE25]       Unlocked     Enabled     Disconnected  2                      P25     
E26[1AE26]       Unlocked     Enabled     Disconnected  4                      P26     
E27[1AE27]       Unlocked     Enabled     Disconnected  4                      P27     
E28[1AE28]       Unlocked     Enabled     Disconnected  2                      P28     
E29[1AE29]       Unlocked     Enabled     Disconnected  2                      P29     
E30[1AE30]       Unlocked     Enabled     Disconnected  4                      P30     
E31[1AE31]       Unlocked     Enabled     Disconnected  2                      P31     
E32[1AE32]       Unlocked     Enabled     Disconnected  2                      P32     
E33[1AE33]       Unlocked     Enabled     Disconnected  2                      P33     
E34[1AE34]       Unlocked     Enabled     Disconnected  2                      P34     
E35[1AE35]       Unlocked     Enabled     Disconnected  2                      P35     
E36[1AE36]       Unlocked     Enabled     Disconnected  2                      P36     
E37[1AE37]       Unlocked     Enabled     Disconnected  2                      P37     
E38[1AE38]       Unlocked     Enabled     Disconnected  2                      P38     
E39[1AE39]       Unlocked     Enabled     Disconnected  2                      P39     
E40[1AE40]       Unlocked     Enabled     Disconnected  2                      P40     
E41[1AE41]       Unlocked     Enabled     Disconnected  2                      P41     
E42[1AE42]       Unlocked     Enabled     Disconnected  2                      P42     
E43[1AE43]       Unlocked     Enabled     Disconnected  0                      P43     
E44[1AE44]       Unlocked     Enabled     Disconnected  2                      P44     
E45[1AE45]       Unlocked     Enabled     Disconnected  0                      P45     
E46[1AE46]       Unlocked     Enabled     Disconnected  0                      P46     
E47[1AE47]       Unlocked     Enabled     Disconnected  0                      P47     
E48[1AE48]       Unlocked     Enabled     Disconnected  0                      P48     
E49[1AE49]       Unlocked     Enabled     Disconnected  0                      P49     
E50[1AE50]       Unlocked     Enabled     Disconnected  0                      P50     
E51[1AE51]       Unlocked     Enabled     Disconnected  2                      P51     
E52[1AE52]       Unlocked     Enabled     Disconnected  0                      P52     
E53[1AE53]       Unlocked     Enabled     Disconnected  0                      P53     
E54[1AE54]       Unlocked     Enabled     Disconnected  0                      P54     
E55[1AE55]       Unlocked     Enabled     Disconnected  0                      P55     
E56[1AE56]       Unlocked     Enabled     Disconnected  0                      P56     
E57[1AE57]       Unlocked     Enabled     Disconnected  2                      P57     
E58[1AE58]       Unlocked     Enabled     Disconnected  0                      P58     
E59[1AE59]       Unlocked     Enabled     Disconnected  0                      P59     
E60[1AE60]       Unlocked     Enabled     Disconnected  4                      P60     
E61[1AE61]       Unlocked     Enabled     Disconnected  0                      P61     
E62[1AE62]       Unlocked     Enabled     Disconnected  0                      P62     
E63[1AE63]       Unlocked     Enabled     Disconnected  0                      P63     
E64[1AE64]       Unlocked     Enabled     Disconnected  0                      P64     
E65[1AE65]       Unlocked     Enabled     Disconnected  2                      P65     
E66[1AE66]       Unlocked     Enabled     Disconnected  2                      P66     
E67[1AE67]       Unlocked     Enabled     Disconnected  0                      P67     
E68[1AE68]       Unlocked     Enabled     Disconnected  0                      P68     
E69[1AE69]       Unlocked     Enabled     Disconnected  0                      P69     
E70[1AE70]       Unlocked     Enabled     Disconnected  0                      P70     
E71[1AE71]       Unlocked     Enabled     Disconnected  0                      P71     
E72[1AE72]       Unlocked     Enabled     Disconnected  0                      P72     
E73[1AE73]       Unlocked     Enabled     Disconnected  0                      P73     
E74[1AE74]       Unlocked     Enabled     Disconnected  0                      P74     
E75[1AE75]       Unlocked     Enabled     Disconnected  0                      P75     
E76[1AE76]       Unlocked     Enabled     Disconnected  0                      P76     
E77[1AE77]       Unlocked     Enabled     Disconnected  2                      P77     
E78[1AE78]       Unlocked     Enabled     Disconnected  2                      P78     
E79[1AE79]       Unlocked     Enabled     Disconnected  0                      P79     
E80[1AE80]       Unlocked     Enabled     Disconnected  0                      P80     
E81[1AE81]       Unlocked     Enabled     Disconnected  0                      P81     
E82[1AE82]       Unlocked     Enabled     Disconnected  2                      P82     
E83[1AE83]       Unlocked     Enabled     Disconnected  0                      P83     
E84[1AE84]       Unlocked     Enabled     Disconnected  0                      P84     
E85[1AE85]       Unlocked     Enabled     Disconnected  0                      P85     
E86[1AE86]       Unlocked     Enabled     Disconnected  0                      P86     
E87[1AE87]       Unlocked     Enabled     Disconnected  0                      P87     
E88[1AE88]       Unlocked     Enabled     Disconnected  0                      P88     
E89[1AE89]       Unlocked     Enabled     Disconnected  2                      P89     
E90[1AE90]       Unlocked     Enabled     Disconnected  2                      P90     
E91[1AE91]       Unlocked     Enabled     Disconnected  0                      P91     
E92[1AE92]       Unlocked     Enabled     Disconnected  0                      P92     
E93[1AE93]       Unlocked     Enabled     Disconnected  0                      P93     
E94[1AE94]       Unlocked     Enabled     Disconnected  0                      P94     
E95[1AE95]       Unlocked     Enabled     Disconnected  0                      P95     
E96[1AE96]       Unlocked     Enabled     Disconnected  0                      P96     
E97[1AE97]       Unlocked     Enabled     Disconnected  0                      P97     
E98[1AE98]       Unlocked     Enabled     Disconnected  0                      P98     
E99[1AE99]       Unlocked     Enabled     Disconnected  0                      P99     
E100[1AE100]     Unlocked     Enabled     Disconnected  4                      P100    
E101[1AE101]     Unlocked     Enabled     Disconnected  0                      P101    
E102[1AE102]     Unlocked     Enabled     Disconnected  0                      P102    
E103[1AE103]     Unlocked     Enabled     Disconnected  0                      P103    
E104[1AE104]     Unlocked     Enabled     Disconnected  0                      P104    
E105[1AE105]     Unlocked     Enabled     Disconnected  4                      P105    
E106[1AE106]     Unlocked     Enabled     Disconnected  2                      P106    
E107[1AE107]     Unlocked     Enabled     Disconnected  0                      P107    
E108[1AE108]     Unlocked     Enabled     Disconnected  0                      P108    
E109[1AE109]     Unlocked     Enabled     Disconnected  0                      P109    
E110[1AE110]     Unlocked     Enabled     Disconnected  0                      P110    
E111[1AE111]     Unlocked     Enabled     Disconnected  0                      P111    
E112[1AE112]     Unlocked     Enabled     Disconnected  0                      P112    
E113[1AE113]     Unlocked     Enabled     Disconnected  0                      P113    
E114[1AE114]     Unlocked     Enabled     Disconnected  0                      P114    
E115[1AE115]     Unlocked     Enabled     Disconnected  2                      P115    
E116[1AE116]     Unlocked     Enabled     Disconnected  2                      P116    
E117[1AE117]     Unlocked     Enabled     Disconnected  0                      P117    
E118[1AE118]     Unlocked     Enabled     Disconnected  0                      P118    
E119[1AE119]     Unlocked     Enabled     Disconnected  2                      P119    
E120[1AE120]     Unlocked     Enabled     Disconnected  0                      P120    
E121[1AE121]     Unlocked     Enabled     Disconnected  0                      P121    
E122[1AE122]     Unlocked     Enabled     Disconnected  0                      P122    
E123[1AE123]     Unlocked     Enabled     Disconnected  0                      P123    
E124[1AE124]     Unlocked     Enabled     Disconnected  0                      P124    
E125[1AE125]     Unlocked     Enabled     Disconnected  2                      P125    
E126[1AE126]     Unlocked     Enabled     Disconnected  2                      P126    
E127[1AE127]     Unlocked     Enabled     Disconnected  0                      P127    
E128[1AE128]     Unlocked     Enabled     Connected     1       W12[1AW12]     P128    
1AE129           Unlocked     Enabled     Disconnected  0                              
1AE130           Unlocked     Enabled     Disconnected  0                              
E129[1BE1]       Unlocked     Enabled     Connected     62      W130[1BW2]     P1      
E130[1BE2]       Unlocked     Enabled     Connected     50      W129[1BW1]     P2      
E131[1BE3]       Unlocked     Enabled     Disconnected  29                     P3      
E132[1BE4]       Unlocked     Enabled     Disconnected  25                     P4      
E133[1BE5]       Unlocked     Enabled     Disconnected  39                     P5      
E134[1BE6]       Unlocked     Enabled     Disconnected  26                     P6      
E135[1BE7]       Unlocked     Enabled     Disconnected  20                     P7      
E136[1BE8]       Unlocked     Enabled     Disconnected  20                     P8      
E137[1BE9]       Unlocked     Enabled     Disconnected  4                      P9      
E138[1BE10]      Unlocked     Enabled     Disconnected  4                      P10     
E139[1BE11]      Unlocked     Enabled     Disconnected  4                      P11     
E140[1BE12]      Unlocked     Enabled     Connected     5       W256[1BW128]   P12     
E141[1BE13]      Unlocked     Enabled     Disconnected  4                      P13     
E142[1BE14]      Unlocked     Enabled     Disconnected  2                      P14     
E143[1BE15]      Unlocked     Enabled     Disconnected  2                      P15     
E144[1BE16]      Unlocked     Enabled     Disconnected  4                      P16     
E145[1BE17]      Unlocked     Enabled     Disconnected  2                      P17     
E146[1BE18]      Unlocked     Enabled     Disconnected  2                      P18     
E147[1BE19]      Unlocked     Enabled     Disconnected  6                      P19     
E148[1BE20]      Unlocked     Enabled     Disconnected  4                      P20     
E149[1BE21]      Unlocked     Enabled     Disconnected  2                      P21     
E150[1BE22]      Unlocked     Enabled     Disconnected  2                      P22     
E151[1BE23]      Unlocked     Enabled     Disconnected  4                      P23     
E152[1BE24]      Unlocked     Enabled     Disconnected  4                      P24     
E153[1BE25]      Unlocked     Enabled     Disconnected  2                      P25     
E154[1BE26]      Unlocked     Enabled     Disconnected  4                      P26     
E155[1BE27]      Unlocked     Enabled     Disconnected  4                      P27     
E156[1BE28]      Unlocked     Enabled     Disconnected  2                      P28     
E157[1BE29]      Unlocked     Enabled     Disconnected  2                      P29     
E158[1BE30]      Unlocked     Enabled     Disconnected  4                      P30     
E159[1BE31]      Unlocked     Enabled     Disconnected  2                      P31     
E160[1BE32]      Unlocked     Enabled     Disconnected  2                      P32     
E161[1BE33]      Unlocked     Enabled     Disconnected  2                      P33     
E162[1BE34]      Unlocked     Enabled     Disconnected  2                      P34     
E163[1BE35]      Unlocked     Enabled     Disconnected  2                      P35     
E164[1BE36]      Unlocked     Enabled     Disconnected  2                      P36     
E165[1BE37]      Unlocked     Enabled     Disconnected  2                      P37     
E166[1BE38]      Unlocked     Enabled     Disconnected  2                      P38     
E167[1BE39]      Unlocked     Enabled     Disconnected  2                      P39     
E168[1BE40]      Unlocked     Enabled     Disconnected  2                      P40     
E169[1BE41]      Unlocked     Enabled     Disconnected  0                      P41     
E170[1BE42]      Unlocked     Enabled     Disconnected  0                      P42     
E171[1BE43]      Unlocked     Enabled     Disconnected  0                      P43     
E172[1BE44]      Unlocked     Enabled     Disconnected  2                      P44     
E173[1BE45]      Unlocked     Enabled     Disconnected  0                      P45     
E174[1BE46]      Unlocked     Enabled     Disconnected  0                      P46     
E175[1BE47]      Unlocked     Enabled     Disconnected  0                      P47     
E176[1BE48]      Unlocked     Enabled     Disconnected  0                      P48     
E177[1BE49]      Unlocked     Enabled     Disconnected  0                      P49     
E178[1BE50]      Unlocked     Enabled     Disconnected  0                      P50     
E179[1BE51]      Unlocked     Enabled     Disconnected  2                      P51     
E180[1BE52]      Unlocked     Enabled     Disconnected  0                      P52     
E181[1BE53]      Unlocked     Enabled     Disconnected  0                      P53     
E182[1BE54]      Unlocked     Enabled     Disconnected  0                      P54     
E183[1BE55]      Unlocked     Enabled     Disconnected  0                      P55     
E184[1BE56]      Unlocked     Enabled     Disconnected  0                      P56     
E185[1BE57]      Unlocked     Enabled     Disconnected  2                      P57     
E186[1BE58]      Unlocked     Enabled     Disconnected  0                      P58     
E187[1BE59]      Unlocked     Enabled     Disconnected  0                      P59     
E188[1BE60]      Unlocked     Enabled     Disconnected  2                      P60     
E189[1BE61]      Unlocked     Enabled     Disconnected  0                      P61     
E190[1BE62]      Unlocked     Enabled     Disconnected  0                      P62     
E191[1BE63]      Unlocked     Enabled     Disconnected  0                      P63     
E192[1BE64]      Unlocked     Enabled     Disconnected  0                      P64     
E193[1BE65]      Unlocked     Enabled     Disconnected  2                      P65     
E194[1BE66]      Unlocked     Enabled     Disconnected  2                      P66     
E195[1BE67]      Unlocked     Enabled     Disconnected  0                      P67     
E196[1BE68]      Unlocked     Enabled     Disconnected  0                      P68     
E197[1BE69]      Unlocked     Enabled     Disconnected  0                      P69     
E198[1BE70]      Unlocked     Enabled     Disconnected  0                      P70     
E199[1BE71]      Unlocked     Enabled     Disconnected  0                      P71     
E200[1BE72]      Unlocked     Enabled     Disconnected  0                      P72     
E201[1BE73]      Unlocked     Enabled     Disconnected  2                      P73     
E202[1BE74]      Unlocked     Enabled     Disconnected  0                      P74     
E203[1BE75]      Unlocked     Enabled     Disconnected  0                      P75     
E204[1BE76]      Unlocked     Enabled     Disconnected  0                      P76     
E205[1BE77]      Unlocked     Enabled     Disconnected  2                      P77     
E206[1BE78]      Unlocked     Enabled     Disconnected  2                      P78     
E207[1BE79]      Unlocked     Enabled     Disconnected  0                      P79     
E208[1BE80]      Unlocked     Enabled     Disconnected  0                      P80     
E209[1BE81]      Unlocked     Enabled     Disconnected  0                      P81     
E210[1BE82]      Unlocked     Enabled     Disconnected  2                      P82     
E211[1BE83]      Unlocked     Enabled     Disconnected  0                      P83     
E212[1BE84]      Unlocked     Enabled     Disconnected  0                      P84     
E213[1BE85]      Unlocked     Enabled     Disconnected  0                      P85     
E214[1BE86]      Unlocked     Enabled     Disconnected  0                      P86     
E215[1BE87]      Unlocked     Enabled     Disconnected  0                      P87     
E216[1BE88]      Unlocked     Enabled     Disconnected  0                      P88     
E217[1BE89]      Unlocked     Enabled     Disconnected  2                      P89     
E218[1BE90]      Unlocked     Enabled     Disconnected  2                      P90     
E219[1BE91]      Unlocked     Enabled     Disconnected  0                      P91     
E220[1BE92]      Unlocked     Enabled     Disconnected  0                      P92     
E221[1BE93]      Unlocked     Enabled     Disconnected  0                      P93     
E222[1BE94]      Unlocked     Enabled     Disconnected  0                      P94     
E223[1BE95]      Unlocked     Enabled     Disconnected  2                      P95     
E224[1BE96]      Unlocked     Enabled     Disconnected  0                      P96     
E225[1BE97]      Unlocked     Enabled     Disconnected  0                      P97     
E226[1BE98]      Unlocked     Enabled     Disconnected  0                      P98     
E227[1BE99]      Unlocked     Enabled     Disconnected  0                      P99     
E228[1BE100]     Unlocked     Enabled     Disconnected  0                      P100    
E229[1BE101]     Unlocked     Enabled     Disconnected  0                      P101    
E230[1BE102]     Unlocked     Enabled     Disconnected  0                      P102    
E231[1BE103]     Unlocked     Enabled     Disconnected  0                      P103    
E232[1BE104]     Unlocked     Enabled     Disconnected  0                      P104    
E233[1BE105]     Unlocked     Enabled     Disconnected  4                      P105    
E234[1BE106]     Unlocked     Enabled     Disconnected  2                      P106    
E235[1BE107]     Unlocked     Enabled     Disconnected  0                      P107    
E236[1BE108]     Unlocked     Enabled     Disconnected  0                      P108    
E237[1BE109]     Unlocked     Enabled     Disconnected  0                      P109    
E238[1BE110]     Unlocked     Enabled     Disconnected  0                      P110    
E239[1BE111]     Unlocked     Enabled     Disconnected  0                      P111    
E240[1BE112]     Unlocked     Enabled     Disconnected  0                      P112    
E241[1BE113]     Unlocked     Enabled     Disconnected  0                      P113    
E242[1BE114]     Unlocked     Enabled     Disconnected  0                      P114    
E243[1BE115]     Unlocked     Enabled     Disconnected  2                      P115    
E244[1BE116]     Unlocked     Enabled     Disconnected  2                      P116    
E245[1BE117]     Unlocked     Enabled     Disconnected  0                      P117    
E246[1BE118]     Unlocked     Enabled     Disconnected  0                      P118    
E247[1BE119]     Unlocked     Enabled     Disconnected  0                      P119    
E248[1BE120]     Unlocked     Enabled     Disconnected  0                      P120    
E249[1BE121]     Unlocked     Enabled     Disconnected  0                      P121    
E250[1BE122]     Unlocked     Enabled     Disconnected  0                      P122    
E251[1BE123]     Unlocked     Enabled     Disconnected  0                      P123    
E252[1BE124]     Unlocked     Enabled     Disconnected  0                      P124    
E253[1BE125]     Unlocked     Enabled     Disconnected  2                      P125    
E254[1BE126]     Unlocked     Enabled     Disconnected  2                      P126    
E255[1BE127]     Unlocked     Enabled     Disconnected  0                      P127    
E256[1BE128]     Unlocked     Enabled     Connected     1       W140[1BW12]    P128    
1BE129           Unlocked     Enabled     Disconnected  0                              
1BE130           Unlocked     Enabled     Disconnected  0                              
W1[1AW1]         Unlocked     Enabled     Connected     88      E2[1AE2]       P1      
W2[1AW2]         Unlocked     Enabled     Connected     86      E1[1AE1]       P2      
W3[1AW3]         Unlocked     Enabled     Disconnected  33                     P3      
W4[1AW4]         Unlocked     Enabled     Disconnected  40                     P4      
W5[1AW5]         Unlocked     Enabled     Disconnected  34                     P5      
W6[1AW6]         Unlocked     Enabled     Disconnected  38                     P6      
W7[1AW7]         Unlocked     Enabled     Disconnected  24                     P7      
W8[1AW8]         Unlocked     Enabled     Disconnected  22                     P8      
W9[1AW9]         Unlocked     Enabled     Disconnected  4                      P9      
W10[1AW10]       Unlocked     Enabled     Disconnected  4                      P10     
W11[1AW11]       Unlocked     Enabled     Disconnected  4                      P11     
W12[1AW12]       Unlocked     Enabled     Connected     3       E128[1AE128]   P12     
W13[1AW13]       Unlocked     Enabled     Disconnected  2                      P13     
W14[1AW14]       Unlocked     Enabled     Disconnected  2                      P14     
W15[1AW15]       Unlocked     Enabled     Disconnected  2                      P15     
W16[1AW16]       Unlocked     Enabled     Disconnected  4                      P16     
W17[1AW17]       Unlocked     Enabled     Disconnected  2                      P17     
W18[1AW18]       Unlocked     Enabled     Disconnected  2                      P18     
W19[1AW19]       Unlocked     Enabled     Disconnected  6                      P19     
W20[1AW20]       Unlocked     Enabled     Disconnected  4                      P20     
W21[1AW21]       Unlocked     Enabled     Disconnected  2                      P21     
W22[1AW22]       Unlocked     Enabled     Disconnected  2                      P22     
W23[1AW23]       Unlocked     Enabled     Disconnected  6                      P23     
W24[1AW24]       Unlocked     Enabled     Disconnected  6                      P24     
W25[1AW25]       Unlocked     Enabled     Disconnected  4                      P25     
W26[1AW26]       Unlocked     Enabled     Disconnected  2                      P26     
W27[1AW27]       Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  2                      P28     
W29[1AW29]       Unlocked     Enabled     Disconnected  2                      P29     
W30[1AW30]       Unlocked     Enabled     Disconnected  4                      P30     
W31[1AW31]       Unlocked     Enabled     Disconnected  2                      P31     
W32[1AW32]       Unlocked     Enabled     Disconnected  2                      P32     
W33[1AW33]       Unlocked     Enabled     Disconnected  2                      P33     
W34[1AW34]       Unlocked     Enabled     Disconnected  2                      P34     
W35[1AW35]       Unlocked     Enabled     Disconnected  2                      P35     
W36[1AW36]       Unlocked     Enabled     Disconnected  2                      P36     
W37[1AW37]       Unlocked     Enabled     Disconnected  2                      P37     
W38[1AW38]       Unlocked     Enabled     Disconnected  2                      P38     
W39[1AW39]       Unlocked     Enabled     Disconnected  2                      P39     
W40[1AW40]       Unlocked     Enabled     Disconnected  2                      P40     
W41[1AW41]       Unlocked     Enabled     Disconnected  0                      P41     
W42[1AW42]       Unlocked     Enabled     Disconnected  0                      P42     
W43[1AW43]       Unlocked     Enabled     Disconnected  0                      P43     
W44[1AW44]       Unlocked     Enabled     Disconnected  2                      P44     
W45[1AW45]       Unlocked     Enabled     Disconnected  0                      P45     
W46[1AW46]       Unlocked     Enabled     Disconnected  0                      P46     
W47[1AW47]       Unlocked     Enabled     Disconnected  0                      P47     
W48[1AW48]       Unlocked     Enabled     Disconnected  0                      P48     
W49[1AW49]       Unlocked     Enabled     Disconnected  0                      P49     
W50[1AW50]       Unlocked     Enabled     Disconnected  2                      P50     
W51[1AW51]       Unlocked     Enabled     Disconnected  0                      P51     
W52[1AW52]       Unlocked     Enabled     Disconnected  0                      P52     
W53[1AW53]       Unlocked     Enabled     Disconnected  0                      P53     
W54[1AW54]       Unlocked     Enabled     Disconnected  0                      P54     
W55[1AW55]       Unlocked     Enabled     Disconnected  0                      P55     
W56[1AW56]       Unlocked     Enabled     Disconnected  0                      P56     
W57[1AW57]       Unlocked     Enabled     Disconnected  0                      P57     
W58[1AW58]       Unlocked     Enabled     Disconnected  0                      P58     
W59[1AW59]       Unlocked     Enabled     Disconnected  0                      P59     
W60[1AW60]       Unlocked     Enabled     Disconnected  0                      P60     
W61[1AW61]       Unlocked     Enabled     Disconnected  0                      P61     
W62[1AW62]       Unlocked     Enabled     Disconnected  0                      P62     
W63[1AW63]       Unlocked     Enabled     Disconnected  2                      P63     
W64[1AW64]       Unlocked     Enabled     Disconnected  2                      P64     
W65[1AW65]       Unlocked     Enabled     Disconnected  2                      P65     
W66[1AW66]       Unlocked     Enabled     Disconnected  2                      P66     
W67[1AW67]       Unlocked     Enabled     Disconnected  0                      P67     
W68[1AW68]       Unlocked     Enabled     Disconnected  0                      P68     
W69[1AW69]       Unlocked     Enabled     Disconnected  0                      P69     
W70[1AW70]       Unlocked     Enabled     Disconnected  2                      P70     
W71[1AW71]       Unlocked     Enabled     Disconnected  0                      P71     
W72[1AW72]       Unlocked     Enabled     Disconnected  0                      P72     
W73[1AW73]       Unlocked     Enabled     Disconnected  0                      P73     
W74[1AW74]       Unlocked     Enabled     Disconnected  0                      P74     
W75[1AW75]       Unlocked     Enabled     Disconnected  2                      P75     
W76[1AW76]       Unlocked     Enabled     Disconnected  0                      P76     
W77[1AW77]       Unlocked     Enabled     Disconnected  2                      P77     
W78[1AW78]       Unlocked     Enabled     Disconnected  2                      P78     
W79[1AW79]       Unlocked     Enabled     Disconnected  0                      P79     
W80[1AW80]       Unlocked     Enabled     Disconnected  0                      P80     
W81[1AW81]       Unlocked     Enabled     Disconnected  0                      P81     
W82[1AW82]       Unlocked     Enabled     Disconnected  4                      P82     
W83[1AW83]       Unlocked     Enabled     Disconnected  0                      P83     
W84[1AW84]       Unlocked     Enabled     Disconnected  0                      P84     
W85[1AW85]       Unlocked     Enabled     Disconnected  0                      P85     
W86[1AW86]       Unlocked     Enabled     Disconnected  0                      P86     
W87[1AW87]       Unlocked     Enabled     Disconnected  0                      P87     
W88[1AW88]       Unlocked     Enabled     Disconnected  0                      P88     
W89[1AW89]       Unlocked     Enabled     Disconnected  2    
02-05-2020 13:05 Connection P1<->P2 completed successfully
                  P89     
W90[1AW90]       Unlocked     Enabled     Disconnected  2                      P90     
W91[1AW91]       Unlocked     Enabled     Disconnected  0                      P91     
W92[1AW92]       Unlocked     Enabled     Disconnected  0                      P92     
W93[1AW93]       Unlocked     Enabled     Disconnected  0                      P93     
W94[1AW94]       Unlocked     Enabled     Disconnected  0                      P94     
W95[1AW95]       Unlocked     Enabled     Disconnected  0                      P95     
W96[1AW96]       Unlocked     Enabled     Disconnected  0                      P96     
W97[1AW97]       Unlocked     Enabled     Disconnected  0                      P97     
W98[1AW98]       Unlocked     Enabled     Disconnected  0                      P98     
W99[1AW99]       Unlocked     Enabled     Disconnected  0                      P99     
W100[1AW100]     Unlocked     Enabled     Disconnected  8                      P100    
W101[1AW101]     Unlocked     Enabled     Disconnected  0                      P101    
W102[1AW102]     Unlocked     Enabled     Disconnected  0                      P102    
W103[1AW103]     Unlocked     Enabled     Disconnected  0                      P103    
W104[1AW104]     Unlocked     Enabled     Disconnected  0                      P104    
W105[1AW105]     Unlocked     Enabled     Disconnected  2                      P105    
W106[1AW106]     Unlocked     Enabled     Disconnected  2                      P106    
W107[1AW107]     Unlocked     Enabled     Disconnected  0                      P107    
W108[1AW108]     Unlocked     Enabled     Disconnected  0                      P108    
W109[1AW109]     Unlocked     Enabled     Disconnected  0                      P109    
W110[1AW110]     Unlocked     Enabled     Disconnected  0                      P110    
W111[1AW111]     Unlocked     Enabled     Disconnected  2                      P111    
W112[1AW112]     Unlocked     Enabled     Disconnected  0                      P112    
W113[1AW113]     Unlocked     Enabled     Disconnected  0                      P113    
W114[1AW114]     Unlocked     Enabled     Disconnected  0                      P114    
W115[1AW115]     Unlocked     Enabled     Disconnected  4                      P115    
W116[1AW116]     Unlocked     Enabled     Disconnected  0                      P116    
W117[1AW117]     Unlocked     Enabled     Disconnected  0                      P117    
W118[1AW118]     Unlocked     Enabled     Disconnected  2                      P118    
W119[1AW119]     Unlocked     Enabled     Disconnected  0                      P119    
W120[1AW120]     Unlocked     Enabled     Disconnected  0                      P120    
W121[1AW121]     Unlocked     Enabled     Disconnected  0                      P121    
W122[1AW122]     Unlocked     Enabled     Disconnected  0                      P122    
W123[1AW123]     Unlocked     Enabled     Disconnected  0                      P123    
W124[1AW124]     Unlocked     Enabled     Disconnected  0                      P124    
W125[1AW125]     Unlocked     Enabled     Disconnected  2                      P125    
W126[1AW126]     Unlocked     Enabled     Disconnected  2                      P126    
W127[1AW127]     Unlocked     Enabled     Disconnected  0                      P127    
W128[1AW128]     Unlocked     Enabled     Connected     1       E12[1AE12]     P128    
1AW129           Unlocked     Enabled     Disconnected  0                              
1AW130           Unlocked     Enabled     Disconnected  0                              
1AW131           Unlocked     Enabled     Disconnected  0                              
1AW132           Unlocked     Enabled     Disconnected  0                              
W129[1BW1]       Unlocked     Enabled     Connected     53      E130[1BE2]     P1      
W130[1BW2]       Unlocked     Enabled     Connected     46      E129[1BE1]     P2      
W131[1BW3]       Unlocked     Enabled     Disconnected  20                     P3      
W132[1BW4]       Unlocked     Enabled     Disconnected  24                     P4      
W133[1BW5]       Unlocked     Enabled     Disconnected  28                     P5      
W134[1BW6]       Unlocked     Enabled     Disconnected  24                     P6      
W135[1BW7]       Unlocked     Enabled     Disconnected  10                     P7      
W136[1BW8]       Unlocked     Enabled     Disconnected  18                     P8      
W137[1BW9]       Unlocked     Enabled     Disconnected  4                      P9      
W138[1BW10]      Unlocked     Enabled     Disconnected  4                      P10     
W139[1BW11]      Unlocked     Enabled     Disconnected  4                      P11     
W140[1BW12]      Unlocked     Enabled     Connected     3       E256[1BE128]   P12     
W141[1BW13]      Unlocked     Enabled     Disconnected  2                      P13     
W142[1BW14]      Unlocked     Enabled     Disconnected  2                      P14     
W143[1BW15]      Unlocked     Enabled     Disconnected  2                      P15     
W144[1BW16]      Unlocked     Enabled     Disconnected  4                      P16     
W145[1BW17]      Unlocked     Enabled     Disconnected  2                      P17     
W146[1BW18]      Unlocked     Enabled     Disconnected  2                      P18     
W147[1BW19]      Unlocked     Enabled     Disconnected  6                      P19     
W148[1BW20]      Unlocked     Enabled     Disconnected  4                      P20     
W149[1BW21]      Unlocked     Enabled     Disconnected  2                      P21     
W150[1BW22]      Unlocked     Enabled     Disconnected  2                      P22     
W151[1BW23]      Unlocked     Enabled     Disconnected  6                      P23     
W152[1BW24]      Unlocked     Enabled     Disconnected  6                      P24     
W153[1BW25]      Unlocked     Enabled     Disconnected  2                      P25     
W154[1BW26]      Unlocked     Enabled     Disconnected  2                      P26     
W155[1BW27]      Unlocked     Enabled     Disconnected  4                      P27     
W156[1BW28]      Unlocked     Enabled     Disconnected  2                      P28     
W157[1BW29]      Unlocked     Enabled     Disconnected  2                      P29     
W158[1BW30]      Unlocked     Enabled     Disconnected  2                      P30     
W159[1BW31]      Unlocked     Enabled     Disconnected  2                      P31     
W160[1BW32]      Unlocked     Enabled     Disconnected  2                      P32     
W161[1BW33]      Unlocked     Enabled     Disconnected  2                      P33     
W162[1BW34]      Unlocked     Enabled     Disconnected  2                      P34     
W163[1BW35]      Unlocked     Enabled     Disconnected  2                      P35     
W164[1BW36]      Unlocked     Enabled     Disconnected  2                      P36     
W165[1BW37]      Unlocked     Enabled     Disconnected  2                      P37     
W166[1BW38]      Unlocked     Enabled     Disconnected  2                      P38     
W167[1BW39]      Unlocked     Enabled     Disconnected  2                      P39     
W168[1BW40]      Unlocked     Enabled     Disconnected  2                      P40     
W169[1BW41]      Unlocked     Enabled     Disconnected  0                      P41     
W170[1BW42]      Unlocked     Enabled     Disconnected  0                      P42     
W171[1BW43]      Unlocked     Enabled     Disconnected  0                      P43     
W172[1BW44]      Unlocked     Enabled     Disconnected  2                      P44     
W173[1BW45]      Unlocked     Enabled     Disconnected  0                      P45     
W174[1BW46]      Unlocked     Enabled     Disconnected  0                      P46     
W175[1BW47]      Unlocked     Enabled     Disconnected  0                      P47     
W176[1BW48]      Unlocked     Enabled     Disconnected  0                      P48     
W177[1BW49]      Unlocked     Enabled     Disconnected  0                      P49     
W178[1BW50]      Unlocked     Enabled     Disconnected  2                      P50     
W179[1BW51]      Unlocked     Enabled     Disconnected  0                      P51     
W180[1BW52]      Unlocked     Enabled     Disconnected  0                      P52     
W181[1BW53]      Unlocked     Enabled     Disconnected  2                      P53     
W182[1BW54]      Unlocked     Enabled     Disconnected  0                      P54     
W183[1BW55]      Unlocked     Enabled     Disconnected  0                      P55     
W184[1BW56]      Unlocked     Enabled     Disconnected  0                      P56     
W185[1BW57]      Unlocked     Enabled     Disconnected  0                      P57     
W186[1BW58]      Unlocked     Enabled     Disconnected  0                      P58     
W187[1BW59]      Unlocked     Enabled     Disconnected  0                      P59     
W188[1BW60]      Unlocked     Enabled     Disconnected  0                      P60     
W189[1BW61]      Unlocked     Enabled     Disconnected  0                      P61     
W190[1BW62]      Unlocked     Enabled     Disconnected  0                      P62     
W191[1BW63]      Unlocked     Enabled     Disconnected  2                      P63     
W192[1BW64]      Unlocked     Enabled     Disconnected  2                      P64     
W193[1BW65]      Unlocked     Enabled     Disconnected  0                      P65     
W194[1BW66]      Unlocked     Enabled     Disconnected  0                      P66     
W195[1BW67]      Unlocked     Enabled     Disconnected  0                      P67     
W196[1BW68]      Unlocked     Enabled     Disconnected  0                      P68     
W197[1BW69]      Unlocked     Enabled     Disconnected  0                      P69     
W198[1BW70]      Unlocked     Enabled     Disconnected  2                      P70     
W199[1BW71]      Unlocked     Enabled     Disconnected  0                      P71     
W200[1BW72]      Unlocked     Enabled     Disconnected  0                      P72     
W201[1BW73]      Unlocked     Enabled     Disconnected  0                      P73     
W202[1BW74]      Unlocked     Enabled     Disconnected  0                      P74     
W203[1BW75]      Unlocked     Enabled     Disconnected  2                      P75     
W204[1BW76]      Unlocked     Enabled     Disconnected  0                      P76     
W205[1BW77]      Unlocked     Enabled     Disconnected  2                      P77     
W206[1BW78]      Unlocked     Enabled     Disconnected  2                      P78     
W207[1BW79]      Unlocked     Enabled     Disconnected  0                      P79     
W208[1BW80]      Unlocked     Enabled     Disconnected  0                      P80     
W209[1BW81]      Unlocked     Enabled     Disconnected  0                      P81     
W210[1BW82]      Unlocked     Enabled     Disconnected  2                      P82     
W211[1BW83]      Unlocked     Enabled     Disconnected  0                      P83     
W212[1BW84]      Unlocked     Enabled     Disconnected  0                      P84     
W213[1BW85]      Unlocked     Enabled     Disconnected  0                      P85     
W214[1BW86]      Unlocked     Enabled     Disconnected  0                      P86     
W215[1BW87]      Unlocked     Enabled     Disconnected  0                      P87     
W216[1BW88]      Unlocked     Enabled     Disconnected  2                      P88     
W217[1BW89]      Unlocked     Enabled     Disconnected  2                      P89     
W218[1BW90]      Unlocked     Enabled     Disconnected  2                      P90     
W219[1BW91]      Unlocked     Enabled     Disconnected  0                      P91     
W220[1BW92]      Unlocked     Enabled     Disconnected  2                      P92     
W221[1BW93]      Unlocked     Enabled     Disconnected  0                      P93     
W222[1BW94]      Unlocked     Enabled     Disconnected  0                      P94     
W223[1BW95]      Unlocked     Enabled     Disconnected  0                      P95     
W224[1BW96]      Unlocked     Enabled     Disconnected  0                      P96     
W225[1BW97]      Unlocked     Enabled     Disconnected  0                      P97     
W226[1BW98]      Unlocked     Enabled     Disconnected  0                      P98     
W227[1BW99]      Unlocked     Enabled     Disconnected  0                      P99     
W228[1BW100]     Unlocked     Enabled     Disconnected  2                      P100    
W229[1BW101]     Unlocked     Enabled     Disconnected  0                      P101    
W230[1BW102]     Unlocked     Enabled     Disconnected  0                      P102    
W231[1BW103]     Unlocked     Enabled     Disconnected  0                      P103    
W232[1BW104]     Unlocked     Enabled     Disconnected  0                      P104    
W233[1BW105]     Unlocked     Enabled     Disconnected  2                      P105    
W234[1BW106]     Unlocked     Enabled     Disconnected  2                      P106    
W235[1BW107]     Unlocked     Enabled     Disconnected  0                      P107    
W236[1BW108]     Unlocked     Enabled     Disconnected  0                      P108    
W237[1BW109]     Unlocked     Enabled     Disconnected  0                      P109    
W238[1BW110]     Unlocked     Enabled     Disconnected  0                      P110    
W239[1BW111]     Unlocked     Enabled     Disconnected  2                      P111    
W240[1BW112]     Unlocked     Enabled     Disconnected  0                      P112    
W241[1BW113]     Unlocked     Enabled     Disconnected  0                      P113    
W242[1BW114]     Unlocked     Enabled     Disconnected  0                      P114    
W243[1BW115]     Unlocked     Enabled     Disconnected  2                      P115    
W244[1BW116]     Unlocked     Enabled     Disconnected  0                      P116    
W245[1BW117]     Unlocked     Enabled     Disconnected  0                      P117    
W246[1BW118]     Unlocked     Enabled     Disconnected  0                      P118    
W247[1BW119]     Unlocked     Enabled     Disconnected  2                      P119    
W248[1BW120]     Unlocked     Enabled     Disconnected  0                      P120    
W249[1BW121]     Unlocked     Enabled     Disconnected  0                      P121    
W250[1BW122]     Unlocked     Enabled     Disconnected  0                      P122    
W251[1BW123]     Unlocked     Enabled     Disconnected  0                      P123    
W252[1BW124]     Unlocked     Enabled     Disconnected  0                      P124    
W253[1BW125]     Unlocked     Enabled     Disconnected  2                      P125    
W254[1BW126]     Unlocked     Enabled     Disconnected  2                      P126    
W255[1BW127]     Unlocked     Enabled     Disconnected  2                      P127    
W256[1BW128]     Unlocked     Enabled     Connected     3       E140[1BE12]    P128    
1BW129           Unlocked     Enabled     Disconnected  0                              
1BW130           Unlocked     Enabled     Disconnected  0                              
1BW131           Unlocked     Enabled     Disconnected  0                              
1BW132           Unlocked     Enabled     Disconnected  0                              
ROME[TECH]# '''


@patch('cloudshell.cli.session.ssh_session.paramiko', MagicMock())
@patch(
    'cloudshell.cli.session.ssh_session.SSHSession._clear_buffer',
    MagicMock(return_value=''),
)
class TestLogInOutput(BaseRomeTestCase):
    def test_log_in_port_show_output(self):
        host = '192.168.1.2'
        output = RomeTemplateExecutor.remove_logs_from_output(PORT_SHOW_WITH_LOG)
        port_table = PortTable.from_output(output, host)

        self.assertEqual(128, len(port_table.logical_ports))
        for logic_port in port_table.logical_ports:
            self.assertEqual(2, len(logic_port.rome_ports))
            for rome_port in logic_port.rome_ports:
                self.assertIsNotNone(rome_port.e_port)
                self.assertIsNotNone(rome_port.w_port)

    def test_remove_logs(self):
        str_to_check = [
            (
                '''W87[1AW87]       Unlocked     Enabled     Disconnected  0                      P87
W88[1AW88]       Unlocked     Enabled     Disconnected  0                      P88
W89[1AW89]       Unlocked     Enabled     Disconnected  2    
02-05-2020 13:05 Connection P1<->P2 completed successfully
                  P89
W90[1AW90]       Unlocked     Enabled     Disconnected  2                      P90
W91[1AW91]       Unlocked     Enabled     Disconnected  0                      P91
''',
                '''W87[1AW87]       Unlocked     Enabled     Disconnected  0                      P87
W88[1AW88]       Unlocked     Enabled     Disconnected  0                      P88
W89[1AW89]       Unlocked     Enabled     Disconnected  2                      P89
W90[1AW90]       Unlocked     Enabled     Disconnected  2                      P90
W91[1AW91]       Unlocked     Enabled     Disconnected  0                      P91
''',
            ),
            (
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27] 
02-09-2020 10:43 Connection P119<->P24 completed successfully

      Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  2                      P28     
W29[1AW29]       Unlocked     Enabled     Disconnected  2                      P29     
''',
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27]       Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  2                      P28     
W29[1AW29]       Unlocked     Enabled     Disconnected  2                      P29     
'''
            ),
            (
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27] 
02-09-2020 12:04 CONNECTION OPERATION SUCCEEDED:E38[1AE38]<->W36[1AW36] OP:connect
      Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  6                      P28     
''',
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27]       Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  6                      P28     
'''
            ),
            (
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27] 
02-08-2020 10:46 CONNECTION OPERATION SKIPPED(already done):E1[1AE1]<->W2[1AW2] OP:connect

      Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  6                      P28     
''',
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27]       Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  6                      P28     
'''
            ),
            (
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27] 
02-08-2020 10:48 CONNECTION OPERATION SKIPPED(already done):E6[1AE6]<->W5[1AW5] OP:disconnect

      Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  6                      P28     
''',
                '''W26[1AW26]       Unlocked     Enabled     Disconnected  4                      P26     
W27[1AW27]       Unlocked     Enabled     Disconnected  4                      P27     
W28[1AW28]       Unlocked     Enabled     Disconnected  6                      P28     
'''
            ),
        ]

        for raw_str, fixed_str in str_to_check:
            self.assertEqual(
                fixed_str, RomeTemplateExecutor.remove_logs_from_output(raw_str)
            )
