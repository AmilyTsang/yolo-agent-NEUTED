import json
import os
import re

class KnowledgeBase:
    def __init__(self):
        self.defect_database = self._load_defect_database()
    
    def _load_defect_database(self):
        """加载缺陷知识库"""
        return {
            '划痕': {
                'name': '划痕',
                'description': '物体表面被尖锐物体划过留下的痕迹',
                'causes': [
                    {'cause': '加工过程中刀具磨损或损坏', 'source': '金属加工工艺手册'},
                    {'cause': '搬运过程中与其他物体摩擦碰撞', 'source': '工业物流指南'},
                    {'cause': '表面处理不当，防护涂层缺失', 'source': '表面工程技术'},
                    {'cause': '环境中的灰尘或砂粒进入加工区域', 'source': '洁净车间管理规范'}
                ],
                'solutions': [
                    {'solution': '更换磨损刀具，定期检查刀具状态', 'source': '设备维护手册'},
                    {'solution': '使用防护包装材料，改进搬运流程', 'source': '工业物流指南'},
                    {'solution': '增加表面防护涂层，优化表面处理工艺', 'source': '表面工程技术'},
                    {'solution': '加强车间清洁管理，安装空气过滤系统', 'source': '洁净车间管理规范'}
                ],
                'prevention': [
                    {'method': '定期维护和更换刀具', 'source': '设备维护手册'},
                    {'method': '实施5S管理，保持工作环境整洁', 'source': '精益生产手册'},
                    {'method': '使用合适的防护措施', 'source': '工业安全规范'},
                    {'method': '员工培训，提高操作规范意识', 'source': '员工培训手册'}
                ]
            },
            '裂纹': {
                'name': '裂纹',
                'description': '材料内部或表面出现的裂缝',
                'causes': [
                    {'cause': '材料疲劳，长期受力导致', 'source': '材料力学导论'},
                    {'cause': '焊接工艺不当，产生残余应力', 'source': '焊接技术手册'},
                    {'cause': '热处理工艺缺陷', 'source': '热处理技术规范'},
                    {'cause': '原材料质量问题，存在杂质或缺陷', 'source': '材料检验标准'}
                ],
                'solutions': [
                    {'solution': '对裂纹进行焊接修复或更换部件', 'source': '焊接修复指南'},
                    {'solution': '进行退火处理，消除残余应力', 'source': '热处理技术规范'},
                    {'solution': '加强原材料检验，确保质量', 'source': '材料检验标准'}
                ],
                'prevention': [
                    {'method': '优化结构设计，避免应力集中', 'source': '结构力学设计'},
                    {'method': '采用合适的焊接工艺参数', 'source': '焊接技术手册'},
                    {'method': '定期进行无损检测', 'source': '无损检测规范'},
                    {'method': '控制原材料质量', 'source': '供应链质量管理'}
                ]
            },
            '凹陷': {
                'name': '凹陷',
                'description': '物体表面向内凹陷的缺陷',
                'causes': [
                    {'cause': '受到外力撞击或压力', 'source': '材料力学导论'},
                    {'cause': '模具设计缺陷，导致成型不良', 'source': '模具设计手册'},
                    {'cause': '铸造过程中气体残留', 'source': '铸造工艺手册'},
                    {'cause': '热处理过程中变形', 'source': '热处理技术规范'}
                ],
                'solutions': [
                    {'solution': '使用液压机进行校平修复', 'source': '钣金加工手册'},
                    {'solution': '修复或更换模具', 'source': '模具维护手册'},
                    {'solution': '优化铸造工艺，减少气体残留', 'source': '铸造工艺手册'}
                ],
                'prevention': [
                    {'method': '加强包装防护，防止运输损坏', 'source': '物流包装规范'},
                    {'method': '优化模具设计和加工精度', 'source': '模具设计手册'},
                    {'method': '控制铸造工艺参数', 'source': '铸造工艺手册'},
                    {'method': '采用合适的支撑结构', 'source': '结构设计规范'}
                ]
            },
            '凸起': {
                'name': '凸起',
                'description': '物体表面向外突出的缺陷',
                'causes': [
                    {'cause': '焊接时焊珠过高', 'source': '焊接技术手册'},
                    {'cause': '喷涂过程中涂料堆积', 'source': '涂装工艺手册'},
                    {'cause': '加工时刀具跳动', 'source': '数控加工手册'},
                    {'cause': '材料热胀冷缩不均匀', 'source': '材料力学导论'}
                ],
                'solutions': [
                    {'solution': '打磨去除多余部分', 'source': '表面处理手册'},
                    {'solution': '调整焊接参数，控制焊珠高度', 'source': '焊接技术手册'},
                    {'solution': '优化喷涂工艺参数', 'source': '涂装工艺手册'},
                    {'solution': '检查并调整刀具，消除跳动', 'source': '数控加工手册'}
                ],
                'prevention': [
                    {'method': '严格控制焊接工艺参数', 'source': '焊接技术手册'},
                    {'method': '优化喷涂工艺，均匀涂布', 'source': '涂装工艺手册'},
                    {'method': '定期检查和维护刀具', 'source': '设备维护手册'},
                    {'method': '控制加工环境温度', 'source': '车间环境管理'}
                ]
            },
            '腐蚀': {
                'name': '腐蚀',
                'description': '材料与周围环境发生化学反应导致的损坏',
                'causes': [
                    {'cause': '暴露在潮湿或腐蚀性环境中', 'source': '腐蚀工程手册'},
                    {'cause': '防护涂层破损或缺失', 'source': '防腐技术规范'},
                    {'cause': '电化学腐蚀，不同金属接触', 'source': '电化学原理'},
                    {'cause': '环境中存在腐蚀性气体或液体', 'source': '工业环境监测'}
                ],
                'solutions': [
                    {'solution': '清除腐蚀层，重新进行防腐处理', 'source': '防腐技术规范'},
                    {'solution': '更换腐蚀严重的部件', 'source': '设备维护手册'},
                    {'solution': '增加防腐涂层或镀层', 'source': '表面工程技术'}
                ],
                'prevention': [
                    {'method': '实施阴极保护或阳极保护', 'source': '腐蚀工程手册'},
                    {'method': '定期检查和维护防腐涂层', 'source': '设备维护手册'},
                    {'method': '控制环境湿度和腐蚀性物质', 'source': '车间环境管理'},
                    {'method': '避免不同金属直接接触', 'source': '材料选用规范'}
                ]
            },
            '磨损': {
                'name': '磨损',
                'description': '物体表面因摩擦导致的材料损失',
                'causes': [
                    {'cause': '长期摩擦导致材料损耗', 'source': '摩擦学导论'},
                    {'cause': '润滑不足或润滑剂失效', 'source': '润滑技术手册'},
                    {'cause': '接触表面存在杂质或异物', 'source': '设备维护手册'},
                    {'cause': '加工精度不足，表面粗糙', 'source': '加工工艺手册'}
                ],
                'solutions': [
                    {'solution': '更换磨损部件', 'source': '设备维护手册'},
                    {'solution': '重新润滑或更换润滑剂', 'source': '润滑技术手册'},
                    {'solution': '修复或重新加工磨损表面', 'source': '机械加工手册'}
                ],
                'prevention': [
                    {'method': '定期润滑和检查润滑系统', 'source': '润滑技术手册'},
                    {'method': '保持工作环境清洁', 'source': '5S管理手册'},
                    {'method': '提高加工精度和表面质量', 'source': '加工工艺手册'},
                    {'method': '选用耐磨材料', 'source': '材料选用规范'}
                ]
            },
            '变形': {
                'name': '变形',
                'description': '物体形状发生非预期的改变',
                'causes': [
                    {'cause': '热加工过程中温度不均匀', 'source': '热处理技术规范'},
                    {'cause': '机械加工应力释放', 'source': '材料力学导论'},
                    {'cause': '长期受力导致蠕变', 'source': '材料力学导论'},
                    {'cause': '运输或存放不当', 'source': '物流存储规范'}
                ],
                'solutions': [
                    {'solution': '进行矫正处理，恢复原有形状', 'source': '钣金加工手册'},
                    {'solution': '重新热处理，消除应力', 'source': '热处理技术规范'},
                    {'solution': '更换严重变形的部件', 'source': '设备维护手册'}
                ],
                'prevention': [
                    {'method': '优化热处理工艺，控制温度均匀性', 'source': '热处理技术规范'},
                    {'method': '采用时效处理，释放内应力', 'source': '材料加工手册'},
                    {'method': '合理设计支撑结构', 'source': '结构设计规范'},
                    {'method': '优化运输和存储方式', 'source': '物流存储规范'}
                ]
            },
            '污渍': {
                'name': '污渍',
                'description': '物体表面附着的污染物',
                'causes': [
                    {'cause': '生产环境不洁净', 'source': '洁净车间管理规范'},
                    {'cause': '操作人员手部污染', 'source': '卫生管理规范'},
                    {'cause': '原材料携带杂质', 'source': '供应链质量管理'},
                    {'cause': '清洗不彻底', 'source': '清洗工艺手册'}
                ],
                'solutions': [
                    {'solution': '使用合适的清洁剂进行清洗', 'source': '清洗工艺手册'},
                    {'solution': '重新进行表面处理', 'source': '表面工程技术'}
                ],
                'prevention': [
                    {'method': '实施严格的5S管理', 'source': '5S管理手册'},
                    {'method': '员工穿戴洁净工作服', 'source': '卫生管理规范'},
                    {'method': '加强原材料检验', 'source': '供应链质量管理'},
                    {'method': '优化清洗工艺', 'source': '清洗工艺手册'}
                ]
            },
            '气泡': {
                'name': '气泡',
                'description': '材料内部或表面形成的气体空隙',
                'causes': [
                    {'cause': '铸造或注塑过程中气体未排出', 'source': '铸造工艺手册'},
                    {'cause': '涂料或粘合剂搅拌时混入空气', 'source': '涂装工艺手册'},
                    {'cause': '焊接过程中保护气体不足', 'source': '焊接技术手册'},
                    {'cause': '原材料含有挥发性物质', 'source': '材料检验标准'}
                ],
                'solutions': [
                    {'solution': '修复或更换受影响部件', 'source': '设备维护手册'},
                    {'solution': '重新涂装或粘合', 'source': '涂装工艺手册'}
                ],
                'prevention': [
                    {'method': '优化铸造/注塑工艺，增加排气', 'source': '铸造工艺手册'},
                    {'method': '使用真空搅拌或脱泡设备', 'source': '材料加工手册'},
                    {'method': '确保焊接保护气体充足', 'source': '焊接技术手册'},
                    {'method': '选用低挥发性原材料', 'source': '材料选用规范'}
                ]
            },
            '断裂': {
                'name': '断裂',
                'description': '材料发生完全分离的严重缺陷',
                'causes': [
                    {'cause': '超过材料屈服强度的载荷', 'source': '材料力学导论'},
                    {'cause': '材料存在内部缺陷或裂纹', 'source': '材料检验标准'},
                    {'cause': '疲劳破坏，长期循环载荷', 'source': '材料力学导论'},
                    {'cause': '低温环境下材料脆性增加', 'source': '材料性能手册'}
                ],
                'solutions': [
                    {'solution': '更换断裂部件', 'source': '设备维护手册'},
                    {'solution': '分析断裂原因，改进设计', 'source': '失效分析手册'}
                ],
                'prevention': [
                    {'method': '优化结构设计，确保强度储备', 'source': '结构力学设计'},
                    {'method': '加强材料检验，排除缺陷', 'source': '材料检验标准'},
                    {'method': '进行疲劳分析，优化载荷设计', 'source': '疲劳设计手册'},
                    {'method': '在低温环境使用耐低温材料', 'source': '材料选用规范'}
                ]
            }
        }
    
    def analyze_defects(self, defects):
        """分析检测到的缺陷，提供详细信息"""
        analysis = []
        
        for defect in defects:
            defect_type = defect['type']
            info = self.defect_database.get(defect_type)
            
            if info:
                analysis.append({
                    'type': defect_type,
                    'confidence': defect['confidence'],
                    'bbox': defect['bbox'],
                    'area': defect['area'],
                    'description': info['description'],
                    'causes': info['causes'],
                    'solutions': info['solutions'],
                    'prevention': info['prevention']
                })
            else:
                analysis.append({
                    'type': defect_type,
                    'confidence': defect['confidence'],
                    'bbox': defect['bbox'],
                    'area': defect['area'],
                    'description': '未知缺陷类型',
                    'causes': [],
                    'solutions': [],
                    'prevention': []
                })
        
        return analysis
    
    def get_defect_info(self, defect_type):
        """获取特定缺陷类型的详细信息"""
        return self.defect_database.get(defect_type)
    
    def search(self, query):
        """搜索知识库"""
        results = []
        
        for defect_type, info in self.defect_database.items():
            # 在名称、描述中搜索
            if query.lower() in defect_type.lower() or \
               query.lower() in info['description'].lower():
                results.append(info)
                continue
            
            # 在原因中搜索
            for cause in info['causes']:
                if query.lower() in cause['cause'].lower():
                    results.append(info)
                    break
            
            if results and results[-1] == info:
                continue
            
            # 在解决方案中搜索
            for solution in info['solutions']:
                if query.lower() in solution['solution'].lower():
                    results.append(info)
                    break
        
        return results