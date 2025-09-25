# cython:language_level=3
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import cpuinfo
import GPUtil
import subprocess
from base64 import urlsafe_b64encode

from typing import Any, Dict
import cv2
import onnxruntime as ort
from openvino.runtime import Core, Tensor
import numpy as np
from frigate.config.config import FrigateConfig

import base64
import datetime
import random
import string
from frigate.comms.event_metadata_updater import (
    EventMetadataPublisher,
    EventMetadataTypeEnum,
)

import os
vehicle_characters_zh = ["金色","棕色","绿色","黄色","银色","灰色","浅蓝色","黑色","白色","蓝色","红色","粉色","橙色","紫色","轿车","SUV","MPV","面包车","卡车","皮卡","巴士","超跑","比亚迪","蔚来","特斯拉","大众","本田","丰田","奥迪","日产","宝马","广汽","奔驰","长安","别克","吉利","领克","哈弗","福特","沃尔沃","奇瑞","五菱","标致","雪佛兰","马自达","保时捷","路虎","雷克萨斯","凯迪拉克","名爵","现代",
                        "Model-3/Y","Model-S","秦Plus-EV","秦Plus-DM-i","海豚","腾势D9","宋Plus-DM-i-2021","速腾-2023","迈腾-2020","朗逸-2023","途观","帕萨特-2019~2020","轩逸-经典-2009/2012/2014/2016~2019","CRV-2021","雅阁-2018","RAV4荣放-2020~2023","欧拉-闪电猫","凯美瑞-2018~2019",
                               "A6L-致雅型-2019~2022","A4L-动感版-2020~2024","Q5-2013~2018","坦克300","3系-2020~2022","GL8-2017~2018","逍客-2021~2022","汉-DM-i","Q8","5系-2014~2017","Mini","理想-L6/L7/L8/l9","C200L/C260L-运动版-2022~2024","GLB-2020~2023","AION-S-魅","帕萨特-2022~2024","速腾-2019~2022","AION-Y","凯美瑞-锋尚版-2018~2019","CRV-2023","雅阁-2022",
                               "迈腾-2017~2019","朗逸-星空版-2023","A6L-动感型-2023~2024","A4L-致雅型-2020~2024","CS75-Plus-第二代-2022~2023","逸动-蓝鲸NE-2022~2023","君威-2020~2022","威朗-2022~2023","飞度","A3-Sportback","M6-2021~2023","H6-第三代-1.5T-2.0T-2021~2024","星越L","帝豪-2022~2024","海鸥","AION-S-MAX",
                               "自由侠","牧马人","几何-E萤火虫","几何-M6","ICON","玛驰","福克斯","蒙迪欧-2022~2025","锐界-2023~2025","Taycan","Macan-2022~2024",
                               "问界-M5","MEGA","问界-M7","S60-2020~2025","C40","元-Plus","思域-2022~2023","途观L-2022~2024","XC60-2022~2025",
                               "艾瑞泽8","瑞虎8-2019~2024","宏光","缤果","锋兰达-2023","红旗-H5","红旗-HS5","408-2019~2020","科鲁兹-2023~2024","昂克赛拉-2020~2023","卡罗拉-2019~2023","宋Pro-DM-i-2023~2024","ES-2023","CT5-2023~2024","P7","ES6","大狗-2024",
                               "卡罗拉锐放-2022~2023","Q5L-动感版-2021~2024","捷达-VS7-2020~2021","轩逸-XE~XL-2020~2022","轩逸-经典-XE~XV~XL-2021~2024/XE~XV~XL-2016~2019","轩逸-超混电驱-2023","轩逸-CVT-2023","3系-2023~2024","5系-豪华套装-2021~2023","5系-运动套装-2021~2023","朗逸-2018~2022","宋Plus-EV-2023~2024","宋Plus-DM-i-2023~2024",
                               "领克-03-2023","领克-03-2020~2022","领克-06-2020~2023","领克-06-EM-P-2023","CS75-Plus-经典款-2022","CS75-Plus-2020~2021","逸动-2020~2022","领克-08-EM-P-2023","途观L-2017~2021","帕萨特-2016~2017","ID3-2021~2023","宝来-2019~2021","MG5-2021~2023","MG7-2023","阿特兹-2020~2021","阿特兹-2017~2018",
                               "CX-30-2020~2022","CX-5-2022~2024","畅巡-2021~2022","迈锐宝XL-2019~2023","探界者-2021~2023","创酷-2019~2023","508-2019~2022","4008-2021~2022","5008-2021","GL8-陆上公务舱-2023","GL8-陆上公务舱-2020~2022","GL8-ES陆尊-2020~2022","GL8-艾维亚-2020~2022","GL8-ES陆尊-艾维亚-2023","赛那-2021~2023",
                               "福田-奥铃M卡","福田-祥菱M2","跃进-福星S80","伊兰特-2023","伊兰特-2022","ix35-2021","ix35-2023","宝骏510-2017","传祺M8-宗师-2023~2024","传祺M8-大师-2020~2023","传祺M8-领秀-2021~2023",
                               "探歌-2018~2022","探歌-2023~2024","探岳-Plus-2023~2024","探岳-R-Line-2019~2022","型格-2022~2023","皓影-2020~2021","UNI-V-2022~2024","驱逐舰05-2022~2024","唐-DM-i-2021~2024","唐-EV-2022~2024","唐-DM-p-2022~2024",
                               "问界-M9","探岳-R-Line-2023~2024","探岳-两驱-2019~2022","途安-2011~2015","CC-2013~2018",
                               "亚洲龙-2022~2023","雷凌-2019~2022","凯美瑞-2021~2023","锋兰达-2022","威兰达-2022~2023","RAV4荣放-2016~2019","汉兰达-2012~2013","汉兰达-2015~2017","汉兰达-2018~2021","汉兰达-2022~2023","YARiS-L-致炫-2016~2022","卡罗拉-2014~2017","威飒-2022~2023",
                               "3系-M-2013~2019","3系-GT-M-2017~2020","3系-GT-2017~2019","5系-2018~2020","5系-M-2018~2020","5系-豪华套装-2024","5系-M-2024","X1-2016~2019","X1-2020~2022","X1-X-2023","X1-M-2023","X3-M-2022~2023","X3-2018~2021","X5-M-2019~2022","X5-X-2019~2021","X5-M-2023","X5-2015~2018","X5-M-2017~2018",
                               "C260L-2022~2024","C260L-2019~2021","C180L/C200L/C260L/C300L-运动版-2019~2021","C260-2019~2020","E级-2021~2023","E级-运动型-2021~2023","E级-2016~2020","E级-运动型-2016~2020","E级-运动型-2024","E级-2024","GLC260L-动感型-2020~2022","GLC260L-豪华型/GLC300L-2020~2022","GLC260L-豪华型/GLC300L-2023~2024",
                               "亚洲龙-2019~2021","卡罗拉-1.2T-2017改~2018","雷凌-2014~2017","凯美瑞-2015~2016","迈腾-2012~2016","朗逸-2015~2017","元-UP","秦-L","海豹06-DM-i","小鹏-G6","ET5T","GL8-ES-艾维亚-2017~2018",
                               "楼兰-2015~2022","奇骏-2014~2016","奇骏-2017~2022/经典2.0L-2023","骐达-2016~2020","天籁-2019~2021","逍客-2016~2017","蓝鸟-2016~2021","小米-su7",
                               "捷途-旅行者-2023","福特-烈马","猛龙","比亚迪-豹5","坦克500","坦克400-Hi4-T","极氪-001","极氪-007","捷途-X70-诸葛-2021~2023","捷途-X70-1.5T-2023~2024","捷途-X70-1.5T-2020~2022",
                               "征程","荣光-2017~2023","荣光小卡","五菱之光-2013~2023","睿行-EM60-M60","睿行-EM80-2022~2024","睿行-M80","跨越星V5","跨越王X5","荣光新卡","五十铃-100P","五十铃-KV100-700P","五十铃-FVZ-FVR","五十铃-巨咖","远程-星享V","菱势-黄金仓","东风-小康-EC36",
                               "威霆-2016~2023","G级-2019~2024","G级-2016~2018","V级-2020~2022","V级-L豪华版-2020~2022","传祺-GS4-2018~2019","传祺-GS4-2020~2023","传祺-GS3-2023~2024","传祺-GS3-2021~2022","汉-EV","海豹-2025",
                               "传祺-GS4-2015~2017","传祺-GS8-领航系列-2022~2025","传祺-GS8-双擎系列-2022~2024","ES8-2018~2022","ES8-2023~2024","EC6-2020~2022","ET7","欧拉-好猫","海狮07-EV","海狮05-DM-i",
                               "S90-2021~2025","XC40-2023~2025","S90-2016~2020","XC60-运动版-2022~2025","XC60-2018~2021","XC60-运动版-2018~2021",
                               "H6-国潮版-2021~2023","M6-2017~2018","M6-2019","H6-Supreme+-2021~2022/DHT-PHEV-2023","依维柯-得意","依维柯-欧胜","MG4-EV","MG-ONE","MG-ZS","江铃-福顺","江淮-星锐","福田-图雅诺","江淮-瑞风M3",
                               "长城-炮/金刚炮/山海炮","长城-风骏5","江铃-大道","江铃-域虎7","江铃-宝典","游骑侠","F-150猛禽-2022~2023","F-150猛禽-2017~2019","坦途","纳瓦拉","Cybertruck",
                               "Cayenne-3.0T-2018~2023","Cayenne-4.0T-2018~2023","Cayenne-GTS-2020~2021","Cayenne-3.0T-2024~2025","Cayenne-2015","Macan-2018~2021","Macan-Turbo-2014~2017","Macan-Turbo-2020","Macan-GTS-2020","Macan-GTS-2016~2017",
                               "UNI-Z-2024","CS55PLUS-2022~2023","CS55PLUS-蓝鲸版-2021~2022","锐程PLUS-2023~2024","CS35PLUS-1.4T-2021~2024","CS35PLUS-1.6L-2018~2022/1.4T-2019~2020","UNI-K-2021~2024","逸达-2023",
                               "瑞虎7-2020~2023","瑞虎7-2016~2019","瑞虎9-2023~2024","风云-T9","艾瑞泽5-2016~2023","探索06-2023~2024","舒享家-2023~2025","风云A8-风版-2024","风云A8-远航版-2024",
                               "帝豪-2019~2020","星瑞-2023~2025","星瑞-2021","博越L-2023~2024","博越-X-2022","博越-2023~2024","博越-2021","博越-2020","博越-2018","缤越-COOL-2022~2023","缤越-2023~2024","缤越-2021","豪越L-2023~2024",
                               "威朗-2020","威朗-2018~2019","威朗-2015~2017","威朗-两厢-2018~2019","AION-S-炫","君威-GS-2020~2023","君威-2017~2019","君威-GS-2017~2019","君威-2014~2015","君威-GS-2014~2015","昂科威S-2020~2023","昂科威Plus-2021~2023","昂科威-2020~2021","昂科威-2018~2019","昂科威-2014~2017","君越-2023~2024","君越-2019~2022","君越-2016~2018","君越-2013~2014","微蓝6-2019~2024","微蓝6-插电混动-2020~2022",
                               "蒙迪欧-国V-国VI-2018~2020","蒙迪欧-2017~2018","蒙迪欧-2013","锐界-2021~2022","锐界-2020","锐界-2015~2018","领睿-2022~2023","探险者-2023~2024","福克斯-2022","福克斯-ST-Line-2019-2020~2021","福克斯-2019","福克斯-两厢-2015~2018","福克斯-2015~2018",
                               "保时捷718","保时捷911","阿斯顿-马丁-V8-Vantage","阿斯顿-马丁-Vanquish","宾利-欧陆","法拉利458","法拉利599","劳斯莱斯-古思特","劳斯莱斯-幻影","劳斯莱斯-库里南","玛莎拉蒂-Ghibli","玛莎拉蒂-总裁","玛莎拉蒂-GranTurismo","仰望U9",
                               "A6L-动感型-2019~2022","C180/C200/C260/C300-运动版-2015~2018","C180/C200/C260/C300-2015~2018","A6L-2016~2018","A6L-致雅型-2023~2024","A4L-运动型-2017~2018/时尚型-2018/进取型-2019","A4L-运动型-时尚型-2019","A4L-风尚型-时尚型-进取型-2017/进取型-2018","A4L-2013~2016",
                               "揽胜极光-2021~2024","揽胜极光-2020","揽胜极光-2016~2018","揽胜-2013~2016","揽胜极光-2012~2015","揽胜运动版-2014~2017","揽胜运动版-2018~2022",
                               "理想-ONE","海豹07-DM-i","D1","秦Pro-2018~2020","秦-2019","普拉多-2010~2019","皇冠-2015~2018","皇冠-2012","途观L-R-Line-2017~2021","途昂-2017~2020","途昂-2021~2024",
                               "帕萨特-2021-PHEV-2019~2020","速腾-2015~2018","宝来-2016~2018","帕萨特-2011~2015","高尔夫-2018~2020","高尔夫-2021~2023","甲壳虫-2012~2014","甲壳虫-2015~2019","ID.4-CROZZ","CR-V-2015~2016","CR-V-2017~2019","CR-V-2012~2013",
                               "英仕派-2023","英仕派-2022","英仕派-2019","奥德赛-2019~2021","奥德赛-2018","奥德赛-2015~2017","奥德赛-2022~2024","皓影-2023~2024","雅阁-2016","雅阁-2014~2015","思域-2021","思域-TURBO-2016~2017","思域-2019","艾力绅-2016","传祺-GS8-2017~2019"
                        ]
