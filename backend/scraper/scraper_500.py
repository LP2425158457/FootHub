import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import re


class Scraper500:
    """
    500彩票网竞彩足球数据爬取类
    用于获取竞彩足球赛事信息和赔率数据
    """
    
    BASE_URL = "https://trade.500.com/jczq/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def get_match_list(self) -> List[Dict]:
        """
        获取竞彩足球赛事列表
        
        Returns:
            List[Dict]: 赛事列表，包含赛事基本信息和赔率数据
        """
        try:
            response = self.session.get(self.BASE_URL, timeout=15)
            response.encoding = 'gb2312'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            matches = []
            match_rows = soup.select('tr.bet-tb-tr')
            
            for row in match_rows:
                match_data = self._parse_match_row(row)
                if match_data:
                    matches.append(match_data)
            
            return matches
        except Exception as e:
            print(f"获取赛事列表失败: {e}")
            return []
    
    def _parse_match_row(self, row) -> Optional[Dict]:
        """
        解析单场赛事数据
        
        Args:
            row: BeautifulSoup元素对象，代表一行赛事数据
            
        Returns:
            Optional[Dict]: 解析后的赛事数据字典，解析失败返回None
        """
        try:
            match_id = row.get('data-fixtureid', '')
            if not match_id:
                return None
            
            match_num = row.get('data-matchnum', '')
            league = row.get('data-simpleleague', '')
            home_team = row.get('data-homesxname', '')
            away_team = row.get('data-awaysxname', '')
            match_date = row.get('data-matchdate', '')
            match_time = row.get('data-matchtime', '')
            rangqiu = row.get('data-rangqiu', '0')
            buy_end_time = row.get('data-buyendtime', '')
            
            odds = self._parse_odds(row)
            
            rangqiu_display = self._get_rangqiu_display(row)
            
            return {
                'match_id': match_id,
                'match_num': match_num,
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'match_date': match_date,
                'match_time': match_time,
                'match_datetime': f"{match_date} {match_time}" if match_date and match_time else '',
                'rangqiu': rangqiu,
                'rangqiu_display': rangqiu_display,
                'buy_end_time': buy_end_time,
                'odds': odds,
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"解析赛事数据失败: {e}")
            return None
    
    def _get_rangqiu_display(self, row) -> str:
        """
        获取让球显示文本
        
        Args:
            row: BeautifulSoup元素对象
            
        Returns:
            str: 让球显示文本
        """
        rang_elem = row.select_one('.itm-rangA1')
        if rang_elem:
            text = rang_elem.get_text(strip=True)
            return text
        return '0'
    
    def _parse_odds(self, row) -> Dict:
        """
        解析赔率数据
        
        Args:
            row: BeautifulSoup元素对象
            
        Returns:
            Dict: 赔率数据字典，包含让球和不 let球胜平负赔率
        """
        odds = {
            'nspf': {},  # 不让球胜平负
            'spf': {}    # 让球胜平负
        }
        
        try:
            betbtns = row.select('p.betbtn')
            for btn in betbtns:
                odds_type = btn.get('data-type', '')
                odds_value = btn.get('data-value', '')
                odds_sp = btn.get('data-sp', '')
                
                if odds_type and odds_value and odds_sp:
                    if odds_type not in odds:
                        odds[odds_type] = {}
                    
                    value_map = {'3': '胜', '1': '平', '0': '负'}
                    label = value_map.get(odds_value, odds_value)
                    odds[odds_type][label] = {
                        'value': odds_value,
                        'sp': odds_sp
                    }
            
            rangqiu = row.get('data-rangqiu', '0')
            if rangqiu != '0':
                odds['rangqiu_info'] = f"主队让{rangqiu}球" if int(rangqiu) > 0 else f"主队受{abs(int(rangqiu))}球"
            else:
                odds['rangqiu_info'] = "不让球"
                
        except Exception as e:
            print(f"解析赔率失败: {e}")
        
        return odds
    
    def get_bjdc_data(self) -> Dict:
        """
        获取竞彩足球完整数据
        
        Returns:
            Dict: 包含所有竞彩足球赛事数据的字典
        """
        matches = self.get_match_list()
        
        return {
            'source': '500彩票网-竞彩足球',
            'url': self.BASE_URL,
            'total_matches': len(matches),
            'matches': matches,
            'updated_at': datetime.now().isoformat()
        }


if __name__ == '__main__':
    scraper = Scraper500()
    data = scraper.get_bjdc_data()
    print(f"获取到 {data['total_matches']} 场赛事")
    for match in data['matches'][:5]:
        print(f"\n{match['match_num']} {match['league']}")
        print(f"  {match['home_team']} vs {match['away_team']}")
        print(f"  时间: {match['match_datetime']}")
        print(f"  让球: {match['rangqiu_display']} ({match['rangqiu']})")
        print(f"  不让球赔率: 胜{match['odds'].get('nspf', {}).get('胜', {}).get('sp', '-')} "
              f"平{match['odds'].get('nspf', {}).get('平', {}).get('sp', '-')} "
              f"负{match['odds'].get('nspf', {}).get('负', {}).get('sp', '-')}")
        print(f"  让球赔率: 胜{match['odds'].get('spf', {}).get('胜', {}).get('sp', '-')} "
              f"平{match['odds'].get('spf', {}).get('平', {}).get('sp', '-')} "
              f"负{match['odds'].get('spf', {}).get('负', {}).get('sp', '-')}")
