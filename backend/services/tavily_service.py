import os
from typing import List, Dict, Optional
from tavily import TavilyClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
        logger.info("Tavily服务初始化成功")
    
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
                    'score': score,
                    'published_date': r.get('published_date', '')
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
        today = datetime.now().strftime('%Y-%m-%d')
        today_cn = datetime.now().strftime('%Y年%m月%d日')
        
        query = f"{home_team} vs {away_team}"
        if league:
            query = f"{league} {query}"
        query += f" 最新 {today} {today_cn} 阵容分析 伤病情况 赛前预测"
        
        try:
            logger.info(f"Tavily搜索赛事资讯: {query}")
            response = self.client.search(
                query=query,
                include_answer="advanced",
                search_depth="advanced",
                max_results=10,
                include_raw_content=False,
                days=3
            )
            
            results = self._filter_results(response.get('results', []), min_score=0.6)
            logger.info(f"Tavily搜索完成, 获取 {len(results)} 条结果")
            
            return {
                'query': query,
                'answer': response.get('answer', ''),
                'results': results,
                'search_time': today,
                'match_info': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league
                }
            }
        except Exception as e:
            logger.error(f"搜索赛事资讯失败: {e}")
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
        today = datetime.now().strftime('%Y-%m-%d')
        today_cn = datetime.now().strftime('%Y年%m月%d日')
        query = f"{team_name} 足球队 最新动态 阵容 伤病 状态 {today} {today_cn}"
        
        try:
            logger.info(f"Tavily搜索球队信息: {team_name}")
            response = self.client.search(
                query=query,
                include_answer="advanced",
                search_depth="advanced",
                max_results=5,
                days=3
            )
            
            results = self._filter_results(response.get('results', []), min_score=0.5)
            logger.info(f"球队信息搜索完成, 获取 {len(results)} 条结果")
            
            return {
                'team_name': team_name,
                'answer': response.get('answer', ''),
                'results': results,
                'search_time': today
            }
        except Exception as e:
            logger.error(f"搜索球队信息失败: {e}")
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
        today = datetime.now().strftime('%Y-%m-%d')
        today_cn = datetime.now().strftime('%Y年%m月%d日')
        query = f"{league_name} 最新新闻 赛程 积分榜 {today} {today_cn}"
        
        try:
            logger.info(f"Tavily搜索联赛新闻: {league_name}")
            response = self.client.search(
                query=query,
                include_answer="advanced",
                search_depth="advanced",
                max_results=5,
                days=3
            )
            
            results = self._filter_results(response.get('results', []), min_score=0.5)
            logger.info(f"联赛新闻搜索完成, 获取 {len(results)} 条结果")
            
            return {
                'league_name': league_name,
                'answer': response.get('answer', ''),
                'results': results,
                'search_time': today
            }
        except Exception as e:
            logger.error(f"搜索联赛新闻失败: {e}")
            return {
                'league_name': league_name,
                'answer': '',
                'results': [],
                'error': str(e)
            }