vehicle_characters_en = ["gold","brown","green","yellow","silver","gray","light blue","black","white","blue","red","pink","orange","purple","sedan","SUV","MPV","van","trcuk","pickup","bus","supercar","BYD","NIO","Tesla","Volkswagen","Honda","Toyota","Audi","Nissan","BMW","GAC","Mercedes-Benz","Changan","Buick","Geely","Lynk & Co","Haval","Ford","Volvo","Chery","Wuling","Peugeot","Chevrolet","Mazda","Porsche","Land Rover","Lexus","Cadillac","MG","Hyundai",
                        "Model-3/Y","Model-S","Qin-Plus-EV","Qin-Plus-DM-i","Dolphin","Denza-D9","Song-Plus-DM-i-2021",
                               "Sagitar-2023","Magotan-2020","Lavida-2023","Tiguan","Passat-2019-2020","Sylphy-Classic-2012/2009/2014/2016-2019","CR-V-2021","Accord-2018","RAV4-Rongfang-2020-2023","Ora-Lightning-Cat","Camry-2018-2019","A6L-Zhiya-2019-2022","A4L-Sporty-2020-2024","Q5-2013-2018","Tank-300","3-Series-2020-2022","GL8-2017-2018","X-Trail-2021-2022",
                               "Han-DM-i","Q8","5-Series-2014-2017","Mini","Li-L6/L7/L8/L9","C200L/C260L-Sport-Edition-2022-2024","GLB-2020-2023","AION-S魅","Passat-2022-2024","Sagitar-2019-2022","AION-Y","Camry-Fengshang-2018-2019","CR-V-2023","Accord-2022","Magotan-2017-2019","Lavida-Starry-Sky-2023","A6L-Dynamic-2023-2024","A4L-Elegance-2020-2024",
                               "CS75-Plus-II-2022-2023","Eado-Blue-Whale-NE-2022-2023","Regal-2020-2022","Verano-2022-2023","Fit","A3-Sportback","M6-2021-2023","H6-3rd-Gen-1.5T/2.0T-2021-2024","Xingyue-L","Emgrand-2022-2024","Seagull","AION-S-MAX","Renegade","Wrangler","Geometry-E-Firefly","Geometry-M6","ICON","March","Focus","Mondeo-2022-2025","Edge-2023-2025",
                               "Taycan","Macan-2022-2024","AITO-M5","MEGA","AITO-M7","S60-2020-2025","C40","Yuan-Plus","Civic-2022-2023","Tiguan-L-2022-2024","XC60-2022-2025","Arrizo-8","Tiggo-8-2019-2024","Hongguang","Binguo","Frontlander-2023","Hongqi-H5","Hongqi-HS5",
                               "408-2019-2020","Cruze-2023-2024","Axela-2020-2023","Corolla-2019-2023","Song-Pro-DM-i-2023-2024","ES-2023","CT5-2023-2024","XPeng-P7","ES6","Big-Dog-2024","Corolla-Cross-2022-2023","Q5L-Sporty-2021-2024","Jetta-VS7-2020-2021","Sylphy-XE-XL-2020-2022","Sylphy-Classic-XE-XV-XL-2021-2024","Sylphy-e-POWER-2023","Sylphy-CVT-2023",
                               "3-Series-2023-2024,","5-Series-Luxury-2021-2023","5-Series-Sport-2021-2023","Lavida-2018-2022","Song-Plus-EV-2023-2024","Song-Plus-DM-i-2023-2024","Lynk-&-Co-03-2023","Lynk-&-Co-03-2020-2022","Lynk-&-Co-06-2020-2023","Lynk-&-Co-06-EM-P-2023","CS75-Plus-Classic-2022","CS75-Plus-2020-2021","Eado-2020-2022",
                               "Lynk-&-Co-08-EM-P-2023","Tiguan-L-2017-2021","Passat-2016-2017","ID.3-2021-2023","Bora-2019-2021","MG5-2021-2023","MG7-2023","Atenza-2020-2021","Atenza-2017-2018","CX-30-2020-2022","CX-5-2022-2024","Menlo-2021-2022","Malibu-XL-2019-2023","Equinox-2021-2023",
                               "Trax-2019-2023","508-2019-2022","4008-2021-2022","5008-2021","GL8-Land-Business-2023","GL8-Land-Business-2020-2022","GL8-ES-2020-2022","GL8-Avenir-2020-2022","GL8-ES-Avenir-2023","Sienna-2021-2023","Foton-Aoling-M-Card","Foton-Xiangling-M2","Yuejin-Fuxing-S80","Elantra-2023","Elantra-2022","ix35-2021","ix35-2023",
                               "Baojun-510-2017","Trumpchi-M8-Master-2023-2024","Trumpchi-M8-Grandmaster-2020-2023","Trumpchi-M8-Leader-2021-2023","T-Roc-2018-2022","T-Roc-2023-2024","Tayron-Plus-2023-2024","Tayron-R-Line-2019-2022","Integra-2022-2023","Breeze-2020-2021","UNI-V-2022-2024","Destroyer-05-2022-2024","Tang-DM-i-2021-2024","Tang-EV-2022-2024","Tang-DM-p-2022-2024",
                               "AITO-M9","Tayron-R-Line-2023-2024","Tayron-2WD-2019-2022","Touran-2011-2015","CC-2013-2018","Avalon-2022-2023","Levin-2019-2022","Camry-2021-2023","Frontlander-2022","Wildlander-2022-2023","RAV4-Rongfang-2016-2019","Highlander-2012-2013","Highlander-2015-2017","Highlander-2018-2021","Highlander-2022-2023","YARiS-L-Zhi-Xuan-2016-2022","Corolla-2014-2017","Venza-2022-2023",
                               "3-Series-M-2013-2019","3-Series-GT-M-2017-2020","3-Series-GT-2017-2019","5-Series-2018-2020","5-Series-M-2018-2020","5-Series-Luxury-2024","5-Series-M-2024","X1-2016-2019","X1-2020-2022","X1-X-2023","X1-M-2023","X3-M-2022-2023","X3-2018-2021","X5-M-2019-2022","X5-X-2019-2021","X5-M-2023","X5-2015-2018","X5-M-2017-2018",
                               "C260L-2022-2024","C260L-2019-2021","C180L/C200L/C260L/C300L-Sport-Edition-2019-2021","C260-2019-2020","E-Class-2021-2023","E-Class-Sport-2021-2023","E-Class-2016-2020","E-Class-Sport-2016-2020","E-Class-Sport-2024","E-Class-2024",
                               "GLC260L-Dynamic-2020-2022","GLC260L-Luxury/GLC300L-2020-2022","GLC260L-Luxury/GLC300L-2023-2024","Avalon-2019-2021","Corolla-1.2T-2017-Facelift-2018","Levin-2014-2017","Camry-2015-2016","Magotan-2012-2016","Lavida-2015-2017","Yuan-UP","Qin-L","Seal-06-DM-i","XPeng-G6","NIO-ET5T","GL8-ES-Avenir-2017-2018",
                               "Murano-2015-2022","X-Trail-2014-2016","X-Trail-2017-2022/Classic-2.0L-2023","Tiida-2016-2020","Altima-2019-2021","Qashqai-2016-2017","Bluebird-Sylphy-2016-2021","Xiaomi-SU7","Jetour-Traveller-2023","Ford-Bronco","Menglong","BYD-Leopard-5","Tank-500","Tank-400-Hi4-T","Zeekr-001","Zeekr-007","Jetour-X70-Zhuge-2021-2023","Jetour-X70-1.5T-2023-2024","Jetour-X70-1.5T-2020-2022",
                               "Journey","Rongguang-2017-2023","Rongguang-Mini-Truck","Wuling-Zhiguang-2013-2023","Ruixing-EM60-M60","Ruixing-EM80-2022-2024","Ruixing-M80","Kuayue-Star-V5","Kuayue-King-X5","Rongguang-New-Truck","Isuzu-100P","Isuzu-KV100/700P","Isuzu-FVZ/FVR","Isuzu-Gigamax","Farizon-Star-Enjoy-V","Lingsei-Gold-Bin","DFSK-EC36","Vito-2016-2023","G-Class-2019-2024","G-Class-2016-2018","V-Class-2020-2022","V-Class-L-Luxury-2020-2022",
                               "Trumpchi-GS4-2018-2019","Trumpchi-GS4-2020-2023","Trumpchi-GS3-2023-2024","Trumpchi-GS3-2021-2022","Han-EV","Seal-2025","Trumpchi-GS4-2015-2017","Trumpchi-GS8-Pilot-Series-2022-2025","Trumpchi-GS8-Dual-Engine-2022-2024","NIO-ES8-2018-2022","NIO-ES8-2023-2024","NIO-EC6-2020-2022","NIO-ET7","Ora-Good-Cat","SeaLion-07-EV","SeaLion-05-DM-i",
                               "Volvo-S90-2021-2025","Volvo-XC40-2023-2025","Volvo-S90-2016-2020","Volvo-XC60-Sport-2022-2025","Volvo-XC60-2018-2021","Volvo-XC60-Sport-2018-2021","H6-National-Edition-2021-2023","M6-2017-2018","M6-2019","H6-Supreme+/DHT-PHEV-2023","Iveco-Deli","Iveco-Ousheng","MG4-EV","MG-ONE","MG-ZS","JMC-Fushun","JAC-Xrui","Foton-Tunland","JAC-Refine-M3","Great-Wall-Pao-King-Kong/Shanhai-Pao","Great-Wall-Fengjun-5",
                               "JMC-Da-Dao","JMC-Yuhu-7","JMC-Baodian","Ranger-Raptor","F-150-Raptor-2022-2023","F-150-Raptor-2017-2019","Tundra","Navara","Cybertruck","Cayenne-3.0T-2018-2023","Cayenne-4.0T-2018-2023","Cayenne-GTS-2020-2021","Cayenne-3.0T-2024-2025","Cayenne-2015","Macan-2018-2021","Macan-Turbo-2014-2017","Macan-Turbo-2020","Macan-GTS-2020","Macan-GTS-2016-2017",
                               "UNI-Z-2024","CS55PLUS-2022-2023","CS55PLUS-Blue-Whale-2021-2022","Ruicheng-PLUS-2023-2024","CS35PLUS-1.4T-2021-2024","CS35PLUS-1.6L-2018-2022/1.4T-2019-2020","UNI-K-2021-2024","Yida-2023","Tiggo7-2020-2023","Tiggo7-2016-2019","Tiggo9-2023-2024","Fengyun-T9","Arrizo5-2016-2023","Explore-06-2023-2024","Comfort-Home-2023-2025","Fengyun-A8-Wind-2024","Fengyun-A8-Long-Range-2024","Emgrand-2019-2020",
                               "Xingyue-2023-2025","Xingyue-2021","Binyue-L-2023-2024","Binyue-X-2022","Binyue-2023-2024","Binyue-2021","Binyue-2020","Binyue-2018","Binyue-COOL-2022-2023","Binyue-2023-2024","Binyue-2021","Haoyue-L-2023-2024","Verano-2020","Verano-2018-2019","Verano-2015-2017","Verano-Hatchback-2018-2019","AION-S-Xuan",
                               "Regal-GS-2020-2023","Regal-2017-2019","Regal-GS-2017-2019","Regal-2014-2015","Regal-GS-2014-2015","Envision-S-2020-2023","Envision-Plus-2021-2023","Envision-2020-2021","Envision-2018-2019","Envision-2014-2017","LaCrosse-2023-2024","LaCrosse-2019-2022","LaCrosse-2016-2018","LaCrosse-2013-2014","Velite-6-2019-2024","Velite-6-PHEV-2020-2022",
                               "Mondeo-China-V/China-VI-2018-2020","Mondeo-2017-2018","Mondeo-2013","Edge-2021-2022","Edge-2020","Edge-2015-2018","Territory-2022-2023","Explorer-2023-2024",
                               "Focus-2022","Focus-ST-Line-2019/2020-2021","Focus-2019","Focus-Hatchback-2015-2018","Focus-2015-2018","Porsche-718","Porsche-911","Aston-Martin-V8-Vantage","Aston-Martin-Vanquish","Bentley-Continental","Ferrari-458","Ferrari-599","Rolls-Royce-Ghost","Rolls-Royce-Phantom","Rolls-Royce-Cullinan",
                               "Maserati-Ghibli","Maserati-Quattroporte","Maserati-GranTurismo","Yangwang-U9","A6L-Dynamic-2019-2022","C180/C200/C260/C300-Sport-2015-2018","C180/C200/C260/C300-2015-2018","A6L-2016-2018","A6L-Zhiya-2023-2024","A4L-Sport-2017-2018/Fashion-2018/Base-2019","A4L-Sport/Fashion-2019","A4L-Premium/Fashion/Base-2017/Base-2018","A4L-2013-2016",
                               "Range-Rover-Evoque-2021-2024","Range-Rover-Evoque-2020","Range-Rover-Evoque-2016-2018","Range-Rover-2013-2016","Range-Rover-Evoque-2012-2015","Range-Rover-Sport-2014-2017","Range-Rover-Sport-2018-2022","Li-ONE","Seal-07-DM-i","D1","Qin-Pro-2018-2020","Qin-2019","Prado-2010-2019","Crown-2015-2018","Crown-2012",
                               "Tiguan-L-R-Line-2017-2021","Teramont-2017-2020","Teramont-2021-2024","Passat-2021-PHEV-2019-2020","Sagitar-2015-2018","Bora-2016-2018","Passat-2011-2015","Golf-2018-2020","Golf-2021-2023","Beetle-2012-2014","Beetle-2015-2019","ID.4-CROZZ","CR-V-2015-2016","CR-V-2017-2019","CR-V-2012-2013",
                               "Inspire-2023","Inspire-2022","Inspire-2019","Odyssey-2019-2021","Odyssey-2018","Odyssey-2015-2017","Odyssey-2022-2024","Breeze-2023-2024","Accord-2016","Accord-2014-2015","Civic-2021","Civic-Turbo-2016-2017","Civic-2019","Elysion-2016","Trumpchi-GS8-2017-2019"
                        ]

