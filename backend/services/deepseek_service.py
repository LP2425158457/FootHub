import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class DeepSeekService:
    """
    DeepSeek API服务类
    用于通过AI分析足球赛事信息
    """
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")
        
        print(f"DeepSeek API Key已加载: {self.api_key[:10]}...")
        print(f"DeepSeek Base URL: {self.base_url}")
    
    def _call_api(self, messages: List[Dict], max_tokens: int = 800) -> str:
        """
        调用DeepSeek API
        
        Args:
            messages: 消息列表
            max_tokens: 最大token数
            
        Returns:
            str: API响应内容
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            print(f"正在调用DeepSeek API: {url}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 401:
                error_detail = response.text
                print(f"DeepSeek API认证失败(401): {error_detail}")
                raise Exception(f"API Key无效或已过期，请检查您的DeepSeek API Key")
            
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            print(f"DeepSeek API HTTP错误: {e}")
            raise Exception(f"DeepSeek API调用失败: {e}")
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            raise e
    
    def analyze_match(self, home_team: str, away_team: str, league: str, 
                      search_results: List[Dict], home_info: Dict = None, 
                      away_info: Dict = None, odds: Dict = None) -> Dict:
        """
        分析赛事信息并生成中文分析报告
        
        Args:
            home_team: 主队名称
            away_team: 客队名称
            league: 联赛名称
            search_results: Tavily搜索结果列表
            home_info: 主队信息
            away_info: 客队信息
            odds: 赔率信息
            
        Returns:
            Dict: 包含分析结果的字典
        """
        context = self._build_context(home_team, away_team, league, 
                                       search_results, home_info, away_info, odds)
        
        prompt = f"""你是一位专业的足球分析师。请根据以下信息，用中文对这场比赛进行详细分析。

比赛信息：
- 联赛：{league}
- 主队：{home_team}
- 客队：{away_team}

相关资讯：
{context}

请从以下几个方面进行分析（用中文回答）：

1. **双方近期状态**：分析两队最近的比赛状态和表现
2. **历史交锋**：两队过往交手情况
3. **关键因素**：影响比赛结果的关键因素（伤病、主客场优势等）
4. **比赛预测**：基于以上分析给出比赛走势预测

请用简洁专业的中文进行分析，总字数控制在300-500字。"""

        try:
            messages = [
                {"role": "system", "content": "你是一位专业的足球分析师，擅长用中文进行赛事分析。你的分析客观、专业、简洁。"},
                {"role": "user", "content": prompt}
            ]
            
            analysis = self._call_api(messages)
            
            return {
                'success': True,
                'analysis': analysis,
                'home_team': home_team,
                'away_team': away_team,
                'league': league
            }
        except Exception as e:
            print(f"DeepSeek分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': f"AI分析暂时不可用，请稍后再试。错误信息：{str(e)}"
            }
    
    def _build_context(self, home_team: str, away_team: str, league: str,
                        search_results: List[Dict], home_info: Dict, 
                        away_info: Dict, odds: Dict) -> str:
        """
        构建上下文信息
        
        Args:
            home_team: 主队名称
            away_team: 客队名称
            league: 联赛名称
            search_results: 搜索结果
            home_info: 主队信息
            away_info: 客队信息
            odds: 赔率信息
            
        Returns:
            str: 构建的上下文字符串
        """
        context_parts = []
        
        if search_results:
            context_parts.append("【比赛相关新闻】")
            for i, result in enumerate(search_results[:3], 1):
                title = result.get('title', '')
                content = result.get('content', '')[:300] if result.get('content') else ''
                if title or content:
                    context_parts.append(f"{i}. {title}")
                    if content:
                        context_parts.append(f"   {content}...")
        
        if home_info and home_info.get('answer'):
            context_parts.append(f"\n【{home_team}动态】")
            context_parts.append(home_info['answer'][:200])
        
        if away_info and away_info.get('answer'):
            context_parts.append(f"\n【{away_team}动态】")
            context_parts.append(away_info['answer'][:200])
        
        if odds:
            context_parts.append("\n【赔率信息】")
            nspf = odds.get('nspf', {})
            spf = odds.get('spf', {})
            rangqiu_info = odds.get('rangqiu_info', '')
            
            if nspf:
                context_parts.append(f"不让球胜平负：胜{nspf.get('胜', {}).get('sp', '-')} "
                                    f"平{nspf.get('平', {}).get('sp', '-')} "
                                    f"负{nspf.get('负', {}).get('sp', '-')}")
            if spf and rangqiu_info:
                context_parts.append(f"{rangqiu_info}：胜{spf.get('胜', {}).get('sp', '-')} "
                                    f"平{spf.get('平', {}).get('sp', '-')} "
                                    f"负{spf.get('负', {}).get('sp', '-')}")
        
        return "\n".join(context_parts) if context_parts else "暂无相关资讯"
    
    def summarize_news(self, results: List[Dict]) -> List[Dict]:
        """
        整理新闻资讯，提取关键信息
        
        Args:
            results: 原始搜索结果列表
            
        Returns:
            List[Dict]: 整理后的新闻列表
        """
        summarized = []
        for result in results[:5]:
            item = {
                'title': result.get('title', '未知标题'),
                'url': result.get('url', ''),
                'summary': result.get('content', '')[:150] + '...' if result.get('content') else '',
                'source': self._extract_source(result.get('url', ''))
            }
            summarized.append(item)
        return summarized
    
    def _extract_source(self, url: str) -> str:
        """
        从URL提取来源网站名称
        
        Args:
            url: 网址
            
        Returns:
            str: 来源名称
        """
        if not url:
            return "未知来源"
        
        domain_map = {
            'sina.com.cn': '新浪体育',
            'qq.com': '腾讯体育',
            '163.com': '网易体育',
            'sohu.com': '搜狐体育',
            'dongqiudi.com': '懂球帝',
            'zhibo8.cc': '直播吧',
            '500.com': '500彩票网',
            'leisu.com': '雷速体育',
            'bbc.co.uk': 'BBC体育',
            'espn.com': 'ESPN',
            'skysports.com': '天空体育',
            'goal.com': 'Goal.com'
        }
        
        for domain, name in domain_map.items():
            if domain in url:
                return name
        
        return "网络来源"


if __name__ == '__main__':
    service = DeepSeekService()
    result = service.analyze_match(
        "曼联", "曼城", "英超",
        [{"title": "曼联近期状态出色", "content": "曼联在最近5场比赛中取得4胜1平的成绩..."}],
        {"answer": "曼联主力前锋伤愈复出"},
        {"answer": "曼城中场核心因伤缺阵"}
    )
    print(result.get('analysis', '分析失败'))
