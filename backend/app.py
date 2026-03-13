from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper.scraper_500 import Scraper500
from services.tavily_service import TavilyService
from services.deepseek_service import DeepSeekService
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

scraper = Scraper500()

try:
    tavily_service = TavilyService()
    logger.info("Tavily服务初始化成功")
except ValueError as e:
    logger.warning(f"Tavily服务初始化失败: {e}")
    tavily_service = None

try:
    deepseek_service = DeepSeekService()
    logger.info("DeepSeek服务初始化成功")
except ValueError as e:
    logger.warning(f"DeepSeek服务初始化失败: {e}")
    deepseek_service = None


@app.route('/')
def index():
    """
    API首页路由
    
    Returns:
        JSON响应，包含API状态信息
    """
    return jsonify({
        'status': 'running',
        'message': '竞彩足球资讯API服务',
        'endpoints': {
            '/api/matches': '获取赛事列表',
            '/api/match/<match_id>/news': '获取赛事资讯',
            '/api/team/<team_name>/info': '获取球队信息'
        }
    })


@app.route('/api/matches', methods=['GET'])
def get_matches():
    """
    获取竞彩足球赛事列表
    
    Returns:
        JSON响应，包含赛事列表数据
    """
    logger.info("获取赛事列表请求")
    try:
        data = scraper.get_bjdc_data()
        logger.info(f"成功获取赛事列表, 共 {data.get('total_matches', 0)} 场比赛")
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"获取赛事列表失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/match/<match_id>/news', methods=['GET'])
def get_match_news(match_id):
    """
    获取特定赛事的资讯信息
    
    Args:
        match_id: 赛事ID
        
    Returns:
        JSON响应，包含赛事资讯数据
    """
    logger.info(f"获取赛事资讯请求, match_id: {match_id}")
    
    if not tavily_service:
        logger.error("Tavily API未配置")
        return jsonify({
            'success': False,
            'error': 'Tavily API未配置，请设置TAVILY_API_KEY环境变量'
        }), 500
    
    try:
        matches = scraper.get_match_list()
        match = next((m for m in matches if m['match_id'] == match_id), None)
        
        if not match:
            logger.warning(f"未找到赛事: {match_id}")
            return jsonify({
                'success': False,
                'error': '未找到该赛事'
            }), 404
        
        logger.info(f"找到赛事: {match['home_team']} vs {match['away_team']}, 联赛: {match['league']}")
        
        logger.info("开始Tavily搜索赛事资讯...")
        match_news = tavily_service.search_match_news(
            match['home_team'],
            match['away_team'],
            match['league']
        )
        logger.info(f"Tavily赛事搜索完成, 结果数: {len(match_news.get('results', []))}")
        
        logger.info(f"开始Tavily搜索主队信息: {match['home_team']}")
        home_info = tavily_service.search_team_info(match['home_team'])
        logger.info(f"主队信息搜索完成")
        
        logger.info(f"开始Tavily搜索客队信息: {match['away_team']}")
        away_info = tavily_service.search_team_info(match['away_team'])
        logger.info(f"客队信息搜索完成")
        
        tavily_answer = match_news.get('answer', '')
        home_answer = home_info.get('answer', '')
        away_answer = away_info.get('answer', '')
        
        if deepseek_service:
            logger.info("开始DeepSeek总结赛事摘要...")
            summary = deepseek_service.summarize_match(
                match['home_team'],
                match['away_team'],
                match['league'],
                tavily_answer,
                home_answer,
                away_answer,
                match.get('odds')
            )
            logger.info("DeepSeek赛事摘要完成")
            
            logger.info(f"开始DeepSeek总结主队动态: {match['home_team']}")
            home_summary = deepseek_service.summarize_team(match['home_team'], home_answer)
            logger.info("主队动态总结完成")
            
            logger.info(f"开始DeepSeek总结客队动态: {match['away_team']}")
            away_summary = deepseek_service.summarize_team(match['away_team'], away_answer)
            logger.info("客队动态总结完成")
        else:
            logger.warning("DeepSeek服务不可用, 使用原始Tavily结果")
            summary = tavily_answer
            home_summary = home_answer
            away_summary = away_answer
        
        logger.info(f"赛事资讯获取完成, match_id: {match_id}")
        return jsonify({
            'success': True,
            'data': {
                'match': match,
                'summary': summary,
                'news': match_news.get('results', []),
                'home_team_info': {
                    'team_name': match['home_team'],
                    'info': home_summary,
                    'news': home_info.get('results', [])[:3]
                },
                'away_team_info': {
                    'team_name': match['away_team'],
                    'info': away_summary,
                    'news': away_info.get('results', [])[:3]
                }
            }
        })
    except Exception as e:
        logger.error(f"获取赛事资讯失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/team/<team_name>/info', methods=['GET'])
def get_team_info(team_name):
    """
    获取球队信息
    
    Args:
        team_name: 球队名称
        
    Returns:
        JSON响应，包含球队信息数据
    """
    logger.info(f"获取球队信息请求, team_name: {team_name}")
    
    if not tavily_service:
        logger.error("Tavily API未配置")
        return jsonify({
            'success': False,
            'error': 'Tavily API未配置，请设置TAVILY_API_KEY环境变量'
        }), 500
    
    try:
        info = tavily_service.search_team_info(team_name)
        logger.info(f"球队信息获取完成: {team_name}")
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"获取球队信息失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/league/<league_name>/news', methods=['GET'])
def get_league_news(league_name):
    """
    获取联赛新闻
    
    Args:
        league_name: 联赛名称
        
    Returns:
        JSON响应，包含联赛新闻数据
    """
    logger.info(f"获取联赛新闻请求, league_name: {league_name}")
    
    if not tavily_service:
        logger.error("Tavily API未配置")
        return jsonify({
            'success': False,
            'error': 'Tavily API未配置，请设置TAVILY_API_KEY环境变量'
        }), 500
    
    try:
        news = tavily_service.search_league_news(league_name)
        logger.info(f"联赛新闻获取完成: {league_name}")
        return jsonify({
            'success': True,
            'data': news
        })
    except Exception as e:
        logger.error(f"获取联赛新闻失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("启动Flask应用...")
    app.run(debug=True, host='0.0.0.0', port=5001)