vehicle_color_characters_zh = {"金色","棕色","绿色","黄色","银色","灰色","浅蓝色","黑色","白色","蓝色","红色","粉色","橙色","紫色"}
vehicle_color_characters_en = {"gold","brown","green","yellow","silver","gray","light blue","black","white","blue","red","pink","orange","purple"}
vehicle_category_characters_zh = {"轿车","SUV","MPV","面包车","卡车","皮卡","巴士","超跑"}
vehicle_category_characters_en = {"sedan","SUV","MPV","van","trcuk","pickup","bus","supercar"}
vehicle_brand_characters_zh = {"比亚迪","蔚来","特斯拉","大众","本田","丰田","奥迪","日产","宝马","广汽","奔驰","长安","别克","吉利","领克","哈弗","福特","沃尔沃","奇瑞","五菱","标致","雪佛兰","马自达","保时捷","路虎","雷克萨斯","凯迪拉克","名爵","现代"}
vehicle_brand_characters_en = {"BYD","NIO","Tesla","Volkswagen","Honda","Toyota","Audi","Nissan","BMW","GAC","Mercedes-Benz","Changan","Buick","Geely","Lynk & Co","Haval","Ford","Volvo","Chery","Wuling","Peugeot","Chevrolet","Mazda","Porsche","Land Rover","Lexus","Cadillac","MG","Hyundai"}
vehicle_model_characters_zh = {"Model-3/Y","Model-S","秦Plus-EV","秦Plus-DM-i","海豚","腾势D9","宋Plus-DM-i-2021","速腾-2023","迈腾-2020","朗逸-2023","途观","帕萨特-2019~2020","轩逸-经典-2009/2012/2014/2016~2019","CRV-2021","雅阁-2018","RAV4荣放-2020~2023","欧拉-闪电猫","凯美瑞-2018~2019",
                               "A6L-致雅型-2019~2022","A4L-动感版-2020~2024","Q5-2013~2018","坦克300","3系-2020~2022","GL8-2017~2018","逍客-2021~2022","汉-DM-i","Q8","5系-2014~2017","Mini","理想-L6/L7/L8/l9","C200L/C260L-运动版-2022~2024","GLB-2020~2023","AION-S-魅","帕萨特-2022~2024","速腾-2019~2022","AION-Y","凯美瑞-锋尚版-2018~2019","CRV-2023","雅阁-2022",
                               "迈腾-2017~2019","朗逸-星空版-2023","A6L-动感型-2023~2024","A4L-致雅型-2020~2024","CS75-Plus-第二代-2022~2023","逸动-蓝鲸NE-2022~2023","君威-2020~2022","威朗-2022~2023","飞度","A3-Sportback","M6-2021~2023","H6-第三代-1.5T-2.0T-2021~2024","星越L","帝豪-2022~2024","海鸥","AION-S-MAX",
                               "自由侠","牧马人","几何-E萤火虫","几何-M6","ICON","玛驰","福克斯","蒙迪欧-2022~2025","锐界-2023~2025","Taycan","Macan-2022~2024",
                               "问界-M5","MEGA","问界-M7","S60-2020~2025","C40","元-Plus","思域-2022~2023","途观L-2022~2024","XC60-2022~2025",
                               "艾瑞泽8","瑞虎8-2019~2024","宏光","缤果","锋兰达-2023","红旗-H5","红旗-HS5","408-2019~2020","科鲁兹-2023~2024","昂克赛拉-2020~2023","卡罗拉-2019~2023","宋Pro-DM-i-2023~2024","ES-2023","CT5-2023~2024","P7","ES6","大狗-2024",
                               "卡罗拉锐放-2022~2023","Q5L-动感版-2021~2024","捷达-VS7-2020~2021","轩逸-XE~XL-2020~2022","轩逸-经典-XE~XV~XL-2021~2024/XE~XV~XL-2016~2019","轩逸-超混电驱-2023","轩逸-CVT-2023","3系-2023~2024","5系-豪华套装-2021~2023","5系-运动套装-2021~2023","朗逸-2018~2022","宋Plus-EV-2023~2024","宋Plus-DM-i-2023~2024",
                               "领克-03-2023","领克-03-2020~2022","领克-06-2020~2023","领克-06-EM-P-2023","CS75-Plus-经典款-2022","CS75-Plus-2020~2021","逸动-2020~2022","领克-08-EM-P-2023","途观L-2017~2021","帕萨特-2016~2017","ID3-2021~2023","宝来-2019~2021","MG5-2021~2023","MG7-2023","阿特兹-2020~2021","阿特兹-2017~2018",
                               "CX-30-2020~2022","CX-5-2022~2024","畅巡-2021~2022","迈锐宝XL-2019~2023","探界者-2021~2023","创酷-2019~2023","508-2019~2022","4008-2021~2022","5008-2021","GL8-陆上公务舱-2023","GL8-陆上公务舱-2020~2022","GL8-ES陆尊-2020~2022","GL8-艾维亚-2020~2022","GL8-ES陆尊-艾维亚-2023","赛那-2021~2023",
                               "福田-奥铃M卡","福田-祥菱M2","跃进-福星S80","伊兰特-2023","伊兰特-2022","ix35-2021","ix35-2023","宝骏510-2017","传祺M8-宗师-2023~2024","传祺M8-大师-2020~2023","传祺M8-领秀-2021~2023",
                               "探歌-2018~2022","探歌-2023~2024","探岳-Plus-2023~2024","探岳-R-Line-2019~2022","型格-2022~2023","皓影-2020~2021","UNI-V-2022~2024","驱逐舰05-2022~2024","唐-DM-i-2021~2024","唐-EV-2022~2024","唐-DM-p-2022~2024",
                               "问界-M9","探岳-R-Line-2023~2024","探岳-两驱-2019~2022","途安-2011~2015","CC-2013~2018",
                               "亚洲龙-2022~2023","雷凌-2019~2022","凯美瑞-2021~2023","锋兰达-2022","威兰达-2022~2023","RAV4荣放-2016~2019","汉兰达-2012~2013","汉兰达-2015~2017","汉兰达-2018~2021","汉兰达-2022~2023","YARiS-L-致炫-2016~2022","卡罗拉-2014~2017","威飒-2022~2023",
                               "3系-M-2013~2019","3系-GT-M-2017~2020","3系-GT-2017~2019","5系-2018~2020","5系-M-2018~2020","5系-豪华套装-2024","5系-M-2024","X1-2016~2019","X1-2020~2022","X1-X-2023","X1-M-2023","X3-M-2022~2023","X3-2018~2021","X5-M-2019~2022","X5-X-2019~2021","X5-M-2023","X5-2015~2018","X5-M-2017~2018",
                               "C260L-2022~2024","C260L-2019~2021","C180L/C200L/C260L/C300L-运动版-2019~2021","C260-2019~2020","E级-2021~2023","E级-运动型-2021~2023","E级-2016~2020","E级-运动型-2016~2020","E级-运动型-2024","E级-2024","GLC260L-动感型-2020~2022","GLC260L-豪华型/GLC300L-2020~2022","GLC260L-豪华型/GLC300L-2023~2024",
                               "亚洲龙-2019~2021","卡罗拉-1.2T-2017改~2018","雷凌-2014~2017","凯美瑞-2015~2016","迈腾-2012~2016","朗逸-2015~2017","元-UP","秦-L","海豹06-DM-i","小鹏-G6","ET5T","GL8-ES-艾维亚-2017~2018",
                               "楼兰-2015~2022","奇骏-2014~2016","奇骏-2017~2022/经典2.0L-2023","骐达-2016~2020","天籁-2019~2021","逍客-2016~2017","蓝鸟-2016~2021","小米-su7",
                               "捷途-旅行者-2023","福特-烈马","猛龙","比亚迪-豹5","坦克500","坦克400-Hi4-T","极氪-001","极氪-007","捷途-X70-诸葛-2021~2023","捷途-X70-1.5T-2023~2024","捷途-X70-1.5T-2020~2022",
                               "征程","荣光-2017~2023","荣光小卡","五菱之光-2013~2023","睿行-EM60-M60","睿行-EM80-2022~2024","睿行-M80","跨越星V5","跨越王X5","荣光新卡","五十铃-100P","五十铃-KV100-700P","五十铃-FVZ-FVR","五十铃-巨咖","远程-星享V","菱势-黄金仓","东风-小康-EC36",
                               "威霆-2016~2023","G级-2019~2024","G级-2016~2018","V级-2020~2022","V级-L豪华版-2020~2022","传祺-GS4-2018~2019","传祺-GS4-2020~2023","传祺-GS3-2023~2024","传祺-GS3-2021~2022","汉-EV","海豹-2025",
                               "传祺-GS4-2015~2017","传祺-GS8-领航系列-2022~2025","传祺-GS8-双擎系列-2022~2024","ES8-2018~2022","ES8-2023~2024","EC6-2020~2022","ET7","欧拉-好猫","海狮07-EV","海狮05-DM-i",
                               "S90-2021~2025","XC40-2023~2025","S90-2016~2020","XC60-运动版-2022~2025","XC60-2018~2021","XC60-运动版-2018~2021",
                               "H6-国潮版-2021~2023","M6-2017~2018","M6-2019","H6-Supreme+-2021~2022/DHT-PHEV-2023","依维柯-得意","依维柯-欧胜","MG4-EV","MG-ONE","MG-ZS","江铃-福顺","江淮-星锐","福田-图雅诺","江淮-瑞风M3",
                               "长城-炮/金刚炮/山海炮","长城-风骏5","江铃-大道","江铃-域虎7","江铃-宝典","游骑侠","F-150猛禽-2022~2023","F-150猛禽-2017~2019","坦途","纳瓦拉","Cybertruck",
                               "Cayenne-3.0T-2018~2023","Cayenne-4.0T-2018~2023","Cayenne-GTS-2020~2021","Cayenne-3.0T-2024~2025","Cayenne-2015","Macan-2018~2021","Macan-Turbo-2014~2017","Macan-Turbo-2020","Macan-GTS-2020","Macan-GTS-2016~2017",
                               "UNI-Z-2024","CS55PLUS-2022~2023","CS55PLUS-蓝鲸版-2021~2022","锐程PLUS-2023~2024","CS35PLUS-1.4T-2021~2024","CS35PLUS-1.6L-2018~2022/1.4T-2019~2020","UNI-K-2021~2024","逸达-2023",
                               "瑞虎7-2020~2023","瑞虎7-2016~2019","瑞虎9-2023~2024","风云-T9","艾瑞泽5-2016~2023","探索06-2023~2024","舒享家-2023~2025","风云A8-风版-2024","风云A8-远航版-2024",
                               "帝豪-2019~2020","星瑞-2023~2025","星瑞-2021","博越L-2023~2024","博越-X-2022","博越-2023~2024","博越-2021","博越-2020","博越-2018","缤越-COOL-2022~2023","缤越-2023~2024","缤越-2021","豪越L-2023~2024",
                               "威朗-2020","威朗-2018~2019","威朗-2015~2017","威朗-两厢-2018~2019","AION-S-炫","君威-GS-2020~2023","君威-2017~2019","君威-GS-2017~2019","君威-2014~2015","君威-GS-2014~2015","昂科威S-2020~2023","昂科威Plus-2021~2023","昂科威-2020~2021","昂科威-2018~2019","昂科威-2014~2017","君越-2023~2024","君越-2019~2022","君越-2016~2018","君越-2013~2014","微蓝6-2019~2024","微蓝6-插电混动-2020~2022",
                               "蒙迪欧-国V-国VI-2018~2020","蒙迪欧-2017~2018","蒙迪欧-2013","锐界-2021~2022","锐界-2020","锐界-2015~2018","领睿-2022~2023","探险者-2023~2024","福克斯-2022","福克斯-ST-Line-2019-2020~2021","福克斯-2019","福克斯-两厢-2015~2018","福克斯-2015~2018",
                               "保时捷718","保时捷911","阿斯顿-马丁-V8-Vantage","阿斯顿-马丁-Vanquish","宾利-欧陆","法拉利458","法拉利599","劳斯莱斯-古思特","劳斯莱斯-幻影","劳斯莱斯-库里南","玛莎拉蒂-Ghibli","玛莎拉蒂-总裁","玛莎拉蒂-GranTurismo","仰望U9",
                               "A6L-动感型-2019~2022","C180/C200/C260/C300-运动版-2015~2018","C180/C200/C260/C300-2015~2018","A6L-2016~2018","A6L-致雅型-2023~2024","A4L-运动型-2017~2018/时尚型-2018/进取型-2019","A4L-运动型-时尚型-2019","A4L-风尚型-时尚型-进取型-2017/进取型-2018","A4L-2013~2016",
                               "揽胜极光-2021~2024","揽胜极光-2020","揽胜极光-2016~2018","揽胜-2013~2016","揽胜极光-2012~2015","揽胜运动版-2014~2017","揽胜运动版-2018~2022",
                               "理想-ONE","海豹07-DM-i","D1","秦Pro-2018~2020","秦-2019","普拉多-2010~2019","皇冠-2015~2018","皇冠-2012","途观L-R-Line-2017~2021","途昂-2017~2020","途昂-2021~2024",
                               "帕萨特-2021-PHEV-2019~2020","速腾-2015~2018","宝来-2016~2018","帕萨特-2011~2015","高尔夫-2018~2020","高尔夫-2021~2023","甲壳虫-2012~2014","甲壳虫-2015~2019","ID.4-CROZZ","CR-V-2015~2016","CR-V-2017~2019","CR-V-2012~2013",
                               "英仕派-2023","英仕派-2022","英仕派-2019","奥德赛-2019~2021","奥德赛-2018","奥德赛-2015~2017","奥德赛-2022~2024","皓影-2023~2024","雅阁-2016","雅阁-2014~2015","思域-2021","思域-TURBO-2016~2017","思域-2019","艾力绅-2016","传祺-GS8-2017~2019"}
