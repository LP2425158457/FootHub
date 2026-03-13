import os
import requests
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeepSeekService:
    """
    DeepSeek API服务类
    用于通过AI分析足球赛事信息
    """
    
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        logger.info(f"读取到的DEEPSEEK_API_KEY: {self.api_key}")
        logger.info(f"读取到的DEEPSEEK_BASE_URL: {self.base_url}")
        
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")
        
        logger.info(f"DeepSeek服务初始化成功, API Key: {self.api_key[:10]}..., Base URL: {self.base_url}")
    
    def _call_api(self, messages: List[Dict], max_tokens: int = 500) -> str:
        """
        调用DeepSeek API
        
        Args:
            messages: 消息列表
            max_tokens: 最大token数
            
        Returns:
            str: API响应内容
        """
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False,
            "temperature": 0.3
        }
        
        logger.info(f"调用DeepSeek API: {url}")
        logger.debug(f"请求参数: model={data['model']}, max_tokens={max_tokens}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            logger.info(f"DeepSeek API响应状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            logger.info(f"DeepSeek API调用成功, 返回内容长度: {len(content)}")
            logger.debug(f"返回内容预览: {content[:100]}...")
            
            return content
        except requests.exceptions.HTTPError as e:
            logger.error(f"DeepSeek API HTTP错误: {e}")
            raise e
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise e
    
    def summarize_match(self, home_team: str, away_team: str, league: str, 
                        tavily_answer: str, home_info: str = None, 
                        away_info: str = None, odds: Dict = None) -> Dict:
        """
        使用DeepSeek总结赛事信息
        
        Args:
            home_team: 主队名称
            away_team: 客队名称
            league: 联赛名称
            tavily_answer: Tavily搜索返回的摘要
            home_info: 主队信息
            away_info: 客队信息
            odds: 赔率信息
            
        Returns:
            Dict: 包含预测结果的字典
        """
        today = datetime.now().strftime('%Y年%m月%d日')
        
        system_prompt = f"""你是欧洲顶级足球数据分析师，拥有15年五大联赛分析经验，曾为威廉希尔、立博等博彩巨头担任数据顾问。精通统计学、运动科学、战术分析，能够从多个维度深度解析比赛，提供机构级分析报告。

【重要约束】
当前日期：{today}
1. 只分析当前日期之后进行的比赛
2. 所有数据必须基于提供的搜索结果，不得编造
3. 如果搜索结果中没有明确数据，使用"暂无数据"标注
4. 伤病信息必须基于搜索结果，不得臆测
5. 预测必须基于客观数据，避免主观臆断

分析要求：
• 内容深度：每次分析涵盖核心维度
• 数据支撑：每个观点必须有具体数据支撑，引用来源
• 专业术语：使用Opta、Wyscout等专业数据指标
• 投注价值：明确给出投注建议
• 信息准确性：标注数据来源和时间

分析框架：
1. 阵容完整度分析：主力球员状态、伤病影响、替补深度
2. 战术体系分析：阵型克制、风格对比、关键对位
3. 技术统计分析：xG/xA数据、进攻效率、防守质量
4. 近期状态分析：战绩走势、进球趋势、状态评分
5. 主客场差异：主场优势、客场表现、球迷影响
6. 历史交锋：过往战绩、战术演进、关键球员表现
7. 战意背景：联赛形势、后续赛程、财务影响
8. 赔率价值：赔率变动、凯利指数、市场偏差
9. 预测模型：泊松分布、Elo评级、蒙特卡洛模拟
10. 风险管理：止损策略、VAR风险、备选方案"""

        user_prompt = f"""请对以下足球比赛进行专业分析（基于搜索结果，确保信息准确）：

## 比赛信息
- 联赛：{league}
- 主队：{home_team}
- 客队：{away_team}
- 分析日期：{today}

## 搜索资讯摘要（数据来源：Tavily实时搜索）
{tavily_answer}

"""
        if home_info:
            user_prompt += f"## 主队{home_team}动态（数据来源：Tavily搜索）\n{home_info}\n\n"
        if away_info:
            user_prompt += f"## 客队{away_team}动态（数据来源：Tavily搜索）\n{away_info}\n\n"
        
        user_prompt += """
【输出要求】
请严格按照以下JSON格式输出分析结果（不要输出其他内容，只输出JSON）：

{
    "prediction": "主胜/平局/客胜",
    "confidence": 75,
    "reasons": [
        "【阵容分析】xxx（数据来源：xxx）",
        "【战术对比】xxx（数据来源：xxx）",
        "【近期状态】xxx（数据来源：xxx）",
        "【主客差异】xxx（数据来源：xxx）",
        "【历史交锋】xxx（数据来源：xxx）"
    ],
    "score_prediction": "2-1",
    "key_points": {
        "home_advantage": "主场优势分析（含数据来源）",
        "form_comparison": "双方状态对比（含数据来源）",
        "injury_impact": "伤病影响分析（含数据来源）",
        "tactical_analysis": "战术分析（含数据来源）"
    },
    "betting_advice": {
        "recommendation": "主胜/让球胜",
        "kelly_index": 0.15,
        "risk_level": "中低"
    },
    "data_sources": ["来源1", "来源2"],
    "analysis_time": "分析时间"
}

注意：
1. prediction 只能是：主胜、平局、客胜 三选一
2. confidence 是0-100的整数，表示预测置信度
3. reasons 数组包含5个分析理由，每个理由需标注数据来源
4. score_prediction 是预测比分，格式为"主队进球-客队进球"，例如：
   - 主胜预测：2-1（主队2球，客队1球）
   - 平局预测：1-1
   - 客胜预测：1-2（主队1球，客队2球）
5. key_points 包含关键分析要点，需标注数据来源
6. betting_advice 包含投注建议
7. data_sources 列出所有数据来源
8. 如果搜索结果中没有相关数据，必须标注"暂无数据"
"""
        try:
            logger.info(f"开始DeepSeek赛事分析, 比赛: {home_team} vs {away_team}")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            result = self._call_api(messages, max_tokens=1500)
            logger.info(f"DeepSeek赛事分析完成")
            
            import json
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    analysis = json.loads(json_str)
                else:
                    analysis = self._parse_text_result(result)
            except:
                analysis = self._parse_text_result(result)
            
            analysis['raw_content'] = result
            analysis['analysis_time'] = today
            return analysis
        except Exception as e:
            logger.error(f"DeepSeek分析失败: {e}")
            return {
                'prediction': '待分析',
                'confidence': 0,
                'reasons': [tavily_answer[:200] if tavily_answer else '暂无分析'],
                'score_prediction': '-',
                'key_points': {},
                'betting_advice': {},
                'data_sources': ['Tavily搜索'],
                'raw_content': tavily_answer,
                'analysis_time': today
            }
    
    def _parse_text_result(self, text: str) -> Dict:
        """
        解析文本结果为字典格式
        
        Args:
            text: 文本内容
            
        Returns:
            Dict: 解析后的字典
        """
        today = datetime.now().strftime('%Y年%m月%d日')
        return {
            'prediction': '待分析',
            'confidence': 50,
            'reasons': [text[:300] if text else '暂无分析'],
            'score_prediction': '-',
            'key_points': {},
            'betting_advice': {},
            'data_sources': [],
            'analysis_time': today
        }
    
    def summarize_team(self, team_name: str, tavily_answer: str) -> str:
        """
        使用DeepSeek总结球队动态
        
        Args:
            team_name: 球队名称
            tavily_answer: Tavily搜索返回的摘要
            
        Returns:
            str: 总结后的球队动态
        """
        today = datetime.now().strftime('%Y年%m月%d日')
        prompt = f"""请用中文总结{team_name}的最新动态（分析日期：{today}），要求简洁清晰，控制在100字以内：

{tavily_answer}

请重点关注：近期战绩、伤病情况、阵容变化。
注意：只使用搜索结果中的信息，不要编造数据。"""
        
        try:
            logger.info(f"开始DeepSeek球队总结, 球队: {team_name}")
            messages = [
                {"role": "system", "content": "你是一位专业的足球分析师，擅长用简洁清晰的中文总结球队信息。必须基于提供的数据进行分析，不得编造信息。"},
                {"role": "user", "content": prompt}
            ]
            result = self._call_api(messages, max_tokens=300)
            logger.info(f"DeepSeek球队总结完成")
            return result
        except Exception as e:
            logger.error(f"DeepSeek总结球队失败: {e}")
            return tavily_answer
