import os
from typing import List, Dict, Optional
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


class TavilyService:
    """
    Tavily API服务类
    用于获取足球赛事相关的新闻资讯
    """
    
    def __init__(self):
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            raise ValueError("请设置TAVILY_API_KEY环境变量")
        self.client = TavilyClient(api_key=api_key)
    
    def _filter_results(self, results: List[Dict], min_score: float = 0.7) -> List[Dict]:
        """
        过滤精选结果
        
        Args:
            results: 原始结果列表
            min_score: 最低分数阈值
            
        Returns:
            List[Dict]: 过滤后的精选结果
        """
        filtered = []
        for r in results:
            score = r.get('score', 0)
            if score >= min_score:
                filtered.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'content': r.get('content', '')[:500] if r.get('content') else '',
                    'score': score
                })
        return filtered[:5]
    
    def search_match_news(self, home_team: str, away_team: str, league: str = "") -> Dict:
        """
        搜索特定赛事的新闻资讯
        
        Args:
            home_team: 主队名称
            away_team: 客队名称
            league: 联赛名称
            
        Returns:
            Dict: 包含搜索结果的字典
        """
        query = f"{home_team} vs {away_team}"
        if league:
            query = f"{league} {query}"
        query += " 最新 阵容分析 Opta Wyscout Transfermarkt 官方联赛数据 足球比赛分析预测"
        
        try:
            response = self.client.search(
                query=query,
                include_answer="advanced",
                search_depth="advanced",
                max_results=10
            )
            
            results = self._filter_results(response.get('results', []), min_score=0.6)
            
            return {
                'query': query,
                'answer': response.get('answer', ''),
                'results': results,
                'match_info': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league
                }
            }
        except Exception as e:
            print(f"搜索赛事资讯失败: {e}")
            return {
                'query': query,
                'answer': '',
                'results': [],
                'error': str(e)
            }
    
    def search_team_info(self, team_name: str) -> Dict:
        """
        搜索球队信息
        
        Args:
            team_name: 球队名称
            
        Returns:
            Dict: 包含球队信息的字典
        """
        query = f"{team_name} 足球队 最新动态 阵容 伤病 状态"
        
        try:
            response = self.client.search(
                query=query,
                include_answer="advanced",
                search_depth="advanced",
                max_results=5
            )
            
            results = self._filter_results(response.get('results', []), min_score=0.5)
            
            return {
                'team_name': team_name,
                'answer': response.get('answer', ''),
                'results': results
            }
        except Exception as e:
            print(f"搜索球队信息失败: {e}")
            return {
                'team_name': team_name,
                'answer': '',
                'results': [],
                'error': str(e)
            }
    
    def search_league_news(self, league_name: str) -> Dict:
        """
        搜索联赛新闻
        
        Args:
            league_name: 联赛名称
            
        Returns:
            Dict: 包含联赛新闻的字典
        """
        query = f"{league_name} 最新新闻 赛程 积分榜"
        
        try:
            response = self.client.search(
                query=query,
                include_answer="advanced",
                search_depth="advanced",
                max_results=5
            )
            
            results = self._filter_results(response.get('results', []), min_score=0.5)
            
            return {
                'league_name': league_name,
                'answer': response.get('answer', ''),
                'results': results
            }
        except Exception as e:
            print(f"搜索联赛新闻失败: {e}")
            return {
                'league_name': league_name,
                'answer': '',
                'results': [],
                'error': str(e)
            }