vehicle_model_characters_en = {"Model-3/Y","Model-S","Qin-Plus-EV","Qin-Plus-DM-i","Dolphin","Denza-D9","Song-Plus-DM-i-2021",
                               "Sagitar-2023","Magotan-2020","Lavida-2023","Tiguan","Passat-2019-2020","Sylphy-Classic-2012/2009/2014/2016-2019","CR-V-2021","Accord-2018","RAV4-Rongfang-2020-2023","Ora-Lightning-Cat","Camry-2018-2019","A6L-Zhiya-2019-2022","A4L-Sporty-2020-2024","Q5-2013-2018","Tank-300","3-Series-2020-2022","GL8-2017-2018","X-Trail-2021-2022",
                               "Han-DM-i","Q8","5-Series-2014-2017","Mini","Li-L6/L7/L8/L9","C200L/C260L-Sport-Edition-2022-2024","GLB-2020-2023","AION-S魅","Passat-2022-2024","Sagitar-2019-2022","AION-Y","Camry-Fengshang-2018-2019","CR-V-2023","Accord-2022","Magotan-2017-2019","Lavida-Starry-Sky-2023","A6L-Dynamic-2023-2024","A4L-Elegance-2020-2024",
                               "CS75-Plus-II-2022-2023","Eado-Blue-Whale-NE-2022-2023","Regal-2020-2022","Verano-2022-2023","Fit","A3-Sportback","M6-2021-2023","H6-3rd-Gen-1.5T/2.0T-2021-2024","Xingyue-L","Emgrand-2022-2024","Seagull","AION-S-MAX","Renegade","Wrangler","Geometry-E-Firefly","Geometry-M6","ICON","March","Focus","Mondeo-2022-2025","Edge-2023-2025",
                               "Taycan","Macan-2022-2024","AITO-M5","MEGA","AITO-M7","S60-2020-2025","C40","Yuan-Plus","Civic-2022-2023","Tiguan-L-2022-2024","XC60-2022-2025","Arrizo-8","Tiggo-8-2019-2024","Hongguang","Binguo","Frontlander-2023","Hongqi-H5","Hongqi-HS5",
                               "408-2019-2020","Cruze-2023-2024","Axela-2020-2023","Corolla-2019-2023","Song-Pro-DM-i-2023-2024","ES-2023","CT5-2023-2024","XPeng-P7","ES6","Big-Dog-2024","Corolla-Cross-2022-2023","Q5L-Sporty-2021-2024","Jetta-VS7-2020-2021","Sylphy-XE-XL-2020-2022","Sylphy-Classic-XE-XV-XL-2021-2024","Sylphy-e-POWER-2023","Sylphy-CVT-2023",
                               "3-Series-2023-2024,","5-Series-Luxury-2021-2023","5-Series-Sport-2021-2023","Lavida-2018-2022","Song-Plus-EV-2023-2024","Song-Plus-DM-i-2023-2024","Lynk-&-Co-03-2023","Lynk-&-Co-03-2020-2022","Lynk-&-Co-06-2020-2023","Lynk-&-Co-06-EM-P-2023","CS75-Plus-Classic-2022","CS75-Plus-2020-2021","Eado-2020-2022",
                               "Lynk-&-Co-08-EM-P-2023","Tiguan-L-2017-2021","Passat-2016-2017","ID.3-2021-2023","Bora-2019-2021","MG5-2021-2023","MG7-2023","Atenza-2020-2021","Atenza-2017-2018","CX-30-2020-2022","CX-5-2022-2024","Menlo-2021-2022","Malibu-XL-2019-2023","Equinox-2021-2023",
                               "Trax-2019-2023","508-2019-2022","4008-2021-2022","5008-2021","GL8-Land-Business-2023","GL8-Land-Business-2020-2022","GL8-ES-2020-2022","GL8-Avenir-2020-2022","GL8-ES-Avenir-2023","Sienna-2021-2023","Foton-Aoling-M-Card","Foton-Xiangling-M2","Yuejin-Fuxing-S80","Elantra-2023","Elantra-2022","ix35-2021","ix35-2023",
                               "Baojun-510-2017","Trumpchi-M8-Master-2023-2024","Trumpchi-M8-Grandmaster-2020-2023","Trumpchi-M8-Leader-2021-2023","T-Roc-2018-2022","T-Roc-2023-2024","Tayron-Plus-2023-2024","Tayron-R-Line-2019-2022","Integra-2022-2023","Breeze-2020-2021","UNI-V-2022-2024","Destroyer-05-2022-2024","Tang-DM-i-2021-2024","Tang-EV-2022-2024","Tang-DM-p-2022-2024",
                               "AITO-M9","Tayron-R-Line-2023-2024","Tayron-2WD-2019-2022","Touran-2011-2015","CC-2013-2018","Avalon-2022-2023","Levin-2019-2022","Camry-2021-2023","Frontlander-2022","Wildlander-2022-2023","RAV4-Rongfang-2016-2019","Highlander-2012-2013","Highlander-2015-2017","Highlander-2018-2021","Highlander-2022-2023","YARiS-L-Zhi-Xuan-2016-2022","Corolla-2014-2017","Venza-2022-2023",
                               "3-Series-M-2013-2019","3-Series-GT-M-2017-2020","3-Series-GT-2017-2019","5-Series-2018-2020","5-Series-M-2018-2020","5-Series-Luxury-2024","5-Series-M-2024","X1-2016-2019","X1-2020-2022","X1-X-2023","X1-M-2023","X3-M-2022-2023","X3-2018-2021","X5-M-2019-2022","X5-X-2019-2021","X5-M-2023","X5-2015-2018","X5-M-2017-2018",
                               "C260L-2022-2024","C260L-2019-2021","C180L/C200L/C260L/C300L-Sport-Edition-2019-2021","C260-2019-2020","E-Class-2021-2023","E-Class-Sport-2021-2023","E-Class-2016-2020","E-Class-Sport-2016-2020","E-Class-Sport-2024","E-Class-2024",
                               "GLC260L-Dynamic-2020-2022","GLC260L-Luxury/GLC300L-2020-2022","GLC260L-Luxury/GLC300L-2023-2024","Avalon-2019-2021","Corolla-1.2T-2017-Facelift-2018","Levin-2014-2017","Camry-2015-2016","Magotan-2012-2016","Lavida-2015-2017","Yuan-UP","Qin-L","Seal-06-DM-i","XPeng-G6","NIO-ET5T","GL8-ES-Avenir-2017-2018",
                               "Murano-2015-2022","X-Trail-2014-2016","X-Trail-2017-2022/Classic-2.0L-2023","Tiida-2016-2020","Altima-2019-2021","Qashqai-2016-2017","Bluebird-Sylphy-2016-2021","Xiaomi-SU7","Jetour-Traveller-2023","Ford-Bronco","Menglong","BYD-Leopard-5","Tank-500","Tank-400-Hi4-T","Zeekr-001","Zeekr-007","Jetour-X70-Zhuge-2021-2023","Jetour-X70-1.5T-2023-2024","Jetour-X70-1.5T-2020-2022",
                               "Journey","Rongguang-2017-2023","Rongguang-Mini-Truck","Wuling-Zhiguang-2013-2023","Ruixing-EM60-M60","Ruixing-EM80-2022-2024","Ruixing-M80","Kuayue-Star-V5","Kuayue-King-X5","Rongguang-New-Truck","Isuzu-100P","Isuzu-KV100/700P","Isuzu-FVZ/FVR","Isuzu-Gigamax","Farizon-Star-Enjoy-V","Lingsei-Gold-Bin","DFSK-EC36","Vito-2016-2023","G-Class-2019-2024","G-Class-2016-2018","V-Class-2020-2022","V-Class-L-Luxury-2020-2022",
                               "Trumpchi-GS4-2018-2019","Trumpchi-GS4-2020-2023","Trumpchi-GS3-2023-2024","Trumpchi-GS3-2021-2022","Han-EV","Seal-2025","Trumpchi-GS4-2015-2017","Trumpchi-GS8-Pilot-Series-2022-2025","Trumpchi-GS8-Dual-Engine-2022-2024","NIO-ES8-2018-2022","NIO-ES8-2023-2024","NIO-EC6-2020-2022","NIO-ET7","Ora-Good-Cat","SeaLion-07-EV","SeaLion-05-DM-i",
                               "Volvo-S90-2021-2025","Volvo-XC40-2023-2025","Volvo-S90-2016-2020","Volvo-XC60-Sport-2022-2025","Volvo-XC60-2018-2021","Volvo-XC60-Sport-2018-2021","H6-National-Edition-2021-2023","M6-2017-2018","M6-2019","H6-Supreme+/DHT-PHEV-2023","Iveco-Deli","Iveco-Ousheng","MG4-EV","MG-ONE","MG-ZS","JMC-Fushun","JAC-Xrui","Foton-Tunland","JAC-Refine-M3","Great-Wall-Pao-King-Kong/Shanhai-Pao","Great-Wall-Fengjun-5",
                               "JMC-Da-Dao","JMC-Yuhu-7","JMC-Baodian","Ranger-Raptor","F-150-Raptor-2022-2023","F-150-Raptor-2017-2019","Tundra","Navara","Cybertruck","Cayenne-3.0T-2018-2023","Cayenne-4.0T-2018-2023","Cayenne-GTS-2020-2021","Cayenne-3.0T-2024-2025","Cayenne-2015","Macan-2018-2021","Macan-Turbo-2014-2017","Macan-Turbo-2020","Macan-GTS-2020","Macan-GTS-2016-2017",
                               "UNI-Z-2024","CS55PLUS-2022-2023","CS55PLUS-Blue-Whale-2021-2022","Ruicheng-PLUS-2023-2024","CS35PLUS-1.4T-2021-2024","CS35PLUS-1.6L-2018-2022/1.4T-2019-2020","UNI-K-2021-2024","Yida-2023","Tiggo7-2020-2023","Tiggo7-2016-2019","Tiggo9-2023-2024","Fengyun-T9","Arrizo5-2016-2023","Explore-06-2023-2024","Comfort-Home-2023-2025","Fengyun-A8-Wind-2024","Fengyun-A8-Long-Range-2024","Emgrand-2019-2020",
                               "Xingyue-2023-2025","Xingyue-2021","Binyue-L-2023-2024","Binyue-X-2022","Binyue-2023-2024","Binyue-2021","Binyue-2020","Binyue-2018","Binyue-COOL-2022-2023","Binyue-2023-2024","Binyue-2021","Haoyue-L-2023-2024","Verano-2020","Verano-2018-2019","Verano-2015-2017","Verano-Hatchback-2018-2019","AION-S-Xuan",
                               "Regal-GS-2020-2023","Regal-2017-2019","Regal-GS-2017-2019","Regal-2014-2015","Regal-GS-2014-2015","Envision-S-2020-2023","Envision-Plus-2021-2023","Envision-2020-2021","Envision-2018-2019","Envision-2014-2017","LaCrosse-2023-2024","LaCrosse-2019-2022","LaCrosse-2016-2018","LaCrosse-2013-2014","Velite-6-2019-2024","Velite-6-PHEV-2020-2022",
                               "Mondeo-China-V/China-VI-2018-2020","Mondeo-2017-2018","Mondeo-2013","Edge-2021-2022","Edge-2020","Edge-2015-2018","Territory-2022-2023","Explorer-2023-2024",
                               "Focus-2022","Focus-ST-Line-2019/2020-2021","Focus-2019","Focus-Hatchback-2015-2018","Focus-2015-2018","Porsche-718","Porsche-911","Aston-Martin-V8-Vantage","Aston-Martin-Vanquish","Bentley-Continental","Ferrari-458","Ferrari-599","Rolls-Royce-Ghost","Rolls-Royce-Phantom","Rolls-Royce-Cullinan",
                               "Maserati-Ghibli","Maserati-Quattroporte","Maserati-GranTurismo","Yangwang-U9","A6L-Dynamic-2019-2022","C180/C200/C260/C300-Sport-2015-2018","C180/C200/C260/C300-2015-2018","A6L-2016-2018","A6L-Zhiya-2023-2024","A4L-Sport-2017-2018/Fashion-2018/Base-2019","A4L-Sport/Fashion-2019","A4L-Premium/Fashion/Base-2017/Base-2018","A4L-2013-2016",
                               "Range-Rover-Evoque-2021-2024","Range-Rover-Evoque-2020","Range-Rover-Evoque-2016-2018","Range-Rover-2013-2016","Range-Rover-Evoque-2012-2015","Range-Rover-Sport-2014-2017","Range-Rover-Sport-2018-2022","Li-ONE","Seal-07-DM-i","D1","Qin-Pro-2018-2020","Qin-2019","Prado-2010-2019","Crown-2015-2018","Crown-2012",
                               "Tiguan-L-R-Line-2017-2021","Teramont-2017-2020","Teramont-2021-2024","Passat-2021-PHEV-2019-2020","Sagitar-2015-2018","Bora-2016-2018","Passat-2011-2015","Golf-2018-2020","Golf-2021-2023","Beetle-2012-2014","Beetle-2015-2019","ID.4-CROZZ","CR-V-2015-2016","CR-V-2017-2019","CR-V-2012-2013",
                               "Inspire-2023","Inspire-2022","Inspire-2019","Odyssey-2019-2021","Odyssey-2018","Odyssey-2015-2017","Odyssey-2022-2024","Breeze-2023-2024","Accord-2016","Accord-2014-2015","Civic-2021","Civic-Turbo-2016-2017","Civic-2019","Elysion-2016","Trumpchi-GS8-2017-2019"}

