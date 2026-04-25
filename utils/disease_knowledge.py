# 农作物病害知识库

DISEASE_KNOWLEDGE = {
    # 苹果病害
    0: {
        'name': '苹果健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    1: {
        'name': '苹果黑星病一般',
        'symptoms': '叶片上出现黄绿色小斑点，逐渐扩大为黑色病斑',
        'prevention': '及时清除病叶病果，加强果园通风',
        'treatment': '喷施波尔多液或多菌灵'
    },
    2: {
        'name': '苹果黑星病严重',
        'symptoms': '叶片上出现大量黑色病斑，叶片卷曲，果实表面出现黑色斑点',
        'prevention': '彻底清除病残体，合理修剪，改善通风透光',
        'treatment': '喷施甲基硫菌灵或戊唑醇'
    },
    3: {
        'name': '苹果灰斑病',
        'symptoms': '叶片上出现灰白色圆形病斑，边缘褐色',
        'prevention': '清除病叶，加强肥水管理，增强树势',
        'treatment': '喷施代森锰锌或百菌清'
    },
    4: {
        'name': '苹果雪松锈病一般',
        'symptoms': '叶片上出现黄色小斑点，逐渐扩大为橙黄色病斑',
        'prevention': '清除果园周围的雪松，发病初期及时防治',
        'treatment': '喷施三唑酮或戊唑醇'
    },
    5: {
        'name': '苹果雪松锈病严重',
        'symptoms': '叶片上出现大量橙黄色病斑，病斑上产生黑色小点',
        'prevention': '果园周围5公里内避免种植雪松，彻底清除病叶',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    
    # 樱桃病害
    6: {
        'name': '樱桃健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    7: {
        'name': '樱桃白粉病一般',
        'symptoms': '叶片表面出现白色粉状物，逐渐扩大',
        'prevention': '及时清除病叶，加强通风透光',
        'treatment': '喷施粉锈宁或戊唑醇'
    },
    8: {
        'name': '樱桃白粉病严重',
        'symptoms': '叶片表面覆盖大量白色粉状物，叶片卷曲，植株生长受阻',
        'prevention': '彻底清除病残体，合理密植，改善通风',
        'treatment': '喷施甲基硫菌灵或嘧菌酯'
    },
    
    # 玉米病害
    9: {
        'name': '玉米健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    10: {
        'name': '玉米灰斑病一般',
        'symptoms': '叶片上出现灰色小斑点，逐渐扩大为灰色病斑',
        'prevention': '清除病叶，合理密植，加强通风',
        'treatment': '喷施代森锰锌或百菌清'
    },
    11: {
        'name': '玉米灰斑病严重',
        'symptoms': '叶片上出现大量灰色病斑，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    12: {
        'name': '玉米锈病一般',
        'symptoms': '叶片上出现黄色小斑点，逐渐扩大为锈色病斑',
        'prevention': '清除病叶，加强田间管理',
        'treatment': '喷施粉锈宁或戊唑醇'
    },
    13: {
        'name': '玉米锈病严重',
        'symptoms': '叶片上出现大量锈色病斑，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施甲基硫菌灵或嘧菌酯'
    },
    14: {
        'name': '玉米叶斑病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施代森锰锌或百菌清'
    },
    15: {
        'name': '玉米叶斑病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    16: {
        'name': '玉米花叶病毒病',
        'symptoms': '叶片上出现黄绿相间的花叶症状，植株矮化',
        'prevention': '防治蚜虫等传播媒介，拔除病株，选用抗病品种',
        'treatment': '无特效治疗方法，主要依靠预防'
    },
    
    # 葡萄病害
    17: {
        'name': '葡萄健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    18: {
        'name': '葡萄黑腐病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑',
        'prevention': '清除病果病叶，加强通风透光',
        'treatment': '喷施波尔多液或多菌灵'
    },
    19: {
        'name': '葡萄黑腐病严重',
        'symptoms': '叶片上出现大量褐色病斑，果实腐烂',
        'prevention': '彻底清除病残体，合理修剪，改善通风',
        'treatment': '喷施甲基硫菌灵或戊唑醇'
    },
    20: {
        'name': '葡萄轮斑病一般',
        'symptoms': '叶片上出现褐色轮纹状病斑',
        'prevention': '清除病叶，加强肥水管理',
        'treatment': '喷施代森锰锌或百菌清'
    },
    21: {
        'name': '葡萄轮斑病严重',
        'symptoms': '叶片上出现大量褐色轮纹状病斑，叶片干枯',
        'prevention': '彻底清除病残体，合理密植，改善通风',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    22: {
        'name': '葡萄褐斑病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑',
        'prevention': '清除病叶，加强田间管理',
        'treatment': '喷施代森锰锌或百菌清'
    },
    23: {
        'name': '葡萄褐斑病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯',
        'prevention': '彻底清除病残体，合理修剪，改善通风',
        'treatment': '喷施甲基硫菌灵或戊唑醇'
    },
    
    # 柑桔病害
    24: {
        'name': '柑桔健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    25: {
        'name': '柑桔黄龙病一般',
        'symptoms': '叶片出现黄化，叶脉间失绿',
        'prevention': '及时清除病株，防治木虱等传播媒介，加强肥水管理',
        'treatment': '无特效治疗方法，主要依靠预防'
    },
    26: {
        'name': '柑桔黄龙病严重',
        'symptoms': '叶片严重黄化，植株矮化，果实畸形',
        'prevention': '彻底清除病株，防治木虱等传播媒介，选用无病苗木',
        'treatment': '无特效治疗方法，主要依靠预防'
    },
    
    # 桃病害
    27: {
        'name': '桃健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    28: {
        'name': '桃疮痂病一般',
        'symptoms': '叶片上出现褐色小斑点，果实表面出现褐色斑点',
        'prevention': '清除病果病叶，加强通风透光',
        'treatment': '喷施波尔多液或多菌灵'
    },
    29: {
        'name': '桃疮痂病严重',
        'symptoms': '叶片上出现大量褐色斑点，果实表面出现大量褐色斑点',
        'prevention': '彻底清除病残体，合理修剪，改善通风',
        'treatment': '喷施甲基硫菌灵或戊唑醇'
    },
    
    # 辣椒病害
    30: {
        'name': '辣椒健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    31: {
        'name': '辣椒疮痂病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为疮痂状病斑',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施农用链霉素或新植霉素'
    },
    32: {
        'name': '辣椒疮结皮结皮结结痂病严重',
        'symptoms': '叶片上出现大量结皮结皮结结痂状病斑，叶片卷曲，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施铜制剂或中生菌素'
    },
    
    # 马铃薯病害
    33: {
        'name': '马铃薯健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    34: {
        'name': '马铃薯早疫病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑',
        'prevention': '清除病叶，加强田间管理',
        'treatment': '喷施代森锰锌或百菌清'
    },
    35: {
        'name': '马铃薯早疫病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    36: {
        'name': '马铃薯晚疫病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑，潮湿条件下产生白色霉层',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施代森锰锌或百菌清'
    },
    37: {
        'name': '马铃薯晚疫病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，块茎腐烂',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施甲霜灵锰锌或烯酰吗素'
    },
    
    # 草莓病害
    38: {
        'name': '草莓健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    39: {
        'name': '草莓叶枯病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施代森锰锌或百菌清'
    },
    40: {
        'name': '草莓叶枯病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，植株生长受阻',
        'prevention': '彻底清除病残体，合理密植，改善通风',
        'treatment': '喷施甲基硫菌灵或戊唑醇'
    },
    
    # 番茄病害
    41: {
        'name': '番茄健康',
        'symptoms': '叶片绿色，无病斑，植株生长正常',
        'prevention': '保持良好的栽培管理，定期检查植株',
        'treatment': '无需治疗'
    },
    42: {
        'name': '番茄白粉病一般',
        'symptoms': '叶片表面出现白色粉状物，逐渐扩大',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施粉锈宁或戊唑醇'
    },
    43: {
        'name': '番茄白粉病严重',
        'symptoms': '叶片表面覆盖大量白色粉状物，叶片卷曲，植株生长受阻',
        'prevention': '彻底清除病残体，合理密植，改善通风',
        'treatment': '喷施甲基硫菌灵或嘧菌酯'
    },
    44: {
        'name': '番茄疮痂病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为疮痂状病斑',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施农用链霉素或新植霉素'
    },
    45: {
        'name': '番茄疮痂病严重',
        'symptoms': '叶片上出现大量疮痂状病斑，叶片卷曲，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施铜制剂或中生菌素'
    },
    46: {
        'name': '番茄早疫病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑，有同心轮纹',
        'prevention': '清除病叶，加强田间管理',
        'treatment': '喷施代森锰锌或百菌清'
    },
    47: {
        'name': '番茄早疫病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    48: {
        'name': '番茄晚疫病菌一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑，潮湿条件下产生白色霉层',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施代森锰锌或百菌清'
    },
    49: {
        'name': '番茄晚疫病菌严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，果实腐烂',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施甲霜灵锰锌或烯酰吗啉'
    },
    50: {
        'name': '番茄叶霉病一般',
        'symptoms': '叶片背面出现灰色霉层，叶片正面出现黄色斑点',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施多菌灵或甲基硫菌灵'
    },
    51: {
        'name': '番茄叶霉病严重',
        'symptoms': '叶片背面覆盖大量灰色霉层，叶片正面出现大量黄色斑点，叶片卷曲',
        'prevention': '彻底清除病残体，合理密植，改善通风',
        'treatment': '喷施嘧菌酯或戊唑醇'
    },
    52: {
        'name': '番茄斑点病一般',
        'symptoms': '叶片上出现褐色小斑点，逐渐扩大为褐色病斑',
        'prevention': '清除病叶，加强田间管理',
        'treatment': '喷施代森锰锌或百菌清'
    },
    53: {
        'name': '番茄斑点病严重',
        'symptoms': '叶片上出现大量褐色病斑，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，选用抗病品种',
        'treatment': '喷施苯醚甲环唑或嘧菌酯'
    },
    54: {
        'name': '番茄斑枯病一般',
        'symptoms': '叶片上出现褐色小斑点，中央灰白色，边缘褐色',
        'prevention': '清除病叶，加强通风透光',
        'treatment': '喷施代森锰锌或百菌清'
    },
    55: {
        'name': '番茄斑枯病严重',
        'symptoms': '叶片上出现大量褐色小斑点，叶片干枯，植株生长受阻',
        'prevention': '彻底清除病残体，合理密植，改善通风',
        'treatment': '喷施甲基硫菌灵或戊唑醇'
    },
    56: {
        'name': '番茄红蜘蛛损伤一般',
        'symptoms': '叶片上出现黄色小斑点，逐渐扩大为黄色斑块',
        'prevention': '加强田间管理，保护天敌',
        'treatment': '喷施阿维菌素或哒螨灵'
    },
    57: {
        'name': '番茄红蜘蛛损伤严重',
        'symptoms': '叶片上出现大量黄色斑块，叶片干枯，植株生长受阻',
        'prevention': '轮作倒茬，清洁田园',
        'treatment': '喷施阿维菌素或螺螨酯'
    },
    58: {
        'name': '番茄黄化曲叶病毒病一般',
        'symptoms': '叶片黄化，卷曲，植株矮化',
        'prevention': '防治烟粉虱等传播媒介，拔除病株，选用抗病品种',
        'treatment': '无特效治疗方法，主要依靠预防'
    },
    59: {
        'name': '番茄黄化曲叶病毒病严重',
        'symptoms': '叶片严重黄化，卷曲，植株严重矮化，果实畸形',
        'prevention': '彻底防治烟粉虱，拔除病株，选用抗病品种',
        'treatment': '无特效治疗方法，主要依靠预防'
    },
    60: {
        'name': '番茄花叶病毒病',
        'symptoms': '叶片上出现黄绿相间的花叶症状，植株矮化',
        'prevention': '防治蚜虫等传播媒介，拔除病株，选用抗病品种',
        'treatment': '无特效治疗方法，主要依靠预防'
    }
}

def get_disease_knowledge(class_id):
    """根据类别ID获取病害知识库信息"""
    return DISEASE_KNOWLEDGE.get(class_id, {
        'name': '未知病害',
        'symptoms': '暂无症状信息',
        'prevention': '暂无预防信息',
        'treatment': '暂无治疗信息'
    })

# 获取所有农作物类型
def get_crop_types():
    """获取所有农作物类型"""
    crops = set()
    for disease_info in DISEASE_KNOWLEDGE.values():
        name = disease_info['name']
        if '健康' in name:
            crop = name.replace('健康', '')
            if crop:
                crops.add(crop)
    return sorted(list(crops))

# 根据农作物类型获取病害列表
def get_diseases_by_crop(crop):
    """根据农作物类型获取病害列表"""
    diseases = []
    for class_id, disease_info in DISEASE_KNOWLEDGE.items():
        name = disease_info['name']
        if crop in name:
            diseases.append((class_id, name))
    return diseases
