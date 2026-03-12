from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper.scraper_500 import Scraper500
from services.tavily_service import TavilyService
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

scraper = Scraper500()

try:
    tavily_service = TavilyService()
except ValueError as e:
    print(f"警告: {e}")
    tavily_service = None


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
    try:
        data = scraper.get_bjdc_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
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
    if not tavily_service:
        return jsonify({
            'success': False,
            'error': 'Tavily API未配置，请设置TAVILY_API_KEY环境变量'
        }), 500
    
    try:
        matches = scraper.get_match_list()
        match = next((m for m in matches if m['match_id'] == match_id), None)
        
        if not match:
            return jsonify({
                'success': False,
                'error': '未找到该赛事'
            }), 404
        
        print(f"正在搜索赛事资讯: {match['home_team']} vs {match['away_team']}")
        
        match_news = tavily_service.search_match_news(
            match['home_team'],
            match['away_team'],
            match['league']
        )
        
        print(f"正在搜索主队信息: {match['home_team']}")
        home_info = tavily_service.search_team_info(match['home_team'])
        
        print(f"正在搜索客队信息: {match['away_team']}")
        away_info = tavily_service.search_team_info(match['away_team'])
        
        return jsonify({
            'success': True,
            'data': {
                'match': match,
                'summary': match_news.get('answer', ''),
                'news': match_news.get('results', []),
                'home_team_info': {
                    'team_name': match['home_team'],
                    'info': home_info.get('answer', ''),
                    'news': home_info.get('results', [])[:3]
                },
                'away_team_info': {
                    'team_name': match['away_team'],
                    'info': away_info.get('answer', ''),
                    'news': away_info.get('results', [])[:3]
                }
            }
        })
    except Exception as e:
        print(f"获取赛事资讯失败: {e}")
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
    if not tavily_service:
        return jsonify({
            'success': False,
            'error': 'Tavily API未配置，请设置TAVILY_API_KEY环境变量'
        }), 500
    
    try:
        info = tavily_service.search_team_info(team_name)
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
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
    if not tavily_service:
        return jsonify({
            'success': False,
            'error': 'Tavily API未配置，请设置TAVILY_API_KEY环境变量'
        }), 500
    
    try:
        news = tavily_service.search_league_news(league_name)
        return jsonify({
            'success': True,
            'data': news
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