person_characters_zh = ["帽子","眼镜","上身白色","上身黑色","上身红色","上身橙色","上身黄色","上身粉色","上身深蓝色","上身蓝色","上身绿色","上身灰色","上身紫色","短袖","长袖","上身条纹","上身图案","上身多色","上身格子","下身条纹","下身图案","长外套","长裤","短裤","裙子","靴子","手提包","肩包","背包","手持物品","老年","成年","未成年","正身","侧身","背面","男性","女性"]
person_characters_en = ["hat","glasses","upper white","upper black","upper red","upper orange","upper yellow","upper pink","upper dark blue","upper blue","upper green","upper grey","upper purple","shortsleeve","longsleeve","upper stride","upper logo","upper plaid","upper splice","lowerstripe","lowerpattern","long coat","trousers","shorts","skirt&dress","boots","handbag","shoulderbag","backpack","hold objects","age over 60","age 18-60","age less 18","front","side","back","male","female"]

person_head_characters_zh = {"帽子","眼镜"}
person_head_characters_en = {"hat","glasses"}
person_upper_color_characters_zh = {"上身白色","上身黑色","上身红色","上身橙色","上身黄色","上身粉色","上身深蓝色","上身蓝色","上身绿色","上身灰色","上身紫色"}
person_upper_color_characters_en = {"upper white","upper black","upper red","upper orange","upper yellow","upper pink","upper dark blue","upper blue","upper green","upper grey","upper purple"}
person_upper_pattern_characters_zh = {"上身条纹","上身图案","上身多色","上身格子"}
person_upper_pattern_characters_en = {"upper stride","upper logo","upper plaid","upper splice"}
person_upper_sleeves_characters_zh = {"短袖","长袖"}
person_upper_sleeves_characters_en = {"shortsleeve","longsleeve"}
person_upper_clothes_characters_zh = {"裙子","长外套"}
person_upper_clothes_characters_en = {"skirt&dress","long coat"}
person_under_pattern_characters_zh = {"下身条纹","下身图案"}
person_under_pattern_characters_en = {"lowerstripe","lowerpattern"}
person_under_clothes_characters_zh = {"长裤","短裤"}
person_under_clothes_characters_en = {"trousers","shorts"}
person_shoes_characters_zh = {"靴子"}
person_shoes_characters_en = {"boots"}
person_bags_characters_zh = {"手提包","肩包","背包"}
person_bags_characters_en = {"handbag","shoulderbag","backpack"}
person_handholds_characters_zh = {"手持物品"}
person_handholds_characters_en = {"hold objects"}
person_age_characters_zh = {"老年","成年","未成年"}
person_age_characters_en = {"age over 60","age 18-60","age less 18"}
person_pose_characters_zh = {"正身","侧身","背面"}
person_pose_characters_en = {"front","side","back"}
person_sex_characters_zh = {"男性","女性"}
person_sex_characters_en = {"male","female"}


class ModelDecryptor:
    """
    硬件加密模型解密器，用于基于硬件信息解密加密的模型文件
    
    功能：
    - 获取CPU型号信息
    - 获取NVIDIA GPU UUID
    - 获取Coral Edge TPU UUID
    - 生成组合硬件标识符
    - 解密加密的模型文件
    """
    
    def __init__(self):
        self._required_hardware = ("NVIDIA GPU", "Coral Edge TPU")
    
    def _get_cpu_id(self):
        """获取CPU型号标识"""
        info = cpuinfo.get_cpu_info()
        return str(info['model'])
    
    def _get_gpu_uuid(self):
        """获取首个NVIDIA GPU的UUID"""
        try:
            gpus = GPUtil.getGPUs()
            return gpus[0].uuid if gpus else ''
        except Exception as e:
            print(f"Error getting GPU UUID: {e}")
            return ''
    
    def _get_coral_edgetpu_uuid(self):
        """获取Coral Edge TPU标识"""
        try:
            info = subprocess.check_output("lspci -nn | grep 089a", shell=True).decode()
            if not info:
                return ''
            return str(info)[-11:-2].replace(':', '')
        except subprocess.CalledProcessError:
            return ''
        except Exception as e:
            print(f"Error getting Coral UUID: {e}")
            return ''
    
    def _generate_hardware_signature(self):
        """生成硬件特征签名"""
        components = [
            self._get_gpu_uuid(),
            self._get_cpu_id(),
            self._get_coral_edgetpu_uuid()
        ]
        
        # 过滤空值并连接有效组件
        valid_components = [c for c in components if c]
        if not valid_components:
            print("No available hardware identifiers found!")
            return None
            
        return urlsafe_b64encode("-".join(valid_components).encode("utf-8"))
    
    def generate_hardware_id(self, output_key_path, password=None, key_length=16):
        """
        生成硬件加密ID文件（安全增强版）
        
        参数：
        output_key_path: 密钥输出路径前缀，自动添加.iv和.key后缀
        password: 可选预设密码（需为bytes类型），若未提供则随机生成
        key_length: 密钥长度（16/24/32对应AES-128/192/256）
        
        返回：
        bool: 是否生成成功
        """
        # 获取硬件特征
        hardware_signature = self._generate_hardware_signature()
        if not hardware_signature:
            print("无法生成硬件特征")
            return False

        try:
            # 生成符合AES要求的密钥
            if not password:
                password = get_random_bytes(key_length)
            elif len(password) not in (16):
                raise ValueError("密码长度必须为16字节")

            aes = AES.new(password, AES.MODE_CFB)
            iv = aes.iv
            raw_signature = aes.encrypt(hardware_signature)

            # 保存文件（自动添加后缀）
            with open(f"{output_key_path}model.iv", "wb") as iv_file, \
                 open(f"{output_key_path}model.id", "wb") as id_file, \
                 open(f"{output_key_path}model.ie", "wb") as ie_file:
                iv_file.write(iv)
                id_file.write(raw_signature)
                ie_file.write(password)
                
            # 加密成功
            return True

        except Exception as e:
            print(f"加密失败: {str(e)}")
            return False

    def decrypt_model(self, key_file_path, encrypted_file_path):
        """
        解密加密模型文件
        
        参数：
        key_file_path: 密钥文件路径
        encrypted_file_path: 加密模型文件路径
        
        返回：
        bytes: 解密后的模型字节流 或 None
        """
        hardware_signature = self._generate_hardware_signature()
        if not hardware_signature:
            print("Hardware validation failed")
            return None

        try:
            # 读取加密密钥
            with open(key_file_path, "rb") as f:
                encryption_key = f.read()
            
            # 生成完整解密密钥
            full_key = encryption_key + hardware_signature
            fernet = Fernet(full_key)

            # 解密模型文件
            with open(encrypted_file_path, "rb") as f:
                encrypted_data = f.read()
                
            return fernet.decrypt(encrypted_data)
            
        except FileNotFoundError as e:
            print(f"File not found: {e.filename}")
        except Exception as e:
            print(f"Decryption failed: {str(e)}")
        
        return None

class InferenceEngine:
    """统一管理推理引擎的初始化与选择"""
    
    def __init__(self, onnx_path: str, thread_num: int, metrics=None):
        """
        初始化推理引擎
        
        Args:
            onnx_path: ONNX模型路径
            thread_num: 线程数
            metrics: 性能指标对象（可选）
        """
        # 添加CPU亲和性设置（Linux有效）绑定到指定核心
        #os.sched_setaffinity(0, [0,1,2,3])
        self.config = FrigateConfig.load(install=True)
        self.threads = thread_num
        self.onnx_path = onnx_path
        self.metrics = metrics
        self.decryptor = ModelDecryptor()
        self.engine_type = self._select_engine()
        self.session = self._create_session(self.threads)
        
    def _select_engine(self) -> str:
        """选择最优的推理引擎"""
        # 获取所有可用的ONNX Runtime providers
        providers = ort.get_available_providers()
        
        # 优先级策略
        if 'CUDAExecutionProvider' in providers:
            #print("Using CUDAExecutionProvider")
            return "cuda"
        
        # 增强 OpenVINO 设备检测
        try:
            core = Core()
            # 支持多 GPU 设备检测 (如 GPU.0, GPU.1)
            gpu_devices = [d for d in core.available_devices if d.startswith("GPU")]
            if gpu_devices:
                #print(f"Selected OpenVINO on GPU: {gpu_devices[0]}")
                return "openvino"
        except Exception as e:
            print(f"OpenVINO init failed: {str(e)[:200]}")
        
        # 优化回退策略
        for provider in ['ROCMExecutionProvider', 'CPUExecutionProvider']:
            if provider in providers:
                #print(f"Selected {provider}")
                return provider.split('Execution')[0].lower()
        
        return "not_intel_cpu"
    
    def _init_openvino(self, thread_num: int) -> Any:
        """初始化OpenVINO引擎"""
        core = Core()
        model = core.read_model(self.load_model_content_or_model_path())
        
        # 自动选择设备 (GPU优先)
        devices = core.available_devices
        gpu_devices = [d for d in devices if d.startswith("GPU")]
        device = gpu_devices[0] if gpu_devices else "CPU"
        
        config = {}
        if "GPU" in device:
            try:
                config["INFERENCE_PRECISION_HINT"] = "f16"
            except RuntimeError:
                config["INFERENCE_PRECISION_HINT"] = "f32"
            config["PERFORMANCE_HINT"] = "THROUGHPUT"
        else:
            config["CPU_THREADS_NUM"] = thread_num
            config["PERFORMANCE_HINT"] = "LATENCY"
        
        #print(f"Compiling OpenVINO for {device} | Threads: {thread_num}")
        return core.compile_model(model, device, config=config)
    
    def _init_onnxruntime(self, thread_num: int) -> ort.InferenceSession:
        """初始化ONNX Runtime会话"""
        opts = ort.SessionOptions()
        # 动态线程分配策略
        if self.engine_type == "not_intel_cpu":
            intra_threads = max(1, thread_num // 2)
            inter_threads = max(1, thread_num - intra_threads)
            opts.intra_op_num_threads = intra_threads
            opts.inter_op_num_threads = inter_threads
            #print(f"CPU Thread config: intra={intra_threads}, inter={inter_threads}")
        # 通用配置
        opts.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
        )

        # 配置执行提供者
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        provider_options = [{'device_id': 0}, {}]
        
        #print(f"Initializing ORT with {self.engine_type.upper()} provider")
        
        return ort.InferenceSession(
            self.load_model_content_or_model_path(),
            opts,
            providers=providers,
            provider_options=provider_options
        )
    
    def _create_session(self, thread_num: int) -> Any:
        # 初始化创建session
        try:
            if self.engine_type == "cuda":
                #print(self.onnx_path + '使用' + self.engine_type + '推理')
                return self._init_onnxruntime(thread_num)
            elif self.engine_type == "openvino":
                #print(self.onnx_path + '使用' + self.engine_type + '推理')
                return self._init_openvino(thread_num)
            else:
                #print(self.onnx_path + '使用' + self.engine_type + '推理')
                return self._init_onnxruntime(thread_num)
        except Exception as e:
            #print(f"Engine init failed: {str(e)[:200]}")
            raise RuntimeError("Failed to initialize inference engine") from e
    
    def _infer(self, engine, frame: np.ndarray, det_class_name: str, min_score: float, lang: str) -> Dict[str, float]:
        """Run ONNX inference to detect characters of a person or vehicle."""
        # 预处理图像（直接返回 NumPy 数组）
        input_tensor = preprocess_image(frame, det_class_name)
        if self.engine_type == "openvino":
            infer_request = engine.session.create_infer_request()
            # 输入数据格式转换（OpenVINO 需要 contiguous 的 float32 数组）
            input_data = np.ascontiguousarray(input_tensor.astype(np.float32))
            # 将 NumPy 数组转换为 OpenVINO Tensor
            openvino_tensor = Tensor(input_data.astype(np.float32))
            # 设置输入数据（假设单输入模型）
            infer_request.set_input_tensor(0, openvino_tensor)
            # 执行推理（GPU 加速）
            infer_request.start_async()
            infer_request.wait()
            # 获取输出结果（假设单输出模型）
            ort_outputs = infer_request.get_output_tensor(0).data
        else:
            ort_inputs = {engine.session.get_inputs()[0].name: input_tensor}
            ort_outputs = engine.session.run(None, ort_inputs)[0]
    
        # Sigmoid 计算
        probs = 1 / (1 + np.exp(-ort_outputs))  # 使用 numpy 计算

        if det_class_name == "person":
            if lang == "Simplified Chinese":
                #class_names = P_ATTR
                class_names = person_characters_zh
            else:
                #class_names = P_ATTR_EN
                class_names = person_characters_en
        else:
            if lang == "Simplified Chinese":
                #class_names = V_ATTR
                class_names = vehicle_characters_zh
            else:
                #class_names = V_ATTR_EN
                class_names = vehicle_characters_en
        results = {}
        for i in np.where(probs[0] > min_score)[0]:
            results[class_names[i]] = probs[0][i]
    
        return results
    
    def load_model_content_or_model_path(self):
        if self.onnx_path.endswith(".m"):
            # 处理加密模型
            file_name_with_extension = os.path.basename(self.onnx_path)
            file_name, _ = os.path.splitext(file_name_with_extension)
            folder = os.path.dirname(self.onnx_path)
            key_path = os.path.join(folder, file_name + '.key')
            model_content = self.decryptor.decrypt_model(key_path, self.onnx_path)
        else:
            # 处理普通模型
            model_content = self.onnx_path
        return model_content
    
    # get person and vehicle characters, and get the bestframe
    def get_pv_bestFrame(
        self,
        TrackedObject,
        frame,
        engine
    ):
        """
        Extract the best frame and characters for a tracked object (person or vehicle).
        """
        # sub_labels
        sub_label_tmp = ()
        # description
        description_tmp = ()

        best_frame = None

        if TrackedObject.thumbnail_data is None:
            return None
    
        label = TrackedObject.obj_data.get("label")
        if label not in ["person", "car"]:
            return None
    
        # 用于检测的坐标
        box = TrackedObject.thumbnail_data["box"]
        #x1, y1, w1, h1 = box[0], box[1], int(box[2] - box[0]), int(box[3] - box[1])
        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        w, h = x2 - x1, y2 - y1

        # Pedestrian ReID
        if self.config.preid.enabled and label == "person" and ((max(w, h) >= self.config.preid.longer_size) or (w == h and w >= self.config.preid.shorter_size)):
            # 行人特征检测图像使用目标检测框范围
            best_frame = frame[y1:y1+h, x1:x1+w]

            person_characters = self._infer(engine, best_frame, "person", self.config.preid.min_score, self.config.preid.lang)
                
            if person_characters:
                if self.config.preid.lang == "Simplified Chinese":
                    head = select_best_score(person_characters, person_head_characters_zh)
                    upper_color = select_best_score(person_characters, person_upper_color_characters_zh)
                    upper_pattern = select_best_score(person_characters, person_upper_pattern_characters_zh)
                    upper_sleeves = select_best_score(person_characters, person_upper_sleeves_characters_zh)
                    upper_clothes = select_best_score(person_characters, person_upper_clothes_characters_zh)
                    under_pattern = select_best_score(person_characters, person_under_pattern_characters_zh)
                    under_clothes = select_best_score(person_characters, person_under_clothes_characters_zh)
                    shoes = select_valid_labels(person_characters, person_shoes_characters_zh)
                    bags = select_valid_labels(person_characters, person_bags_characters_zh)
                    handholds = select_valid_labels(person_characters, person_handholds_characters_zh)
                    pose = select_best_score(person_characters, person_pose_characters_zh)
                    age = select_best_score(person_characters, person_age_characters_zh)
                    sex = select_best_score(person_characters, person_sex_characters_zh)
                else:
                    head = select_best_score(person_characters, person_head_characters_en)
                    upper_color = select_best_score(person_characters, person_upper_color_characters_en)
                    upper_pattern = select_best_score(person_characters, person_upper_pattern_characters_en)
                    upper_sleeves = select_best_score(person_characters, person_upper_sleeves_characters_en)
                    upper_clothes = select_best_score(person_characters, person_upper_clothes_characters_en)
                    under_pattern = select_best_score(person_characters, person_under_pattern_characters_en)
                    under_clothes = select_best_score(person_characters, person_under_clothes_characters_en)
                    shoes = select_valid_labels(person_characters, person_shoes_characters_en)
                    bags = select_valid_labels(person_characters, person_bags_characters_en)
                    handholds = select_valid_labels(person_characters, person_handholds_characters_en)
                    pose = select_best_score(person_characters, person_pose_characters_en)
                    age = select_best_score(person_characters, person_age_characters_en)
                    sex = select_best_score(person_characters, person_sex_characters_en)

                dict_tmp = merge_characters_top_multi_keys(head, upper_color, upper_pattern, upper_sleeves, upper_clothes, under_pattern, under_clothes, shoes, bags, handholds, age, sex, pose, self.config.preid.lang)
                sub_label_tmp = dict_tmp
                description_tmp = dict_tmp

            # 保存的抓拍使用目标检测框扩展并模糊扩展内容的图像
            if self.config.preid.square_snap_enabled:
                best_frame = square_pad(x1, y1, x2, y2, frame)
        
        # Vehicle ReID
        elif self.config.vreid.enabled and label == "car" and ((max(w, h) >= self.config.vreid.longer_size) or (w == h and w >= self.config.vreid.shorter_size)):
            # 保存的抓拍使用目标检测框扩展后的图像
            if w >= h:
                y1 = max(0, y1 - (w - h) // 2)
                best_frame = frame[y1:y1+w, x1:x1+w]
            else:
                x1 = max(0, x1 - (h - w) // 2)
                best_frame = frame[y1:y1+h, x1:x1+h]

            vehicle_characters = self._infer(engine, best_frame, "car", self.config.vreid.min_score, self.config.vreid.lang)
                

            if vehicle_characters:
                if self.config.vreid.lang == "Simplified Chinese":
                    color = select_best_score(vehicle_characters, vehicle_color_characters_zh)
                    category = select_best_score(vehicle_characters, vehicle_category_characters_zh)
                    model = select_best_score(vehicle_characters, vehicle_model_characters_zh)
                    brand = select_best_score(vehicle_characters, vehicle_brand_characters_zh)
                else:
                    color = select_best_score(vehicle_characters, vehicle_color_characters_en)
                    category = select_best_score(vehicle_characters, vehicle_category_characters_en)
                    model = select_best_score(vehicle_characters, vehicle_model_characters_en)
                    brand = select_best_score(vehicle_characters, vehicle_brand_characters_en)
                sub_label_tmp = merge_characters_top_two_keys(brand, model, self.config.vreid.lang)
                #print(sub_label_tmp)
                description_tmp = merge_characters_top_four_keys(color, brand, model, category, self.config.vreid.lang)
                #print(description_tmp)
                
        else:
            best_frame = None

        if sub_label_tmp:
            TrackedObject.obj_data["sub_label"] = sub_label_tmp
            TrackedObject.obj_data["description"] = description_tmp


        # Save snapshot
        if best_frame is not None:
            best_frame = cv2.cvtColor(best_frame, cv2.COLOR_RGB2BGR, )
            ret, jpg = cv2.imencode(".jpg", best_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            return jpg.tobytes() if ret else None
        else:
            return None

def preprocess_image(frame: np.ndarray, det_class_name: str) -> np.ndarray:
    """
    使用 OpenCV + NumPy 实现的预处理（适配 OpenVINO）
    返回格式：float32 的 NCHW 格式数组
    """
    # Validate frame
    if frame is None or frame.size == 0:
        raise ValueError("Invalid input frame")
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    # 根据检测类别设置图像大小（注意 OpenCV 尺寸顺序是 (width, height)）
    if det_class_name == "person":
        target_size = (192, 256)  # (width, height) 与 PyTorch 的 (h,w) 相反
    elif det_class_name == "car":
        target_size = (256, 256)
    else:
        raise ValueError("Unsupported class name")

    # 使用 OpenCV 调整大小（代替 PIL）
    resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)

    # 转换通道顺序 HWC -> CHW（与 PyTorch ToTensor 一致）
    chw_image = resized.transpose(2, 0, 1)  # [3, H, W]

    # 归一化（假设 mean/std 已定义，例如：mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]）
    normalized = (chw_image / 255.0 - np.array(mean).reshape(3,1,1)) / np.array(std).reshape(3,1,1)

    # 添加 batch 维度 [1, 3, H, W]
    input_array = np.expand_dims(normalized, axis=0).astype(np.float32)

    return input_array
    
def square_pad(x1, y1, x2, y2, frame: np.ndarray) -> np.ndarray:
    w, h = x2 - x1, y2 - y1
    # 1. 计算正方形的边长（取 max(w, h)）
    side_length = max(w, h)

    # 2. 计算正方形的坐标（确保 box 居中）
    center_x = x1 + w // 2
    center_y = y1 + h // 2
    square_x = max(0, center_x - side_length // 2)
    square_y = max(0, center_y - side_length // 2)

    # 3. 确保不超出图像边界
    frame_height, frame_width = frame.shape[:2]
    square_x_end = min(square_x + side_length, frame_width)
    square_y_end = min(square_y + side_length, frame_height)
    square_x = square_x_end - side_length if square_x_end == frame_width else square_x
    square_y = square_y_end - side_length if square_y_end == frame_height else square_y

    # 4. 提取正方形区域并模糊
    square_region = frame[square_y:square_y+side_length, square_x:square_x+side_length]
    blurred_square = cv2.GaussianBlur(square_region, (51, 51), 0)  # 调整模糊强度

    # 5. 计算原始 box 在正方形中的相对位置
    box_in_square_x = x1 - square_x
    box_in_square_y = y1 - square_y
    box_in_square_x_end = box_in_square_x + w
    box_in_square_y_end = box_in_square_y + h

    # 6. 恢复原始 box 区域（使其清晰）
    blurred_square[box_in_square_y:box_in_square_y_end, box_in_square_x:box_in_square_x_end] = frame[y1:y2, x1:x2]
    
    return blurred_square

def select_labels(res, valid_labels):
    valid_keys = set(valid_labels.values())
    return {k: res[k] for k in valid_keys if k in res}
    
def select_best_score(res, valid_labels):
    # 筛选出有效标签并找到最大值
    max_score = -float('inf')
    max_key = None
    
    for key, value in res.items():
        if key in valid_labels and value > max_score:
            max_score = value
            max_key = key
    
    # 返回包含最高分项的字典（如果没有匹配项则返回空字典）
    return {max_key: max_score} if max_key is not None else {}
    
def select_valid_labels(res, valid_labels):
    # 筛选出所有有效标签的项
    filtered = {key: value for key, value in res.items() if key in valid_labels}
    return filtered
    
def merge_characters_top_two_keys(brand, model, lang):
    """合并各字典最高分键，并取二者最大值"""
    def get_max_item(d):
        return max(d.items(), key=lambda x: x[1], default=(None, 0.0))
    
    model_key, model_score = get_max_item(model)
    brand_key, brand_score = get_max_item(brand)
    
    combined_keys = []
    for k in [brand_key, model_key]:
        if k: combined_keys.append(k)
    
    if lang == "Simplified Chinese":
        combined_key = " ".join(combined_keys) if combined_keys else ""
    else:
        combined_key = " ".join(combined_keys) if combined_keys else ""

    max_value = max(brand_score, model_score)
    return (combined_key, float(max_value))

def merge_characters_top_four_keys(color, brand, model, category, lang):
    """直接合并所有键，不筛选最高分项"""
    combined_keys = []
    # 提取所有非空键（不验证分数）
    combined_keys.extend(color.keys() if color else [])
    combined_keys.extend(brand.keys() if brand else [])
    combined_keys.extend(model.keys() if model else [])
    combined_keys.extend(category.keys() if category else [])
    
    # 处理合并逻辑
    if lang == "Simplified Chinese":
        combined_key = " ".join(combined_keys) if combined_keys else ""
    else:
        combined_key = " ".join(combined_keys) if combined_keys else ""
    
    # 计算全局最大分数（若需保留分数逻辑）
    all_scores = []
    all_scores.extend(color.values() if color else [0.0])
    all_scores.extend(brand.values() if brand else [0.0])
    all_scores.extend(model.values() if model else [0.0])
    all_scores.extend(category.values() if category else [0.0])
    max_score = max(all_scores) if all_scores else 0.0
    
    return (combined_key, float(max_score)) if combined_key else ()

def merge_characters_top_multi_keys(head, upper_color, upper_pattern, upper_sleeves, upper_clothes, under_pattern, under_clothes, shoes, bags, handholds, age, sex, pose, lang):
    """合并所有字典的键，并取所有值中的最高分"""
    # 合并各部分的键
    head_keys = list(head.keys())
    upper_keys = [k for d in (upper_color, upper_pattern, upper_sleeves, upper_clothes) for k in d.keys()]
    under_keys = [k for d in (under_pattern, under_clothes) for k in d.keys()]
    shoe_keys = list(shoes.keys())
    bag_keys = list(bags.keys())
    handhold_keys = list(handholds.keys())
    other_keys = [k for d in (age, sex) for k in d.keys()]
    pose_keys = list(pose.keys())
    
    # 定义各部分的处理规则：键列表，无前置时的前缀，有前置时的前缀
    if lang == "Simplified Chinese":
        sections = [
            (head_keys, '戴', '-戴'),
            (upper_keys, '穿着', '-穿着'),
            (under_keys, '', ''),
            (shoe_keys, '', ''),
            (bag_keys, '携带', '-携带'),
            (handhold_keys, '', '-'),
            (other_keys, '', '-'),
            (pose_keys, '', '-'),
        ]
    else:
        sections = [
            (head_keys, '', '•'),
            (upper_keys, 'upper ', '•upper '),
            (under_keys, '', ' '),
            (shoe_keys, '', '•'),
            (bag_keys, '', '•'),
            (handhold_keys, '', '•'),
            (other_keys, '', '•'),
            (pose_keys, '', '•'),
        ]
    
    combined_parts = []
    has_previous = False
    
    for keys, prefix_no_prev, prefix_with_prev in sections:
        if not keys:
            continue  # 跳过空键部分
        if lang == "Simplified Chinese":
            part = ''.join(keys)
        else:
            part = ' '.join(keys)
        # 根据是否已有内容选择前缀
        prefix = prefix_with_prev if has_previous else prefix_no_prev
        combined_part = prefix + part
        if combined_part:  # 非空部分才添加
            combined_parts.append(combined_part)
            has_previous = True
    
    combined_key = ''.join(combined_parts)
    
    # 收集所有值并计算最高分
    all_dicts = [head, upper_color, upper_pattern, upper_sleeves, upper_clothes,
                under_pattern, under_clothes, shoes, bags, handholds, age, sex, pose]
    all_values = [v for d in all_dicts for v in d.values()]
    max_score = max(all_values) if all_values else 0.0
    
    return (combined_key, float(max_score))


# ============================================================================
# Embedding引擎集成支持
# ============================================================================

def create_inference_engine(onnx_path: str, thread_num: int):
    """
    创建推理引擎的工厂函数
    
    根据配置选择使用embedding引擎或传统reid引擎
    
    Args:
        onnx_path: ONNX模型路径
        thread_num: 线程数
        
    Returns:
        推理引擎实例
    """
    try:
        # 尝试使用embedding引擎工厂
        from .reid_engine_factory import InferenceEngine as EmbeddingInferenceEngine
        return EmbeddingInferenceEngine(onnx_path, thread_num)
    except ImportError:
        # 回退到传统引擎
        print("Embedding engine not available, using traditional reid engine")
        return InferenceEngine(onnx_path, thread_num)


# 为了向后兼容，保持原有的InferenceEngine类
# 但推荐使用create_inference_engine工厂函数
