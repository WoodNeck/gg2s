# -*- coding: utf-8 -*-

import os
import webapp2
import logging
import datetime
import json
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.datastore.datastore_query import Cursor

from random import randint
from random import choice

#NOT version of website!
#This is a version of plug-in
version = 'v1.5.0'

#현재 시즌
GG2S_CURRENT_SEASON = 4

_CLASSES = ["Runner", "Firebug", "Rocketman", "Overweight", "Detonator", "Healer", "Constructor", "Infiltrator", "Rifleman", "Quote"]

BAN_LIST = ["httpslashoff",
			"olivertosic21",
			"momongki123",
			"saiyu915"]

#일퀘, index=퀘스트 타입, 0: 퀘스트 이름, 1:퀘스트 설명, 2: 퀘스트 목표 카운트, 3: 퀘스트 보상액, 4: 퀘스트 종류(포괄), 5: 퀘스트 종류(세부)
#4: OVERALL_STAT, OVERALL_PLAYTIME, CLASS_KILL, CLASS_DEATH, CLASS_ASSIST, CLASS_PLAYTIME, WIN_TYPE
#5:
#OVERALL_STAT
#[0: KILL, 1: DEATH, 2: ASSIST, 3: CAP, 4: DESTORY, 5: STAB, 6: HEAL, 7:DEFENSE, 8: INVULN]
#OVERALL_PLAYTIME
#[0: TOTAL, 1: TEAM_RED, 2: TEAM_BLUE, 3: TEAM_SPECTATOR]
#CLASS_ORDER
#[0: SCOUT, 1: SOLDIER, 2: SNIPER, 3:DEMOMAN, 4: MEDIC, 5: ENGINEER, 6: HEAVY, 7: SPY, 8: PYRO, 9: QUOTE]
#WIN_TYPE
#[0: WIN, 1: LOSE, 2: STALEMATE, 3: DISCONNECT]
_QUESTS = [["Domination", "Kill 50 enemies", 50, 30, 0, 0],
					["Hua Tuo", "Heal 10000 points", 10000, 30, 0, 6],
					["Charge!", 'Kill 30 enemies with Firebug or Quote', 30, 30, 2, [8, 9]],
					["WHAAM!", 'Kill 30 enemies with Rocketman or Detonator', 30, 30, 2, [1, 3]],
					["Bad Company", 'Kill 30 enemies with Infiltrator or Rifleman', 30, 30, 2, [7, 2]],
					["Stay Close", 'Kill 30 enemies with Firebug or Overweight', 30, 30, 2, [8, 6]],
					["Happy Camping", 'Kill 30 enemies with Constructor or Rifleman', 30, 30, 2, [5, 2]],
					["Intel Carriers", 'Kill 30 enemies with Runner or Infiltrator', 30, 30, 2, [0, 7]],
					["Creator, Destroyer", 'Kill 30 enemies with Detonator or Constructor', 30, 30, 2, [3, 5]],
					["Giant & Tiny", 'Kill 30 enemies with Overweight or Quote', 30, 30, 2, [6, 9]],
					["Airbornes", 'Kill 30 enemies with Runner or Rocketman', 30, 30, 2, [0, 1]],
					["Runner Beginner", "Play 15 minutes as Runner", 27000, 40, 5, 0],
					["Firebug Beginner", "Play 15 minutes as Firebug", 27000, 40, 5, 8],
					["Rocketman Beginner", "Play 15 minutes as Rocketman", 27000, 40, 5, 1],
					["Overweight Beginner", "Play 15 minutes as Overweight", 27000, 40, 5, 6],
					["Detonator Beginner", "Play 15 minutes as Detonator", 27000, 40, 5, 3],
					["Healer Beginner", "Play 15 minutes as Healer", 27000, 40, 5, 4],
					["Constructor Beginner", "Play 15 minutes as Constructor", 27000, 40, 5, 5],
					["Infiltrator Beginner", "Play 15 minutes as Infiltrator", 27000, 40, 5, 7],
					["Rifleman Beginner", "Play 15 minutes as Rifleman", 27000, 40, 5, 2],
					["Quote Beginner", "Play 15 minutes as Quote", 27000, 40, 5, 9],
					["!", "Kill 10 enemies with Backstab", 10, 30, 0, 5],
					["Bullefproof!", "Use invuln 5 times", 5, 30, 0, 8],
					["3 Victories!", "Win 3 games", 3, 30, 6, 0],
					["His crop, My points", 'Destroy 5 autoguns', 5, 30, 0, 4],
					["Runner Master", "Play 30 minutes as Runner", 54000, 60, 5, 0],
					["Firebug Master", "Play 30 minutes as Firebug", 54000, 60, 5, 8],
					["Rocketman Master", "Play 30 minutes as Rocketman", 54000, 60, 5, 1],
					["Overweight Master", "Play 30 minutes as Overweight", 54000, 60, 5, 6],
					["Detonator Master", "Play 30 minutes as Detonator", 54000, 60, 5, 3],
					["Healer Master", "Play 30 minutes as Healer", 54000, 60, 5, 4],
					["Constructor Master", "Play 30 minutes as Constructor", 54000, 60, 5, 5],
					["Infiltrator Master", "Play 30 minutes as Infiltrator", 54000, 60, 5, 7],
					["Rifleman Master", "Play 30 minutes as Rifleman", 54000, 60, 5, 2],
					["Quote Master", "Play 30 minutes as Quote", 54000, 60, 5, 9],
					["Garrison Gang", "Play for 3 hours", 324000, 100, 1, 0]
				   ]

#User property class
class UserEntity(ndb.Model):
	user_id = ndb.StringProperty()
	user_clan = ndb.StringProperty(default='', indexed=False)
	user_word = ndb.StringProperty(default='', indexed=False)
	user_favclass = ndb.StringProperty(default='Runner')
	user_region = ndb.StringProperty(default='', indexed=False)
	user_message = ndb.StringProperty(default='Hi', indexed=False)
	user_title = ndb.StringProperty(default='', indexed=False)
	user_avatar = ndb.BlobProperty(indexed=False)
	user_coin = ndb.IntegerProperty(default=0, indexed=False)
	user_level = ndb.IntegerProperty(default=1)
	user_exp = ndb.IntegerProperty(default=0, indexed=False)
	google_id = ndb.UserProperty()

#User's Stat Entity
class UserStatEntity(ndb.Model):
	user_point = ndb.IntegerProperty(default=1000)
	user_kill = ndb.IntegerProperty(default=0)
	user_death = ndb.IntegerProperty(default=0)
	user_assist = ndb.IntegerProperty(default=0)
	user_cap = ndb.IntegerProperty(default=0, indexed=False)
	user_destruction = ndb.IntegerProperty(default=0, indexed=False)
	user_stab = ndb.IntegerProperty(default=0, indexed=False)
	user_healing = ndb.FloatProperty(default=0.0, indexed=False)
	user_defense = ndb.IntegerProperty(default=0, indexed=False)
	user_invuln = ndb.IntegerProperty(default=0, indexed=False)
	user_kda = ndb.FloatProperty(default=0.0)
	user_playcount = ndb.IntegerProperty(default=0)
	user_playtime = ndb.IntegerProperty(default=0)
	user_redtime = ndb.IntegerProperty(default=0, indexed=False)
	user_bluetime = ndb.IntegerProperty(default=0, indexed=False)
	user_spectime = ndb.IntegerProperty(default=0, indexed=False)
	user_win = ndb.IntegerProperty(default=0, indexed=False)
	user_lose = ndb.IntegerProperty(default=0, indexed=False)
	user_stalemate = ndb.IntegerProperty(default=0, indexed=False)
	user_escape = ndb.IntegerProperty(default=0, indexed=False)

#Season Stat Entity
class SeasonStatEntity(ndb.Model):
	season = ndb.IntegerProperty()
	season_owner = ndb.IntegerProperty()
	user_point = ndb.IntegerProperty(default=1000)
	user_kill = ndb.IntegerProperty(default=0)
	user_death = ndb.IntegerProperty(default=0)
	user_assist = ndb.IntegerProperty(default=0)
	user_cap = ndb.IntegerProperty(default=0, indexed=False)
	user_destruction = ndb.IntegerProperty(default=0, indexed=False)
	user_stab = ndb.IntegerProperty(default=0, indexed=False)
	user_healing = ndb.FloatProperty(default=0.0, indexed=False)
	user_defense = ndb.IntegerProperty(default=0, indexed=False)
	user_invuln = ndb.IntegerProperty(default=0, indexed=False)
	user_kda = ndb.FloatProperty(default=0.0)
	user_playcount = ndb.IntegerProperty(default=0)
	user_playtime = ndb.IntegerProperty(default=0)
	user_redtime = ndb.IntegerProperty(default=0, indexed=False)
	user_bluetime = ndb.IntegerProperty(default=0, indexed=False)
	user_spectime = ndb.IntegerProperty(default=0, indexed=False)
	user_win = ndb.IntegerProperty(default=0, indexed=False)
	user_lose = ndb.IntegerProperty(default=0, indexed=False)
	user_stalemate = ndb.IntegerProperty(default=0, indexed=False)
	user_escape = ndb.IntegerProperty(default=0, indexed=False)
	class_kill = ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	class_death = ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	class_assist = ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	class_playtime = ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)

#Today's user property class
class TodayEntity(ndb.Model):
	user_kill = ndb.IntegerProperty(default=0, indexed=False)
	user_death = ndb.IntegerProperty(default=0, indexed=False)
	user_assist = ndb.IntegerProperty(default=0, indexed=False)
	user_cap = ndb.IntegerProperty(default=0, indexed=False)
	user_destruction = ndb.IntegerProperty(default=0, indexed=False)
	user_stab = ndb.IntegerProperty(default=0, indexed=False)
	user_healing = ndb.FloatProperty(default=0.0, indexed=False)
	user_defense = ndb.IntegerProperty(default=0, indexed=False)
	user_invuln = ndb.IntegerProperty(default=0, indexed=False)
	user_kda = ndb.FloatProperty(default=0.0, indexed=False)
	user_playcount = ndb.IntegerProperty(default=0, indexed=False)
	user_point = ndb.IntegerProperty(default=0)

#각 병과별 스탯 통합 Entity
class ClassEntity(ndb.Model):
	kill = ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	death=ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	assist=ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	playtime=ndb.StringProperty(default='0,0,0,0,0,0,0,0,0,0', indexed=False)
	
#짧은 로그용 스탯 엔티티
class MatchEntity(ndb.Model):
	match_result = ndb.IntegerProperty(indexed=False)
	match_kill = ndb.IntegerProperty(default=0, indexed=False)
	match_death = ndb.IntegerProperty(default=0, indexed=False)
	match_assist = ndb.IntegerProperty(default=0, indexed=False)
	match_playtime = ndb.IntegerProperty(default=0, indexed=False)
	match_server = ndb.StringProperty(default='', indexed=False)
	match_mode = ndb.StringProperty(default='', indexed=False)
	match_map = ndb.StringProperty(default='', indexed=False)
	match_datetime = ndb.DateTimeProperty(auto_now_add=True)
	match_redteam = ndb.StringProperty(default='', indexed=False)
	match_blueteam = ndb.StringProperty(default='', indexed=False)
	match_myself = ndb.IntegerProperty(default=-1, indexed=False)
	match_score = ndb.StringProperty(default='', indexed=False) #레드:블루 성적
	match_owner = ndb.IntegerProperty()

#아이템 정보 참조용 DB Entity, 아이템의 이름이 Key
class ItemEntity(ndb.Model):
	item_nickname = ndb.StringProperty(indexed=False)
	item_author = ndb.StringProperty(indexed=False)
	item_desc = ndb.StringProperty(default='', indexed=False)
	item_part = ndb.IntegerProperty()
	item_classlist = ndb.StringProperty(indexed=False) #리스트를 스트링의 형태로 형변환
	can_get = ndb.BooleanProperty(default=True)
	is_vintage = ndb.BooleanProperty(default=False)
	
#실제 플레이어의 백팩 정보
class BackpackEntity(ndb.Model):
	item_name = ndb.StringProperty(indexed=False) #ItemEntity Key 참조용
	item_owner = ndb.IntegerProperty()
	item_rarity = ndb.IntegerProperty(default=0, indexed=False) #아이템의 레어도 0 = normal, 1 = strange, 2 = unusual...
	item_part = ndb.IntegerProperty()
	item_effect = ndb.IntegerProperty(indexed=False)
	item_strangeType = ndb.IntegerProperty(indexed=False)
	item_strangeCount = ndb.IntegerProperty(default=0, indexed=False)
	item_level = ndb.IntegerProperty(default=1, indexed=False)
	item_getdate = ndb.DateTimeProperty(auto_now_add=True)
	is_trading = ndb.BooleanProperty(default=False, indexed=False)

#플레이어의 로드아웃 정보 저장	
class LoadoutEntity(ndb.Model):
	head_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	torso_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	leg_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	weapon_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	misc_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	taunt_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	pet_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	death_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	humiliation_list = ndb.StringProperty(default=',,,,,,,,,', indexed=False)
	
class DailyquestEntity(ndb.Model):
	quest_owner = ndb.IntegerProperty()
	quest_type = ndb.IntegerProperty(indexed=False)
	quest_count = ndb.IntegerProperty(default=0, indexed=False)
	
class TrophyEntity(ndb.Model):
	trophy_owner = ndb.IntegerProperty()
	trophy_index = ndb.IntegerProperty(indexed=False)
	trophy_getdate = ndb.DateTimeProperty(auto_now_add=True)

#거래(만드는 쪽)
class TradeEntity(ndb.Model):
	trade_item = ndb.IntegerProperty(indexed=False)
	trade_coin = ndb.IntegerProperty()
	trade_itemname = ndb.StringProperty() #아이템 이름
	trade_enddate = ndb.DateProperty()
	trade_owner = ndb.UserProperty()

#거래(제안하는 쪽)
class OfferEntity(ndb.Model):
	offer_owner = ndb.UserProperty()
	offer_target = ndb.IntegerProperty()
	offer_item = ndb.StringProperty(indexed=False)
	offer_targetuser = ndb.UserProperty()
	
#각종 로그 기록, 메인 페이지에 표시
class LogEntity(ndb.Model):
	log_owner = ndb.UserProperty()
	log_content = ndb.StringProperty(indexed=False)
	log_date = ndb.DateTimeProperty(auto_now_add=True)
	log_checked = ndb.BooleanProperty(default=False)
	
#프로필 페이지 댓글
class ReplyEntity(ndb.Model):
	reply_owner = ndb.UserProperty()
	reply_target = ndb.UserProperty()
	reply_content = ndb.StringProperty(indexed=False)
	reply_date = ndb.DateTimeProperty(auto_now_add=True)
	reply_checked = ndb.BooleanProperty(default=False)
	
#게시판 글
class ArticleEntity(ndb.Model):
	article_owner = ndb.KeyProperty()
	article_title = ndb.StringProperty(indexed=False)
	article_content = ndb.StringProperty(indexed=False)
	article_date = ndb.DateTimeProperty(auto_now_add=True)
	article_type = ndb.IntegerProperty(indexed=False)
	article_replycnt = ndb.IntegerProperty(default=0, indexed=False)

#게시판 댓글
class ArticleReplyEntity(ndb.Model):
	reply_owner = ndb.KeyProperty()
	reply_target = ndb.KeyProperty()
	reply_content = ndb.StringProperty(indexed=False)
	reply_date = ndb.DateTimeProperty(auto_now_add=True)
	
#삭제된 댓글 저장용
class DeletedArticleReplyEntity(ndb.Model):
	reply_owner = ndb.KeyProperty()
	reply_target = ndb.KeyProperty()
	reply_content = ndb.StringProperty(indexed=False)
	reply_date = ndb.DateTimeProperty(auto_now_add=True)
	
#Clan의 이미지가 있을 시 클랜의 이미지 주소를, 없을시 빈 스트링을 반환하는 함수
def findClanImage(clan_str):
	if clan_str.lower() == '[hark]' or clan_str.lower() == 'hark':
		found_image = '/clan/clan_hark.gif'
	elif clan_str.lower() == '[knu]' or clan_str.lower() == 'knu':
		found_image = '/clan/clan_knu.gif'
	elif clan_str.lower() == '[k:nu]' or clan_str.lower() == 'k:nu':
		found_image = '/clan/clan_k_nu.gif'
	elif clan_str.lower() == '[ivalice]' or clan_str.lower() == 'ivalice':
		found_image = '/clan/clan_ivalice.gif'
	elif clan_str.lower() == '[darkwhispr]' or clan_str.lower() == 'darkwhispr':
		found_image = '/clan/clan_darkwhispr.gif'
	elif clan_str.lower() == '[pyromania]' or clan_str.lower() == 'pyromania':
		found_image = '/clan/clan_pyromania.gif'
	else:
		found_image = ''
	return found_image

#주어진 String에 따라 해당하는 클래스의 이미지 주소를 반환하는 함수, 해당값이 없을 시 빈 스트링을 반환
def findClassImage(class_string, team=0):
	if (team==0):
		if class_string == 'Runner':
			class_image = '/images/class_scout.png'
		elif class_string == 'Firebug':
			class_image = '/images/class_pyro.png'
		elif class_string == 'Rocketman':
			class_image = '/images/class_soldier.png'
		elif class_string == 'Overweight':
			class_image = '/images/class_heavy.png'
		elif class_string == 'Detonator':
			class_image = '/images/class_demoman.png'
		elif class_string == 'Healer':
			class_image = '/images/class_medic.png'
		elif class_string == 'Constructor':
			class_image = '/images/class_engineer.png'
		elif class_string == 'Infiltrator':
			class_image = '/images/class_spy.png'
		elif class_string == 'Rifleman':
			class_image = '/images/class_sniper.png'
		elif class_string == 'Quote':
			class_image = '/images/class_quote.png'
		else:
			class_image = ''
	else:
		if class_string == 'Runner':
			class_image = '/images/class_scout_b.png'
		elif class_string == 'Firebug':
			class_image = '/images/class_pyro_b.png'
		elif class_string == 'Rocketman':
			class_image = '/images/class_soldier_b.png'
		elif class_string == 'Overweight':
			class_image = '/images/class_heavy_b.png'
		elif class_string == 'Detonator':
			class_image = '/images/class_demoman_b.png'
		elif class_string == 'Healer':
			class_image = '/images/class_medic_b.png'
		elif class_string == 'Constructor':
			class_image = '/images/class_engineer_b.png'
		elif class_string == 'Infiltrator':
			class_image = '/images/class_spy_b.png'
		elif class_string == 'Rifleman':
			class_image = '/images/class_sniper_b.png'
		elif class_string == 'Quote':
			class_image = '/images/class_quote_b.png'
		else:
			class_image = ''
	return class_image
	
#주어진 String에 따라 해당하는 클래스 초상화의 이미지 주소를 반환하는 함수, 해당값이 없을 시 빈 스트링을 반환
def findPortraitImage(class_string, direction):
	if direction: #True시 오리지날
		class_image = '/images/' + class_string + '_port_o.gif'
	else:		  #False시 반대
		class_image = '/images/' + class_string + '_port_a.gif'
	return class_image

#플레이타임 템플릿, 시 단위가 존재시 초 단위 삭제,
def makePlaytimeTemplate(user_time):
	time_string = ''
	time_h = 0
	if user_time // 108000:
		time_h = user_time // 108000
		user_time -= 108000*time_h
		if time_h < 100:
			time_string += str(time_h) + "h "
		else:
			time_string += str(time_h) + "h"
	if user_time // 1800 and time_h < 100:
		time_m = user_time // 1800
		user_time -= 1800*time_m
		if time_h and time_m:
			time_string += str(time_m) + "m"
		else:
			time_string += str(time_m) + "m "
	if not time_h:
		time_s = user_time // 30
		if time_s or time_string == '':
			time_string += str(time_s) + "s"
	return time_string
	
def makeLevelTemplate(user_level):
	level_string = '<level style="color: '
	if (user_level < 11):
		level_string += 'white'
	elif (user_level < 21):
		level_string += 'tomato'
	elif (user_level < 31):
		level_string += 'orange'
	elif (user_level < 41):
		level_string += 'yellow'
	elif (user_level < 51):
		level_string += 'chartreuse'
	elif (user_level < 61):
		level_string += 'royalblue'
	elif (user_level < 71):
		level_string += 'navy'
	elif (user_level < 81):
		level_string += 'purple'
	else:
		level_string += 'black'
	level_string += '">' + str(user_level) + '</level>'
	return level_string

def findClassConstant(class_string):
	if (class_string == "Runner"):
		return 0
	elif (class_string == "Rocketman"):
		return 1
	elif (class_string == "Rifleman"):
		return 2
	elif (class_string == "Detonator"):
		return 3
	elif (class_string == "Healer"):
		return 4
	elif (class_string == "Constructor"):
		return 5
	elif (class_string == "Overweight"):
		return 6
	elif (class_string == "Infiltrator"):
		return 7
	elif (class_string == "Firebug"):
		return 8
	elif (class_string == "Quote"):
		return 9
		
def classStringConvert(class_string):
	if (class_string == "Runner"):
		return "Scout"
	elif (class_string == "Rocketman"):
		return "Soldier"
	elif (class_string == "Rifleman"):
		return "Sniper"
	elif (class_string == "Detonator"):
		return "Demoman"
	elif (class_string == "Healer"):
		return "Medic"
	elif (class_string == "Constructor"):
		return "Engineer"
	elif (class_string == "Overweight"):
		return "Heavy"
	elif (class_string == "Infiltrator"):
		return "Spy"
	elif (class_string == "Firebug"):
		return "Pyro"
	elif (class_string == "Quote"):
		return "Quote"

def rarityIntegerConvert(item_rarity):
	if item_rarity == 0:
		item_class = "normal"
	elif item_rarity == 1:
		item_class = "strange"
	elif item_rarity == 2:
		item_class = "unusual"
	elif item_rarity == 3:
		item_class = "vintage"
	elif item_rarity == 4:
		item_class=  "self-made"
	else:
		item_class = "normal"
	return item_class
	
def findWeaponString(class_string):
	if (class_string == "Runner"):
		return "Scattergun"
	elif (class_string == "Rocketman"):
		return "Rocketlauncher"
	elif (class_string == "Rifleman"):
		return "Rifle"
	elif (class_string == "Detonator"):
		return "Minegun"
	elif (class_string == "Healer"):
		return "Medigun"
	elif (class_string == "Constructor"):
		return "Shotgun"
	elif (class_string == "Overweight"):
		return "Minigun"
	elif (class_string == "Infiltrator"):
		return "Revolver"
	elif (class_string == "Firebug"):
		return "Flamethrower"
	elif (class_string == "Quote"):
		return "Blade"

def partToString(item_part):
	if (item_part == 0):
		return "Head"
	elif (item_part == 1):
		return "Torso"
	elif (item_part == 2):
		return "Leg"
	elif (item_part == 3):
		return "Weapon"
	elif (item_part == 4):
		return "Misc"
	elif (item_part == 5):
		return "Taunt"
	elif (item_part == 6):
		return "Pet"
	elif (item_part == 7):
		return "Death Animation"
	elif (item_part == 8):
		return "Humiliation"
	else:
		raise IndexError("Item part out of range")

def strangeCountToString(strange_count):
	if (strange_count < 10):
		return "Strange"
	elif (strange_count < 25):
		return "Unremarkable"
	elif (strange_count < 45):
		return "Scarcely Lethal"
	elif (strange_count < 70):
		return "Mildly Menacing"
	elif (strange_count < 100):
		return "Somewhat Threatening"
	elif (strange_count < 135):
		return "Uncharitable"
	elif (strange_count < 175):
		return "Notably Dangerous"
	elif (strange_count < 225):
		return "Sufficiently Lethal"
	elif (strange_count < 275):
		return "Truly Feared"
	elif (strange_count < 350):
		return "Spectacularly Lethal"
	elif (strange_count < 500):
		return "Gore-Spattered"
	elif (strange_count < 750):
		return "Wicked Nasty"
	elif (strange_count < 999):
		return "Positively Inhumane"
	elif (strange_count < 1000):
		return "Totally Ordinary"
	elif (strange_count < 1500):
		return "Face-Melting"
	elif (strange_count < 2500):
		return "Rage-Inducing"
	elif (strange_count < 5000):
		return "Server-Clearing"
	elif (strange_count < 7500):
		return "Epic"
	elif (strange_count < 7617):
		return "Legendary"
	elif (strange_count < 8500):
		return "Australian"
	elif (strange_count >= 8500):
		return "Hale's Own"
	else:
		raise IndexError("Strange count out of range")
		
def strangeTypeToString(strange_type):
	if (strange_type == 0):
		return "Kills"
	elif (strange_type == 1):
		return "Runners Killed"
	elif (strange_type == 2):
		return "Firebugs Killed"
	elif (strange_type == 3):
		return "Rocketmans Killed"
	elif (strange_type == 4):
		return "Overweights Killed"
	elif (strange_type == 5):
		return "Detonators Killed"
	elif (strange_type == 6):
		return "Healers Killed"
	elif (strange_type == 7):
		return "Constructors Killed"
	elif (strange_type == 8):
		return "Infiltrators Killed"
	elif (strange_type == 9):
		return "Riflemans Killed"
	elif (strange_type == 10):
		return "Quotes Killed"
	elif (strange_type == 11):
		return "Sentries Destroyed"
	elif (strange_type == 12):
		return "Invulns"
	elif (strange_type == 13):
		return "Knife Kills"
	else:
		raise IndexError("Strange type out of range")

#이 상수 추가해야 아이템 업로드 페이지에서 제대로 작동함
_UNUSUALS = [0, 1, 2, 3, 4, 5, 6, 7, 100, 101, 102, 103]
		
def unusualTypeToString(unusual_type):
	#Circling 시리즈
	if (unusual_type == 0):
		return "Circling GG Logo"
	elif(unusual_type == 1):
		return "Circling Heart"
	elif(unusual_type == 2):
		return "Circling Peace Sign"
	elif(unusual_type == 3):
		return "Strolling Blackmage"
	elif(unusual_type == 4):
		return "Haunted Ghosts"
	elif(unusual_type == 5):
		return "Circling Coin"
	elif(unusual_type == 6):
		return "Orbiting Invaders"
	elif(unusual_type == 7):
		return "Orbiting Saturn"
	#머리 위치에서 고정형
	elif(unusual_type == 100):
		return "Green Energy"
	elif(unusual_type == 101):
		return "Purple Energy"
	elif(unusual_type == 102):
		return "Red Energy"
	elif(unusual_type == 103):
		return "Blue Energy"
	else:
		return ""

#K, M단위로 수치 표시
def strlize(num):
	if (num >= 1000):
		return "%.1f" %(num/1000.0) + "K"
	elif (num >= 1000000):
		return "%.1f" %(num/1000000.0) + "M"
	else:
		return str(num)
		
def getMaxExp(current_level):
	return 1500*current_level
	
#=========================================================================================================================#
														#PAGES#
#=========================================================================================================================#	
#메인 페이지
class MainPage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				@font-face {
					font-family: "Mother";
					src: url('/fonts/apple_kid.eot'); /* IE9 Compat Modes */
					src: url('/fonts/apple_kid.eot?#iefix') format('embedded-opentype'), /* IE6-IE8 */
							url('/fonts/apple_kid.woff2') format('woff2'), /* Super Modern Browsers */
							url('/fonts/apple_kid.woff') format('woff'), /* Pretty Modern Browsers */
							url('/fonts/apple_kid.ttf')  format('truetype'), /* Safari, Android, iOS */
							url('/fonts/apple_kid.svg#svgFontName') format('svg'); /* Legacy iOS */
				}
				@font-face {
					font-family: "Saturn";
					src: url('/fonts/saturn_boing.eot'); /* IE9 Compat Modes */
					src: url('/fonts/saturn_boing.eot?#iefix') format('embedded-opentype'), /* IE6-IE8 */
							url('/fonts/saturn_boing.woff2') format('woff2'), /* Super Modern Browsers */
							url('/fonts/saturn_boing.woff') format('woff'), /* Pretty Modern Browsers */
							url('/fonts/saturn_boing.ttf')  format('truetype'), /* Safari, Android, iOS */
							url('/fonts/saturn_boing.svg#svgFontName') format('svg'); /* Legacy iOS */
				}
				html, body {
					height:100%;
					width:100%;
					padding: 0;
					margin: 0;
				}
				html{
					display: table;
				}
				body{
					font-family: 'Press Start 2P', sans-serif, cursive;
					display: table-cell;
					background: #C6BEBC; /* For browsers that do not support gradients */
					background: -webkit-linear-gradient(#A29994, #C6BEBC, #716967); /* For Safari 5.1 to 6.0 */
					background: -o-linear-gradient(#A29994, #C6BEBC, #716967); /* For Opera 11.1 to 12.0 */
					background: -moz-linear-gradient(#A29994, #C6BEBC, #716967); /* For Firefox 3.6 to 15 */
					background: linear-gradient(#A29994, #C6BEBC, #716967);
					text-align: center;
					color: white;
				}
				div.Menu{
					width: 100%;
					height: 68px;
					background: #363030; /* For browsers that do not support gradients */
					background: -webkit-linear-gradient(#363030, #A29994); /* For Safari 5.1 to 6.0 */
					background: -o-linear-gradient(#363030, #A29994); /* For Opera 11.1 to 12.0 */
					background: -moz-linear-gradient(#363030, #A29994); /* For Firefox 3.6 to 15 */
					background: linear-gradient(#363030, #A29994)
					display: inline-block;
					margin: auto;
					margin-bottom: 0px;
					text-align: center;
				}
				p.Menu{
					float: left;
					height: 36px;
				}
				a.menu{
					font-size: 14px;
					margin-right: 20px;
				}
				img.menu{
					width: 36px;
					height: 36px;
				}
				div.motd{
					margin: auto;
					margin-bottom: 50px;
					padding: auto;
					clear: left;
				}
				/* unvisited link */
				a:link {
					color: white;
					text-decoration: none;
				}
				/* visited link */
				a:visited {
					color: white;
					text-decoration: none;
				}
				/* mouse over link */
				a:hover {
					color: hotpink;
					text-decoration: none;
				}
				/* selected link */
				a:active {
					color: hotpink;
					text-decoration: none;
				}
				a.first{
					color: yellow;
				}
				p{
					width: 100%;
					image-rendering: crisp-edges;
					image-rendering: pixelated;
				}
				#normal{
					color: #F7DC07;
				}
				#strange{
					color: #CF6A32;
				}
				#unusual{
					color: #8650AC;
				}
				#vintage{
					color: #476291;
				}
				#self-made{
					color: #70B04A;
				}
				p.motd-head{
					background-image:url("/images/motd_head.png");
					background-repeat: no-repeat;
					background-position:center center;
					background-size: 1024px 180px;
					height: 180px;
					margin: 0;
				}
				p.motd-body{
					background-image:url("/images/motd_body.png");
					background-repeat: repeat-y;
					background-position:center center;
					background-size: 1024px 136px;
					height: 242px;
					margin: 0;
				}
				p.motd-tail{
					background-image:url("/images/motd_tail.png");
					background-repeat: no-repeat;
					background-position:center center;
					background-size: 1024px 180px;
					height: 180px;
					margin: 0;
				}
				div.quest{
					margin-bottom: 50px;
				}
				table.quest{
					font-family: Mother, sans-serif;
					vertical-align: middle;
					line-height: 1.5;
					color: #716967;
					text-align: justify;
					width: 608px;
					margin: auto;
					margin-top: 20px;
					border-spacing: 0px 0px;
				}
				td.head{
					background-image:url("/images/mother_head.png");
					background-repeat: no-repeat;
					background-position:center center;
					background-size: 608px 20px;
					height: 20px;
					margin: 0;
				}
				td.body{
					background-image:url("/images/mother_body.png");
					background-repeat: repeat-y;
					background-position:center center;
					background-size: 608px 4px;
					height: 100px;
					margin: 0;
				}
				td.tail{
					background-image:url("/images/mother_tail.png");
					background-repeat: no-repeat;
					background-position:center center;
					background-size: 608px 20px;
					height: 20px;
					margin: 0;
				}
				tr.quest{
					height: 20px;
				}
				span.title{
					font-size: 40px;
					text-shadow: 2px 2px #000000;
					font-family: Saturn;
					color: #716967;
				}
				span.questname{
					margin-left: 30px;
					text-align: justify;
					font-size: 50px;
					color: white;
				}
				span.questcontent{
					margin-left: 30px;
					text-align: justify;
					font-size: 30px;
				}
				span.questcount{
					margin-left: 10px;
					text-align: justify;
					font-size: 30px;
				}
				span.questreward{
					float: right;
					margin-right: 50px;
					text-align: justify;
					font-size: 30px;
					color: yellow;
				}
				div.rank{
					text-align: center;
					margin-bottom: 100px;
				}
				fieldset{
					display: inline;
					Border: 5px;
					border-style: solid;
					border-radius:0.4em;
				}
				table.rank{
					width: 800px;
					vertical-align: middle;
					text-align: center;
					margin: auto;
				}
				th{
					color: #8E8464;
				}
				tr{
					height: 32px;
				}
				tr.first{
					color: yellow;
				}
				div.howto{
					text-align: center;
					width: 100%;
					line-height: 5;
				}
				div.copyright{
					text-align: center;
					width: 100%;
					color: #FBECCB;
					line-height: 2;
				}
			</style>
		"""
		script = """
		<script type="text/javascript">
			if (window.top.location != window.location) {
				window.top.location = window.location;
			}
		</script>
		"""
		#로그인 검정, 로그인이 되었을시 user_logged_on의 값은 True, 아닐시 False
		user = users.get_current_user()
		user_id = ''
		user_logged_on = False
		if user:
			current_user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', user).get()
			if current_user:
				user_id = current_user.user_id
				user_logged_on = True

		#페이지 시작
		html = '<HTML>'
		html += '<HEAD>' + '<TITLE>Gang Garrison 2 Stats</TITLE>' + css + script + '</HEAD>'
		html += '<BODY>'
		#상단 메뉴, 로그인시의 메뉴, 검색창, 로그인 페이지를 포함
		html += '<div class="Menu">'
		html += '<p class="Menu">'
		html += '<a class="menu" href="/rank"><img class="menu" src="/images/menu_leaderboard.png" title="LeaderBoard"></a>'
		html += '<a class="menu" href="/search"><img class="menu" src="/images/menu_search.png" title="Search"></a>'
		html += '<a class="menu" href="/gallery"><img class="menu" src="/images/menu_gallery.png" title="Item Gallery"></a>'
		html += '<a class="menu" href="/down"><img class="menu" src="/images/menu_download.png" title="Download"></a>'
		if user_logged_on:#로그인 되었을시의 백팩과 로드아웃, 가챠 메뉴 표시
			html += '<a class="menu" href="/backpack?id=' + user_id + '"><img class="menu" src="/images/menu_backpack.png" title="Backpack"></a>'
			html += '<a class="menu" href="/loadout"><img class="menu" src="/images/menu_loadout.png" title="Loadout"></a>'
			html += '<a class="menu" href="/gacha"><img class="menu" src="/images/menu_gacha.png" title="Gacha"></a>'
			html += '<a class="menu" href="/mytrade"><img class="menu" src="/images/menu_trade.png" title="My Trade"></a>'
			html += '<a class="menu" href="/market"><img class="menu" src="/images/menu_market.png" title="Market"></a>'
		html += ''#검색창
		if user_logged_on:
			if current_user.user_avatar:
				html += '<a href="/myprofile"><img class="menu" src="/upload?img_id=%s" title="My Profile"></a>&nbsp' %current_user.key.urlsafe()
			else:
				html +='<a href="/myprofile"><img src="/images/gg2slogo.png" title="My Profile"></a>&nbsp'
			html += '<a class="menu" style="color: yellow;">' + str(current_user.user_coin) + 'G</a>'
			logout_url = users.create_logout_url('/')
			html += '<a class="menu" href="' + logout_url + '">Logout</a>'
		else:
			html += '<a class="menu" href="%s">Login</a>' %users.create_login_url('/')
			html += '<a class="menu" class="register" href="/register">Register</a>'
		if str(self.request.headers.get('X-AppEngine-Country')) == 'KR':
			html += '<a class="menu" href="http://cafe.naver.com/ganggarrison2k/16040">'
		else:
			html += '<a class="menu" href="http://www.ganggarrison.com/forums/index.php?topic=37158.0">'
		html += '<img class="menu" src="/images/menu_howto.png" title="How To Use">'
		html += '</a>'
		html += '</p>'
		html += '</div>'
		
		if user_logged_on:
			if (current_user.user_region != str(self.request.headers.get('X-AppEngine-Country'))):
				current_user.user_region = str(self.request.headers.get('X-AppEngine-Country'))
				current_user.put()
		
		#NOTICE
		if user_logged_on:
			offer_count = ndb.gql('SELECT __key__ FROM OfferEntity WHERE offer_targetuser=:1', user).count()
			log_list = ndb.gql('SELECT * FROM LogEntity WHERE log_owner=:1 AND log_checked=False', user)
			reply_count = ndb.gql('SELECT __key__ FROM ReplyEntity WHERE reply_target=:1 AND reply_checked=False', user).count()
			html += '<div class="notice" style="font-family: Mother, sans-serif; text-shadow: 2px 2px #454545;">'
			html += '<img src="/images/icon_notice.png">'
			html += '<span class="title"> NOTICE </span>'
			html += '<img src="/images/icon_notice.png">'
			ndb_put_list = []
			if offer_count:
				html += '<br>'
				html += '<span class="questname" style="text-align: center;">'
				html += '<image src="images/mother_dot.png">&nbsp'
				html += 'There\'re <span style="color: yellow;">' + str(offer_count) + '</span> offers for your item.'
				html += '</span>'
			if reply_count:
				html += '<br>'
				html += '<span class="questname" style="text-align: center;">'
				html += '<image src="images/mother_dot.png">&nbsp'
				html += 'There\'re <span style="color: yellow;">' + str(reply_count) + '</span> unread comments on your profile.'
				html += '</span>'
			for log in log_list:
				html += '<br>'
				html += '<span class="questname" style="text-align: center;">'
				html += '<image src="images/mother_dot.png">&nbsp'
				html += log.log_content
				html += '</span>'
				log.log_checked = True
				ndb_put_list.append(log)
			if ndb_put_list:
				ndb.put_multi(ndb_put_list)
			html += '</div>'
		
		#MOTD
		html += '<div class="motd" style="text-align: center;">'
		html += '<p class="motd-head"></p>'
		html += '<p class="motd-body" style="font-size: 48px; font-family: Mother, sans-serif; text-shadow: 2px 2px #454545;">'
		html += '<img src="/images/gg2slogo_200.png">'
		html += '<br>'
		html += '<span>Gang Garrison 2 Stats</span>'
		html += '</p>'
		html += '<p class="motd-tail">'
		html += '</p>'
		html += '</div>'

		#일퀘
		if user_logged_on:
			html += '<div class="quest">'
			html += '<span class="title">DAILY QUESTS</span>'

			#Memcache Read
			quest_list = memcache.get(current_user.user_id + ':quest')
			if quest_list is None:
				quest_list = ndb.gql('SELECT * FROM DailyquestEntity WHERE quest_owner=:1', current_user.key.id())
				if not quest_list.count():
					quest_list = ''
				if not memcache.add(current_user.user_id + ':quest', quest_list, 3600): #1시간
					logging.error('Memcache set failed for ' + current_user.user_id + '_QUEST')

			i = 1
			if (quest_list): #퀘스트가 하나라도 있을 경우
				html += '<table class="quest">'
				for quest in quest_list:
					html += '<tr class="quest"><td class="head"></td></tr>'
					html += '<tr class="quest"><td class="body">'
					html += '<span class="questname">' + str(i) + '. ' + str(_QUESTS[quest.quest_type][0]) + ': </span><br>'
					html += '<span class="questcontent"><image src="images/mother_dot.png">&nbsp' + str(_QUESTS[quest.quest_type][1]) + '</span>'
					if (_QUESTS[quest.quest_type][4] == 1 or _QUESTS[quest.quest_type][4] == 5):#시간 관련 퀘스트
						html += '<span class="questcount">(' + makePlaytimeTemplate(quest.quest_count) + ' / ' + makePlaytimeTemplate(_QUESTS[quest.quest_type][2]) + ')</span>'
					else:
						html += '<span class="questcount">(' + str(quest.quest_count) + ' / ' + str(_QUESTS[quest.quest_type][2]) + ')</span>'
					html += '<span class="questreward">' + str(_QUESTS[quest.quest_type][3]) + ' Coin</span>'
					html += '</td></tr>'
					html += '<tr class="quest"><td class="tail"></td></tr>'
					html += '<tr class="quest"></tr>'
					i += 1
				html += '</table>'
			else: #퀘스트가 하나도 없을 경우
				html += '<table class="quest">'
				html += '<tr class="quest"><td class="head"></td></tr>'
				html += '<tr class="quest"><td class="body">'
				html += '<span class="questname" style="text-align: center;"><image src="images/mother_dot.png">&nbsp'
				html += "You've finished all of your daily quests!"
				html += '</span>'
				html += '</td></tr>'
				html += '<tr class="quest"><td class="tail"></td></tr>'
				html += '</span>'
				html += '</table>'
			html += '</div>'
			
		#TOP10(TODAY) IN MAIN PAGE
		html += '<div class="rank">'
		html += '<span class="title">Today\'s TOP10</span><br>'
		html += '<fieldset>'
		html += '<table class="rank">'
		html += "<thead>"
		html += "<tr>"
		html += '<th width="24px">' + '<img src="/images/r_icon.png">' + "</th>" #RANK
		html += '<th width="">' + '<img src="/images/n_icon.png">' + "</th>" #이름
		html += '<th width="24px">' + "</th>" #선호 클래스
		html += '<th width="72px">' + '<img src="/images/k_icon.png">' + "</th>"
		html += '<th width="72px">' + '<img src="/images/d_icon.png">' + "</th>"
		html += '<th width="72px">' + '<img src="/images/a_icon.png">' + "</th>"
		html += '<th width="48px">' + '<img src="/images/kda_icon.png">' + "</th>"
		html += '<th width="72px">' + 'Points' + "</th>"
		html += "</thead>"
		html += "<tbody>"
		cnt = 0
		#Memcache Read
		today_list = memcache.get('today_rank')
		if today_list is None:
			today_list = ndb.gql('SELECT * FROM TodayEntity ORDER BY user_point DESC LIMIT 10')
			today_memcache = []

			for today in today_list:
				user_key = today.key.id()
				user = ndb.Key(UserEntity, user_key).get()
				if cnt == 0:
					html += '<tr class="first">'
				else:
					html += '<tr>'
				html += '<td>' + str(cnt + 1) + '</td>'
				if cnt == 0:
					html += '<td>' + '<a class="first" href="/profile?id=' + user.user_id + '">' + user.user_id + '</td>'
				else:
					html += '<td>' + '<a class="name" href="/profile?id=' + user.user_id + '">' + user.user_id + '</td>'
				class_image = findClassImage(user.user_favclass)
				html += '<td>' + '<img src="' + class_image + '">' + '</td>'
				html += '<td>' + strlize(today.user_kill) + '</td>'
				html += '<td>' + strlize(today.user_death) + '</td>'
				html += '<td>' + strlize(today.user_assist) + '</td>'
				html += '<td>' + '%.1f' %today.user_kda + '</td>'
				html += '<td>' + str(today.user_point) + '</td>'
				today_cache = []
				today_cache.append(user.user_id)
				today_cache.append(user.user_favclass)
				today_cache.append(today.user_kill)
				today_cache.append(today.user_death)
				today_cache.append(today.user_assist)
				today_cache.append(today.user_kda)
				today_cache.append(today.user_point)
				today_memcache.append(today_cache)
				html += '</tr>'
				cnt += 1
			if not memcache.add('today_rank', today_memcache, 3600): #1시간
				logging.error('Memcache set failed for TODAY_RANK.')
		
		else: #Memcache exists
			for today in today_list:
				if cnt == 0:
					html += '<tr class="first">'
				else:
					html += '<tr>'
				html += '<td>' + str(cnt + 1) + '</td>'
				if cnt == 0:
					html += '<td>' + '<a class="first" href="/profile?id=' + today[0] + '">' + today[0] + '</td>'
				else:
					html += '<td>' + '<a class="name" href="/profile?id=' + today[0] + '">' + today[0] + '</td>'
				class_image = findClassImage(today[1])
				html += '<td>' + '<img src="' + class_image + '">' + '</td>'
				html += '<td>' + strlize(today[2]) + '</td>'
				html += '<td>' + strlize(today[3]) + '</td>'
				html += '<td>' + strlize(today[4]) + '</td>'
				html += '<td>' + '%.1f' %today[5] + '</td>'
				html += '<td>' + str(today[6]) + '</td>'
				html += '</tr>'
				cnt += 1
		html += '</tbody>'
		html += '</table>'
		html += '</fieldset>'
		html += '</div>'
		html += '<div class="copyright">'
		html += 'Copyright &copy;2016 by WoodNeck. All rights reserved.<br>'
		html += 'This site is optimized for Chrome browser.'
		html += '</div>'
		html += '</BODY>'
		html += '</HTML>'
		self.response.out.write(html)

#New Main Page		
class MainPage2(webapp2.RequestHandler):
	def putLogoOnContentPane(self):
		logoHtml = '<img id="logo-nw" class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		logoHtml += '<img id="logo-ne" class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		logoHtml += '<img id="logo-sw" class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		logoHtml += '<img id="logo-se" class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		return logoHtml

	def get(self):
		current_user = users.get_current_user()
		user_logged_on = False
		user_have_id = False
		if current_user:
			user_logged_on = True
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
			if user:
				user_have_id = True
		html = '<!DOCTYPE html>'
		html += '<html>'
		html += '<head>'
		html += '<title>Gang Garrison 2 Stats</title>'
		html += '<link rel="stylesheet" type="text/css" href="/css/main.css">'
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</head>'
		
		html += '<body>'
		
		#IE CHECK
		html += '<!--[if IE]>'
		html += '<div class="body-wrapper">'
		html += 'PLEASE USE CHROME/FIREFOX BROWSER'
		html += '</div>'
		html += '<![endif]-->'
		
		
		html += '<div class="top-wrapper">'
		
		html += '<div class="top-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_beige.png" />'
		html += '<span>Gang Garrison 2 Stats</span>'
		html += '</div>' #top-gg2s-text
		html += '<div class="top-user-wrapper">'
		if user_have_id:
			html += '<div class="user-image-wrapper">'
			if user.user_avatar:
				html += '<a href="/profile?id={}"><img src="/upload?img_id={}"></a>'.format(user.user_id, user.key.urlsafe())
			else:
				html +='<a href="/profile?id={}"><img src="/images/gg2slogo_beige.png"></a>'.format(user.user_id)
			html += '</div>' #user-image-wrapper
			
			html += '<div class="user-info-wrapper">'
			html += '<div class="info-table-wrapper">'
			html += '<div class="info-table-top">'
			html += '<div class="table-top-left">'
			html += '<img id="class-icon" src="/images/icon_{}_gameboy.png" />'.format(user.user_favclass)
			html += '<span id="level-text">Lv.{} {}</span>'.format(user.user_level, user.user_favclass)
			html += '</div>' #table-top-left
			html += '<div class="table-top-right">'
			html += '<span id="coin-text"><span id="coin-amount">{}</span> Coins</span>'.format(user.user_coin)
			html += '</div>' #table-top-right
			html += '</div>' #info-table-top
			html += '<div class="info-table-bottom">'
			html += '<div class="table-bottom-left">'
			html += '<a href="/profile?id={0}"><span id="userid-text">{0}</span></a>'.format(user.user_id)
			html += '</div>' #table-bottom-left
			html += '<div class="table-bottom-right">'
			html += '<a class="menu" href="{}">LOGOUT</a>'.format(users.create_logout_url('/'))
			html += '</div>' #table-bottom-right
			html += '</div>' #info-table-bottom
			html += '</div>' #info-table-wrapper
			html += '</div>' #top-info-wrapper
		else:
			html += '<div class="top-login-wrapper">'
			html += '<div class="top-login-left">'
			html += '<a href="%s">LOGIN</a>' %users.create_login_url('/')
			html += '</div>' #top-login-left
			html += '<div class="top-login-right">'
			html += '<a href="/register">REGISTER</a>'
			html += '</div>' #top-login-right
			html += '</div>' #top-login-wrapper
		html += '</div>' #top-user-wrapper
		
		html += '<div class="top-leftmenu-wrapper top-menu">'
		html += '<div class="menu-menu-wrapper">'
		html += '<div class="menu-menu-item" id="first-child">'
		html += '<a href="/rank">RANK</a>'
		html += '</div>'
		html += '<div class="menu-menu-item">'
		html += '<a href="/search">SEARCH</a>'
		html += '</div>'
		html += '<div class="menu-menu-item" id="last-child">'
		html += '<a href="/gallery">GALLERY</a>'
		html += '</div>'
		html += '</div>' #menu-menu-wrapper
		html += '</div>' #top-leftmenu-wrapper
		
		html += '<div class="top-logo-wrapper">'
		html += '<img id="top-logo" src="/images/gg2slogo_beige_192.png" />'
		html += '</div>' #top-logo-wrapper
		
		html += '<div class="top-rightmenu-wrapper top-menu">'
		html += '<div class="menu-menu-wrapper">'
		html += '<div class="menu-menu-item" id="first-child">'
		html += '<a href="/down">DOWNLOAD</a>'
		html += '</div>'
		html += '<div class="menu-menu-item">'
		html += '<a href="/board">BOARD</a>'
		html += '</div>'
		html += '<div class="menu-menu-item" id="last-child">'
		if str(self.request.headers.get('X-AppEngine-Country')) == 'KR':
			html += '<a class="menu" href="http://cafe.naver.com/ganggarrison2k/16040">'
		else:
			html += '<a class="menu" href="http://www.ganggarrison.com/forums/index.php?topic=37158.0">'
		html += 'HELP'
		html += '</a>'
		html += '</div>'
		html += '</div>' #menu-menu-wrapper
		html += '</div>' #top-rightmenu-wrapper
		
		html += '</div>' #top-wrapper
		
		if user_have_id:
			offer_count = ndb.gql('SELECT __key__ FROM OfferEntity WHERE offer_targetuser=:1', current_user).count()
			log_list = ndb.gql('SELECT * FROM LogEntity WHERE log_owner=:1 AND log_checked=False', current_user)
			reply_count = ndb.gql('SELECT __key__ FROM ReplyEntity WHERE reply_target=:1 AND reply_checked=False', current_user).count()
			html += '<div class="body-notice">'
			ndb_put_list = []
			if offer_count:
				html += '<div class="notice-wrapper">'
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_admin.png" />'
				html += 'There\'{} <span id="notice-count">{}</span> {} for your item.'.format('re' if offer_count > 1 else 's', offer_count, 'offers' if offer_count > 1 else 'offer')
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_admin.png" />'
				html += '</div>'
			if reply_count:
				html += '<div class="notice-wrapper">'
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_admin.png" />'
				html += 'There\'{} <span id="notice-count">{}</span> unread {} on your profile.'.format('re' if reply_count > 1 else 's', reply_count, 'comments' if reply_count >1 else 'comment')
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_admin.png" />'
				html += '</div>'
			for log in log_list:
				html += '<div class="notice-wrapper">'
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_admin.png" />'
				html += log.log_content
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_admin.png" />'
				html += '</div>'
				log.log_checked = True
				ndb_put_list.append(log)
			html += '</div>'
			if ndb_put_list:
				ndb.put_multi(ndb_put_list)
		
		html += '<div class="body-wrapper">'
		
		html += '<div class="body-content-left">'
		html += '<div class="content-left-menu">'
		html += '<div class="menu-motd-wrapper" id="content-wrapper">'
		html += self.putLogoOnContentPane()
		html += '<div class="motd-head-wrapper" id="content-head">MOTD</div>'
		html += '<div class="motd-body-wrapper">'
		html += '<img src="/images/trophy/trophy_season1_no1.png" style="width: 96px; height: 96px;">'
		html +=	'<br>'
		html += '<a href="/award">SEASON {} WINNERS</a>'.format(GG2S_CURRENT_SEASON - 1)
		html += '</div>' #motd-body-wrapper
		html += '</div>' #menu-motd-wrapper
		html += '<div class="menu-spacing"></div>'
		if user_have_id:
			html += '<div class="content-menu-wrapper" id="content-wrapper">'
			html += self.putLogoOnContentPane()
			html += '<div class="content-menu-menu">'
			html += '<div id="menu-backpack"><a href="/backpack?id={}">BACKPACK</a></div>'.format(user.user_id)
			html += '<div id="menu-loadout"><a href="/loadout">LOADOUT</a></div>'
			html += '<div id="menu-market"><a href="/market">MARKET</a></div>'
			html += '<div id="menu-trade"><a href="/mytrade">TRADE</a></div>'
			html += '<div id="menu-gacha"><a href="/gacha">GACHA</a></div>'
			html += '</div>' #content-menu-menu
			html += '</div>' #content-menu-wrapper'
		else:
			html += '<div class="content-menu-wrapper" id="content-wrapper">'
			html += self.putLogoOnContentPane()
			html += '<div class="content-menu-menu">'
			playerCount = memcache.get('playerCount')
			if playerCount is None:
				playerCount = ndb.gql('SELECT __key__ FROM UserEntity').count()
				memcache.add('playerCount', playerCount, 86400) #1 day
			html += '<div style="font-size: 72px;">{}</div>'.format(playerCount)
			html += '<div>USERS USING GG2S</div>'
			html += '</div>' #content-menu-menu
			html += '</div>' #content-menu-wrapper'
		html += '</div>' #content-left-menu
		html += '<div class="content-left-recent">'
		html += '<div class="recent-activity-wrapper" id="content-wrapper">'
		html += '<div class="activity-head-wrapper" id="content-head">LATEST ACTIVITY</div>'
		html += self.putLogoOnContentPane()
		latestLogInfo = memcache.get('latestLogInfo')
		if latestLogInfo is None:
			latestLog = ndb.gql('SELECT * FROM LogEntity ORDER BY log_date DESC').get()
			if latestLog:
				latestLogOwner = ndb.gql('SELECT user_id FROM UserEntity WHERE google_id=:1', latestLog.log_owner).get()
			else:
				latestLogOwner = None
			latestLogInfo = [latestLog, latestLogOwner]
			memcache.add('latestLogInfo', latestLogInfo, 300) #5min
		else:
			latestLog = latestLogInfo[0]
			latestLogOwner = latestLogInfo[1]
		html += '<div class="activity-body-wrapper">'
		if latestLog:
			html += '<span id="activity-content"><a href="/profile?id={0}" id="activity-owner">{0}</a> {1}</span>'.format(latestLogOwner.user_id, latestLog.log_content)
		else:
			html += '<span id="activity-content">NO LOG!</span>'
		html += '</div>' #activity-body-wrapper
		html += '</div>' #recent-activity-wrapper
		html += '</div>' #content-left-recent
		if user_have_id:
			html += '<div class="content-left-quest" id="content-wrapper">'
			html += self.putLogoOnContentPane()
			html += '<div class="quest-head-wrapper" id="content-head">DAILY QUESTS</div>'
			questInfo = memcache.get('questInfo-' + str(user.key.id()))
			if questInfo is None:
				questInfo = ndb.gql('SELECT * FROM DailyquestEntity WHERE quest_owner=:1', user.key.id())
				questInfo = [quest for quest in questInfo]
				memcache.add('questInfo-' + str(user.key.id()), questInfo, 900) #15min
			html += '<div class="quest-body-wrapper">'
			if questInfo:
				for quest in questInfo:
					html += '<div class="quest-wrapper">'
					html += '<div class="quest-name-wrapper">{}</div>'.format(_QUESTS[quest.quest_type][0])
					html += '<div class="quest-content-wrapper">{}</div>'.format(_QUESTS[quest.quest_type][1])
					if (_QUESTS[quest.quest_type][4] == 1 or _QUESTS[quest.quest_type][4] == 5):#시간 관련 퀘스트
						html += '<div class="quest-count-wrapper">{}/{}</div>'.format(makePlaytimeTemplate(quest.quest_count), makePlaytimeTemplate(_QUESTS[quest.quest_type][2]))
					else:
						html += '<div class="quest-count-wrapper">{}/{}</div>'.format(quest.quest_count, _QUESTS[quest.quest_type][2])
					html += '<div class="quest-reward-wrapper"><span id="quest-reward">{}</span> Coins</div>'.format(_QUESTS[quest.quest_type][3])
					html += '</div>' #quest-wrapper
			else:
				html += '<div class="quest-wrapper">'
				html += 'NO QUESTS AVAILABLE'
				html += '</div>'
			html += '</div>' #quest-body-wrapper
			html += '</div>' #content-left-quest
		else:
			html += '<div class="content-left-quest" id="content-wrapper">'
			html += self.putLogoOnContentPane()
			html += '<div class="quest-head-wrapper" id="content-head">FAQ</div>'
			html += '<div class="quest-name-wrapper">How can I make ID?</div>'
			html += '<div class="quest-wrapper">Click <a href="{}">REGISTER</a> Button to make an ID.<br>You need a google account to register.</div>'.format('/register')
			html += '<div class="quest-name-wrapper">How can I download the plugin?</div>'
			html += '<div class="quest-wrapper">Click <a href="{}">DOWNLOAD</a> Button.<br>Download the "GG2S Plugin" and put it into Plugins folder.</div>'.format('/down')
			html += '<div class="quest-name-wrapper">I forgot my unique key!</div>'
			html += '<div class="quest-wrapper">Check it at <a href="{}">HERE</a></div>'.format('/profilesetting')
			html += '</div>' #content-left-quest
		html += '</div>' #body-content-left
		
		html += '<div class="body-content-right">'
		html += '<div class="content-right-todayrank" id="content-wrapper">'
		html += self.putLogoOnContentPane()
		html += '<div class="todayrank-body-wrapper">'
		html += '<div class="todayrank-head-wrapper" id="content-head">'
		html += 'TODAY\'S RANK'
		html += '</div>' #todayrank-head-wrapper
		todayRankInfo = memcache.get('todayRankInfo')
		if todayRankInfo is None:
			todayRank = ndb.gql('SELECT * FROM TodayEntity ORDER BY user_point DESC LIMIT 10')
			todayUser = []
			for todayScore in todayRank:
				todayUser.append(ndb.Key(UserEntity, todayScore.key.id()))
			todayUser = ndb.get_multi(todayUser)
			todayUser = [u for u in todayUser]
			todayRank = [t for t in todayRank]
			todayRankInfo = [todayRank, todayUser]
			memcache.add('todayRankInfo', todayRankInfo, 900) #15min
		todayRank = todayRankInfo[0]
		todayUser = todayRankInfo[1]
		for i in range(len(todayRank)):
			html += '<div class="todayrank-user-wrapper">'
			html += '<div class="todayrank-info-wrapper">'
			html += '<div class="todayrank-info-rank">'
			html += '<span id="info-rank">{}.</span>'.format(i + 1)
			html += '</div>' #todayrank-info-rank
			html += '<div class="todayrank-info-user">'
			html += '<div class="info-user-top">'
			html += '<img id="class-icon" src="/images/icon_{}_gameboy.png" />'.format(todayUser[i].user_favclass)
			html += 'Lv.{} {}'.format(todayUser[i].user_level, todayUser[i].user_favclass)
			html += '</div>' #info-user-top
			html += '<div class="info-user-bottom">'
			html += '<a href="/profile?id={0}"><span id="info-id">{0}</span></a>'.format(todayUser[i].user_id)
			html += '</div>' #info-user-bottom
			html += '</div>' #todayrank-info-user
			html += '<div class="todayrank-info-score">'
			html += '<div class="info-score-top">'
			html += '<span id="info-score">{}</span>'.format(todayRank[i].user_point)
			html += '</div>' #info-score-top
			html += '<div class="info-score-bottom">'
			html += '<span id="info-score-kda">{}/{}/{}</span>'.format(todayRank[i].user_kill, todayRank[i].user_death, todayRank[i].user_assist)
			html += '</div>' #info-score-bottom
			html += '</div>' #todayrank-info-score
			html += '</div>' #todayrank-info-wrapper
			html += '</div>' #todayrank-user-wrapper
		html += '</div>' #todayrank-body-wrapper
		html += '</div>' #content-right-todayrank
		html += '</div>' #body-content-right
		
		html += '</div>' #body-wrapper
		
		mainVisitorCounter = memcache.get('mainVisitorCounter')
		if mainVisitorCounter is None:
			mainVisitorCounter = 1
			memcache.add('mainVisitorCounter', mainVisitorCounter, 2592000) #1 day
		else:
			memcache.incr('mainVisitorCounter')
		html += '<div class="footer-wrapper"><span id="visit-count">{}</span> VISITED TODAY</div>'.format(mainVisitorCounter)
			
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)


#웹의 아이디 등록페이지
class RegisterPage(webapp2.RequestHandler):
	css = """
		<style>
			html{
				height: 100%;
				display: table;
				margin: auto;
			}
			body{
				display: table-cell;
				vertical-align: middle;
				margin: auto;
				font-family: sans-serif, cursive;
				display: table-cell;
				vertical-align: middle;
				text-align: center;
				font-weight: bold;
				background: #454545;
				color: white;
				line-height: 3;
			}
		</style>
	"""
	def get(self):
		current_user = users.get_current_user()
		if str(current_user) in BAN_LIST:
			return
		html = '<HTML>'
		html += '<HEAD>' + '<TITLE>GG2S:Register</TITLE>' + self.css + '</HEAD>'
		html += '<a href="/"><img src="/images/GG2SLogoBig.png" style="margin-bottom: 50px;"></a>'
		html += '<br>'
		html += '<fieldset>'
		html += 'Greetings, New Player!<br>'
		html += 'New to GG2S? Check <a href="http://www.ganggarrison.com/forums/index.php?topic=37158.0" style="color: yellow;">>HERE<</a> first!<br>'
		html += 'What is an Itemserver? Check <a href="http://www.ganggarrison.com/forums/index.php?topic=37222.0" style="color: yellow;">GG2I</a>, too!<br>'
		html += '</fieldset>'
		html += '<fieldset>'
		html += '<legend>Register</legend>'
		html += '<form method = "POST">'
		html += 'NickName: ' + '<input type="text" name="register_id" maxlength="20">&nbsp'
		html += '<input type = "submit">'
		html += '<div>'
		html += '<a href="/">' + '<input type="button" value="Return">' + '</a>'
		html += '</form>'
		html += '</fieldset>'
		self.response.out.write(html)

	def post(self):
		html = '<html>'
		html += '<HEAD>' + '<TITLE>GG2S:Register</TITLE>' + self.css + '</HEAD>'
		html += '<body>'
		current_user = users.get_current_user()
		if str(current_user) in BAN_LIST:
			return
		register_id = self.request.get('register_id')
		
		register_id = register_id[:20]
		
		register_id = register_id.replace('<', '&lt')
		register_id = register_id.replace('>', '&gt')
		register_id = register_id.replace('#', '')
		register_id = register_id.replace('&', '')
		register_id = register_id.replace(';', '')
		register_id = register_id.replace('+', '')
		register_id = register_id.replace(',', '')
		register_id = register_id.replace('(', '')
		register_id = register_id.replace(')', '')
		register_id = register_id.replace('[', '')
		register_id = register_id.replace(']', '')
		register_id = register_id.replace('.', '')
		
		if (register_id) == '':
			register_id = ' '
		
		try:
			register_id.decode('ascii')
		except UnicodeDecodeError:
			html += "You can only use ascii character set for your ID!<br>"
			html += '<a href="/register">' + '<input type="button" value="Return">' + '</a>'
		else:
			register_success = UserEntity.query(ndb.OR(UserEntity.user_id == register_id, UserEntity.google_id == current_user))
			if not register_success.count():  #등록 성공
				new_user = self.makeNewAccount(register_id)
				html += 'Register Successful!<br>'
				html += '<fieldset>'
				html += new_user.user_id + "'s Unique ID: " + '<span style="color: yellow">' + str(new_user.key.id()) + '</span>'
				html += '</fieldset>'
				html += '<fieldset>'
				html += '<legend>HOW TO USE</legend>'
				html += '1. <a href="http://gg2statsapp.appspot.com/download/GG2StatsGAE.gml" style="color: yellow;">Download</a> GG2S and put it into GG2\'s \'Plugin\' folder.'
				html += '<br>'
				html += '2. Execute your Gang Garrison 2'
				html += '<br>'
				html += '<img src="http://i66.tinypic.com/2akh2lh.png"><br>'
				html += '3. Click the \'Login\' menu and login with your Unique ID'
				html += '<br>'
				html += '<img src="http://i64.tinypic.com/2jexoxv.png"><br>'
				html += '4. If \'Logout\' button appears, your log-in has succeeded!'
				html += '<br>'
				html += '<a href="/">' + '<input type="button" value="Return">' + '</a>'
			else:
				html += "Nickname already exists or you can't make more than one ID!<br>"
				html += '<a href="/register">' + '<input type="button" value="Return">' + '</a>'
		html += '</body>'
		self.response.out.write(html)
	
	@ndb.transactional(xg=True)
	def makeNewAccount(self, register_id):
		current_user = users.get_current_user()
		new_user = UserEntity()
		new_user.user_id = register_id #닉네임
		new_user.google_id = current_user
		new_user.user_region = str(self.request.headers.get('X-AppEngine-Country'))
		new_user.user_coin = 0
		new_user.put()
		user_key = new_user.key.id()
		new_today = TodayEntity()
		new_today.key = ndb.Key(TodayEntity, user_key)
		new_stat = UserStatEntity()
		new_stat.key = ndb.Key(UserStatEntity, user_key)
		class_stat = ClassEntity()
		class_stat.key = ndb.Key(ClassEntity, user_key)
		loadout = LoadoutEntity()
		loadout.key = ndb.Key(LoadoutEntity, user_key)
		seasons = []
		for i in range(GG2S_CURRENT_SEASON + 1):
			season = SeasonStatEntity()
			season.season = i
			season.season_owner = user_key
			seasons.append(season)
		quest_available = list(range(len(_QUESTS)))
		quest = list()
		for i in range(3):
			quest.append(DailyquestEntity())
		for i in range(3):
			quest[i].quest_type = choice(quest_available)
			quest_available.remove(quest[i].quest_type)
			quest[i].quest_owner = user_key
		ndb.put_multi([new_today, new_stat, class_stat, loadout, quest[0], quest[1], quest[2]] + seasons)
		return new_user

#로그인용 페이지
class LoginPage(webapp2.RequestHandler):
	#인게임의 경우 이 post 메소드를 사용
	def post(self):
		user_key = self.request.get('user_key')
		plugin_version = self.request.get('plugin_version')
		if plugin_version != version:
			self.response.out.write('Need to Update!')
		else:
			try:
				user_key = ndb.Key(UserEntity, int(user_key))
				user = user_key.get()
				if user:
					self.response.out.write('') #Key의 아이디를 반환
				else:
					self.response.out.write('Login Failed')
			except ValueError:
				self.response.out.write('Login Failed')

class GetStatPage(webapp2.RequestHandler):
	def get(self):
		user_id = self.request.get("nickname")
		stat_info = dict()
		
		try:
			user = memcache.get('user:{}'.format(user_id))
			if user is None:
				user = ndb.gql('SELECT * FROM UserEntity WHERE user_id=:id', id = user_id).get()
		except:
			user = ''
		
		if user:
			stat = ndb.Key(UserStatEntity, user.key.id()).get()
			class_stat = ndb.Key(ClassEntity, user.key.id()).get()
			class_kill_list     = [eval(i) for i in class_stat.kill.split(',')]
			class_death_list    = [eval(i) for i in class_stat.death.split(',')]
			class_assist_list   = [eval(i) for i in class_stat.assist.split(',')]
			class_playtime_list = [eval(i) for i in class_stat.playtime.split(',')]
			
			stat_info["nickname"] = user.user_id
			stat_info["clan"] = user.user_clan
			stat_info["fav_class"] = user.user_favclass
			stat_info["region"] = user.user_region
			stat_info["title"] = user.user_title
			stat_info["coin"] = user.user_coin
			stat_info["level"] = user.user_level
			stat_info["exp"] = user.user_exp
			
			stat_info["kill"] = stat.user_kill
			stat_info["death"] = stat.user_death
			stat_info["assist"] = stat.user_assist
			stat_info["capture"] = stat.user_cap
			stat_info["defense"] = stat.user_defense
			stat_info["destruction"] = stat.user_destruction
			stat_info["stab"] = stat.user_stab
			stat_info["healing"] = stat.user_healing
			stat_info["invuln"] = stat.user_invuln
			stat_info["win"] = stat.user_win
			stat_info["lose"] = stat.user_lose
			stat_info["draw"] = stat.user_stalemate
			stat_info["disconnect"] = stat.user_escape
			stat_info["playcount"] = stat.user_playcount
			stat_info["time_total"] = stat.user_playtime
			stat_info["time_red"] = stat.user_redtime
			stat_info["time_blue"] = stat.user_bluetime
			stat_info["time_spectate"] = stat.user_spectime
			for i in range(10):
				class_name = _CLASSES[i].lower()
				stat_info["{}_kill".format(class_name)] = class_kill_list[i]
				stat_info["{}_death".format(class_name)] = class_death_list[i]
				stat_info["{}_assist".format(class_name)] = class_assist_list[i]
				stat_info["{}_playtime".format(class_name)] = class_playtime_list[i]
		
		self.response.out.write(json.dumps(stat_info))
				
#입력용 페이지
class StatUpdatePage(webapp2.RequestHandler):
	def post(self):
		#값 받아오기
		user_key = self.request.get('user_key')
		try:
			#건네받은 값을 검정하는 부분
			int(user_key) #적절한 값인지 검정
			overall_stat = self.request.get('overall_stat')
			overall_stat = overall_stat.split(',')
			overall_stat[0] = int(overall_stat[0])
			overall_stat[1] = int(overall_stat[1])
			overall_stat[2] = int(overall_stat[2])
			if (overall_stat[3]):
				overall_stat[3] = int(overall_stat[3])
			else:
				overall_stat[3] = 0
			if (overall_stat[4]):
				overall_stat[4] = int(overall_stat[4])
			else:
				overall_stat[4] = 0
			if (overall_stat[5]):
				overall_stat[5] = int(overall_stat[5])
			else:
				overall_stat[5] = 0
			if (overall_stat[6]):
				overall_stat[6] = float(overall_stat[6])
			else:
				overall_stat[6] = 0.0
			if (overall_stat[7]):
				overall_stat[7] = int(overall_stat[7])
			else:
				overall_stat[7] = 0
			if (overall_stat[8]):
				overall_stat[8] = int(overall_stat[8])
				if (overall_stat[8] > 20):
					logging.info('Unexpected Value For Invuln: [' + str(user_key) + '] -> ' + str(overall_stat[8]))
					overall_stat[8] = 0
			else:
				overall_stat[8] = 0

			for stat in overall_stat:
				if stat < 0:
					logging.info('Unexpected Value For Overall Stat: [' + str(user_key) + '] -> ' + str(overall_stat))
					return
			
			user_kill = overall_stat[0]
			user_death = overall_stat[1]
			user_assist = overall_stat[2]
			user_cap = overall_stat[3]
			user_destruction = overall_stat[4]
			user_stab = overall_stat[5]
			user_healing = overall_stat[6]
			user_defense = overall_stat[7]
			user_invuln = overall_stat[8]

			overall_playtime = self.request.get('overall_playtime')
			overall_playtime = overall_playtime.split(',')
			for playtime in overall_playtime:
				if playtime < 0:
					playtime = 0
			if (overall_playtime[0]):
				overall_playtime[0] = int(float(overall_playtime[0]))
			else:
				overall_playtime[0]
			if (overall_playtime[1]):
				overall_playtime[1] = int(float(overall_playtime[1]))
			else:
				overall_playtime[1]
			if (overall_playtime[2]):
				overall_playtime[2] = int(float(overall_playtime[2]))
			else:
				overall_playtime[2]
			if (overall_playtime[3]):
				overall_playtime[3] = int(float(overall_playtime[3]))
			else:
				overall_playtime[3]

			for time in overall_playtime:
				if time < 0:
					logging.info('Unexpected Value For Overall Playtime: [' + str(user_key) + '] -> ' + str(overall_playtime))
					return

			user_playtime = overall_playtime[0]
			user_redtime = overall_playtime[1]
			user_bluetime = overall_playtime[2]
			user_spectime = overall_playtime[3]
			
			#DB에 기록하는 부분
			#킬이나 어시를 1이라도 올렸을 경우에만 스탯이 기록된다.
			if (user_kill + user_assist):
				class_timer = self.request.get('class_timer')
				class_kills = self.request.get('class_kills')
				class_deaths = self.request.get('class_deaths')
				class_assists = self.request.get('class_assists')
				timer_list = class_timer.split(',')
				kill_list = class_kills.split(',')
				death_list = class_deaths.split(',')
				assist_list = class_assists.split(',')
				
				for i in range(10):
					timer_list[i] = int(float(timer_list[i]))
					kill_list[i] = int(kill_list[i])
					death_list[i] = int(death_list[i])
					assist_list[i] = int(assist_list[i])
					if timer_list[i] < 0:
						logging.info('Unexpected Value For Class Playtime: [' + str(user_key) + '] -> ' + str(timer_list))
						return
					if kill_list[i] < 0:
						logging.info('Unexpected Value For Class Kill: [' + str(user_key) + '] -> ' + str(kill_list))
						return
					if death_list[i] < 0:
						logging.info('Unexpected Value For Class Death: [' + str(user_key) + '] -> ' + str(death_list))
						return
					if assist_list[i] < 0:
						logging.info('Unexpected Value For Class Assist: [' + str(user_key) + '] -> ' + str(assist_list))
						return
						
				server_name = self.request.get('server_name')
				map_name = self.request.get('map_name')
				player_count = self.request.get('player_count')

				#해당 유저 찾기
				userEntity_key = ndb.Key(UserEntity, int(user_key))
				statEntity_key = ndb.Key(UserStatEntity, int(user_key))
				todayEntity_key = ndb.Key(TodayEntity, int(user_key))
				classEntity_key = ndb.Key(ClassEntity, int(user_key))
				entity_list = ndb.get_multi([userEntity_key, statEntity_key, todayEntity_key, classEntity_key])
				user = entity_list[0]
				stat = entity_list[1]
				today = entity_list[2]
				class_stat = entity_list[3]
				season = ndb.gql('SELECT * FROM SeasonStatEntity WHERE season_owner=:1 AND season=:2', int(user_key), GG2S_CURRENT_SEASON).get()
				
				#값 입력
				stat.user_kill += user_kill
				stat.user_death += user_death
				stat.user_assist += user_assist
				stat.user_playtime += user_playtime
				stat.user_redtime += user_redtime
				stat.user_bluetime += user_bluetime
				stat.user_spectime += user_spectime
				stat.user_cap += user_cap
				stat.user_destruction += user_destruction
				stat.user_stab += user_stab
				stat.user_healing += user_healing
				stat.user_defense += user_defense
				stat.user_invuln += user_invuln
				
				today.user_kill += user_kill
				today.user_death += user_death
				today.user_assist += user_assist
				today.user_cap += user_cap
				today.user_destruction += user_destruction
				today.user_stab += user_stab
				today.user_healing += user_healing
				today.user_defense += user_defense
				today.user_invuln += user_invuln
				
				season.user_kill += user_kill
				season.user_death += user_death
				season.user_assist += user_assist
				season.user_playtime += user_playtime
				season.user_redtime += user_redtime
				season.user_bluetime += user_bluetime
				season.user_spectime += user_spectime
				season.user_cap += user_cap
				season.user_destruction += user_destruction
				season.user_stab += user_stab
				season.user_healing += user_healing
				season.user_defense += user_defense
				season.user_invuln += user_invuln
				
				#kda
				if stat.user_death != 0:
					stat.user_kda = float(stat.user_kill + stat.user_assist)/stat.user_death
				else:
					stat.user_kda = stat.user_kill + stat.user_assist
				if today.user_death != 0:
					today.user_kda = float(today.user_kill + today.user_assist)/today.user_death
				else:
					today.user_kda = today.user_kill + today.user_assist
				if season.user_death != 0:
					season.user_kda = float(season.user_kill + season.user_assist)/season.user_death
				else:
					season.user_kda = season.user_kill + season.user_assist
						
				#클래스별 값 입력
				class_kill = class_stat.kill.split(',')
				class_death = class_stat.death.split(',')
				class_assist = class_stat.assist.split(',')
				class_playtime = class_stat.playtime.split(',')
				season_class_kill = season.class_kill.split(',')
				season_class_death = season.class_death.split(',')
				season_class_assist = season.class_assist.split(',')
				season_class_playtime = season.class_playtime.split(',')
				for i in range(10):
					class_kill[i] = int(class_kill[i])
					class_death[i] = int(class_death[i])
					class_assist[i] = int(class_assist[i])
					class_playtime[i] = int(class_playtime[i])
					season_class_kill[i] = int(season_class_kill[i])
					season_class_death[i] = int(season_class_death[i])
					season_class_assist[i] = int(season_class_assist[i])
					season_class_playtime[i] = int(season_class_playtime[i])
				
				class_list = [0, 2, 8, 4, 5, 6, 3, 7, 1, 9] #상수 리스트가 실제 클래스 번호랑 다르므로 주의
				
				for i in range(10):
					class_playtime[class_list[i]] += timer_list[i]
					class_kill[class_list[i]] += kill_list[i]
					class_death[class_list[i]] += death_list[i]
					class_assist[class_list[i]] += assist_list[i]
					season_class_playtime[class_list[i]] += timer_list[i]
					season_class_kill[class_list[i]] += kill_list[i]
					season_class_death[class_list[i]] += death_list[i]
					season_class_assist[class_list[i]] += assist_list[i]
					
				for i in range(10):
					class_kill[i] = str(class_kill[i])
					class_death[i] = str(class_death[i])
					class_assist[i] = str(class_assist[i])
					class_playtime[i] = str(class_playtime[i])
					season_class_kill[i] = str(season_class_kill[i])
					season_class_death[i] = str(season_class_death[i])
					season_class_assist[i] = str(season_class_assist[i])
					season_class_playtime[i] = str(season_class_playtime[i])
				
				class_stat.kill = ','.join(class_kill)
				class_stat.death = ','.join(class_death)
				class_stat.assist = ','.join(class_assist)
				class_stat.playtime = ','.join(class_playtime)
				season.class_kill = ','.join(season_class_kill)
				season.class_death = ','.join(season_class_death)
				season.class_assist = ','.join(season_class_assist)
				season.class_playtime = ','.join(season_class_playtime)
				
				#승패 판별
				team_win = self.request.get('team_win')
				try:
					team_win = int(team_win)
				except:
					team_win = -1
				
				match_result = ''
				if (team_win == 0):
					match_result = 'Win'
					stat.user_win += 1
					season.user_win += 1
				elif (team_win == 1):
					match_result = 'Lose'
					stat.user_lose += 1
					season.user_lose += 1
				elif (team_win == 2):
					match_result = 'Stalemate'
					stat.user_stalemate += 1
					season.user_stalemate += 1
				elif (team_win == 3):
					match_result = 'Disconnect'
					stat.user_escape += 1
					season.user_escape += 1

				#포인트 계산
				earned_point = 0
				earned_point += 2*user_kill
				earned_point -= 1*user_death
				earned_point += 1*user_assist
				earned_point += 2*user_cap
				earned_point += 1*user_destruction
				earned_point += 1*user_stab
				earned_point += user_healing // 400
				earned_point += 1*user_defense
				earned_point += 4*user_invuln
				earned_point = int(earned_point)	
				
				stat.user_point += earned_point
				today.user_point += earned_point
				season.user_point += earned_point
				
				stat.user_playcount += 1
				today.user_playcount += 1
				season.user_playcount += 1
				
				ndb_put_list = [stat, today, season, class_stat]
				
				'''
				#킬 혹은 포인트가 과도하게 높을 경우 메일
				if user_death != 0:
					cheat_kda = float(user_kill + user_assist)/user_death
				else:
					cheat_kda = user_kill + user_assist
				if (user_kill >= 100 or earned_point >= 200 or cheat_kda >= 10):
					subject = "Cheat Warning for : " + user.user_id
					body = user.user_id + ' has uploaded suspicious stat\n'
					body += 'Server Name: ' + server_name + '\n'
					body += 'Map Name: ' + map_name + '\n'
					body += 'Player Count: ' + player_count + '\n' 
					body += 'Match Result: ' + match_result + '\n'
					body += 'Earned Point: ' + str(earned_point) + '\n'
					body += 'Times played: ' + makePlaytimeTemplate(user_playtime) + '\n'
					body += 'Times played as spectator: ' + makePlaytimeTemplate(user_spectime) + '\n' 
					body += 'Kill: ' + str(user_kill) + '\n'
					body += 'Death: ' + str(user_death) + '\n'
					body += 'Assist: ' + str(user_assist) + '\n'
					body += 'Cap: ' + str(user_cap) + '\n'
					body += 'Dest: ' + str(user_destruction) + '\n'
					body += 'Stab: ' + str(user_stab) + '\n'
					body += 'Healing: ' + str(user_healing) + '\n'
					body += 'Defense: ' + str(user_defense) + '\n'
					body += 'Invuln: ' + str(user_invuln) + '\n'
					
					_timer_list = list()
					_kill_list = list()
					_death_list = list()
					_assist_list = list()
					
					for i in range(10):
						_timer_list.append(str(timer_list[i]))
						_kill_list.append(str(kill_list[i]))
						_death_list.append(str(death_list[i]))
						_assist_list.append(str(assist_list[i]))
					
					body += 'C_Playtime: ' + ','.join(_timer_list) + '\n'
					body += 'C_Kill: ' + ','.join(_kill_list) + '\n'
					body += 'C_Death: ' + ','.join(_death_list) + '\n'
					body += 'C_Assist: ' + ','.join(_assist_list) + '\n'
					user_address = "WN <saiyu915@naver.com>"
					sender_address = "GG2S Support <noreply@gg2statsapp.appspotmail.com>"
					mail.send_mail(sender_address, user_address, subject, body)
				'''
				
				#레벨 계산
				gotExp = 4*(user_playtime/30 - user_spectime/30)
				
				if (gotExp > 0):
					requiredExp = getMaxExp(user.user_level)
					if (user.user_exp + gotExp > requiredExp):
						if (user.user_level >= 99):
							pass
						else:
							user.user_level += 1
							user.user_coin += 100
							user.user_exp = 0
							log = LogEntity()
							log.log_content = 'Leveled up to ' + makeLevelTemplate(user.user_level)
							log.log_owner = user.google_id
							ndb_put_list.append(log)
					else:
						user.user_exp += gotExp
					if (user.user_level >= 99):
						user.user_exp = 0
						
				#퀘스트 계산
				quest_list = ndb.gql('SELECT * FROM DailyquestEntity WHERE quest_owner=:1', user.key.id())
				if (quest_list.count()):
					statList = list()
					statList.append(overall_stat)
					statList.append(overall_playtime)
					statList.append(kill_list)
					statList.append(death_list)
					statList.append(assist_list)
					statList.append(timer_list)
					win_list = [0, 0, 0, 0]
					win_list[team_win] += 1
					statList.append(win_list)
					for quest in quest_list:
						#한개짜리
						if (type(_QUESTS[quest.quest_type][5]) != list):
							if (quest.quest_count + statList[_QUESTS[quest.quest_type][4]][_QUESTS[quest.quest_type][5]] >= _QUESTS[quest.quest_type][2]):
								user.user_coin += _QUESTS[quest.quest_type][3]
								ndb.Key(DailyquestEntity, quest.key.id()).delete()
							else:
								quest.quest_count += int(statList[_QUESTS[quest.quest_type][4]][_QUESTS[quest.quest_type][5]])
								ndb_put_list.append(quest)
						#여러개짜리
						else:
							count_total = 0
							for i in _QUESTS[quest.quest_type][5]:
								count_total += int(statList[_QUESTS[quest.quest_type][4]][i])
							if (quest.quest_count + count_total >= _QUESTS[quest.quest_type][2]):
								user.user_coin += _QUESTS[quest.quest_type][3]
								ndb.Key(DailyquestEntity, quest.key.id()).delete()
							else:
								quest.quest_count += count_total
								ndb_put_list.append(quest)
					memcache.delete('questInfo-' + str(user.key.id()))
				
				#매치 기록
				try:
					match_myself = int(self.request.get('match_myself'))
				except:
					match_myself = -1
				if match_myself > -1:
					match = MatchEntity()
					match.match_result = team_win
					match.match_kill = user_kill
					match.match_death = user_death
					match.match_assist = user_assist
					match.match_playtime = user_redtime + user_bluetime
					match.match_server = server_name
					match.match_mode = self.request.get('match_mode')
					match.match_map = map_name
					match.match_redteam = self.request.get('match_redteam')
					match.match_blueteam = self.request.get('match_blueteam')
					match.match_score = self.request.get('match_score')
					match.match_owner = user.key.id()
					match.match_myself = match_myself
					ndb_put_list.append(match)

				ndb_put_list.append(user)
				
				#Save
				ndb.put_multi(ndb_put_list)
			
			else: # 킬이나 어시를 1이라도 올리지 않았을 경우
				#플레이타임만 기록한다, 퀘스트는 깨지지 않는다
				stat = ndb.Key(UserStatEntity, int(user_key)).get()
				stat.user_playtime += user_playtime
				stat.user_redtime += user_redtime
				stat.user_bluetime += user_bluetime
				stat.user_spectime += user_spectime
				
				season = ndb.gql('SELECT * FROM SeasonStatEntity WHERE season_owner=:1 AND season=:2', int(user_key), GG2S_CURRENT_SEASON).get()
				season.user_playtime += user_playtime
				season.user_redtime += user_redtime
				season.user_bluetime += user_bluetime
				season.user_spectime += user_spectime
				
				ndb.put_multi([stat, season])

		except ValueError: #Error occured during changing str value to integer value
			pass
			
class TestUpdatePage(webapp2.RequestHandler):
	def get(self):
		current_user = users.get_current_user()
		user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
		html = '<HTML>'
		html += '<form action="/statupdate" method="POST">'
		html += '<input type="hidden" name="user_key" value="{}">'.format(user.key.id())
		html += 'overall_stat: <input type="text" name="overall_stat" value="0,0,0,0,0,0,0,0,0">'
		html += '<br />'
		html += 'overall_playtime: <input type="text" name="overall_playtime" value="0,0,0,0">'
		html += '<br />'
		html += 'class_timer: <input type="text" name="class_timer" value="0,0,0,0,0,0,0,0,0,0">'
		html += '<br />'
		html += 'class_kills: <input type="text" name="class_kills" value="0,0,0,0,0,0,0,0,0,0">'
		html += '<br />'
		html += 'class_deaths: <input type="text" name="class_deaths" value="0,0,0,0,0,0,0,0,0,0">'
		html += '<br />'
		html += 'class_assists: <input type="text" name="class_assists" value="0,0,0,0,0,0,0,0,0,0">'
		html += '<br />'
		html += 'server_name: <input type="text" name="server_name" value="SERVER">'
		html += '<br />'
		html += 'map_name: <input type="text" name="map_name" value="ctf_truefort">'
		html += '<br />'
		html += 'player_count: <input type="text" name="player_count" value="1">'
		html += '<br />'
		html += 'team_win: <input type="text" name="team_win" value="0">'
		html += '<br />'
		html += 'match_myself: <input type="text" name="match_myself" value="-1">'
		html += '<br />'
		html += '<input type="submit">'
		html += '</form>'
		html += '</HTML>'
		
		self.response.out.write(html)
			
class UpdateStrangePage(webapp2.RequestHandler):
	def post(self):
		#값 받아오기
		user_key = self.request.get('user_key')
		user_key = int(user_key) #적절한 값인지 검정

		#해당 유저 찾기
		loadout = ndb.Key(LoadoutEntity, user_key).get()
		weapon_list = loadout.weapon_list.split(',')
		strange_list = self.request.get('strange_count')
		strange_list = strange_list.split(',')
		for i in range(10):
			strange_list[i] = int(strange_list[i])
			if (strange_list[i] < 0):
				strange_list[i] = 0
			if (weapon_list[i] != ''):
				weapon_list[i] = int(weapon_list[i])

		for i in range(10):
			if strange_list[i] != 0:
				weapon = ndb.Key(BackpackEntity, weapon_list[i]).get()
				weapon.item_strangeCount += strange_list[i]
				weapon.put()

#포인트 및 등수 확인용 페이지(인게임)
class PointViewPage(webapp2.RequestHandler):
	def post(self):
		user_key = self.request.get('user_key')
		user = ndb.Key(UserEntity, int(user_key)).get()
		stat = ndb.Key(UserStatEntity, int(user_key)).get()
		user_point = stat.user_point
		user_list = ndb.gql("SELECT * FROM UserStatEntity WHERE user_point>=:1 ORDER BY user_point DESC", user_point)
		user_rank = user_list.count()
		self.response.out.write(str(user_rank))
		self.response.out.write(',')
		self.response.out.write(str(user_point))
		self.response.out.write(',')
		self.response.out.write(user.user_message)
		
#검색페이지
class SearchPage(webapp2.RequestHandler):
	def get(self):
		html = '<HTML>'
		html += '<HEAD>'
		html += '<TITLE>GG2S:Search</TITLE>'
		html += '<script src="/js/jquery.js"></script>'
		html += '<script src="/js/search.js"></script>'
		html += "<link rel='stylesheet prefetch' href='https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css'>"
		html += '<link rel="stylesheet" type="text/css" href="/css/search.css">'
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</HEAD>'
		
		html += '<body>'
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '<div class="head-search">'
		html += 'NICKNAME: '
		html += '<input type="text" name="user_id" id="search-input" placeholder="INPUT NICKNAME" class="head-search-input" autocomplete="off" />'
		html += '<button type="submit" id="search-submit" class="ion ion-search" onclick="submitInput()">'
		html += '</div>' #head-search
		html += '</div>' #head-wrapper
		
		html += '<div class="result-wrapper">'
		html += '<div id="search-result">'
		html += '</div>' #search-result
		html += '</div>' #result-wrapper
		
		html += '</body>'
		html += '</HTML>'
		self.response.out.write(html)

#유저검색결과페이지
class SearchResultPage(webapp2.RequestHandler):
	def get(self):
		user_id = self.request.get('id')
		
		html = '<div id="result-content">'
		try:
			user_list = ndb.gql('SELECT user_id FROM UserEntity')
			cnt = 0
			for user in user_list:
				if user_id.lower() in user.user_id.lower():
					cnt += 1
					html += '<div class="user-wrapper">'
					html += '<div class="user-info">'
					html += '<div id="user-rank">' + str(cnt) + '</div>'
					html += '<div id="user-id">'
					html += '<a href="profile?id={}">'.format(user.user_id) + user.user_id.upper() + '</a>'
					html += '</div>' #user-id
					html += '</div>' #user-info
					html += '</div>' #user-wrapper
			if not cnt:
				html += '<div class="user-info">'
				html += 'USER NOT FOUND!'
				html += '</div>'
		except:
			html += '<div class="user-info">'
			html += 'AN ERROR OCCURED, CHECK YOUR INPUT!'
			html += '</div>'
		html += '</div>'
		self.response.out.write(html)
	
#RANK페이지
class RankPage(webapp2.RequestHandler):
	def get(self):
		page = self.request.get('page')
		if (page == ''):
			page = 1
		else:
			try:
				page = int(page)
			except:
				self.redirect('/rank')

		html = '<!DOCTYPE HTML>'
		html += '<HTML>'
		html += '<HEAD>'
		html += '<TITLE>GG2S:LEADERBOARD</TITLE>'
		html += '<link rel="stylesheet" type="text/css" href="/css/rank.css">'
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</HEAD>'
		html += '<BODY>'
		
		rankInfo = memcache.get('rank:' + str(page))
		user_number = memcache.get('user_number')
		if rankInfo is None:
			stat_list = UserStatEntity.query()
			user_number = stat_list.count()
			stat_list = stat_list.order(-UserStatEntity.user_point).fetch(10, offset=10*(int(page)-1))
			stat_list = [stat for stat in stat_list]
			user_list = [ndb.Key(UserEntity, stat.key.id()) for stat in stat_list]
			user_list = ndb.get_multi(user_list)
			trophy_list = [ndb.gql('SELECT * FROM TrophyEntity WHERE trophy_owner=:1 ORDER BY trophy_getdate ASC', user.key.id()) for user in user_list]
			trophy_list = [[trophy for trophy in trophy_innerlist] for trophy_innerlist in trophy_list]
			rankInfo = [user_list, stat_list, trophy_list]
			memcache.add('rank:' + str(page), rankInfo, 10800) #3hours
		else:
			user_list = rankInfo[0]
			stat_list = rankInfo[1]
			trophy_list = rankInfo[2]
			
		if user_number is None:
			user_number = ndb.gql('SELECT __key__ FROM UserStatEntity').count()
			memcache.add('user_number', user_number, 10800) #3hours
		
		html += '<div class="page-wrapper">'
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '<div class="page-selector-wrapper">'
		for i in range(((user_number - 1) // 10) + 1):
			if (page == i + 1):
				html += '<a id="selected" href="/rank?page={}">{:3d}</a>'.format(i + 1, i + 1)
			else:
				html += '<a href="/rank?page={}">{:3d}</a>'.format(i + 1, i + 1)
			if not ((i + 1) % 20) and (i != ((user_number - 1) // 10)):
				html += '</div>'
				html += '<div class="page-selector-wrapper">'
		html += '</div>' #page-selector-wrapper
		html += '</div>' #head-wrapper
		
		html += '<div class="body-wrapper">'
		html += '<div class="body-user-wrapper">'
		for i in range(len(user_list)):
			user = user_list[i]
			stat = stat_list[i]
			trophy_innerlist = trophy_list[i]
			html += '<div class="user-wrapper">'
			html += '<div class="trophies-wrapper">'
			for trophy in trophy_innerlist:
				html += '<img src="/{}" />'.format(ProfilePage2.getTrophyImage(trophy.trophy_index))
			html += '</div>' #trophies-wrapper
			html += '<div class="user-info">'
			html += '<span id="user-rank">{}</span>'.format(10*(page - 1) + i + 1)
			html += '<a href="/profile?id={}"><span id="user-id">{}</span></a>'.format(user.user_id, user.user_id.upper())
			html += '<span id="user-level">LV.{} {}</span>'.format(user.user_level, user.user_favclass.upper())
			html += '<span id="user-region">{}</span>'.format(user.user_region)
			html += '</div>' #user-info
			html += '<div class="user-stat">'
			html += '<div class="stats-wrapper">'
			html += '<span id="user-point">{}</span>'.format(stat.user_point)
			html += '<span id="user-kill">{}</span>'.format(strlize(stat.user_kill))
			html += '<span id="user-death">{}</span>'.format(strlize(stat.user_death))
			html += '<span id="user-assist">{}</span>'.format(strlize(stat.user_assist))
			html += '<span id="user-kda">{:.2f}</span>'.format(stat.user_kda)
			html += '<span id="user-playtime">{}</span>'.format(makePlaytimeTemplate(stat.user_playtime))
			html += '<span id="user-playcount">{}</span>'.format(stat.user_playcount)
			html += '</div>' #stats-wrapper
			html += '</div>' #user-stat
			html += '</div>' #user-wrapper
		html += '</div>' #body-user-wrapper
		html += '</div>' #body-wrapper
		html += '</div>' #page-wrapper
		
		html += '</BODY>'
		html += '</HTML>'
		self.response.out.write(html)

class RankPage2(webapp2.RequestHandler):
	def get(self):
		css = "<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet'>"
		css += '''
			<style>
			html {
			  width: 100%;
			  background-color: #252525;
			  text-align: center;
			}
			body {
			  display: inline-block;
			  margin-top: 20px;
			  width: 80%;
			  font-family: 'Press Start 2P', sans-serif;
			}
			.highscore-wrapper {
			  width: 100%;
			  margin-bottom: 100px;
			}
			.highscore-1p, .highscore, .highscore-2p {display: inline-block; width: 33%;}
			.highscore-1p {text-align: left; color: rgb(68, 216, 66);}
			.highscore {text-align: center; color: rgb(222, 11, 4);}
			.highscore-2p {text-align: right; color: rgb(70, 160, 194);}
			#score {color: white;}
			.userlist-wrapper {width: 100%; color: white;}
			table {text-align: right; border-spacing: 10px;}
			table .user_id {text-align: center;}
			table td {padding: 0 20px 0 20px;}
			</style>
		'''
		html = '<!DOCTYPE html>'
		html += '<html>'
		html += '<head><title>GG2S: Rank</title>' + css + '</head>'
		html += '<body>'
		
		html += '<div class="highscore-wrapper">'
		
		html += '<div class="highscore-title">'
		html += '<div class="highscore-1p">1UP&nbsp</div>'
		html += '<div class="highscore">HIGH SCORE</div>'
		html += '<div class="highscore-2p">2UP&nbsp</div>'
		html += '</div>'
		
		html += '<div class="highscore-point">'
		html += '<div class="highscore-1p" id="score">&nbsp&nbsp00</div>'
		html += '<div class="highscore" id="score">42600</div>'
		html += '<div class="highscore-2p" id="score">&nbsp&nbsp00</div>'
		html += '</div>'
		
		html += '</div>' #<!--highscore-wrapper-->
		
		html += '<div class="userlist-wrapper">'
		html += '<span style="font-size: 40px;">TOP10<br><br>SEASON ' + str(GG2S_CURRENT_SEASON) + '</span>'
		html += '<table align="center">'
		html += '<tbody>'
		season_list = SeasonStatEntity.query().filter(SeasonStatEntity.season==GG2S_CURRENT_SEASON).order(-SeasonStatEntity.user_point).fetch(10)
		cnt = 0
		for season in season_list:
			cnt += 1
			user = ndb.Key(UserEntity, season.season_owner).get()
			html += '<tr>'
			html += '<td>' + str(cnt) + '.</td>'
			html += '<td class="user_id">' + user.user_id + '</td>'
			html += '<td>' + str(user.user_level) + '</td>'
			html += '<td>' + str(season.user_point) + '</td>'
			html += '</tr>' 
		
		html += '</tbody>'
		html += '</table>'
		html += '</div>'
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)

#프로필페이지
class ProfilePage(webapp2.RequestHandler):
	@classmethod
	def getTrophyName(self, trophy_index):
		if (trophy_index == 0):
			return "Beta Gang"
		elif (trophy_index == 1):
			return "Beta-1st"
		elif (trophy_index == 2):
			return "Beta-2nd"
		elif (trophy_index == 3):
			return "Beta-3rd"

	@classmethod
	def getTrophyDesc(self, trophy_index):
		if (trophy_index == 0):
			return "Rewarded for participating GG2S&GG2I Beta"
		elif (trophy_index == 1):
			return "Rewarded for 1st prize in Beta season"
		elif (trophy_index == 2):
			return "Rewarded for 2nd prize in Beta season"
		elif (trophy_index == 3):
			return "Rewarded for 3rd prize in Beta season"

	@classmethod
	def getTrophyImage(self, trophy_index):
		if (trophy_index == 0):
			return "images/trophy_beta_gang.png"
		elif (trophy_index == 1):
			return "images/trophy_no_1.png"
		elif (trophy_index == 2):
			return "images/trophy_no_2.png"
		elif (trophy_index == 3):
			return "images/trophy_no_3.png"

	def get(self):
		html = '<!doctype html>'
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					background-color: #454545;
					color: white;
					font-family: 'Press Start 2P', sans-serif, cursive;
					vertical-align: middle;
				}
				img {
				  width: inherit;
				  max-width: 100%;
				  height: auto;
				}
				p.logobig{
					display: table;
					margin: auto;
					margin-top: 50px;
					margin-bottom: 50px;
				}
				div.ProfileTop{
					margin: auto;
					width: 1120px;
					display: table;
					margin-top: 20px;
					margin-bottom: 20px;
					line-height: 1.6;
					float: left;
				}
				p.avatar{
					width: 200px;
					height: 200px;
					Border: 5px;
					border-style: solid;
					border-radius:0.4em;
					display: table-cell;
					margin-left: 30px;
					margin-right: 30px;
					vertical-align: middle;
					text-align: center;
					float: left;
				}
				p.LevelTag{
					float: left;
					margin-right: 30px;
				}
				thead{
					color: #8E8464;
				}
				th{
					font-weight: normal;
				}
				table.stat{
					margin-left: 30px;
					margin-right: 30px;
					text-align: center;
					border-spacing: 10px 5px;
					border-collapse: separate;
					float: left;
				}
				div.MainLeft{
					clear: left;
					float: left;
				}
				p.SeasonSelect{
					text-align: right;
				}
				fieldset{
					margin-bottom:20px;
				}
				fieldset.message{
					float:left;
					width: 807px;
				}
				fieldset.team{
					clear: left;
					float: left;
					width: 280px;
					height: 384px;
				}
				fieldset.class{
					width: 495px;
					height: 384px;
				}
				table.class{
					height: 340px;
					border-spacing: 5px;
				}
				div.timechart{
					margin-top: 5px;
				}
				td.teamtime{
					width: 80px;
					text-align: center;
				}
				fieldset.class_details{
					CLEAR:LEFT;
					width: 807px;
				}
				div.MainRight{
					
				}
			</style>
		"""
		user_id = self.request.get('id')
		user_list = ndb.gql('SELECT * '
			'FROM UserEntity '
			'WHERE user_id=:id'
			, id = user_id)
		user = user_list.get()
			
		if user:
			user_key = user.key.id()
			data_season = self.request.get('season')
			if (data_season):
				stat = ndb.Key(SeasonStatEntity, data_season + str(user_key)).get()
				try:
					class_kill = stat.class_kill.split(',')
					class_death = stat.class_death.split(',')
					class_assist = stat.class_assist.split(',')
					class_playtime = stat.class_playtime.split(',')
				except:
					stat = ndb.Key(UserStatEntity, user_key).get()
					class_stat = ndb.Key(ClassEntity, user_key).get()
					class_kill = class_stat.kill.split(',')
					class_death = class_stat.death.split(',')
					class_assist = class_stat.assist.split(',')
					class_playtime = class_stat.playtime.split(',')
			else:
				stat = ndb.Key(UserStatEntity, user_key).get()
				class_stat = ndb.Key(ClassEntity, user_key).get()
				class_kill = class_stat.kill.split(',')
				class_death = class_stat.death.split(',')
				class_assist = class_stat.assist.split(',')
				class_playtime = class_stat.playtime.split(',')
			for i in range(10):
				class_kill[i] = int(class_kill[i])
				class_death[i] = int(class_death[i])
				class_assist[i] = int(class_assist[i])
				class_playtime[i] = int(class_playtime[i])
			script = '<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>'
			script += '<script type="text/javascript">'
			script += "google.charts.load('current', {'packages':['bar']});"
			script += "google.charts.setOnLoadCallback(drawChart);"
			script += "function drawChart() {"
			script += "var class_time_data = google.visualization.arrayToDataTable(["
			script += "['Class', 'Time'],"
			for i in range(10):
				if not i == 9:
					script += "['" + _CLASSES[i] + "'," + str(class_playtime[i]) + "],"
				else:
					script += "['" + _CLASSES[i] + "'," + str(class_playtime[i]) + "]"
			script += "]);"
			script += "var team_time_data = google.visualization.arrayToDataTable(["
			script += "['TEAM', 'Time'],"
			script += "['RED', " +  str(stat.user_redtime) + "],"
			script += "['BLUE', " + str(stat.user_bluetime) + "],"
			script += "['SPECTATOR', " + str(stat.user_spectime) + "]"
			script += "]);"
			script += "var class_kda_data = google.visualization.arrayToDataTable(["
			script += "['Class', 'Kill', 'Death', 'Assist'],"
			for i in range(10):
				if not i == 9:
					script += "['" + _CLASSES[i] + "'," + str(class_kill[i]) + ", " + str(class_death[i]) + ", " + str(class_assist[i]) + "],"
				else:
					script += "['" + _CLASSES[i] + "'," + str(class_kill[i]) + ", " + str(class_death[i]) + ", " + str(class_assist[i]) + "]"
			script += "]);"
			script += "var options_class_time = {"
			script += "width: 335,"
			script += "height: 362,"
			script += "bars: 'horizontal',"
			script += 'backgroundColor: "#454545",'
			script += 'bar: {groupWidth: "80%"},'
			script += 'legend: { position: "none" }'
			script += "};"
			script += "var options_team_time = {"
			script += "width: 270,"
			script += "height: 340,"
			script += 'backgroundColor: "#454545",'
			script += 'bar: {groupWidth: "80%"},'
			script += 'legend: { position: "none" }'
			script += "};"
			script += "var options_class_kda = {"
			script += "width: 800,"
			script += "height: 362,"
			script += 'backgroundColor: "#454545",'
			script += "colors: ['tomato', 'royalblue', 'darkorange'],"
			script += 'bar: {groupWidth: "80%"},'
			script += 'legend: { position: "none" }'
			script += "};"
			script += "var class_time_chart = new google.charts.Bar(document.getElementById('class_time_barchart'));"
			script += "class_time_chart.draw(class_time_data, google.charts.Bar.convertOptions(options_class_time));"
			script += "var team_time_chart = new google.charts.Bar(document.getElementById('team_time_barchart'));"
			script += "team_time_chart.draw(team_time_data, google.charts.Bar.convertOptions(options_team_time));"
			script += "var class_kda_chart = new google.charts.Bar(document.getElementById('class_kda_barchart'));"
			script += "class_kda_chart.draw(class_kda_data, google.charts.Bar.convertOptions(options_class_kda));"
			script += "}"
			script += 'function changeSeason(){'
			script += "var season = document.getElementById('season').value;"
			script += "var seasonValue = parseInt(season);"
			script += "if (seasonValue <= " + str(GG2S_CURRENT_SEASON) + "){"
			script += "if (seasonValue == -1) {window.location.href='/profile?id=" + user_id + "';}"
			script += "else {window.location.href='/profile?id=" + user_id + "&season=' + season;}}"
			script += "}</script>"
			
			html += '<HTML>'
			html += '<HEAD>' + '<TITLE>GG2S:Profile</TITLE>' + css + script + '</HEAD>'
			html += '<BODY>'
			html += '<div>'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			#아바타
			html += '<div class="ProfileTop">'
			html += '<p class="avatar">'
			if user.user_avatar:
				html +='<img style="width: 200px; height: 200px; margin-bottom: 20px;" src="/upload?img_id=%s"></img>' %user.key.urlsafe()
			else:
				html +='<img src="/images/gg2slogo_200.png" style="margin-bottom: 20px;">'
			current_user = users.get_current_user()
			if user.google_id == current_user:
				html += '<span style="color: gold;">' + str(user.user_coin) + 'G' + '</span>'
			html += '</p>'
			#스탯 표
			if (stat.user_lose + stat.user_win > 0):
				winrate = 100*stat.user_win/float(stat.user_win + stat.user_lose)
			else:
				winrate = 0.0
			if (stat.user_win+stat.user_lose+stat.user_stalemate+stat.user_escape > 0):
				escaperate = 100*(stat.user_escape/float(stat.user_win+stat.user_lose+stat.user_stalemate+stat.user_escape))
			else:
				escaperate = 0.0
			html += '<table class="stat">'
			html += '<thead>'
			if (user.user_clan):
				found_image = findClanImage(user.user_clan)
				if found_image != '':
					html += '<th colspan="6">' + '<img src="' + found_image + '">' + '</th>'
				else:
					html += '<th colspan="6">' + user.user_clan + '</th>'
			html += '</thead>'
			html += '<thead>'
			html += '<th colspan="6" style="color:white; text-decoration:none;">'
			html += user.user_id
			html += '<select id="season" name="season" onchange="changeSeason()" style="float: right;">'
			html += '<option value="-1">Total</option>'
			if (data_season == '0'):
				html += '<option value="0" selected>Beta</option>'
			else:
				html += '<option value="0">Beta</option>'
			for i in range(GG2S_CURRENT_SEASON):
				if (data_season):
					if (int(data_season) == i + 1):
						html += '<option value="' + str(i + 1) + '" selected>Season ' + str(i + 1) + '</option>'
					else:
						html += '<option value="' + str(i + 1) + '">Season ' + str(i + 1) + '</option>'
				else:
					html += '<option value="' + str(i + 1) + '">Season ' + str(i + 1) + '</option>'
			html += '</select>'
			html += '</th>'
			html += '</thead>'
			html += '<thead>'
			html += '<th>' + '<img src="/images/k_icon.png">' +  '</th>'
			html += '<th>' + '<img src="/images/d_icon.png">' +  '</th>'
			html += '<th>' + '<img src="/images/a_icon.png">' +  '</th>'
			html += '<th>' + '<img src="/images/kda_icon.png">' +  '</th>'
			html += '<th>' + 'PlayTime' +  '</th>'
			html += '<th>' + '<img src="/images/p_icon.png">' +  '</th>'
			html += '</thead>'
			html += '<tbody>'
			html += '<tr>'
			html += '<td>' + strlize(stat.user_kill) + '</td>'
			html += '<td>' + strlize(stat.user_death) + '</td>'
			html += '<td>' + strlize(stat.user_assist) + '</td>'
			html += '<td>' + "%.1f" %stat.user_kda + '</td>'
			html += '<td>' + makePlaytimeTemplate(stat.user_playtime) + '</td>'
			html += '<td>' + strlize(stat.user_playcount) + '</td>'
			html += '</tr>'
			html += '</tbody>'
			html += '<thead>'
			html += '<th>' + 'Cap' +  '</th>'
			html += '<th>' + 'Des' +  '</th>'
			html += '<th>' + 'Stab' +  '</th>'
			html += '<th>' + 'Def' +  '</th>'
			html += '<th>' + 'Heal' +  '</th>'
			html += '<th>' + 'Uber' +  '</th>'
			html += '</thead>'
			html += '<tbody>'
			html += '<tr>'
			html += '<td>' + strlize(stat.user_cap) + '</td>'
			html += '<td>' + strlize(stat.user_destruction) + '</td>'
			html += '<td>' + strlize(stat.user_stab) + '</td>'
			html += '<td>' + strlize(stat.user_defense) + '</td>'
			html += '<td>' + strlize(stat.user_healing) + '</td>'
			html += '<td>' + strlize(stat.user_invuln) + '</td>'
			html += '</tr>'
			html += '<thead>'
			html += '<th>' + 'Win' +  '</th>'
			html += '<th>' + 'Lose' +  '</th>'
			html += '<th>' + 'Draw' +  '</th>'
			html += '<th>' + 'Esc' +  '</th>'
			html += '<th>' + 'W/L' +  '</th>'
			html += '<th>' + 'E/T' +  '</th>'
			html += '</thead>'
			html += '<tbody>'
			html += '<tr>'
			html += '<td>' + strlize(stat.user_win) + '</td>'
			html += '<td>' + strlize(stat.user_lose) + '</td>'
			html += '<td>' + strlize(stat.user_stalemate) + '</td>'
			html += '<td>' + strlize(stat.user_escape) + '</td>'
			html += '<td>' + "%.f" %winrate + '%' + '</td>'
			html += '<td>' + "%.f" %escaperate + '%' + '</td>'
			html += '</tr>'
			html += '<tr>'
			html += '<td colspan="6" style="color: gold;">' +"Total Point: " + str(stat.user_point) + '</td>'
			html += '</tr>'
			html += '</tbody>'
			html += '</table>'
			html += '<p class="LevelTag">'
			html += '<span style="font-size:24px;">Level&nbsp' + makeLevelTemplate(user.user_level) + '</span>'
			html += '</p>'
			requiredExp = getMaxExp(user.user_level)
			expPercentage = int(user.user_exp*100.0/requiredExp)
			html += '<table style="width: 200px; margin-bottom: 40px; border-spacing: 0px;">'
			html += '<tbody>'
			html += '<tr>'
			html += '<td colspan=' + str(expPercentage) + ' style="background-color:yellow;">' + '</td>'
			html += '<td colspan=' + str(100 - expPercentage) + ' style="background-color:grey;">' + '</td>' #for blank space
			html += '</tr>'
			html += '<tr>'
			for i in range(100):
				html += '<td>' + '</td>'
			html += '</tr>'
			html += '<tr>'
			html += '<td colspan=50 style="text-align: left;">' + str(user.user_level) + '</td>'
			html += '<td colspan=50 style="text-align: right;">' + str(user.user_level + 1) + '</td>'
			html += '</tr>'
			html += '</tbody>'
			html += '</table>'
			if user.google_id == current_user:
				html += '<a href="/profilesetting" style="color:white; vertical-align: bottom;">Edit Profile</a>&nbsp&nbsp'
			html += '</div>'
			#페이지 하단 2단 구성 중 좌측
			html += '<div class="MainLeft">'
			html += '<fieldset class="message">'
			html += '<LEGEND>Message</LEGEND>'
			html += user.user_word
			html += '</fieldset>'
			html += '<FIELDSET class="team">'
			html += '<LEGEND>Playtime.Team</LEGEND>'
			html += '<p class="timechart" id="team_time_barchart"></p>'
			redtime = makePlaytimeTemplate(stat.user_redtime)
			bluetime = makePlaytimeTemplate(stat.user_bluetime)
			spectime = makePlaytimeTemplate(stat.user_spectime)
			html += '<table style="width:255px; margin-left:20px; font-size:9px; position: relative; top: -30px;">'
			html += '<tr>'
			html += '<td class="teamtime">' + redtime + '</td>'
			html += '<td class="teamtime">' + bluetime + '</td>'
			html += '<td class="teamtime">' + spectime + '</td>'
			html += '</tr>'
			html += '</table>'
			html += '</FIELDSET>'
			html += '<FIELDSET class="class">'
			html += '<LEGEND>Playtime.Class</LEGEND>'
			html += '<table class="class" style="float: left; position: relative; top: 15px; left: 5px;">'
			for i in range(10):
				html += '<tr><td><img src="'+  findClassImage(_CLASSES[i]) + '"></td><td>' + makePlaytimeTemplate(class_playtime[i]) + '</td></tr>' 
			html += '</table>'
			html += '<p class="timechart" id="class_time_barchart" style="float: left;"></p>'
			html += '</FIELDSET>'
			html += '<FIELDSET class="class_details">'
			html += '<LEGEND>Class.Details</LEGEND>'
			html += '<p id="class_kda_barchart"></p>'
			html += '<table style="width:800px; text-align:center;">'
			html += '<thead>'
			html += '<th></th>' #INDEX용
			for i in range(10):
				html += '<th><img src="'+  findClassImage(_CLASSES[i]) + '"></th>' 
			html += '</thead>'
			#K
			html += '<tr>'
			html += '<td><img src="/images/k_icon.png"></td>'
			for each_stat in class_kill:
				html += '<td>' + strlize(each_stat) + '</td>' 
			html += '</tr>'
			#D
			html += '<tr>'
			html += '<td><img src="/images/d_icon.png"></td>'
			for each_stat in class_death:
				html += '<td>' + strlize(each_stat) + '</td>' 
			html += '</tr>'
			#A
			html += '<tr>'
			html += '<td><img src="/images/a_icon.png"></td>'
			for each_stat in class_assist:
				html += '<td>' + strlize(each_stat) + '</td>' 
			html += '</tr>'
			#KDA
			html += '<tr>'
			html += '<td><img src="/images/kda_icon.png"></td>'
			for i in range(10):
				kda = 0.0
				if class_death[i] is not 0:
					kda = (class_kill[i]+class_assist[i])/float(class_death[i])
				else:
					kda = class_kill[i]+class_assist[i]
				html += '<td>' + "%.1f" %kda +  '</td>' 
			html += '</tr>'
			html += '</table>'
			html += '</FIELDSET>'
			html += '<br>'
			html += '</div>'
			
			#페이지 하단 2단 구성 중 우측
			html += '<div class="MainRight">'
			html += '<fieldset><legend>Trophies</legend>'
			trophy_list = ndb.gql('SELECT * FROM TrophyEntity WHERE trophy_owner=:1', user.key.id()).order(TrophyEntity.trophy_getdate)
			if (trophy_list.count()):
				for trophy in trophy_list:
					html += '<p>'
					html += '<img src="' + self.getTrophyImage(trophy.trophy_index) + '" title="' + self.getTrophyDesc(trophy.trophy_index) + '" style="margin-right: 10px;">'
					html += '<span style="font-size: 20px; color: yellow;">' + self.getTrophyName(trophy.trophy_index) + '</span>'
					html += '</p>'
			else:
				html += 'No Trophies Available!'
			html += '</fieldset>'
			html += '</div>'
			html += '<div style="text-align: center; margin-bottom:50px; clear:left;">'
			html += '<a href="/backpack?id=' + user.user_id + '" style="color:white;">Backpack</a>&nbsp&nbsp'
			html += '<a href="/" style="color:white;">Return</a>'
			html += '</div>'
			html += '</BODY>'
			html += '</HTML>'
		else:
			html = '<HTML style="text-align: center;">'
			html += '<HEAD>' + '<TITLE>GG2S:Profile</TITLE>' + css + '</HEAD>'
			html += '<BODY>'
			html += '<div>'
			html += '<p style="margin: 50px;">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '<div>404 Player Not Found ;)</div><br>'
			html += '<a href="/" style="color:white;">Return</a>'
		self.response.out.write(html)
		
#프로필페이지(New)
class ProfilePage2(webapp2.RequestHandler):
	@classmethod
	def getTrophyName(self, trophy_index):
		if (trophy_index == 0):
			return "Beta Gang"
		elif (trophy_index == 1):
			return "Beta-1st"
		elif (trophy_index == 2):
			return "Beta-2nd"
		elif (trophy_index == 3):
			return "Beta-3rd"
		elif (trophy_index == 4):
			return "Season1-1st"
		elif (trophy_index == 5):
			return "Season1-2nd"
		elif (trophy_index == 6):
			return "Season1-3rd"
		elif (trophy_index == 7):
			return "Anniversary Cake"

	@classmethod
	def getTrophyDesc(self, trophy_index):
		if (trophy_index == 0):
			return "Rewarded for participating GG2S&GG2I Beta"
		elif (trophy_index == 1):	
			return "Rewarded for being 1st in Beta season leaderboard"
		elif (trophy_index == 2):
			return "Rewarded for being 2nd in Beta season leaderboard"
		elif (trophy_index == 3):
			return "Rewarded for being 3rd in Beta season leaderboard"
		elif (trophy_index == 4):	
			return "Rewarded for being 1st in Season 1 leaderboard"
		elif (trophy_index == 5):
			return "Rewarded for being 2nd in Season 1 leaderboard"
		elif (trophy_index == 6):
			return "Rewarded for being 3rd in Season 1 leaderboard"
		elif (trophy_index == 7):
			return "Happy birthday GG2S!"

	@classmethod
	def getTrophyImage(self, trophy_index):
		image = "images/trophy/"
		if (trophy_index == 0):
			image += "trophy_beta_gang.png"
		elif (trophy_index == 1):
			image += "trophy_no_1.png"
		elif (trophy_index == 2):
			image += "trophy_no_2.png"
		elif (trophy_index == 3):
			image += "trophy_no_3.png"
		elif (trophy_index == 4):
			image += "trophy_season1_no1.png"
		elif (trophy_index == 5):
			image += "trophy_season1_no2.png"
		elif (trophy_index == 6):
			image += "trophy_season1_no3.png"
		elif (trophy_index == 7):
			image += "trophy_anniversary_cake.png"
		return image

	def get(self):
		html = '<!DOCTYPE html>'
		user_id = self.request.get('id')
		
		user = memcache.get('user:{}'.format(user_id))
		if user is None:
			user = ndb.gql('SELECT * FROM UserEntity WHERE user_id=:id', id = user_id).get()

		page_title = ''
		
		#해당 유저 존재시
		if user:
			#페이지 요청자의 로그인 여부 및 해당 플레이어 여부 확인
			user_logged_on = False
			is_current_user = False

			current_user = users.get_current_user()
			if current_user:
				user_logged_on = True
			
			if user.google_id == current_user:
				is_current_user = True

		#유저가 존재하지 않는 케이스
		else:
			page_title = 'GG2S:404'
		
		html = '<!DOCTYPE html>'
		html += '<HTML onkeydown="changeSeason();">'
		
		#HEAD
		html += '<HEAD>' + '<TITLE>' + 'GG2S:' + user.user_id + '\'s Profile' + '</TITLE>'
		html += '<meta charset="UTF-8">'
		html += '<meta name="viewport" content="width=device-width, initial-scale=1">'
		html += '<script src="/js/jquery.js"></script>'
		html += "<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>"
		html += "<link rel='stylesheet prefetch' href='https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css'>"
		html += '<link rel="stylesheet" href="/css/profile.css" type="text/css">'
		html += '<link rel="stylesheet" href="/css/profile_overall.css" type="text/css">'
		html += '<link rel="stylesheet" href="/css/profile_loadout.css" type="text/css">'
		html += '</HEAD>'
		#<!--HEAD END-->
		
		#BODY
		html += '<BODY onload="changeMenu(\'overall\');">'
		html += '<div class="body-content">'
		
		#GAMEBOY_TOP
		html += '<div class="gameboy-top">'
		html += '<i class="ion ion-arrow-left-b"></i><a href="/"><i class="ion ion-home"></i></a>&middot<i class="ion ion-social-python"></i><i class="ion ion-arrow-right-b"></i>'
		html += '</div>'
		#<--GAMEBOY_TOP END-->
		
		#TOPMENU
		if user:
			html += '<div class="region-wrapper">{}</div>'.format(user.user_region)
		html += '<div class="title-wrapper">'
		if user:
			html += user.user_clan + user.user_id
			if is_current_user:
				html += '<a href="/profilesetting"><i class="ion ion-gear-b" title="Setting"></i></a>' #Make a Link to profile setting page
		else:
			html += '404 Player Not Found ;)'
		html += '</div>'
		html += '<form method="GET" action="/profile">'
		html += '<div class="search-wrapper">'
		html += '<input type="text" name="id" placeholder="Search Player..." class="search-input" autocomplete="off" />'
		html += '<i class="ion ion-search"></i>' #Search Icon, http://ionicons.com/
		html += '</form>'
		html += '</div>'
		#<!--TOPMENU END-->
		
		#PROFILE
		if user:
			html += '<div class="profile-wrapper">'
			if user.user_avatar:
				html += '<img class="avatar" src="/upload?img_id=%s"></img>' %user.key.urlsafe()
			else:
				html += '<img class="avatar" src="/images/gg2slogo_green.png">'
			html += '<div class="profile-word-wrapper">'
			html += '<p class="profile-word">'
			html += '<i class="ion ion-quote"></i>'
			if user.user_word:
				html += '<textarea id="user-word" resize="none" wrap="hard" disabled>' + user.user_word + '</textarea>'
			else:
				html += '. . .'
			html += '</div>'
			html += '</p>'
			html += '</div>'
		#<!--PROFILE END-->
		
		#TROPHY
		if user:
			trophy_list = ndb.gql('SELECT * FROM TrophyEntity WHERE trophy_owner=:1', user.key.id()).order(TrophyEntity.trophy_getdate)
			TROPHY_PER_SHELF_MAX = 5
			html += '<div class="relative-wrapper">'
			html += '<div class="trophy-wrapper">'
			if (trophy_list.count()):
				html += '<p class="trophy-shelf">'
				trophy_count = 0
				for trophy in trophy_list:
					html += '<a class="tooltip-wrapper">'
					html += '<img class="trophy" src="' + self.getTrophyImage(trophy.trophy_index) + '">'
					html += '<span class="trophy-tooltip">' + self.getTrophyDesc(trophy.trophy_index) + '</span>'
					html += '</a>'
					trophy_count += 1
					if not trophy_count % TROPHY_PER_SHELF_MAX:
						html += '</p><p class="trophy-shelf">'
				if trophy_count % TROPHY_PER_SHELF_MAX:
					html += '</p>'
			else:
				html += '<p class="trophy-shelf">'
				html += '<span>No Trophies Available!</span>'
				html += '</p>'
			html += '</div>'
			html += '</div>'
		#<!--TROPHY END-->
		
		#SELECTOR
		if user:
			html += '<div class="selector-wrapper">'
			html += '<a id="menu_overall" onClick="changeMenu(\'overall\');" class="selected"><i class="ion ion-earth"></i>OVERALL</a>' # 메뉴1
			html += '<a id="menu_match" onClick="changeMenu(\'match\');"><i class="ion ion-ios-game-controller-b"></i>MATCHES</a>' # 메뉴2
			html += '<a id="menu_stat" onClick="changeMenu(\'stat\');"><i class="ion ion-stats-bars"></i>STATS</a>' # 메뉴3
			html += '<a id="menu_profilebackpack" onClick="changeMenu(\'profilebackpack\');"><i class="ion ion-bag"></i>BACKPACK</a>' # 메뉴4
			html += '<a id="menu_profileloadout" onClick="changeMenu(\'profileloadout\');"><i class="ion ion-bowtie"></i>LOADOUT</a>' # 메뉴5
			html += '<hr>'
			html += '</div>'
		#<!--SELECTOR END-->
		
		#CONTENT
		if user:
			html += '<div class="main-wrapper" id="main-content">'
			html += '</div>'
		#<!--CONTENT END-->

		#GAMEBOY_BOTTOM
		html += '<div class="gameboy-bottom">'
		html += '<i class="ion ion-android-add"></i>'
		html += '</div>'
		html += '<div class="gameboy-button">'
		html += '<i class="ion ion-record" id="button-a"></i>'
		html += '<i class="ion ion-record" id="button-b"></i>'
		html += '</div>'
		#<!--GAMEBOY_BOTTOM END-->
		
		html += '</div>'
		#<!--body-content END-->
				
		html += '</BODY>'
		#<!--BODYEND-->
		html += '</HTML>'
		
		html += '<script src="/js/profile.js"></script>'
		if user:
			html += '<script>'
			html += 'var user_url = "' + user.key.urlsafe() + '";';
			html += 'var current_season = "' + str(GG2S_CURRENT_SEASON) + '";';
			html += '</script>'

		self.response.out.write(html)

#PROFILE::OVERALL
class ProfileOverall(webapp2.RequestHandler):
	def get(self):
		try:
			user = ndb.Key(urlsafe=self.request.get('id')).get()
		except:
			user = ''

		html = '<div class="overall" id="content">'

		if user:
			stat = ndb.Key(UserStatEntity, user.key.id()).get()
			class_stat = ndb.Key(ClassEntity, user.key.id()).get()
			
			#LEVEL
			html += '<div class="overall-level">'
			html += 'LEVEL ' + makeLevelTemplate(user.user_level) + ' EXP ' + str(user.user_exp) + '/' + str(getMaxExp(user.user_level))
			html += '</div>'
			#<!--LEVEL END-->
			
			#ACTIVITY
			html += '<div class="overall-activity">'
			html += '<div class="title">'
			html += '<i class="ion ion-android-walk"></i> RECENT ACTIVITIES '
			html += '<i class="ion ion-arrow-left-b log-page" id="log-left" onclick="changeActivity(0)"></i> '
			html += '<i class="ion ion-arrow-right-b log-page" id="log-right" onclick="changeActivity(1)"></i>'
			html += '</div>'
			html += '<div class="activity-logs" id="activity-logs">'
			html += '<i class="ion ion-refresh proxy"></i>'
			html += '</div>'
			html += '</div>'
			#<!--ACTIVITY END-->
			
			#TRADE
			html += '<div class="overall-trade">'
			html += '<div class="title"><i class="ion ion-ios-cart"></i> Items Trading</div>'
			trade_list = ndb.gql('SELECT * FROM TradeEntity WHERE trade_owner=:1', user.google_id)
			for trade in trade_list:
				item = ndb.Key(BackpackEntity, trade.trade_item).get()
				item_nickname = ndb.Key(ItemEntity, item.item_name).get().item_nickname
				html += '<a href="/trade?item=%s' %trade.key.urlsafe() + '">'
				html += '<div class="trade-wrapper">'
				html += '<div class="trade-img">'
				html += '<img src="/itemthumb/' + trade.trade_itemname + '.png">'
				html += '</div>'
				html += '<div class="trade-desc" id="' + rarityIntegerConvert(item.item_rarity) + '">'
				html += '<span>' + item_nickname
				if item.item_rarity == 2: #Unusual
					html += '<br>' + '(' + unusualTypeToString(item.item_effect) + ')'
				html += '</span>'
				html += '</div>'
				html += '</a>'
				html += '<div class="trade-coin">' + str(trade.trade_coin) + 'G</div>'
				html += '</div>'
			html += '</div>'
			#<!--TRADE END-->
			
			#SKILL
			html += '<div class="overall-skill">'
			html += '<div class="title"><i class="ion ion-arrow-graph-up-right"></i> SKILL</div>'
			if stat.user_death is not 0:
				html += '<div class="skill-wrapper">K/D : ' + '%.2f' %(float(stat.user_kill) / stat.user_death) + '</div>'
			else:
				html += '<div class="skill-wrapper">K/D : ' + '%.2f' %(float(stat.user_kill)) + '</div>'
			if stat.user_redtime + stat.user_bluetime is not 0:
				html += '<div class="skill-wrapper">KPM : ' + '%.2f' %(float(stat.user_kill)/((stat.user_redtime + stat.user_bluetime)/900)) + '</div>'
			else:
				html += '<div class="skill-wrapper">KPM : ' + '0.00' + '</div>'
			html += '<div class="skill-wrapper">POINTS : ' + str(stat.user_point) + '</div>'
			html += '<div class="skill-wrapper">PLAYTIME : ' + makePlaytimeTemplate(stat.user_playtime) + '</div>'
			html += '<div class="skill-wrapper">IN ' + str(stat.user_playcount) + ' ROUNDS</div>'
			html += '</div>'
			#<!--SKILL END-->
			
			#WINRATE
			if stat.user_win + stat.user_lose:
				winrate = 100 * float(stat.user_win) / (stat.user_win + stat.user_lose)
			else:
				if stat.user_win:
					winrate = 100
				else:
					winrate = 0
			win_degree = int(360 * (winrate/100))
			
			win_color = '#0f380f'
			lose_color = '#306230'
			
			if win_degree > 180:
				back_color = win_color
			else:
				back_color = lose_color
			
			
			html += '''
				<style>
					.overall-winrate {
					  float: left;
					  width: 33%;
					  text-align: center;
					}
					.overall-winrate .title {font-size: 40px; text-align: left;}
					.winrate-piewrapper {
					  position: relative;
					  left: 65px;
					  height: 200px;
					}
					.winrate-piebackground{
					  z-index: 0;
					  background-color: ''' + back_color + ''';
					  position: absolute;
					  width: 200px;
					  height: 200px;
					  -Moz-border-radius: 100px;
					  -Webkit-border-radius: 100px;
					  -O-border-radius: 100px;
					  border-radius: 100px;
					}
					.pie {
					  position: absolute;
					  width: 200px;
					  height: 200px;
					  -moz-border-radius: 100px;
					  -webkit-border-radius: 100px;
					  -o-border-radius: 100px;
					  border-radius: 100px;
					  clip: rect(0px, 100px, 200px, 0px);
					}
					.hold {
					  position: absolute;
					  width: 200px;
					  height: 200px;
					  -moz-border-radius: 100px;
					  -webkit-border-radius: 100px;
					  -o-border-radius: 100px;
					  border-radius: 100px;
					  clip: rect(0px, 200px, 200px, 100px);
					}
					#winrate-win .pie {
					  z-index: 1;
					  background-color: ''' + win_color + ''';
					  -webkit-transform:rotate(''' + str(win_degree) + '''deg);
					  -moz-transform:rotate(''' + str(win_degree) + '''deg);
					  -o-transform:rotate(''' + str(win_degree) + '''deg);
					  transform:rotate(''' + str(win_degree) + '''deg);
					}
					#winrate-lose {
					  -webkit-transform:rotate(''' + str(win_degree) + '''deg);
					  -moz-transform:rotate(''' + str(win_degree) + '''deg);
					  -o-transform:rotate(''' + str(win_degree) + '''deg);
					  transform:rotate(''' + str(win_degree) + '''deg);
					}
					#winrate-lose .pie {
					  z-index: 2;
					  background-color: ''' + lose_color + ''';
					  -webkit-transform:rotate(''' + str(360 - win_degree) + '''deg);
					  -moz-transform:rotate(''' + str(360 - win_degree) + '''deg);
					  -o-transform:rotate(''' + str(360 - win_degree) + '''deg);
					  transform:rotate(''' + str(360 - win_degree) + '''deg);
					}
					.overall-winrate span {
					  color: white;
					  text-shadow: 4px 4px #306230;
					}
				</style>
			'''
			html += '<div class="overall-winrate">'
			html += '<div class="title"><i class="ion ion-pie-graph"></i> WINRATE</div>'
			html += '<div class="winrate-piewrapper">'
			html += '<div class="winrate-piebackground"></div>'
			html += '<div id="winrate-win" class="hold"><div class="pie"></div></div>'
			html += '<div id="winrate-lose" class="hold"><div class="pie"></div></div>'
			html += '</div>'
			html += '<span>%.1f' %(winrate) + '%</span>'
			html += '</div>'
			#<!--WINRATE END-->
			
			#MATCH
			html += '<div class="overall-match">'
			html += '<div class="title"><i class="ion ion-ios-game-controller-a"></i> LAST 5 MATCHES</div>'
			match_list = ndb.gql('SELECT * FROM MatchEntity WHERE match_owner=:1 ORDER BY match_datetime DESC LIMIT 5', user.key.id())
			match_result = ['WIN', 'LOSE', 'DRAW', 'D/C']
			for match in match_list:
				html += '<div class="match-wrapper" id="' + match_result[match.match_result].replace('/', '') + '">'
				html += '<div class="match-result">'
				if match.match_result < 4 and match.match_result > -1:
					html += '<span>' + match_result[match.match_result] + '</span>'
				else:
					html += 'NULL'
				html += '</div>'
				html += '<div class="match-desc">'
				html += str(match.match_kill) + '/' + str(match.match_death) + '/' + str(match.match_assist)
				html += '</div>'
				html += '</div>'
			html += '</div>'
			#<!--MATCH END-->
		
			#REPLY
			PAGE_REPLY_LIMIT = 5
			html += '<div class="overall-reply">'
			html += '<div class="title">'
			html += '<i class="ion ion-chatboxes"></i> COMMENTS '
			html += '<i class="ion ion-arrow-left-b reply-page" id="reply-left" onclick="changeReply(0)"></i> '
			html += '<i class="ion ion-arrow-right-b reply-page" id="reply-right" onclick="changeReply(1)"></i>'
			html += '</div>'
			html += '<div class="reply-replies" id="reply-replies">'
			html += '<i class="ion ion-refresh proxy"></i>'
			html += '</div>'
			current_user = users.get_current_user()
			if current_user:
				current_user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
				html += '<div class="reply-newreply">'
				if current_user.user_avatar:
					html += '<div class="reply-avatar-wrapper"><img class="reply-avatar" src="/upload?img_id=%s"></img></div>' %current_user.key.urlsafe()
				else:
					html += '<div class="reply-avatar-wrapper"><img class="reply-avatar" src="/images/gg2slogo_green.png"></div>'
				html += '<div class="newreply-content-wrapper">'
				html += '<input type="text" class="newreply-content" maxlength="200" placeholder="Leave a Comment for {}..." onkeyup="checkReplyReady();">'.format(user.user_id)
				html += '<span id="newreply-counter">0/200</span>'
				html += '</div>'
				html += '<i class="ion ion-edit" id="reply-submit" onclick="submitReply();"></i>'
				html += '</div>'
			html += '</div>'
			#<!--REPLY END-->

		html += '<div style="clear: both;"></div>'
		
		html += '</div>'
			
		self.response.out.write(html)

#PROFILE::MATCH
class ProfileMatch(webapp2.RequestHandler):
	def get(self):
		try:
			user = ndb.Key(urlsafe=self.request.get('id')).get()
		except:
			user = ''

		html = '<div id="content">'
		
		html += '''
			<style>
				.match-wrapper{
					clear: both;
					position: relative;
					width: 100%;
					color: white;
					margin-bottom: 50px;
				}
				.match-datetime {color: #0f380f;}
				.match-datetime i {font-size: 50px; margin-right: 10px;}
				.match-top {
					display: flex;
					position: relative;
					padding: 20px 20px 0 20px;
					border-bottom: 2px solid #fff;
					text-shadow: 2px 2px #0f380f;
				}
				.match-resultimg {
					display: block;
					float: left;
				}
				.match-resultimg img {
					width: 600px;
				}
				.match-resultstat {
					display: block;
					text-align: right;
					width: 100%;
				}
				.match-resultstat #desc {font-size: 20px;}
				.match-bottom {
					clear: both;
					position: relative;
				}
				.scoreboard-wrapper {
					clear: both;
					display: table;
					width: 100%;
				}
				.scoreboard-wrapper i {font-size: 40px; margin-right: 10px;}
				#red-title {background-color: rgba(255, 0, 0, 0.45);}
				#blue-title {background-color: rgba(0, 0, 255, 0.4);}
				.scoreboard-red {
					display: table-cell;
					width: 50%;
					border-right: 2px solid #fff;
					padding: 0 20px 0 20px;
					background-color: rgba(69, 69, 69, 0.7);
				}
				#red-title .name, #red-title .point{font-size: 60px; font-weight: bold;} #blue-title .name, #blue-title .point{font-size: 60px; font-weight: bold;}
				.name{float: left; font-size: 40px; font-weight: normal;} .point{float: right; font-size: 40px; font-weight: normal;}
				.scoreboard-wrapper #owner{color: yellow;}
				.scoreboard-blue {
					display: table-cell;
					width: 50%;
					padding: 0 20px 0 20px;
					background-color: rgba(69, 69, 69, 0.7);
				}
				.scoreboard-bottom {
					font-weight: normal;
					color: white;
					clear: both;
					display: table;
					width: 100%;
					font-size: 45px;
				}
				.scoreboard-bottom .bottom-cell {
					display: table-cell;
					width: 50%;
					padding: 0 20px 0 20px;
					border-top: 2px solid #fff;
					background-color: #454545;
				}
				.scoreboard-bottom #server{border-bottom-left-radius: 20px;}
				.scoreboard-bottom #map{text-align: right; border-bottom-right-radius: 20px;}
			</style>
		'''
		
		if user:
			match_list = ndb.gql('SELECT * FROM MatchEntity WHERE match_owner=:1 ORDER BY match_datetime DESC LIMIT 5', user.key.id())
			for match in match_list:
				if match.match_myself > -1:
					match_redteam = match.match_redteam.split(':')[:-1]
					match_blueteam = match.match_blueteam.split(':')[:-1]
					
					if match.match_result in [0, 1]:
						if match.match_myself < len(match_redteam):
							if not match.match_result: #0
								team_win = 'red'
							else:
								team_win = 'blue'
						else:
							if match.match_result: #1
								team_win = 'red'
							else:
								team_win = 'blue'
					elif match.match_result is 3:
						team_win = 'disconnect'
					else:
						team_win = 'draw'
					
					html += '<div class="match-wrapper">'
					
					#MATCH_DATETIME
					html += '<div class="match-datetime">'
					html += '<i class="ion ion-ios-game-controller-a"></i>'
					html += match.match_datetime.strftime("%b.%d %I:%M %p")
					html += '</div>'
					#<!--MATCH_DATETIME END-->
					
					#MATCH_TOP
					html += '<div class="match-top">'
					
					#RESULT IMAGE
					html += '<div class="match-resultimg">'
					html += '<img src="/images/scoreboard_' + team_win + '.png">'
					html += '</div>'
					#<!--RESULT IMAGE END-->
					
					#RESULT STATS
					html += '<div class="match-resultstat">'
					
					#KDA
					html += '<div id="desc">K/D/A</div>'
					html += '<div class="match-kda">'
					html += str(match.match_kill) + '/' + str(match.match_death) + '/' + str(match.match_assist)
					html += '</div>'
					#<!--KDA END-->
					
					#PLAYTIME
					html += '<div id="desc">Playtime</div>'
					html += '<div class="match-playtime">'
					html += makePlaytimeTemplate(match.match_playtime)
					html += '</div>'
					#<!--PLAYTIME END-->
					
					html += '</div>'
					#<!--RESULT STATS END-->
					
					html += '</div>'
					#<!--MATCH_TOP END-->
					
					#MATCH_BOTTOM
					html += '<div class="match-bottom">'
					
					#SCOREBOARD
					html += '<div class="scoreboard-wrapper">'
					if match.match_score:
						match_score = match.match_score.split(':')
						if match.match_mode in ['KOTH', 'DKOTH']:
							match_score[0] = '<i class="ion ion-ios-stopwatch"></i>' + makePlaytimeTemplate(int(eval(match_score[0])))
							match_score[1] = '<i class="ion ion-ios-stopwatch"></i>' + makePlaytimeTemplate(int(eval(match_score[1])))
						elif match.match_mode == 'CTF':
							match_score[0] = '<i class="ion ion-briefcase"></i>' + match_score[0]
							match_score[1] = '<i class="ion ion-briefcase"></i>' + match_score[1]
						elif match.match_mode == 'GEN':
							match_score[0] = '<i class="ion ion-battery-charging"></i>' + str(int(eval(match_score[0]))) + '%'
							match_score[1] = '<i class="ion ion-battery-charging"></i>' + str(int(eval(match_score[1]))) + '%'
						elif match.match_mode == 'CP':
							match_score[0] = '<i class="ion ion-flag"></i>' + match_score[0]
							match_score[1] = '<i class="ion ion-flag"></i>' + match_score[1]
						elif match.match_mode == 'ARENA':
							match_score[0] = '<i class="ion ion-ribbon-b"></i>' + match_score[0]
							match_score[1] = '<i class="ion ion-ribbon-b"></i>' + match_score[1]
					else:
						match_score = ['', '']
					html += '<div class="scoreboard-red" id="red-title">'
					html += '<div class="name">'
					html += 'RED'
					html += '</div>'
					html += '<div class="point">'
					html += match_score[0]
					html += '</div>'
					html += '</div>'
					html += '<div class="scoreboard-blue" id="blue-title">'
					html += '<div class="name">'
					html += match_score[1]
					html += '</div>'
					html += '<div class="point">'
					html += 'BLU'
					html += '</div>'
					html += '</div>'
					html += '</div>'
					red_count = len(match_redteam)
					blue_count = len(match_blueteam)
					if red_count >= blue_count:
						bigger_count = red_count
					else:
						bigger_count = blue_count
					for i in range(bigger_count):
						html += '<div class="scoreboard-wrapper">'
						
						html += '<div class="scoreboard-red">'
						if i < red_count:
							player = match_redteam[i].split(',')
							if (match.match_myself == i):
								html += '<div class="name" id="owner">'
							else:
								html += '<div class="name">'
							html += player[0].replace('!cm', ',').replace('!cl', ':') #name
							html += '</div>'
							if (match.match_myself == i):
								html += '<div class="point" id="owner">'
							else:
								html += '<div class="point">'
							html += str(int(eval(player[1]))) #score
							html += '</div>'
						html += '</div>'
						html += '<div class="scoreboard-blue">'
						if i < blue_count:
							player = match_blueteam[i].split(',')
							if (match.match_myself == i + red_count):
								html += '<div class="name" id="owner">'
							else:
								html += '<div class="name">'
							html += player[0].replace('!cm', ',').replace('!cl', ':')
							html += '</div>'
							if (match.match_myself == i +red_count):
								html += '<div class="point" id="owner">'
							else:
								html += '<div class="point">'
							html += str(int(eval(player[1])))
							html += '</div>'
						html += '</div>'
						html += '</div>'
					html += '<div class="scoreboard-bottom">'
					html += '<div class="bottom-cell" id="server">'
					html += 'Server: ' + match.match_server
					html += '</div>'
					html += '<div class="bottom-cell" id="map">'
					html += 'Map: ' + match.match_map + '(' + match.match_mode + ')'
					html += '</div>'
					html += '</div>'
					#<!--SCOREBOARD END-->
					
					html += '</div>'
					#<!--MATCH_BOTTOM END-->
					
					html += '</div>'
			
		html += '</div>'
		
		self.response.out.write(html)
		
#PROFILE::STAT
class ProfileStat(webapp2.RequestHandler):
	def get(self):
		try:
			user = ndb.Key(urlsafe=self.request.get('id')).get()
		except:
			user = ''
		
		html = '<div id="content">'
		html += '''
			<style>
				.stat-wrapper {
				  display: block;
				  width: 100%;
				  margin: auto;
				  text-align: center;
				}
				.stat-wrapper .stat-selector {
				  display: block;
				  text-align: center;
				}
				.stat-wrapper .selector-arrow {display: inline-block; min-width: 10%; margin: auto; padding-bottom: 10px; position: relative;}
				.stat-wrapper .selector-title-wrapper {
				  position: relative;
				  display: inline-block;
				  width: 60%;
				  height: 60px;
				  overflow-x: hidden;
				  border: 10px solid #5A2729;
				  background-color: #763931;
				  border-radius: 10px;
				  white-space: nowrap;
				  margin: auto;
				  box-shadow: 0 4px #000,
				}
				.stat-selector i {
				  position: absolute;
				  font-size: 80px;
				  color: #f4f4f0;
				  text-shadow: 0 4px #000;
				  top: -70px;
				}
				.stat-selector i:hover {cursor: pointer;}
				.stat-selector .dead {color: gray;}
				.stat-selector .dead:hover {pointer-events: none;}
				.stat-selector .arrow-left {left: 0%;}
				.stat-selector .arrow-right {right: 0%;}
				.stat-selector {width: 100%;}
				.stat-selector .selector-title {
				  position: absolute;
				  width: 100%;
				  text-align: center;
				  display: inline-block;
				  overflow: hidden;
				  -webkit-transform: transformX(0);
						  transform: transformX(0);
				  -webkit-transition: 275ms ease;
						  transition: 275ms ease;
				  color: #fff;
				  text-shadow: 4px 4px #000;
				}
				.stat-selector .seasonleft {left: -100%;}
				.stat-selector .seasonselected {left: 0%;}
				.stat-selector .seasonright {left: 100%;}
				
				.stat-season {width: 100%; text-align: center;}
				.stat-content-wrapper {
				  position: relative;
				  overflow-x: hidden;
				  width: 100%;
				  margin: auto;
				  display: inline-block;
				  margin-top: 40px;
				  text-align: center;
				  min-height: 1000px;
				  border-radius: 10px;
				}
				.stat-content {
				  position: absolute;
				  font-size: 40px;
				  width: 100%;
				  background-color: #232323;
				  -webkit-transform: transformX(0);
						  transform: transformX(0);
				  -webkit-transition: 275ms ease;
						  transition: 275ms ease;
				}
				.stat-content-wrapper .contentleft {left: -100%;}
				.stat-content-wrapper .contentselected {left: 0%;}
				.stat-content-wrapper .contentright {left: 100%;}
				.stat-content table {width: 100%; text-align: center; font-size: 40px; border-collapse: collapse; color: #f6f4f1; table-layout : fixed;}
				.stat-content table td, table th {border: 2px solid rgba(246, 244, 241, 0.5);}
				.stat-content table tr:first-child th {border-top: 0;}
				.stat-content table tr:last-child td {border-bottom: 0;}
				.stat-content table tr td:first-child, table tr th:first-child {border-left: 0;}
				.stat-content table tr td:last-child, table tr th:last-child {border-right: 0;}
				.stat-content table th {color: #bcdf8a;}
				.stat-content table td {font-weight: normal; font-size: 30px;}
				.stat-content div {margin: 20px;}
				.stat-content .content-title {font-family: 'Press Start 2P', 'Mother'; color: #94c0cc; }
				.stat-content .stat-additional {font-family: 'Press Start 2P', 'Mother'; color: #ed7777; font-size: 30px;}
				.stat-content #highlight {color: #f5f9ad;}
				.stat-content .class-icon {height: 29px;}
			</style>
		'''
		
		if user:
			stat = ndb.Key(UserStatEntity, user.key.id()).get()
			class_stat = ndb.Key(ClassEntity, user.key.id()).get()
			season_stat_list = list()
			season_stat_list.append(stat)
			for i in range(GG2S_CURRENT_SEASON + 1):
				season = ndb.gql('SELECT * FROM SeasonStatEntity WHERE season_owner=:1 AND season=:2', user.key.id(), i).get()
				season_stat_list.append(season)
			html += '<div class="stat-wrapper">'
			
			#SELECTOR
			html += '<div class="stat-selector" ondragstart="return false">'
			html += '<div class="selector-arrow" onselectstart="return false"><i class="ion ion-arrow-left-b arrow-left dead" onclick="selectorClickLeft();"></i></div>'
			#SELECTOR-TITLE
			html += '<div class="selector-title-wrapper" onselectstart="return false">'
			html += '<div class="selector-title seasonselected" id="title-1">'
			html += '<span class="stat-title ">Overall</span>'
			html += '</div>'
			for i in range(GG2S_CURRENT_SEASON + 1):
				html += '<div class="selector-title seasonright" id="title' + str(i) + '">'
				if i is 0:
					html += '<span class="stat-title">' + 'Beta Season' '</span>'
				else:
					html += '<span class="stat-title">' + 'Season ' + str(i) + '</span>'
				html += '</div>'
			html += '</div>'
			#<!--SELECTOR-TITLE END-->
			html += '<div class="selector-arrow" onselectstart="return false"><i class="ion ion-arrow-right-b arrow-right" onclick="selectorClickRight();"></i></div>'
			html += '</div>'
			#<!--SELECTOR END-->
			
			#CONTENT
			def makeTH(string):
				return '<th>' + string + '</th>'
			def makeTD(string):
				return '<td>' + string + '</td>'
			html += '<div class="stat-season">'
			
			html += '<div class="stat-content-wrapper">'
			for i in range(-1, GG2S_CURRENT_SEASON + 1):
				season = season_stat_list[i + 1]
				if i is -1:
					html += '<div class="stat-content contentselected" id="content' + str(i) + '">'
				else:
					html += '<div class="stat-content contentright" id="content' + str(i) + '">'
				
				#GENERAL VALUES
				html += '<div class="stat-general">'
				html += '<span class="content-title">GENERAL</span>'
				html += '<table>'
				html += '<thead>'
				html += makeTH('KILL')
				html += makeTH('DEATH')
				html += makeTH('ASSIST')
				html += makeTH('K/D')
				html += makeTH('KDA')
				html += '</thead>'
				html += '<tbody>'
				html += makeTD(str(season.user_kill))
				html += makeTD(str(season.user_death))
				html += makeTD(str(season.user_assist))
				if season.user_death is not 0:
					season_kd = season.user_kill/float(season.user_death)
					season_kda = (season.user_kill + season.user_assist)/float(season.user_death)
				else:
					season_kd = season.user_kill
					season_kda = season.user_kill + season.user_assist
				html += makeTD('%.1f' %season_kd)
				html += makeTD('%.1f' %season_kda)
				html += '</tbody>'
				html += '</table>'
				html += '</div>'
				#<!--GENERAL VALUES END-->
				
				#SPECIAL VALUES
				html += '<div class="stat-special">'
				html += '<span class="content-title">SPECIAL</span>'
				html += '<table>'
				html += '<thead>'
				html += makeTH('CAP')
				html += makeTH('DEF')
				html += makeTH('DES')
				html += makeTH('STAB')
				html += makeTH('HEAL')
				html += makeTH('INVULN')
				html += '</thead>'
				html += '<tbody>'
				html += makeTD(str(season.user_cap))
				html += makeTD(str(season.user_defense))
				html += makeTD(str(season.user_destruction))
				html += makeTD(str(season.user_stab))
				html += makeTD(strlize(season.user_healing))
				html += makeTD(str(season.user_invuln))
				html += '</tbody>'
				html += '</table>'
				html += '</div>'
				#<!--SPECIAL VALUES END-->
				
				#MATCH RESULT
				html += '<div class="stat-matchresult">'
				html += '<span class="content-title">MATCH RESULT</span>'
				html += '<table>'
				html += '<thead>'
				html += makeTH('WIN')
				html += makeTH('LOSE')
				html += makeTH('DRAW')
				html += makeTH('D/C')
				html += makeTH('WIN RATE')
				html += makeTH('D/C RATE')
				html += '</thead>'
				html += '<tbody>'
				html += makeTD(str(season.user_win))
				html += makeTD(str(season.user_lose))
				html += makeTD(str(season.user_stalemate))
				html += makeTD(str(season.user_escape))
				if season.user_lose is not 0:
					season_winrate = 100*float(season.user_win) / (season.user_win + season.user_lose)
				else:
					if season.user_win is not 0:
						season_winrate = 100
					else:
						season_winrate = 0
				if season.user_win + season.user_lose + season.user_stalemate + season.user_escape is not 0:
					season_dcrate = 100*float(season.user_escape) / (season.user_win + season.user_lose + season.user_stalemate + season.user_escape)
				else:
					season_dcrate = 0
				html += makeTD('%.1f' %season_winrate + '%')
				html += makeTD('%.1f' %season_dcrate + '%')
				html += '</tbody>'
				html += '</table>'
				html += '</div>'
				#<!--MATCH RESULT END-->
				
				#TIME VALUES
				html += '<div class="stat-time">'
				html += '<span class="content-title">TIME</span>'
				html += '<table>'
				html += '<thead>'
				html += makeTH('TOTAL')
				html += makeTH('RED')
				html += makeTH('BLUE')
				html += makeTH('SPECTATOR')
				html += '</thead>'
				html += '<tbody>'
				html += makeTD(makePlaytimeTemplate(season.user_playtime))
				html += makeTD(makePlaytimeTemplate(season.user_redtime))
				html += makeTD(makePlaytimeTemplate(season.user_bluetime))
				html += makeTD(makePlaytimeTemplate(season.user_spectime))
				html += '</tbody>'
				html += '</table>'
				html += '</div>'
				#<!--TIME VALUES END-->
				
				#CLASSES
				if i is -1:
					class_kill_list = [eval(j) for j in class_stat.kill.split(',')]
					class_death_list = [eval(j) for j in class_stat.death.split(',')]
					class_assist_list = [eval(j) for j in class_stat.assist.split(',')]
					class_playtime_list = [eval(j) for j in class_stat.playtime.split(',')]
				else:
					class_kill_list = [eval(j) for j in season.class_kill.split(',')]
					class_death_list = [eval(j) for j in season.class_death.split(',')]
					class_assist_list = [eval(j) for j in season.class_assist.split(',')]
					class_playtime_list = [eval(j) for j in season.class_playtime.split(',')]
				html += '<div class="stat-class">'
				html += '<span class="content-title">CLASSES</span>'
				html += '<table>'
				html += '<thead>'
				html += makeTH('')
				for class_str in _CLASSES:
					html += makeTH('<img class="class-icon" src="/images/icon_' + class_str + '.png">')
				html += '</thead>'
				html += '<tr>'
				html += makeTD('K')
				for j in range(10):
					html += makeTD(str(class_kill_list[j]))
				html += '</tr>'
				html += '<tr>'
				html += makeTD('D')
				for j in range(10):
					html += makeTD(str(class_death_list[j]))
				html += '</tr>'
				html += '<tr>'
				html += makeTD('A')
				for j in range(10):
					html += makeTD(str(class_assist_list[j]))
				html += '</tr>'
				html += '<tr>'
				html += makeTD('K/D')
				for j in range(10):
					if class_death_list[j] is not 0:
						class_kd = class_kill_list[j]/float(class_death_list[j])
					else:
						class_kd = class_kill_list[j]
					html += makeTD('%.1f' %class_kd)
				html += '</tr>'
				html += '<tr>'
				html += makeTD('KDA')
				for j in range(10):
					if class_death_list[j] is not 0:
						class_kda = (class_kill_list[j] + class_assist_list[j])/float(class_death_list[j])
					else:
						class_kda = class_kill_list[j] + class_assist_list[j]
					html += makeTD('%.1f' %class_kda)
				html += '</tr>'
				html += '<tr>'
				html += makeTD('PlayTime')
				for j in range(10):
					html += makeTD(makePlaytimeTemplate(class_playtime_list[j]))
				html += '</tr>'
				html += '</table>'
				html += '</div>'
				#<!--CLASSES END-->
				
				#MOST PLAYED AS?
				most_played = 0
				for j in range(1, 10):
					if class_playtime_list[j] > class_playtime_list[most_played]:
						most_played = j
				html += '<div><span class="stat-additional">MOST PLAYED AS: <span id="highlight">' + _CLASSES[most_played].upper() + '</span></span></div>'
				
				#IN HOW MUCH ROUNDS?
				html += '<div><span class="stat-additional">IN <span id="highlight">' + str(season.user_playcount) + '</span> ROUNDS</span></div>'
				html += '</div>'
			html += '</div>'
			
			html += '</div>'
			#<!--CONTENT END-->
			
			html += '</div>'
			
			html += '<div style="clear: both;"></div>'

		html += '</div>'
		
		self.response.out.write(html)
		
#플레이어의 백팩 페이지
class ProfileBackpack(webapp2.RequestHandler):
	def get(self):
		try:
			user = ndb.Key(urlsafe=self.request.get('id')).get()
		except:
			user = ''
			
		html = ''
		html += '<div id="content" style="text-align: center;">'
		html += '''
			<style>
				.backpack-wrapper {
					width: 740px;
					text-align: center;
					position: relative;
					min-height: 370px;
					display: inline-block;
					background-color: #2B2726;
					border: 10px solid #221F1E;
					border-radius: 20px;
					padding: 15px 30px 15px 30px;
					overflow: hidden;
				}
				.backpack-page {
					position: absolute;
					text-align: left;
				}
				.backpack-wrapper .backpack-row {
					display: block; position: relative; height: 74px;
				}
				.backpack-wrapper .backpack-visible {
					visibility: visible;
				}
				.backpack-wrapper .backpack-invisible {
					visibility: hidden;
				}
				.backpack-wrapper img {width: 64px; height: 64px;}
				.backpack-wrapper .backpack-item {
					display: inline-block;
					border: 5px solid white;
					border-radius: 10px;
					width: 64px; height: 64px;
					position: relative; top: 0;
				}
				.backpack-wrapper .backpack-item a {
					display: inline-block;
					width: 64px; height: 64px;
				}
				.backpack-wrapper .none{
					Border-color: #2B2726;
					background-color: #3C352E;
				}
				.backpack-wrapper .normal{
					Border-color: #F7DC07;
					background-color: #4B4314;
				}
				.backpack-wrapper .strange{
					Border-color: #BB7343;
					background-color: #472B1F;
				}
				.backpack-wrapper .unusual{
					Border-color: #835699;
					background-color: #372A3C;
				}
				.backpack-wrapper .vintage{
					Border-color: #476291;
					background-color: #292D36;
				}
				.backpack-wrapper .self-made{
					Border-color: #70B04A;
					background-color: #2B3E24;
				}
				.backpack-wrapper #trading img {
					-webkit-filter: opacity(50%);
					filter: opacity(50%);
				}
				.backpack-wrapper #trading:before{
					content: "";
					width: 64px;
					height: 64px;
					border-radius: 10px;
					background-color: rgba(20, 20, 20, 0.6);
					position: absolute;
				}
				.backpack-wrapper #trading:after{
					font-size: 24px;
					font-weight: bold;
					color: white;
					content: 'TRADING';
					position: absolute;
					left: 4px;
					top: 24px;
				}
				.backpack-selector {
					display: inline-block;
					width: 820px;
					min-height: 50px;
				}
				.backpack-selector .hex {
					margin: 10px;
					font-size: 20px;
					display: inline-block;
					margin-top: 20px;
					width: 35px;
					height: 20px;
					background-color: #454545;
					position: relative;
				}
				.backpack-selector .hex:before {
					content: " ";
					width: 0; height: 0;
					border-bottom: 10px solid #454545;
					border-left: 17px solid transparent;
					border-right: 17px solid transparent;
					position: absolute;
					left: 0px;
					top: -10px;
				}
				.backpack-selector .hex:after {
					content: " ";
					width: 0; height: 0;
					border-top: 10px solid #454545;
					border-left: 17px solid transparent;
					border-right: 17px solid transparent;
					position: absolute;
					left: 0px;
					bottom: -10px;
				}
				.backpack-selector .hex.selected {background-color: yellow; color: black;}
				.backpack-selector .hex.selected:before {border-bottom: 10px solid yellow;}
				.backpack-selector .hex.selected:after {border-top: 10px solid yellow;}
				
				.backpack-selector .hex:hover {background-color: yellow; color: black; cursor: pointer;}
				.backpack-selector .hex:hover:before {border-bottom: 10px solid yellow;}
				.backpack-selector .hex:hover:after {border-top: 10px solid yellow;}
			</style>
		'''
		
		if user:
			item_list = ndb.gql('SELECT * FROM BackpackEntity WHERE item_owner=:1', user.key.id()).order(BackpackEntity.item_getdate)
			html += '<div class="profile-backpack">'
			
			html += '<div class="backpack-wrapper">'
			
			html += '<div class="backpack-page backpack-visible" id="backpack-1">'
			cnt = 0
			html += '<div class="backpack-row">'
			for item in item_list:
				if (cnt % 10 == 0) and (cnt != 0):
					if cnt % 50 is 0:
						html += '</div></div><div class="backpack-page backpack-invisible" id="backpack-' + str(cnt // 50 + 1) + '"><div class="backpack-row">'
					else:
						html += '</div><div class="backpack-row">'
				html += '<div '
				if (item.is_trading):
					html += 'id="trading" '
				html += 'class="backpack-item ' + rarityIntegerConvert(item.item_rarity) + '">'
				html += '<a href="/item?item=%s&backpack=' %item.key.urlsafe() + user.user_id + '">'
				html += '<img src="/itemthumb/' + item.item_name + '.png" />'
				html += '</a>'
				html += '</div>'
				cnt += 1
			
			if cnt % 50 or cnt == 0:
				while (cnt % 50 or cnt == 0):
					if not cnt % 10 and cnt != 0:
						html += '</div><div class="backpack-row">'
					html += '<div class="backpack-item none"><a></a></div>'
					cnt += 1
					
			html += '</div>' #backpack-row
			html += '</div>' #backpack-page
		
			html += '</div>' #backpack-wrapper
			
			html += '<div class="backpack-selector">'
			for i in range(cnt // 50):
				if i == 0:
					html += '<div class="selector hex selected" id="selector-1" onclick="changeBackpackPage(1);">' + str(i + 1) + '</div>'
				else:
					html += '<div class="selector hex" id="selector-' + str(i + 1) + '" onclick="changeBackpackPage(' + str(i + 1) +');">' + str(i + 1) + '</div>'
			html += '</div>' #backpack-selector
			
			html += '</div>' #profile-backpack
		
		html += '</div>'
		self.response.out.write(html)
		
#프로필 로드아웃 페이지
class ProfileLoadout(webapp2.RequestHandler):
	def makeItemKey(self, str):
		if str:
			return ndb.Key(BackpackEntity, int(str))
		else:
			return None
		
	def get(self):
		try:	
			user = ndb.Key(urlsafe=self.request.get('id')).get()
		except:
			user = ''
		html = ''
		html += '<div id="content" style="text-align: center;">'
		
		if user:
			loadout = ndb.Key(LoadoutEntity, user.key.id()).get()
			head_list = [self.makeItemKey(item) for item in loadout.head_list.split(',')]
			torso_list = [self.makeItemKey(item) for item in loadout.torso_list.split(',')]
			leg_list = [self.makeItemKey(item) for item in loadout.leg_list.split(',')]
			weapon_list = [self.makeItemKey(item) for item in loadout.weapon_list.split(',')]
			misc_list = [self.makeItemKey(item) for item in loadout.misc_list.split(',')]
			taunt_list = [self.makeItemKey(item) for item in loadout.taunt_list.split(',')]
			pet_list = [self.makeItemKey(item) for item in loadout.pet_list.split(',')]
			death_list = [self.makeItemKey(item) for item in loadout.death_list.split(',')]
			humiliation_list = [self.makeItemKey(item) for item in loadout.humiliation_list.split(',')]
			
			ndb_get_list = []
			for item in head_list + torso_list + leg_list + weapon_list + misc_list + taunt_list + pet_list + death_list + humiliation_list:
				if item:
					ndb_get_list.append(item)
			loadout_list = ndb.get_multi(ndb_get_list)
			
			lists = [head_list, torso_list, leg_list, weapon_list, misc_list, taunt_list, pet_list, death_list, humiliation_list]
			
			cnt = 0
			for list in lists:
				for i in range(10):
					if list[i]:
						list[i] = loadout_list[cnt]
						cnt += 1
					else:
						list[i] = None
						
			html += '<div class="loadout-wrapper">'
			for each_class in _CLASSES:
				html += '<div class="loadout-preview">'
				if head_list[findClassConstant(each_class)]:
					html += '<img class="loadout-preview-image" id="None" src="/itempart/{}_{}_{}.png" />'.format(head_list[findClassConstant(each_class)].item_name, each_class, 'Red')
				else:
					html += '<img class="loadout-preview-image" id="None" src="/charpart/{}_{}_{}.png" />'.format(each_class, 'Head', 'Red')
				if torso_list[findClassConstant(each_class)]:
					html += '<img class="loadout-preview-image" id="None" src="/itempart/{}_{}_{}.png" />'.format(torso_list[findClassConstant(each_class)].item_name, each_class, 'Red')
				else:
					html += '<img class="loadout-preview-image" id="None" src="/charpart/{}_{}_{}.png" />'.format(each_class, 'Torso', 'Red')
				if each_class != 'Quote':
					if leg_list[findClassConstant(each_class)]:
						html += '<img class="loadout-preview-image" id="None" src="/itempart/{}_{}_{}.png" />'.format(leg_list[findClassConstant(each_class)].item_name, each_class, 'Red')
					else:
						html += '<img class="loadout-preview-image" id="None" src="/charpart/{}_{}_{}.png" />'.format(each_class, 'Leg', 'Red')
					if weapon_list[findClassConstant(each_class)]:
						html += '<img class="loadout-preview-image" id="{}" src="/weaponpart/{}_{}.png" />'.format(findWeaponString(each_class), weapon_list[findClassConstant(each_class)].item_name, 'Red')
					else:
						html += '<img class="loadout-preview-image" id="{}" src="/weaponpart/{}_{}.png" />'.format(findWeaponString(each_class), findWeaponString(each_class), 'Red')
				else:
					if weapon_list[findClassConstant(each_class)]:
						html += '<img class="loadout-preview-image" id="{}" src="/weaponpart/{}_{}.png" />'.format(findWeaponString(each_class), weapon_list[findClassConstant(each_class)].item_name, 'Red')
					else:
						html += '<img class="loadout-preview-image" id="{}" src="/weaponpart/{}_{}.png" />'.format(findWeaponString(each_class), findWeaponString(each_class), 'Red')
					
				html += '</div>' #loadout-preview

			for each_class in _CLASSES:
				html += '<div class="loadout-class-wrapper">'
				
				html += '<div class="loadout-class-string">'
				html += '<span id="class-string">' + each_class.upper() + '</span>'
				html += '</div>' #loadout-class-string
				
				html += '<div class="loadout-items">'
				html += '<div class="loadout-head"'
				if head_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(head_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(head_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-head" src="/itemthumb/{}.png" />'.format(head_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-torso"'
				if torso_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(torso_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(torso_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-torso" src="/itemthumb/{}.png" />'.format(torso_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-leg"'
				if each_class != 'Quote':
					if leg_list[findClassConstant(each_class)]:
						html += ' id="{}">'.format(rarityIntegerConvert(leg_list[findClassConstant(each_class)].item_rarity))
						html += '<a href="/item?item={}">'.format(leg_list[findClassConstant(each_class)].key.urlsafe())
						html += '<img class="loadout-image" id="image-leg" src="/itemthumb/{}.png" />'.format(leg_list[findClassConstant(each_class)].item_name)
						html += '</a>'
					else:
						html += ' id="none">'
						html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				else:
					html += '>'
					html += '<img class="loadout-image" src="/download/items/blank64.png" style="width: 74px; height: 69px;" />'					
				html += '</div>'	
				html += '<div class="loadout-weapon"'
				if weapon_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(weapon_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(weapon_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-weapon" src="/itemthumb/{}.png" />'.format(weapon_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-misc"'
				if misc_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(misc_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(misc_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-misc" src="/itemthumb/{}.png" />'.format(misc_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-taunt"'
				if taunt_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(taunt_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(taunt_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-taunt" src="/itemthumb/{}.png" />'.format(taunt_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-pet"'
				if pet_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(pet_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(pet_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-pet" src="/itemthumb/{}.png" />'.format(pet_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-death"'
				if death_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(death_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(death_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-death" src="/itemthumb/{}.png" />'.format(death_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'
				html += '</div>'
				html += '<div class="loadout-humiliation"'
				if humiliation_list[findClassConstant(each_class)]:
					html += ' id="{}">'.format(rarityIntegerConvert(humiliation_list[findClassConstant(each_class)].item_rarity))
					html += '<a href="/item?item={}">'.format(humiliation_list[findClassConstant(each_class)].key.urlsafe())
					html += '<img class="loadout-image" id="image-humiliation" src="/itemthumb/{}.png" />'.format(humiliation_list[findClassConstant(each_class)].item_name)
					html += '</a>'
				else:
					html += ' id="none">'
					html += '<img class="loadout-image" src="/download/items/blank64.png" />'	
				html += '</div>'
				html += '</div>' #loadout-items
				
				html += '</div>' #loadout-class-wrapper
			html += '</div>' #loadout-wrapper
		
		html += '</div>'
		self.response.out.write(html)
		
#자신의 프로필 페이지:리다이렉션
class MyProfilePage(webapp2.RequestHandler):
	def get(self):
		current_user = users.get_current_user()
		user_list = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user)
		cnt = 0
		for user in user_list:
			cnt += 1
		if cnt:
			self.redirect('/profile?id=' + user.user_id)
		else:
			self.redirect('/')
		
#프로필 설정 페이지
class ProfileSettingPage(webapp2.RequestHandler):
	def get(self):
		current_user = users.get_current_user()
		user_have_id = False
		if current_user:
			user_list = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user)
			user = user_list.get()
			if user:
				user_have_id = True
		
		if user_have_id:
			html = '<!DOCTYPE HTML>'
			html += '<HTML>'
			
			html += '<HEAD>'
			html += '<TITLE>GG2S: PROFILESETTING</TITLE>'
			html += '<link rel="stylesheet" type="text/css" href="/css/bootstrap.min.css">'
			html += '<link rel="stylesheet" type="text/css" href="/css/profile_setting.css">'
			html += '<script src="/js/jquery.js"></script>'
			html += '<script src="/js/bootstrap.min.js"></script>'
			html += '<script src="/js/bootstrap-filestyle.min.js"></script>'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS : PROFILESETTING</span></a>'
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper
			
			html += '<form method ="post" enctype="multipart/form-data">'
			html += '<div class="setting-wrapper">'
			html += '<div class="setting key-wrapper">'
			html += '<div class="column-left"><span id="key-string">UNIQUE KEY </span></div>'
			html += '<div class="column-right"><span id="id-string">{}</span></div>'.format(user.key.id())
			html += '</div>' #setting-key-wrapper
			
			html += '<div class="setting nickname-wrapper">'
			html += '<div class="column-left"><span id="nickname-string">NICKNAME</span></div>'
			html += '<div class="column-right"><input type="text" name="user_id" size="20" maxlength="20" value="{}"></div>'.format(user.user_id)
			html += '</div>' #setting-nickname-wrapper
			
			html += '<div class="setting clan-wrapper">'
			html += '<div class="column-left"><span id="clan-string">CLAN</span></div>'
			html += '<div class="column-right"><input type="text" name="user_clan" size="10" maxlength="10" value="{}"></div>'.format(user.user_clan)
			html += '</div>' #setting-clan-wrapper
			
			html += '<div class="setting class-wrapper">'
			html += '<div class="column-left"><span id="class-string">FAVORITE CLASS</span></div>'
			html += '<div class="column-right"><select name="user_favclass">'
			for class_string in _CLASSES:
				if user.user_favclass == class_string:
					html += '<option value="{}" selected>{}</option>'.format(class_string, class_string.upper())
				else:
					html += '<option value="{}">{}</option>'.format(class_string, class_string.upper())
			html += '</select></div>'
			html += '</div>' #setting-class-wrapper
			
			html += '<div class="setting title-wrapper">'
			html += '<div class="column-left"><span id="title-string">TITLE</span></div>'
			html += '<div class="column-right"><select name="user_title">'
			trophy_list = ndb.gql('SELECT * FROM TrophyEntity WHERE trophy_owner=:1', user.key.id()).order(TrophyEntity.trophy_getdate)
			html += '<option value=""></option>'
			for trophy in trophy_list:
				if user.user_title == ProfilePage2.getTrophyName(trophy.trophy_index):
					html += '<option value="{}" selected>{}</option>'.format(ProfilePage2.getTrophyName(trophy.trophy_index), ProfilePage2.getTrophyName(trophy.trophy_index).upper())
				else:
					html += '<option value="{}">{}</option>'.format(ProfilePage2.getTrophyName(trophy.trophy_index), ProfilePage2.getTrophyName(trophy.trophy_index).upper())
			html += '</select></div>'
			html += '</div>' #setting-title-wrapper
			
			html += '<div class="setting desc-wrapper">'
			html += '<div class="column-left"><span id="desc-string">DESCRIPTION</span></div>'
			html += '<div class="column-right"><textarea rows="4" cols="50" name="user_word" resize="none">{}</textarea></div>'.format(user.user_word.replace('<br>', '\n'))
			html += '</div>' #setting-desc-wrapper
			
			html += '<div class="setting message-wrapper">'
			html += '<div class="column-left"><span id="message-string">HELLO MESSAGE(FOR GG2SM)</span></div>'
			html += '<div class="column-right"><input type="text" name="user_message" size="50" maxlength="50" value="{}"></div>'.format(user.user_message)
			html += '</div>' #setting-message-wrapper
			
			html += '<div class="setting avatar-wrapper">'
			html += '<div class="column-left"><span id="avatar-string">AVATAR</span></div>'
			html += '<div class="column-right">'
			html += '<input type="file" name="user_avatar" class="filestyle" data-placeholder="No file" data-classButton="btn btn-primary" data-classIcon="icon-plus" data-buttonText="">'
			html += '</div>'
			html += '</div>' #setting-avatar-wrapper
			
			html += '<div class="setting menu-wrapper">'
			html += '<input type="submit" value="UPDATE" />'
			html += '</div>' #setting-menu-wrapper
			
			html += '</div>' #setting-wrapper
			html += '</form>'
			
			html += '</body>'
			html += '</html>'
			self.response.out.write(html)
		else:
			self.redirect('/')
		
	def post(self):
		new_id = self.request.get('user_id')
		new_id = new_id[:20]
		
		new_id = new_id.replace('<', '&lt')
		new_id = new_id.replace('>', '&gt')
		new_id = new_id.replace('#', '')
		new_id = new_id.replace('&', '')
		new_id = new_id.replace(';', '')
		new_id = new_id.replace('+', '')
		new_id = new_id.replace(',', '')
		new_id = new_id.replace('(', '')
		new_id = new_id.replace(')', '')
		new_id = new_id.replace('[', '')
		new_id = new_id.replace(']', '')
		new_id = new_id.replace('.', '')
		
		error_string = ''
		
		if (new_id) == '':
			new_id = 'BLANK'

		try:
			new_id.decode('ascii')
		except UnicodeDecodeError:
			error_string = "You can only use ascii character set for your NickName!"
		else:
			isIdExist = ndb.gql('SELECT * FROM UserEntity WHERE user_id=:id', id = new_id)
			cnt = 0
			current_user = users.get_current_user()
			for user in isIdExist:
				cnt += 1
			if cnt and user.google_id != current_user:
				error_string += new_id + ' Already Exists!'
			else:
				user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
				user_clan = self.request.get('user_clan')
				user_word = self.request.get('user_word').replace('<', '&lt').replace('>', '&gt')
				user_title = self.request.get('user_title')
				user_favclass = self.request.get('user_favclass')
				user_message = self.request.get('user_message')
				user_avatar = str(self.request.get('user_avatar'))
				if new_id:
					user.user_id = new_id
				user_clan = user_clan[:10]
				user_clan = user_clan.lstrip()
				user_clan = user_clan.rstrip()
				user_clan = user_clan.replace('[', '')
				user_clan = user_clan.replace(']', '')
				if not (user_clan == ''):
					user_clan = '[' + user_clan + ']'
				user.user_clan = user_clan
				user_word = user_word.replace('Javascript', '')
				user_word = user_word.replace('javascript', '')
				user.user_word = user_word
				user.user_title = user_title
				user.user_favclass = user_favclass
				user.user_message = user_message
				if user_avatar:
					user_avatar = images.resize(user_avatar, 200, 200)
					user.user_avatar = user_avatar
				user.put()
		html = '<script type="text/javascript">'
		if error_string:
			html += 'alert("{}");'.format(error_string)
			html += 'location.href="/profilesetting";'
		else:
			html += 'alert("{}");'.format('Change successfully applied!')
			html += 'location.href="/myprofile";'
		html += '</script>'
		
		self.response.out.write(html)

#플레이어의 백팩 페이지
class BackpackPage(webapp2.RequestHandler):
	def get(self):
		user_id = self.request.get('id')
		user = ndb.gql('SELECT * FROM UserEntity WHERE user_id=:1', user_id).get()
		if not user:
			self.redirect('/')
		else:
			html = '<!DOCTYPE html>'
			html += '<HTML>'
			
			html += '<HEAD>'
			html += '<TITLE>GG2S:{}\'s backpack</TITLE>'.format(user_id)
			html += '<script type="text/javascript" src="/js/jquery.js"></script>'
			html += '<script type="text/javascript" src="/js/backpack.js"></script>'
			html += '<link rel="stylesheet" type="text/css" href="/css/backpack.css">'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS : {}\'S BACKPACK</span></a>'.format(user_id.upper())
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper
			
			html += '<div class="backpack-wrapper">'
			html += '<div class="backpack-page backpack-visible" id="backpack-1">'
			cnt = 0
			html += '<div class="backpack-row">'
			item_list = ndb.gql('SELECT * FROM BackpackEntity WHERE item_owner=:1', user.key.id()).order(BackpackEntity.item_getdate)
			for item in item_list:
				if (cnt % 10 == 0) and (cnt != 0):
					if cnt % 50 is 0:
						html += '</div></div><div class="backpack-page backpack-invisible" id="backpack-{}"><div class="backpack-row">'.format(cnt // 50 + 1)
					else:
						html += '</div><div class="backpack-row">'
				html += '<div '
				if (item.is_trading):
					html += 'id="trading" '
				html += 'class="backpack-item {}">'.format(rarityIntegerConvert(item.item_rarity))
				html += '<a href="/item?item={}&backpack={}">'.format(item.key.urlsafe(), user.user_id)
				html += '<img src="/itemthumb/{}.png" />'.format(item.item_name)
				html += '</a>'
				html += '</div>'
				cnt += 1
			
			if cnt % 50 or cnt == 0:
				while (cnt % 50 or cnt == 0):
					if not cnt % 10 and cnt != 0:
						html += '</div><div class="backpack-row">'
					html += '<div class="backpack-item none"><a></a></div>'
					cnt += 1
					
			html += '</div>' #backpack-row
			html += '</div>' #backpack-page
			html += '</div>' #backpack-wrapper
			
			html += '<div class="backpack-selector">'
			for i in range(cnt // 50):
				if i == 0:
					html += '<div class="selector-wrapper selected" id="selector-1" onclick="changeBackpackPage(1);">1</div>'
				else:
					html += '<div class="selector-wrapper" id="selector-{0}" onclick="changeBackpackPage({0});">{0}</div>'.format(i + 1)
			html += '</div>' #backpack-selector
			
			self.response.out.write(html)
			
#로드아웃 페이지
class LoadoutPage(webapp2.RequestHandler):
	def get(self):
		google_id = users.get_current_user()
		if not google_id:
			self.redirect('/')
		else:
			current_class = self.request.get('class')
			current_team = self.request.get('team')
			current_show = self.request.get('show')
			if not current_class:
				current_class = "Runner"
			if not current_team:
				current_team = "Red"
			if not current_show:
				current_show = "Normal"
			
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', google_id).get()
			user_key = user.key.id() #integer key
			
			loadout = ndb.Key(LoadoutEntity, user_key).get()
			loadout_head = loadout.head_list
			loadout_torso = loadout.torso_list
			loadout_leg = loadout.leg_list
			loadout_weapon = loadout.weapon_list
			loadout_misc = loadout.misc_list
			loadout_taunt = loadout.taunt_list
			loadout_pet = loadout.pet_list
			loadout_death = loadout.death_list
			loadout_humiliation = loadout.humiliation_list
			loadout_head = loadout_head.split(',')
			loadout_torso = loadout_torso.split(',')
			loadout_leg = loadout_leg.split(',')
			loadout_weapon = loadout_weapon.split(',')
			loadout_misc = loadout_misc.split(',')
			loadout_taunt = loadout_taunt.split(',')
			loadout_pet = loadout_pet.split(',')
			loadout_death = loadout_death.split(',')
			loadout_humiliation = loadout_humiliation.split(',')
			
			html = '<!DOCTYPE html>'
			html += '<HTML>'
			
			html += '<HEAD>'
			html += '<TITLE>GG2S:LOADOUT</TITLE>'
			html += '<link rel="stylesheet" type="text/css" href="/css/loadout.css">'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS : LOADOUT</span></a>'
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper
			
			html += '<div class="class-selector-wrapper">'
			for each_class in _CLASSES:
				html += '<a href="/loadout?class={}&team={}"><img id="class-icon" src="images/icon_{}_outline.png" /></a>'.format(each_class, current_team, each_class)
			html += '</div>' #class-selector-wrapper
			
			if(loadout_head[findClassConstant(current_class)] != ''):
				item_head = ndb.Key(BackpackEntity, int(loadout_head[findClassConstant(current_class)])).get()
			else:
				item_head = ''
			if(loadout_torso[findClassConstant(current_class)] != ''):
				item_torso = ndb.Key(BackpackEntity, int(loadout_torso[findClassConstant(current_class)])).get()
			else:
				item_torso = ''
			if(loadout_leg[findClassConstant(current_class)] != ''):
				item_leg = ndb.Key(BackpackEntity, int(loadout_leg[findClassConstant(current_class)])).get()
			else:
				item_leg = ''
			if(loadout_weapon[findClassConstant(current_class)] != ''):
				item_weapon = ndb.Key(BackpackEntity, int(loadout_weapon[findClassConstant(current_class)])).get()
			else:
				item_weapon = ''
			if(loadout_misc[findClassConstant(current_class)] != ''):
				item_misc= ndb.Key(BackpackEntity, int(loadout_misc[findClassConstant(current_class)])).get()
			else:
				item_misc = ''
			if(loadout_taunt[findClassConstant(current_class)] != ''):
				item_taunt = ndb.Key(BackpackEntity, int(loadout_taunt[findClassConstant(current_class)])).get()
			else:
				item_taunt = ''
			if(loadout_pet[findClassConstant(current_class)] != ''):
				item_pet = ndb.Key(BackpackEntity, int(loadout_pet[findClassConstant(current_class)])).get()
			else:
				item_pet = ''
			if(loadout_death[findClassConstant(current_class)] != ''):
				item_death = ndb.Key(BackpackEntity, int(loadout_death[findClassConstant(current_class)])).get()
			else:
				item_death = ''
			if(loadout_humiliation[findClassConstant(current_class)] != ''):
				item_humiliation = ndb.Key(BackpackEntity, int(loadout_humiliation[findClassConstant(current_class)])).get()
			else:
				item_humiliation = ''
				
			item_list = [item_head, item_torso, item_leg, item_weapon, item_misc, item_taunt, item_pet, item_death, item_humiliation]
			item_part_string = ["head", "torso", "leg", "weapon", "misc", "taunt", "pet", "death", "humiliation"]
			
			html += '<div class="loadout-wrapper">'
			
			html += '<div class="loadout-column-left">'
			for i in range(3):
				if current_class != "Quote" or item_part_string[i] != "leg":
					html += '<div class="loadout-{}" id="'.format(item_part_string[i])
					if item_list[i]:
						html += rarityIntegerConvert(item_list[i].item_rarity)
					else:
						html += 'none'
					html += '">'
					html += '<span>{}</span>'.format(item_part_string[i].upper())
					html += '<a href="/changeloadout?part={}&class={}&team={}">'.format(i, current_class, current_team)
					if item_list[i]:
						html += '<img class="loadout-image" src="/itemthumb/' + item_list[i].item_name + '.png">'
					else:
						html += '<img class="loadout-image" src="/images/blank64.png">'
					html += '</a>'
					html += '</div>'
				else:
					html += '<div class="loadout-{}">'.format(item_part_string[i])
					html += '<img class="loadout-image" src="/images/blank64.png">'
					html += '</div>'
			html += '</div>' #loadout-column-left
			
			html += '<div class="loadout-column-middle">'
			html += '<div class="loadout-portrait">'
			if (current_show == "Normal") or (current_show == "Taunt" and not item_taunt):
				for i in range(3):
					if current_class != "Quote" or item_part_string[i] != "leg":
						if item_list[i]:
							html += '<img class="loadout-preview-image" id="None" src="/itempart/{}_{}_{}.png">'.format(item_list[i].item_name, current_class, current_team)
						else:
							html += '<img class="loadout-preview-image" id="None" src="/charpart/{}_{}_{}.png">'.format(current_class, item_part_string[i].capitalize(), current_team)
				if item_weapon:
					html += '<img class="loadout-preview-image" id="{}" src="/weaponpart/{}_{}.png">'.format(findWeaponString(current_class), item_weapon.item_name, current_team)
				else:
					html += '<img class="loadout-preview-image" id="{}" src="/weaponpart/{}_{}.png">'.format(findWeaponString(current_class), findWeaponString(current_class), current_team)
			elif (current_show == "Taunt"):
				if item_taunt:
					html += '<img class="loadout-preview-image" id="None" src="/tauntpart/{}_{}.gif">'.format(item_taunt.item_name, current_team)
					
			html += '<div class="portrait-menu-wrapper">'
			if current_team == "Red":
				html += '<div class="portrait-menu-team" id="blue">'
				html += '<a class="menu" href="/loadout?class={}&team=Blue">'.format(current_class)
			else:
				html += '<div class="portrait-menu-team" id="red">'
				html += '<a class="menu" href="/loadout?class={}&team=Red">'.format(current_class)
			html += '<span>CHANGE TEAM</span>'
			html += '</a>'
			html += '</div>' #portrait-menu-team
			html += '<div class="portrait-menu-taunt">'
			if current_show == "Taunt":
				html += '<a class="menu" href="/loadout?class={}&team={}">'.format(current_class, current_team)
				html += '<span>SHOW PORTRAIT</span>'
			else:
				html += '<a class="menu" href="/loadout?class={}&team={}&show=Taunt">'.format(current_class, current_team)
				html += '<span>SHOW TAUNT</span>'
			html += '</a>'
			html += '</div>' #portrait-menu-taunt
			html += '</div>' #portrait-menu-wrapper
			
			html += '</div>' #loadout-portrait
			html += '</div>' #loadout-column-middle

			html += '<div class="loadout-column-right">'
			for i in range(3, 6):
				html += '<div class="loadout-{}" id="'.format(item_part_string[i])
				if item_list[i]:
					html += rarityIntegerConvert(item_list[i].item_rarity)
				else:
					html += 'none'
				html += '">'
				html += '<span>{}</span>'.format(item_part_string[i].upper())
				html += '<a href="/changeloadout?part={}&class={}&team={}">'.format(i, current_class, current_team)
				if item_list[i]:
					html += '<img class="loadout-image" src="/itemthumb/' + item_list[i].item_name + '.png">'
				else:
					html += '<img class="loadout-image" src="/images/blank64.png">'
				html += '</a>'
				html += '</div>'
			html += '</div>' #loadout-column-right
			
			html += '<div class="loadout-footer">'
			for i in range(6, 9):
				html += '<div class="loadout-{}" id="'.format(item_part_string[i])
				if item_list[i]:
					html += rarityIntegerConvert(item_list[i].item_rarity)
				else:
					html += 'none'
				html += '">'
				html += '<span>{}</span>'.format(item_part_string[i].upper())
				html += '<a href="/changeloadout?part={}&class={}&team={}">'.format(i, current_class, current_team)
				if item_list[i]:
					html += '<img class="loadout-image" src="/itemthumb/' + item_list[i].item_name + '.png">'
				else:
					html += '<img class="loadout-image" src="/images/blank64.png">'
				html += '</a>'
				html += '</div>'
			html += '</div>' #loadout-column-footer
			html += '</div>' #loadout-wrapper
			
			#Backpack + Return
			html += '<div class="page-footer">'
			html += '<a href="/backpack?id=' + user.user_id + '" style="color:white;">Backpack</a>&nbsp&nbsp'
			html += '<a href="/" style="color:white;">Return</a>'
			html += '</div>'
			html += '</BODY>'
			html += '</HTML>'
			self.response.out.write(html)

class LoadoutChangePage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					background-color: #454545;
					color: white;
					font-family: 'Press Start 2P', sans-serif, cursive;
					vertical-align: middle;
				}
				img{
					image-rendering: crisp-edges;
					image-rendering: pixelated;
				}
				p.logobig{
					text-align: center;
					display: table;
					margin: auto;
					margin-top: 50px;
					margin-bottom: 50px;
				}
				fieldset.backpack{
					margin: auto;
					background-color: #2B2726;
					width: 870px;
					height: 445px;
					margin-bottom: 30px;
				}
				table{
					border-collapse: seperate;
					cellpadding: 0px;
					border-spacing: 10px;
				}
				td{
					padding: auto;
					width: 64px;
					height: 76px;
					Border: 5px;
					border-style: solid;
					border-radius:0.4em;
				}
				td.none{
					Border-color: #2B2726;
					background-color: #3C352E;
				}
				td.normal{
					Border-color: #F7DC07;
					background-color: #4B4314;
				}
				td.strange{
					Border-color: #BB7343;
					background-color: #472B1F;
				}
				td.unusual{
					Border-color: #835699;
					background-color: #372A3C;
				}
				td.vintage{
					Border-color: #476291;
					background-color: #292D36;				
				}
				td.self-made{
					Border-color: #70B04A;
					background-color: #2B3E24;
				}
				button{
					background-color: Transparent;
					background-repeat:no-repeat;
					border: none;
					cursor:pointer;
					overflow: hidden;
					outline:none;
					padding: 0px;
				}
				form{
					margin: 0px;
				}
			</style>
		"""
		google_id = users.get_current_user()
		if not google_id:
			self.redirect('/')
		else:
			current_part = int(self.request.get('part'))
			current_class = self.request.get('class')
			current_team = self.request.get('team')
			try:
				page = int(self.request.get('page'))
			except ValueError:
				page = 1
			if (page < 1):
				page = 1
			if current_part == '':
				self.redirect('/loadout')
			if not current_class:
				self.redirect('/loadout')
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', google_id).get()
			if not user:
				self.redirect('/')
			user_key = user.key.id()
			total_item = ndb.gql('SELECT * FROM BackpackEntity WHERE item_owner=:1 AND item_part=:2', user_key, current_part)
			item_list = total_item.order(BackpackEntity.item_getdate).fetch(offset=50*(page - 1))
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S:ChangeLoadout</TITLE>' + css + '</HEAD>'
			html += '<body>'
			html += '<div>'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			html += '<fieldset class="backpack">'
			html += '<legend>Available Item for ' + partToString(current_part) + '</legend>'
			html += '<table>'
			cnt = 0
			page_cnt = 0
			html += '<tr>'
			#로드아웃 해제버튼
			cnt += 1
			page_cnt += 1
			html += '<td class="none">'
			html += '<form method="POST">'
			html += '<input type="hidden" name="name" value="">'
			html += '<input type="hidden" name="part" value="' + str(current_part) + '">'
			html += '<input type="hidden" name="class" value="' + current_class + '">'
			html += '<input type="hidden" name="team" value="' + current_team + '">'
			html += '<button type="submit" class="itemsubmit"><img style="width: 64px; height: 64px;" src="/images/buttons_nope.png"></img></button>'
			html += '</div>'
			html += '</form>' + '</td>'
			for item in item_list:
				item_info = ndb.Key(ItemEntity, item.item_name).get()
				class_list = item_info.item_classlist.split(',')
				if current_class in class_list:
					if cnt < 50:
						cnt += 1
						html += '<td class="' + rarityIntegerConvert(item.item_rarity) + '">'
						html += '<form method="POST">'
						html += '<input type="hidden" name="key" value="' + str(item.key.id()) + '">'
						html += '<input type="hidden" name="part" value="' + str(current_part) + '">'
						html += '<input type="hidden" name="class" value="' + current_class + '">'
						html += '<button type="submit" class="itemsubmit"><img style="width: 64px; height: 64px;" src="/itemthumb/' + item.item_name + '.png"></img></button>'
						html += '</div>'
						html += '</form>' + '</td>'
						if cnt % 10 == 0:
							html += '</tr><tr>'
					page_cnt += 1
				else:
					pass
			while(cnt < 50):
				cnt += 1
				html += '<td class="none">' + '</td>'
				if cnt % 10 == 0 and cnt < 50:
					html += '</tr><tr>'
			html += '</tr>'
			html += '</table>'
			html += '</fieldset>'
			html += '<div style="text-align: center; margin-bottom:20px;">'
			for i in range((page_cnt // 49) + page):
				html += '<a href="/changeloadout?part=%s&class=%s&team=%s&page=%s" style="color: white; text-decoration: none;">' %(str(current_part), current_class, current_team, str(i + 1)) + str(i + 1) + ' </a>'
			html += '</div>'
			html += '<div style="text-align: center; margin-bottom:50px;">'
			current_user = users.get_current_user()
			if user.google_id == current_user:
				html += '<a href="/loadout" style="color:white;">Loadout</a>&nbsp&nbsp'
			html += '<a href="/profile?id=' + user.user_id + '" style="color:white;">Return</a>'
			html += '</div>'
			self.response.out.write(html)
	
	def post(self):
		google_id = users.get_current_user()
		if not google_id:
			self.redirect('/')
		else:
			item_key = self.request.get('key')
			current_part = int(self.request.get('part'))
			current_class = self.request.get('class')
			current_team = self.request.get('team')
			if current_part == '':
				self.redirect('/loadout')
			if not current_class:
				self.redirect('/loadout')
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', google_id).get()
			if not user:
				self.redirect('/')
			user_key = user.key.id()
			loadout = ndb.Key(LoadoutEntity, user_key).get()
			if current_part == 0:
				loadout_list = loadout.head_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.head_list = loadout_str
			elif current_part == 1:
				loadout_list = loadout.torso_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.torso_list = loadout_str
			elif current_part == 2:
				loadout_list = loadout.leg_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.leg_list = loadout_str
			elif current_part == 3:
				loadout_list = loadout.weapon_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.weapon_list = loadout_str
			elif current_part == 4:
				loadout_list = loadout.misc_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.misc_list = loadout_str
			elif current_part == 5:
				loadout_list = loadout.taunt_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.taunt_list = loadout_str
			elif current_part == 6:
				loadout_list = loadout.pet_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.pet_list = loadout_str
			elif current_part == 7:
				loadout_list = loadout.death_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.death_list = loadout_str
			elif current_part == 8:
				loadout_list = loadout.humiliation_list.split(',')
				loadout_list[findClassConstant(current_class)] = str(item_key)
				loadout_str = ''
				if loadout_list:
					for each_item in loadout_list:
						loadout_str += each_item + ','
				if loadout_str:
					loadout_str = loadout_str[:-1]
				loadout.humiliation_list = loadout_str
			else:
				self.redirect('/loadout')
			loadout.put()
			if not current_part == 5:
				self.redirect('/loadout?class=' + current_class + '&team=' + current_team)
			else:
				self.redirect('/loadout?class=' + current_class + '&team=' + current_team + '&show=Taunt')
			
#cron activity용				
class ResetTodayEntityPage(webapp2.RequestHandler):
	def get(self):
		today_list = ndb.gql('SELECT * FROM TodayEntity')
		for today in today_list:
			if (today.user_kill or today.user_death or today.user_assist or today.user_cap or today.user_destruction or today.user_stab or today.user_healing or today.user_defense or today.user_invuln or today.user_kda or today.user_playcount or today.user_point):
				today.user_kill = 0
				today.user_death = 0
				today.user_assist = 0
				today.user_cap = 0
				today.user_destruction = 0
				today.user_stab = 0
				today.user_healing = 0
				today.user_defense = 0
				today.user_invuln = 0
				today.user_kda = 0
				today.user_playcount = 0
				today.user_point = 0
				today.put()
		memcache.delete('mainVisitorCounter') #메인페이지 카운터 리셋

class MakeDailyQuestPage(webapp2.RequestHandler):
	def get(self):
		user_list = ndb.gql('SELECT * FROM UserEntity')
		for user in user_list:
			quest_list = ndb.gql('SELECT * FROM DailyquestEntity WHERE quest_owner=:1', user.key.id())
			if (quest_list.count() < 3):
				quest = DailyquestEntity()
				quest_available = list(range(len(_QUESTS)))
				for item in quest_list:
					quest_available.remove(item.quest_type)
				quest.quest_type = choice(quest_available)
				quest.quest_owner = user.key.id()
				quest.put()
				memcache.delete('questInfo-' + str(user.key.id()))
			else:
				pass
		
#아바타 이미지 프로세서
class ImagePage(webapp2.RequestHandler):
	def get(self):
		user_key = ndb.Key(urlsafe=self.request.get('img_id'))
		user = user_key.get()
		if user.user_avatar:
			self.response.headers['Content-Type'] = 'image/gif'
			self.response.out.write(user.user_avatar)
		else:
			self.response.out.write('No Image')

class AvatarPage(webapp2.RequestHandler):
	def get(self):
		user_id = self.request.get('nickname')
		user = memcache.get('user:{}'.format(user_id))
		if user is None:
			user = ndb.gql('SELECT * FROM UserEntity WHERE user_id=:id', id = user_id).get()
		if user.user_avatar:
			self.response.headers['Content-Type'] = 'image/gif'
			self.response.out.write(user.user_avatar)
		else:
			self.response.headers['Content-Type'] = 'image/gif'
			path = os.path.join(os.path.split(__file__)[0], 'images/gg2slogo_beige_192.png')
			with open(path, 'rb') as f:
				avatar = f.read()
			self.response.out.write(avatar)
		
#로드아웃 반환 페이지		
class GetLoadoutPage(webapp2.RequestHandler):
	def get(self):
		html = '<html>'
		html += '<body>'
		
		html += '<form method="POST">'
		
		html += '<input name="user_key" type="text" />'
		html += '<input type="submit" />'
		
		html += '</form>'
		
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)
		
	def post(self):
		user_key = self.request.get('user_key')
		try:
			loadout = ndb.Key(LoadoutEntity, int(user_key)).get()
			head_list = loadout.head_list.split(',')
			torso_list = loadout.torso_list.split(',')
			leg_list = loadout.leg_list.split(',')
			weapon_list = loadout.weapon_list.split(',')
			misc_list = loadout.misc_list.split(',')
			taunt_list = loadout.taunt_list.split(',')
			pet_list = loadout.pet_list.split(',')
			death_list = loadout.death_list.split(',')
			humiliation_list = loadout.humiliation_list.split(',')
			
			item_key_head = []
			item_key_torso = []
			item_key_leg = []
			item_key_weapon = []
			item_key_misc = []
			item_key_taunt = []
			item_key_pet = []
			item_key_death = []
			item_key_humiliation = []
			
			for i in range(10):
				if not (head_list[i] == ''):
					item_key_head.append(ndb.Key(BackpackEntity, int(head_list[i])))
				if not (torso_list[i] == ''):
					item_key_torso.append(ndb.Key(BackpackEntity, int(torso_list[i])))
				if not (leg_list[i] == ''):
					item_key_leg.append(ndb.Key(BackpackEntity, int(leg_list[i])))
				if not (weapon_list[i] == ''):
					item_key_weapon.append(ndb.Key(BackpackEntity, int(weapon_list[i])))
				if not (misc_list[i] == ''):
					item_key_misc.append(ndb.Key(BackpackEntity, int(misc_list[i])))
				if not (taunt_list[i] == ''):
					item_key_taunt.append(ndb.Key(BackpackEntity, int(taunt_list[i])))
				if not (pet_list[i] == ''):
					item_key_pet.append(ndb.Key(BackpackEntity, int(pet_list[i])))
				if not (death_list[i] == ''):
					item_key_death.append(ndb.Key(BackpackEntity, int(death_list[i])))
				if not (humiliation_list[i] == ''):
					item_key_humiliation.append(ndb.Key(BackpackEntity, int(humiliation_list[i])))
					
			ndb_get_list = item_key_head + item_key_torso + item_key_leg + item_key_weapon + item_key_misc + item_key_taunt + item_key_pet + item_key_death + item_key_humiliation
			ndb_get_list.append(ndb.Key(UserEntity, int(user_key)))
			
			item_list = ndb.get_multi(ndb_get_list)
			
			cnt = 0
			for i in range(10):
				if not (head_list[i] == ''):
					item_head = item_list[cnt]
					head_list[i] = item_head.item_name
					if (item_head.item_effect != None):
						head_list[i] += '+' + str(item_head.item_effect)
					cnt += 1
				else:
					head_list[i] = ''
			for i in range(10):
				if not (torso_list[i] == ''):
					torso_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					torso_list[i] = ''
			for i in range(10):
				if not (leg_list[i] == ''):
					leg_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					leg_list[i] = ''
			for i in range(10):
				if not (weapon_list[i] == ''):
					item_weapon = item_list[cnt]
					weapon_list[i] = item_weapon.item_name
					if (item_weapon.item_strangeType != None):
						weapon_list[i] += '+' + str(item_weapon.item_strangeType)
						weapon_list[i] += '-' + str(item_weapon.item_strangeCount)
					cnt += 1
				else:
					weapon_list[i] = ''
			for i in range(10):
				if not (misc_list[i] == ''):
					misc_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					misc_list[i] = ''
			for i in range(10):
				if not (taunt_list[i] == ''):
					taunt_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					taunt_list[i] = ''
			for i in range(10):
				if not (pet_list[i] == ''):
					pet_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					pet_list[i] = ''
			for i in range(10):
				if not (death_list[i] == ''):
					death_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					death_list[i] = ''
			for i in range(10):
				if not (humiliation_list[i] == ''):
					humiliation_list[i] = item_list[cnt].item_name
					cnt += 1
				else:
					humiliation_list[i] = ''
			loadout_str = ''
			for item in head_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in torso_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in leg_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in weapon_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in misc_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in taunt_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in pet_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in death_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			for item in humiliation_list:
				loadout_str += item + ','
			loadout_str = loadout_str[:-1] + ';'
			loadout_str += item_list[cnt].user_title
		except:
			loadout_str = ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ',,,,,,,,,' + ';' + ''
		self.response.out.write(loadout_str)

#아이템 설명 페이지
class ItemPage(webapp2.RequestHandler):
	def get(self):
		backpack = self.request.get('backpack')
		try:
			item = ndb.Key(urlsafe=self.request.get('item')).get() #실제 참조중인 개체는 BackpackEntity
			item_info = ndb.Key(ItemEntity, item.item_name).get()
			html = '<!DOCTYPE html>'
			html += '<HTML>'
			
			html += '<HEAD>'
			html += '<TITLE>GG2S: {}</TITLE>'.format(item_info.item_nickname)
			html += '<link rel="stylesheet" type="text/css" href="/css/item.css">'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS : {}</span></a>'.format(item_info.item_nickname.upper())
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper

			html += '<div class="item-wrapper">'
			html += '<div class="item-image-wrapper" id="{}">'.format(rarityIntegerConvert(item.item_rarity))
			html += '<a href="/iteminfo?item={}"><img id="item-image" src="/itemthumb/{}.png"></a>'.format(item_info.key.id(), item.item_name)
			html += '</div>' #item-image-wrapper
			
			if (item.item_rarity == 1):
				html += '<div class="item-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('strange', strangeCountToString(item.item_strangeCount).upper())
			elif (item.item_rarity == 2):
				html += '<div class="item-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('unusual', 'UNUSUAL')
			elif (item.item_rarity == 3):
				html += '<div class="item-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('vintage', 'VINTAGE')
			html += '<div class="item-name-wrapper"><span id="{}" class="name-string">{}</span></div>'.format(rarityIntegerConvert(item.item_rarity), item_info.item_nickname.upper())
			
			html += '<div class="item-level-wrapper"><span id="level-string">LEVEL {} {}</span></div>'.format(item.item_level, partToString(item_info.item_part).upper())
			if	(item.item_rarity == 1):
				html += '<div class="item-strangetype-wrapper"><span id="{}" class="strangetype-string">{}: {}</span></div>'.format(rarityIntegerConvert(item.item_rarity), strangeTypeToString(item.item_strangeType).upper(), item.item_strangeCount)
			elif (item.item_rarity == 2):
				html += '<div class="item-unusualtype-wrapper"><span id="{}" class="unusualtype-string">UNUSUAL EFFECT: {}</span></div>'.format(rarityIntegerConvert(item.item_rarity), unusualTypeToString(item.item_effect).upper())
			html += '<div class="item-desc-wrapper"><span id="desc-string">{}</span></div>'.format(item_info.item_desc.upper())
			html += '<div class="item-classlist-wrapper"><span id="classlist-string">'
			if (item_info.item_classlist.split(',') == _CLASSES):
				html += 'ITEM FOR: ALL CLASSES'
			elif (item_info.item_classlist.split(',') + ["Quote"] == _CLASSES):
				html += 'ITEM FOR: ALL CLASSES EXCEPT QUOTE'
			else:
				html += 'ITEM FOR: {}'.format(item_info.item_classlist.upper())
			html += '</span></div>'
			html += '</div>' #item-wrapper
					
			current_user = users.get_current_user()
			user = ndb.Key(UserEntity, item.item_owner).get()
			if user:
				if user.google_id == current_user:
					if not item.item_part == 6:
						if item.item_rarity == 0:
							item_price = 25
						elif item.item_rarity == 1:
							item_price = 50
						elif item.item_rarity == 2:
							item_price = 100
						elif item.item_rarity == 3:
							item_price = 25
						elif item.item_rarity == 4:
							item_price = 0
					else:
						if not item.item_rarity == 4:
							item_price = 100
						else:
							item_price = 0
					if not (item_price == 0):
						if not (item.is_trading):
							html += '<div class="item-menu-wrapper"><button type="button" id="menu-button"><a href="/sell?item={}">SELL FOR {} COINS</a></button></div>'.format(item.key.urlsafe(), item_price)
							html += '<div class="item-menu-wrapper"><button type="button" id="menu-button"><a href="/maketrade?item={}">MAKE A TRADE</a></button></div>'.format(item.key.urlsafe())

			if item.is_trading:
				html += '<div class="item-menu-wrapper"><button type="button" id="menu-button" disabled>REGISTERED FOR TRADING!</button></div>'

			html += '<div class="item-menu-wrapper"><button type="button" id="menu-button"><a href="/backpack?id={}">RETURN</a></button></div>'.format(backpack)	
			self.response.out.write(html)
		except:
			self.redirect('/')

#아이템 설명 페이지(Abstract)
class ItemInfoPage(webapp2.RequestHandler):
	def get(self):
		item_name = self.request.get('item')
		if item_name:
			item_info = ndb.Key(ItemEntity, item_name).get()
			html = '<!DOCTYPE html>'
			html += '<HTML>'
			
			html += '<HEAD>'
			html += '<TITLE>GG2S: {}</TITLE>'.format(item_info.item_nickname)
			html += '<link rel="stylesheet" type="text/css" href="/css/item.css">'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS : {}</span></a>'.format(item_info.item_nickname.upper())
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper

			html += '<div class="item-wrapper">'
			if item_info.is_vintage:
				html += '<div class="item-image-wrapper" id="vintage">'
			else:
				html += '<div class="item-image-wrapper" id="normal">'
			html += '<img id="item-image" src="/itemthumb/{}.png">'.format(item_info.key.id())
			html += '</div>' #item-image-wrapper
			
			if item_info.is_vintage:
				html += '<div class="item-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('vintage', 'VINTAGE')
				html += '<div class="item-name-wrapper"><span id="{}" class="name-string">{}</span></div>'.format('vintage', item_info.item_nickname.upper())
			else:
				html += '<div class="item-name-wrapper"><span id="{}" class="name-string">{}</span></div>'.format('normal', item_info.item_nickname.upper())
			
			html += '<div class="item-level-wrapper"><span id="level-string">ITEM CREATOR: {}</span></div>'.format(item_info.item_author.upper())
			html += '<div class="item-desc-wrapper"><span id="desc-string">{}</span></div>'.format(item_info.item_desc.upper())
			html += '<div class="item-classlist-wrapper"><span id="classlist-string">'
			if (item_info.item_classlist.split(',') == _CLASSES):
				html += 'ITEM FOR: ALL CLASSES'
			elif (item_info.item_classlist.split(',') + ["Quote"] == _CLASSES):
				html += 'ITEM FOR: ALL CLASSES EXCEPT QUOTE'
			else:
				html += 'ITEM FOR: {}'.format(item_info.item_classlist.upper())

			if item_info.item_part is not 4:
				html += '<div class="item-preview-wrapper">'
				if item_info.item_part in [0, 1, 2, 3, 5]:
					if item_info.item_part in [0, 1, 2]: #Head, Torso, Leg
						for class_part in item_info.item_classlist.split(','):
							html += '<div class="item-preview-row">'
							html += '<img class="{}" src="/itempart/{}_{}_Red.png">'.format(partToString(item_info.item_part), item_name, class_part)
							html += '<img class="{}" src="/itempart/{}_{}_Blue.png">'.format(partToString(item_info.item_part), item_name, class_part)
							html += '</div>' #item-preview-row
					elif item_info.item_part == 3: #Weapon
						html += '<img src="/weaponpart/{}_Red.png">'.format(item_name)
						html += '<img src="/weaponpart/{}_Blue.png">'.format(item_name)
					else:		#Taunt
						html += '<img src="/tauntpart/{}_Red.gif">'.format(item_name)
						html += '<img src="/tauntpart/{}_Blue.gif>'.format(item_name)
				else:
					if item_info.item_part in [6, 7, 8]: #Pet, D.Anim, Humiliation
						misc_dir = '/download/items/misc'
						if item_info.item_part is 6: #Pet
							html += '<img src="{}/Pet/{}/idle.png">'.format(misc_dir, item_name)
						elif item_info.item_part is 7: #D.Anim
							html += '<img src="{}/Death/{}/Death.gif">'.format(misc_dir, item_name)
						elif item_info.item_part is 8: #Humiliation
							html += '<img src="{}/Humiliation/{}/Red.png">'.format(misc_dir, item_name)
							html += '<img src="{}/Humiliation/{}/Blue.png">'.format(misc_dir, item_name)
				html += '</div>' #item-preview-wrapper
			self.response.out.write(html)
		else:
			self.redirect('/')

#아이템 구매 페이지(코인 이용)
class ItemBuyPage(webapp2.RequestHandler):
	def get(self):
		css = '''
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					background-color: #454545;
					color: white;
					text-align: center;
					font-family: 'Press Start 2P', sans-serif, cursive;
					vertical-align: middle;
				}
				img{
					image-rendering: crisp-edges;
					image-rendering: pixelated;
				}
				p.logobig{
					text-align: center;
					display: table;
					margin: auto;
					margin-top: 50px;
					margin-bottom: 50px;
				}
			</style>
		'''
		script = """
			<script type="text/javascript">
			function limit(){
				document.getElementById('okayButton').disabled=true;
				var form = document.createElement('form');
				form.method = 'POST';
				form.action = '/buy';
				var input = document.createElement('input');
				input.type = 'hidden';
				input.name = 'item';
				input.value = '""" + self.request.get('item') +	"""';
				form.appendChild(input);
				document.body.appendChild(form);
				form.submit();
			}
			</script>
		"""
		item_url = self.request.get('item')
		current_user = users.get_current_user()
		if (not item_url) or (not current_user):
			self.redirect('/')
		else:
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S: Buy</TITLE>' + css + script + '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			html += '<div>'
			html += 'Do you really want to buy this item?'
			html += '</div><br>'
			html += '<form method="GET">'
			html += '<button type="submit" style="background: none; border: none;" id="okayButton" onClick="limit();">'
			html += '<img src="/images/buttons_okay.png" />'
			html += '</button>'
			html += '<a href="javascript:history.back()"><img src="/images/buttons_nope.png"></a>'
			html += '</form>'
		
			self.response.out.write(html)
			
	def post(self):
		trade_url = self.request.get('item')
		trade = ndb.Key(urlsafe=trade_url).get()
		if (not trade) or (not trade_url):
			self.redirect('/')
		current_user = users.get_current_user()
		
		if not (trade.trade_owner == current_user):
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get() #구매할 유저
			item_owner = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', trade.trade_owner).get() #판매할 유저
			
			if (user.user_coin >= trade.trade_coin):
				ndb_put_list = []
				ndb_delete_list = []
				
				item = ndb.Key(BackpackEntity, trade.trade_item).get() #구매할 아이템
				item.item_owner = user.key.id()
				item.is_trading = False
				ndb_put_list.append(item)
				
				user.user_coin -= trade.trade_coin
				item_owner.user_coin += trade.trade_coin
				ndb_put_list.append(user)
				ndb_put_list.append(item_owner)
				
				log = LogEntity() #로그 기록
				log.log_owner = item_owner.google_id
				log.log_content = 'Sold ' + '<span id="' + rarityIntegerConvert(item.item_rarity) + '">' + trade.trade_itemname + '</span> to ' + user.user_id
				log.log_content += ' for <span style="color: yellow;">' + str(trade.trade_coin) + '</span> Coins'
				ndb_put_list.append(log)
					
				user_loadout = ndb.Key(LoadoutEntity, item_owner.key.id()).get() #판매자의 로드아웃
				
				item_key = str(item.key.id())
				
				if (item.item_part == 0):
					user_loadout.head_list = user_loadout.head_list.replace(item_key, '')
				elif (item.item_part == 1):
					user_loadout.torso_list =user_loadout.torso_list.replace(item_key, '')
				elif (item.item_part == 2):
					user_loadout.leg_list = user_loadout.leg_list.replace(item_key, '')
				elif (item.item_part == 3):
					user_loadout.weapon_list = user_loadout.weapon_list.replace(item_key, '')
				elif (item.item_part == 4):
					user_loadout.misc_list = user_loadout.misc_list.replace(item_key, '')
				elif (item.item_part == 5):
					user_loadout.taunt_list = user_loadout.taunt_list.replace(item_key, '')
				elif (item.item_part == 6):
					user_loadout.pet_list = user_loadout.pet_list.replace(item_key, '')
				elif (item.item_part == 7):
					user_loadout.death_list = user_loadout.death_list.replace(item_key, '')
				elif (item.item_part == 8):
					user_loadout.humiliation_list = user_loadout.humiliation_list.replace(item_key, '')

				ndb_put_list.append(user_loadout)
				
				offer_list = ndb.gql('SELECT * FROM OfferEntity WHERE offer_target=:1', trade.key.id())
				for each_offer in offer_list:
					item_offer_list = each_offer.offer_item.split(',')
					key_list = []
					for item_offer in item_offer_list:
						key_list.append(ndb.Key(BackpackEntity, int(item_offer)))
					item_offer_list = ndb.get_multi(key_list)
					for item_offer in item_offer_list:
						item_offer.is_trading = False
					ndb_put_list += item_offer_list
					ndb_delete_list.append(ndb.Key(OfferEntity, each_offer.key.id()))
					
				ndb_delete_list.append(ndb.Key(TradeEntity, trade.key.id()))
				
				ndb.put_multi(ndb_put_list)
				ndb.delete_multi(ndb_delete_list)
					
				self.redirect('/backpack?id=%s' %user.user_id)

		#예외 처리
		else:
			self.redirect('/')
	
#아이템 판매 페이지
class ItemSellPage(webapp2.RequestHandler):
	def get(self):
		css = '''
		<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
		<style>
			html{
				display: table;
				margin: auto;
			}
			body{
				background-color: #454545;
				color: white;
				text-align: center;
				font-family: 'Press Start 2P', sans-serif, cursive;
				vertical-align: middle;
			}
			img{
				image-rendering: crisp-edges;
				image-rendering: pixelated;
			}
			p.logobig{
				text-align: center;
				display: table;
				margin: auto;
				margin-top: 50px;
				margin-bottom: 50px;
			}
		</style>
		'''
		script = """
			<script type="text/javascript">
			function limit(){
				document.getElementById('okayButton').disabled=true;
				var form = document.createElement('form');
				form.method = 'POST';
				form.action = '/sell';
				var input = document.createElement('input');
				input.type = 'hidden';
				input.name = 'item';
				input.value = '""" + self.request.get('item') +	"""';
				form.appendChild(input);
				document.body.appendChild(form);
				form.submit();
			}
			</script>
		"""
		item_url = self.request.get('item')
		current_user = users.get_current_user()
		if (not item_url) or (not current_user):
			self.redirect('/')
		else:
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S: Sell</TITLE>' + css + script + '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			html += '<div>'
			html += 'Do you really want to sell this item?'
			html += '</div><br>'
			html += '<form method="GET">'
			html += '<button type="submit" style="background: none; border: none;" id="okayButton" onClick="limit();">'
			html += '<img src="/images/buttons_okay.png" />'
			html += '</button>'
			html += '<a href="javascript:history.back()"><img src="/images/buttons_nope.png"></a>'
			html += '</form>'
		
			self.response.out.write(html)

	def post(self):
		item_url = self.request.get('item')
		current_user = users.get_current_user()
		if (not item_url) or (not current_user):
			self.redirect('/')
		else:
			item = ndb.Key(urlsafe=item_url).get()
			if (not item):
				self.redirect('/')
			if (item.is_trading):
				self.redirect('/')
			else:
				user = ndb.Key(UserEntity, item.item_owner).get()
				loadout = ndb.Key(LoadoutEntity, item.item_owner).get()
				if user:
					if user.google_id == current_user:
						if not item.item_rarity == 4: #Self-Made 아이템은 판매 불가
							if (item.item_part == 0):
								loadout.head_list = loadout.head_list.replace(str(item.key.id()), '')
							elif (item.item_part == 1):
								loadout.torso_list = loadout.torso_list.replace(str(item.key.id()), '')
							elif (item.item_part == 2):
								loadout.leg_list = loadout.leg_list.replace(str(item.key.id()), '')
							elif (item.item_part == 3):
								loadout.weapon_list = loadout.weapon_list.replace(str(item.key.id()), '')
							elif (item.item_part == 4):
								loadout.misc_list = loadout.misc_list.replace(str(item.key.id()), '')
							elif (item.item_part == 5):
								loadout.taunt_list = loadout.taunt_list.replace(str(item.key.id()), '')
							elif (item.item_part == 6):
								loadout.pet_list = loadout.pet_list.replace(str(item.key.id()), '')
							elif (item.item_part == 7):
								loadout.death_list = loadout.death_list.replace(str(item.key.id()), '')
							elif (item.item_part == 8):
								loadout.humiliation_list = loadout.humiliation_list.replace(str(item.key.id()), '')
							
							if not item.item_part == 6:
								if item.item_rarity == 0:
									item_price = 25 #Normal
								elif item.item_rarity == 1:
									item_price = 50 #Strange
								elif item.item_rarity == 2:
									item_price = 100 #Unusual
								elif item.item_rarity == 3:
									item_price = 10 #Vintage
							else:
								item_price = 100 #Pet
								
							logging.info(user.user_id  + " sold " + item.item_name + " for " + str(item_price) + "G")
							
							ndb.Key(urlsafe=item_url).delete()
							user.user_coin += item_price
							user.put()
							loadout.put()
						self.redirect('/backpack?id=%s' %(user.user_id))
					else:
						self.redirect('/')
				else:
					self.redirect('/')

#아이템 교환소 페이지
class MarketPage(webapp2.RequestHandler):
	def get(self):
		current_user = users.get_current_user()
		user = ndb.gql('SELECT __key__ FROM UserEntity WHERE google_id=:1', current_user)
		if not user:
			self.redirect('/')
		else:
			#Memcache Read
			trade_list = memcache.get('market_list')
			if trade_list is None:
				trade_list = ndb.gql('SELECT * FROM TradeEntity')
				if not trade_list.count():
					trade_list = []
				if not memcache.add('market_list', trade_list, 900): #15min
					logging.error('Memcache set failed for MARKET_LIST')
			
			html = '<!DOCTYPE html>'
			html += '<html>'
			html += '<HEAD>'
			html += '<TITLE>GG2S:Market</TITLE>'
			html += '<link rel="stylesheet" type="text/css" href="/css/market.css">'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<body>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper
			
			html += '<div class="market-wrapper">'
			today = datetime.date.today()
			for trade in trade_list:
				item = ndb.Key(BackpackEntity, trade.trade_item).get()
				item_info = ndb.Key(ItemEntity, item.item_name).get()
				html += '<div class="item-wrapper">'
				html += '<a href="trade?item=%s">' %trade.key.urlsafe()
				html += '<div class="item-image-wrapper" '
				if not trade.trade_owner == current_user:
					html += 'id="' + rarityIntegerConvert(item.item_rarity) + '">'
				else:
					html += 'id="self-made">'
					
				html += '<img id="item-image" src="/itemthumb/' + trade.trade_itemname + '.png">'
				html += '</div>'
				
				html += '<div class="item-price-wrapper">'
				html += '<span id="item-price">'
				html += str(trade.trade_coin) + ' COINS'
				html += '</span>'
				html += '</div>' #item-price-wrapper
				
				html += '</a>'
				html += '</div>' #item-wrapper
			html += '</div>' #market-wrapper
			
			html += '</body>'
			html += '</html>'
			self.response.out.write(html)
					
#아이템 거래 페이지
class TradePage(webapp2.RequestHandler):
	css = '''
	<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
	<style>
		html{
			display: table;
			margin: auto;
		}
		body{
			background-color: #454545;
			color: white;
			text-align: center;
			font-family: 'Press Start 2P', sans-serif, cursive;
			vertical-align: middle;
		}
		img{
			image-rendering: crisp-edges;
			image-rendering: pixelated;
		}
		p.logobig{
			text-align: center;
			display: table;
			margin: auto;
			margin-top: 50px;
			margin-bottom: 50px;
		}
		fieldset{
			text-align: left;
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
		}
		td{
		}
		td.normal{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #F7DC07;
		}
		td.strange{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #CF6A32;
		}
		td.unusual{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #8650AC;
		}
		td.vintage{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #476291;
		}
		td.self-made{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #70B04A;
		}
		span.normal{
			color: #F7DC07;
		}
		span.strange{
			color: #CF6A32;
		}
		span.unusual{
			color: #8650AC;
		}
		span.vintage{
			color: #476291;
		}
		span.self-made{
			color: #70B04A;
		}
		img.item{
			width: 128px;
			height: 128px;
		}
		td{
			word-break:break-all;
			white-space:pre-wrap;
		}
	</style>
	'''
	def get(self):
		trade_url = self.request.get('item')
		script = """
			<script type="text/javascript">
			function offer_accept(offer_num){
				if (confirm('Accept this offer?'))
				{
					var form = window.top.document.createElement('form');
					form.method = 'POST';
					form.action = '/trade';
					var offer = window.top.document.createElement('input');
					offer.name = 'offer';
					offer.type = 'hidden';
					offer.value = offer_num;
					
					var trade = window.top.document.createElement('input');
					trade.name = 'trade';
					trade.type = 'hidden';
					trade.value = '""" + trade_url + """';
				
					var type = window.top.document.createElement('input');
					type.name = 'type';
					type.type = 'hidden';
					type.value = true;
					
					form.appendChild(offer);
					form.appendChild(trade);
					form.appendChild(type);
					document.body.appendChild(form);
					form.submit();
				}
			}
			function offer_decline(offer_num){
				if (confirm('Decline this offer?'))
				{
					var form = window.top.document.createElement('form');
					form.method = 'POST';
					form.action = '/trade';
					var offer = window.top.document.createElement('input');
					offer.name = 'offer';
					offer.type = 'hidden';
					offer.value = offer_num;
					
					var trade = window.top.document.createElement('input');
					trade.name = 'trade';
					trade.type = 'hidden';
					trade.value = '""" + trade_url + """';
					
					var type = window.top.document.createElement('input');
					type.name = 'type';
					type.type = 'hidden';
					type.value = false;
					
					form.appendChild(offer);
					form.appendChild(trade);
					form.appendChild(type);
					document.body.appendChild(form);
					form.submit();
				}
			}
			</script>
		"""
		current_user = users.get_current_user()
		
		trade = ndb.Key(urlsafe=trade_url).get()
		
		if (not trade) or (not current_user):
			self.redirect('/')
		else:
			item = ndb.Key(BackpackEntity, trade.trade_item).get()
			owner = ndb.Key(UserEntity, item.item_owner).get()
			html = '<!DOCTYPE html>'
			html += '<html>'
			html += '<HEAD>' + '<TITLE>GG2S:Trade</TITLE>' + self.css + script + '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			if not (trade.trade_owner == current_user):
				html += '<div style="font-size: 24px; margin-bottom: 24px;">' + owner.user_id + ' is selling:' + '</div>'
			else:
				html += '<div style="font-size: 24px; margin-bottom: 24px;">' + 'You\'re selling:' + '</div>'
			html += '<table style="float: left; margin-right: 50px; margin-bottom: 50px;">'
			html += '<td class="%s">' %rarityIntegerConvert(item.item_rarity)
			html += '<a href="/iteminfo?item=' + item.item_name + '">'
			html += '<img src="/itemthumb/' + item.item_name + '.png" style="width: 256px; height: 256px;">'
			html += '</a>'
			html += '</td>'
			html += '</table>'
			
			html += '<table style="line-height: 2;">'
			html += '<tr><td>'
			if (item.item_rarity == 1):
				html += '<span class="strange">' + strangeCountToString(item.item_strangeCount) + '</span>'
			elif (item.item_rarity == 2):
				html += '<span class="unusual">'+ 'Unusual' + '</span>'
			elif (item.item_rarity == 3):
				html += '<span class="vintage">' + 'Vintage' + '</span>'
			elif (item.item_rarity == 4):
				self.redirect('/') #거래할 수 없다.
			html += '</td></tr>'
			
			item_info = ndb.Key(ItemEntity, item.item_name).get()
			html += '<tr><td>'
			html += '<span class="%s" style="font-size:28px;"><b>' %rarityIntegerConvert(item.item_rarity) + item_info.item_nickname + '</b></span>'
			html += '</td></tr>'

			html += '<tr><td>'
			if	(item.item_rarity == 1):
				html += '<span class="%s">' %rarityIntegerConvert(item.item_rarity) + strangeTypeToString(item.item_strangeType) + ': ' + str(item.item_strangeCount) + '</span>'
			elif (item.item_rarity == 2):
				html += '<span class="%s">' %rarityIntegerConvert(item.item_rarity) + 'Unusual Effect: ' + unusualTypeToString(item.item_effect) + '</span>'
			html += '</td></tr>'
			
			html += '<tr><td>'
			html += '<span style="color: #666666;">Level %d %s</span>' %(item.item_level, partToString(item_info.item_part))
			html += '</td></tr>'
			
			html += '<tr><td>'
			html += 'Instabuy price: <price style="color: yellow;">' + str(trade.trade_coin) + '</price> '
			
			#코인을 이용한 즉시 구매
			if not (trade.trade_owner == current_user):
				offer_count = ndb.gql('SELECT __key__ FROM OfferEntity WHERE offer_target=:1 AND offer_owner=:2', trade.key.id(), current_user).count()
				#자신이 제시한 오퍼가 없을 경우
				if not offer_count:
					current_coin = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get().user_coin
					if (current_coin >= trade.trade_coin):
						html += '<a href="/buy?item=%s"><input type="button" value="Buy Now"></a>' %trade.key.urlsafe()
					else:
						html += '<button type="button" disabled>' + 'You need ' + str(trade.trade_coin - current_coin) + ' more coins' + '</button>'
			
			html += '</form>'
			html += '</td></tr>'
			
			html += '<tr><td>'
			enddate = trade.trade_enddate
			html += 'This trade will end in <date style="color: tomato">' + enddate.strftime("%b.%d") + '</date>'
			html += '</td></tr>'
			
			#거래 삭제
			if (trade.trade_owner == current_user):
				html += '<tr><td>'
				html += '<a href="/removetrade?trade=%s' %trade.key.urlsafe() + '" style="color: white;">'
				html += 'Remove Trade'
				html += '</a>'
				html += '</td></tr>'
			
			if not (trade.trade_owner == current_user):
				#자신이 제시한 오퍼가 없을 경우
				if not offer_count:
					html += '<tr><td>'
					html += '<a href="/makeoffer?item=' + trade_url +'" style="color: white;">Make an offer</a>'
					html += '</td></tr>'
			html += '</table>'

			html += '<div style="clear: left;">'
			html += '<hr>'
			
			#자신의 거래에 대해 오퍼가 있을시 표시
			if (trade.trade_owner == current_user):
				offer_count = ndb.gql('SELECT __key__ FROM OfferEntity WHERE offer_target=:1', trade.key.id()).count()
				if offer_count:
					offers = ndb.gql('SELECT * FROM OfferEntity WHERE offer_target=:1', trade.key.id())
					html += '<table style="border-spacing: 10px; table-layout:fixed;">'
					html += '<th colspan="10" style="text-align: left;">Offers Received</th>'
					html += '<col width="*" />'
					html += '<col width="128px" />'
					html += '<col width="128px" />'
					html += '<col width="128px" />'
					html += '<col width="128px" />'
					html += '<col width="128px" />'
					cnt = 0
					for offer in offers:
						cnt += 1
						_offer_items = offer.offer_item.split(',')
						offer_items = []
						for offer_item in _offer_items:
							offer_items.append(ndb.Key(BackpackEntity, int(offer_item)))
						offer_items = ndb.get_multi(offer_items)
						html += '<tr>'
						html += '<td>'
						html += str(cnt)
						html += '<br>'
						html += '<button style="background: none; border: none;" id="gachaButton" onClick="offer_accept(' + str(offer.key.id()) + ');">'
						html += '<img src="/images/buttons_okay.png" style="width: 48px;" />'
						html += '</button>'
						html += '<button style="background: none; border: none;" id="gachaButton" onClick="offer_decline(' + str(offer.key.id()) + ');">'
						html += '<img src="/images/buttons_nope.png" style="width: 48px;">'
						html += '</button>'
						html += '</td>'
						item_cnt = 0
						for offer_item in offer_items:
							html += '<td class="' + rarityIntegerConvert(offer_item.item_rarity) + '">'
							html += '<a href="/item?item={}">'.format(offer_item.key.urlsafe())
							html += '<img class="item" src="/itemthumb/' + offer_item.item_name + '.png">'
							html += '</a>'
							if (offer_item.item_rarity == 1):
								html += '<br><span class="strange" style="font-size: 10px;">' + strangeTypeToString(offer_item.item_strangeType).replace(' ', '<br>') + ': ' + strlize(offer_item.item_strangeCount) + '</span>'
							elif (offer_item.item_rarity == 2):
								html += '<br><span class="unusual" style="font-size: 10px;">'+ unusualTypeToString(offer_item.item_effect).replace(' ', '<br>')  + '</span>'
							html += '</td>'
							item_cnt += 1
							if not item_cnt % 5:
								html += '</tr><tr><td></td>'
						html += '</tr>'
					html += '</table>'
			
			#자신이 제시한 오퍼를 표시
			if not (trade.trade_owner == current_user):
				if offer_count:
					my_offer = ndb.gql('SELECT * FROM OfferEntity WHERE offer_target=:1 AND offer_owner=:2', trade.key.id(), current_user).get()
					my_offer_items = my_offer.offer_item
					my_offer_items = my_offer_items.split(',')
					offer_items = []
					for offer_item in my_offer_items:
						offer_items.append(ndb.Key(BackpackEntity, int(offer_item)))
					my_offer_items = ndb.get_multi(offer_items)
					html += '<table style="border-spacing: 10px; table-layout:fixed;">'
					html += '<th colspan="10" style="text-align: left;">'
					html += 'My offer'
					html += '<a href="/removeoffer?offer=%s">' %my_offer.key.urlsafe()
					html += '<img src="/images/buttons_nope.png" style="width: 48px;">'
					html += '</a>'
					html += '</th>'
					if (len(offer_items) > 4):
						html += '<col width="128px" />'
						html += '<col width="128px" />'
						html += '<col width="128px" />'
						html += '<col width="128px" />'
						html += '<col width="128px" />'
					else:
						for i in range(len(offer_items)):
							html += '<col width="128px" />'
					html += '<tr>'
					item_cnt = 0
					for offer_item in my_offer_items:
						html += '<td class="' + rarityIntegerConvert(offer_item.item_rarity) + '">'
						html += '<a href="/item?item={}">'.format(offer_item.key.urlsafe())
						html += '<img class="item" src="/itemthumb/' + offer_item.item_name + '.png">'
						html += '</a>'
						if (offer_item.item_rarity == 1):
							html += '<br><span class="strange" style="font-size: 10px;">' + strangeTypeToString(offer_item.item_strangeType).replace(' ', '<br>') + ': ' + strlize(offer_item.item_strangeCount) + '</span>'
						elif (offer_item.item_rarity == 2):
							html += '<br><span class="unusual" style="font-size: 10px;">'+ unusualTypeToString(offer_item.item_effect).replace(' ', '<br>')  + '</span>'
						html += '</td>'
						item_cnt += 1
						if not item_cnt % 5:
							html += '</tr><tr>'
					html += '</tr>'
					html += '</table>'
			html += '</div>'
			html += '</body>'
			html += '</html>'
			
			self.response.out.write(html)
			
	def post(self):
		offer_key = self.request.get('offer')
		trade_url = self.request.get('trade')
		work_type = self.request.get('type')
		
		trade = ndb.Key(urlsafe=trade_url).get()
		offer = ndb.Key(OfferEntity, int(offer_key)).get()
		
		current_user = users.get_current_user()
		
		if (trade.trade_owner == current_user):
			#승인
			if (work_type == 'true'):
				user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get() #판매자
				other = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', offer.offer_owner).get() #구매자
				
				ndb_put_list = []
				ndb_delete_list = []
				
				user_item = ndb.Key(BackpackEntity, trade.trade_item).get()
				other_item = offer.offer_item.split(',')
				_otheritem = []
				for each_item in other_item:
					_otheritem.append(ndb.Key(BackpackEntity, int(each_item)))
				other_item = ndb.get_multi(_otheritem)
				
				user_item.item_owner = other.key.id()
				user_item.is_trading = False
				ndb_put_list.append(user_item)
				for each_item in other_item:
					each_item.item_owner = user.key.id()
					each_item.is_trading = False
					ndb_put_list.append(each_item)
					
				log = LogEntity() #로그 기록
				log.log_owner = other.google_id
				log.log_content = 'Bought ' + user.user_id + "'s " + '<span id="' + rarityIntegerConvert(user_item.item_rarity) + '">' + trade.trade_itemname + '</span>'
				log.log_content += ' for <span style="color: yellow;">' + str(len(other_item)) + '</span> Items'
				ndb_put_list.append(log)
					
				user_loadout = ndb.Key(LoadoutEntity, user.key.id()).get()
				other_loadout = ndb.Key(LoadoutEntity, other.key.id()).get()
				
				item_key = str(user_item.key.id())
				
				if (user_item.item_part == 0):
					user_loadout.head_list = user_loadout.head_list.replace(item_key, '')
				elif (user_item.item_part == 1):
					user_loadout.torso_list =user_loadout.torso_list.replace(item_key, '')
				elif (user_item.item_part == 2):
					user_loadout.leg_list = user_loadout.leg_list.replace(item_key, '')
				elif (user_item.item_part == 3):
					user_loadout.weapon_list = user_loadout.weapon_list.replace(item_key, '')
				elif (user_item.item_part == 4):
					user_loadout.misc_list = user_loadout.misc_list.replace(item_key, '')
				elif (user_item.item_part == 5):
					user_loadout.taunt_list = user_loadout.taunt_list.replace(item_key, '')
				elif (user_item.item_part == 6):
					user_loadout.pet_list = user_loadout.pet_list.replace(item_key, '')
				elif (user_item.item_part == 7):
					user_loadout.death_list = user_loadout.death_list.replace(item_key, '')
				elif (user_item.item_part == 8):
					user_loadout.humiliation_list = user_loadout.humiliation_list.replace(item_key, '')
					
				ndb_put_list.append(user_loadout)
					
				for each_item in other_item:
					item_key = str(each_item.key.id())
					if (each_item.item_part == 0):
						other_loadout.head_list = other_loadout.head_list.replace(item_key, '')
					elif (each_item.item_part == 1):
						other_loadout.torso_list =other_loadout.torso_list.replace(item_key, '')
					elif (each_item.item_part == 2):
						other_loadout.leg_list = other_loadout.leg_list.replace(item_key, '')
					elif (each_item.item_part == 3):
						other_loadout.weapon_list = other_loadout.weapon_list.replace(item_key, '')
					elif (each_item.item_part == 4):
						other_loadout.misc_list = other_loadout.misc_list.replace(item_key, '')
					elif (each_item.item_part == 5):
						other_loadout.taunt_list = other_loadout.taunt_list.replace(item_key, '')
					elif (each_item.item_part == 6):
						other_loadout.pet_list = other_loadout.pet_list.replace(item_key, '')
					elif (each_item.item_part == 7):
						other_loadout.death_list = other_loadout.death_list.replace(item_key, '')
					elif (each_item.item_part == 8):
						other_loadout.humiliation_list = other_loadout.humiliation_list.replace(item_key, '')
				
				ndb_put_list.append(other_loadout)
				
				offer_list = ndb.gql('SELECT * FROM OfferEntity WHERE offer_target=:1', trade.key.id())
				for each_offer in offer_list:
					#이중삭제 안하도록 체크
					if not (each_offer.key.id() == offer.key.id()):
						item_offer_list = each_offer.offer_item.split(',')
						key_list = []
						for item_offer in item_offer_list:
							key_list.append(ndb.Key(BackpackEntity, int(item_offer)))
						item_offer_list = ndb.get_multi(key_list)
						for item_offer in item_offer_list:
							item_offer.is_trading = False
						ndb_put_list += item_offer_list
						ndb_delete_list.append(ndb.Key(OfferEntity, each_offer.key.id()))
					
				ndb_delete_list.append(ndb.Key(TradeEntity, trade.key.id()))
				ndb_delete_list.append(ndb.Key(OfferEntity, offer.key.id()))
				
				ndb.put_multi(ndb_put_list)
				ndb.delete_multi(ndb_delete_list)
					
				self.redirect('/mytrade')

			#거절
			elif (work_type == 'false'):
				item_offer_list = offer.offer_item.split(',')
				key_list = []
				for item_offer in item_offer_list:
					key_list.append(ndb.Key(BackpackEntity, int(item_offer)))
				item_offer_list = ndb.get_multi(key_list)
				for item_offer in item_offer_list:
					item_offer.is_trading = False

				log = LogEntity() #로그 기록
				log.log_owner = offer.offer_owner
				log.log_content ="Offer for " + trade.trade_itemname + ' is declined by its owner.'
				item_offer_list.append(log)

				ndb.put_multi(item_offer_list)
				ndb.Key(OfferEntity, offer.key.id()).delete()
				
				self.redirect('/trade?item=%s' %trade_url)
			#예외 처리
			else:
				self.redirect('/')

		#예외 처리
		else:
			self.redirect('/')

#자신의 트레이드 관리
class MyTradePage(webapp2.RequestHandler):
	css = '''
	<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
	<style>
		html{
			display: table;
			margin: auto;
		}
		body{
			background-color: #454545;
			color: white;
			text-align: center;
			font-family: 'Press Start 2P', sans-serif, cursive;
			vertical-align: middle;
		}
		img{
			image-rendering: crisp-edges;
			image-rendering: pixelated;
		}
		p.logobig{
			text-align: center;
			display: table;
			margin: auto;
			margin-top: 50px;
			margin-bottom: 50px;
		}
		div.trades{
			margin: 50px;
		}
		div.offers{
			margin: 50px;
		}
		fieldset{
			text-align: left;
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
		}
		td{

		}
		td.normal{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #F7DC07;
		}
		td.strange{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #CF6A32;
		}
		td.unusual{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #8650AC;
		}
		td.vintage{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #476291;
		}
		td.self-made{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #70B04A;
		}
		span.normal{
			color: #F7DC07;
		}
		span.strange{
			color: #CF6A32;
		}
		span.unusual{
			color: #8650AC;
		}
		span.vintage{
			color: #476291;
		}
		span.self-made{
			color: #70B04A;
		}
		span.alert{
			color: tomato;
		}
		img.item{
			width: 128px;
			height: 128px;
		}
		table{
			border-spacing: 20px;
		}
	</style>
	'''
	script = """
	<script type="text/javascript">
		if (window.top.location != window.location) {
			window.top.location = window.location;
		}
	</script>
	"""
	def get(self):
		current_user = users.get_current_user()
		
		if (not current_user):
			self.redirect('/')
		else:
			trade_list = ndb.gql('SELECT * FROM TradeEntity WHERE trade_owner=:1', current_user)
			offer_list = ndb.gql('SELECT * FROM OfferEntity WHERE offer_owner=:1', current_user)
			html = '<!DOCTYPE html>'
			html += '<html>'
			html += '<HEAD>' + '<TITLE>GG2S:My Trade</TITLE>' + self.css + self.script +  '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			
			html += '<div class="trades">'
			html += 'Items Selling'
			html += '<table>'
			cnt = 0
			for trade in trade_list:
				enddate = trade.trade_enddate
				offer_count = ndb.gql('SELECT __key__ FROM OfferEntity WHERE offer_target=:1', trade.key.id()).count()
				html += '<td class="none">'
				html += '<a href="/trade?item=%s' %trade.key.urlsafe() + '">'
				html += '<img class="item" src="/itemthumb/' + trade.trade_itemname + '.png">'
				html += '</a>'
				html += '<br>'
				html += '<span class="alert">' + enddate.strftime("%b.%d") + '</span>'
				html += '<br>'
				if offer_count:
					html += '<span style="color: yellow">' + str(offer_count) + '</span> Offers'
				else:
					html += '0 Offer'
				html += '</td>'
				cnt += 1
			if not cnt:
				html += '<td>'
				html += 'No items trading!'
				html += '</td>'
			html += '</table>'
			html += '</div>'
			
			html += '<div class="offers">'
			html += 'Items Buying'
			html += '<table>'
			cnt = 0
			for offer in offer_list:
				offer_item_list = offer.offer_item.split(',')
				offer_target = ndb.Key(TradeEntity, offer.offer_target).get()
				html += '<td class="none">'
				html += '<a href="/trade?item=%s' %offer_target.key.urlsafe() + '">'
				html += '<img class="item" src="/itemthumb/' + offer_target.trade_itemname + '.png">'
				html += '</a>'
				html += '<br>'
				html += '<center>^</center>'
				html += '<br>'
				html += str(len(offer_item_list)) + ' Items'
				html += '</td>'
				cnt += 1
			if not cnt:
				html += '<td>'
				html += 'No items offering!'
				html += '</td>'
			html += '</table>'
			html += '</div>'
			
			html += '</body>'
			html += '</html>'
			
			self.response.out.write(html)

#거래 생성 페이지
class MakeTradePage(webapp2.RequestHandler):
	css = '''
	<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
	<style>
		html{
			display: table;
			margin: auto;
		}
		body{
			background-color: #454545;
			color: white;
			text-align: center;
			font-family: 'Press Start 2P', sans-serif, cursive;
			vertical-align: middle;
		}
		img{
			image-rendering: crisp-edges;
			image-rendering: pixelated;
		}
		p.logobig{
			text-align: center;
			display: table;
			margin: auto;
			margin-top: 50px;
			margin-bottom: 50px;
		}
		fieldset{
			text-align: left;
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
		}
		td{

		}
		td.normal{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #F7DC07;
		}
		td.strange{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #CF6A32;
		}
		td.unusual{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #8650AC;
		}
		td.vintage{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #476291;
		}
		td.self-made{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #70B04A;
		}
		span.normal{
			color: #F7DC07;
		}
		span.strange{
			color: #CF6A32;
		}
		span.unusual{
			color: #8650AC;
		}
		span.vintage{
			color: #476291;
		}
		span.self-made{
			color: #70B04A;
		}
	</style>
	'''
	trade_duration = 7 #7일간 진행
	
	def get(self):
		script = """
			<script type="text/javascript">
			function limit(){
				var price = parseInt(document.getElementById('form_coin').value);
				document.getElementById('okayButton').disabled=true;
				var form = document.createElement('form');
				form.method = 'POST';
				form.action = '/maketrade';
				var item = document.createElement('input');
				item.type = 'hidden';
				item.name = 'item';
				item.value = '""" + self.request.get('item') +	"""';
				var coin = document.createElement('input');
				coin.type = 'hidden';
				coin.name = 'coin';
				coin.value = price;
				document.getElementById('okayButton').disabled=true;
				form.appendChild(item);
				form.appendChild(coin);
				document.body.appendChild(form);
				form.submit();
			}
			function makeTen(){
				var form_coin = document.getElementById('form_coin');
				if (form_coin.value % 10)
					form_coin.value = 10*Math.floor(form_coin.value / 10);
				if (form_coin.value <= 0)
					form_coin.value = 10;
				if (form_coin.value >= 10000)
					form_coin.value = 10000;
			}
			</script>
		"""
		item_url = self.request.get('item')
		current_user = users.get_current_user()
		
		item = ndb.Key(urlsafe=item_url).get()
		
		if (not item) or (not current_user):
			self.redirect('/')
		else:
			html = '<!DOCTYPE html>'
			html += '<html>'
			html += '<HEAD>' + '<TITLE>GG2S:Trade</TITLE>' + self.css + script + '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			trade_count = ndb.gql('SELECT __key__ FROM TradeEntity WHERE trade_owner=:1', current_user).count()
			
			if trade_count >= 5:
				html += 'You can\'t make more than 5 trades!'
				html += '<a href="/mytrade" style="color: white;">Return to My Trade</a>'
			else:
				html += '<div style="font-size: 24px; margin-bottom: 24px;">You\'re selling:</div>'
				html += '<table style="float: left; margin-right: 50px;">'
				html += '<td class="%s">' %rarityIntegerConvert(item.item_rarity)
				html += '<img src="/itemthumb/' + item.item_name + '.png" style="width: 256px; height: 256px;">'
				html += '</td>'
				html += '</table>'
				
				html += '<table style="line-height: 2;">'
				html += '<tr><td>'
				if (item.item_rarity == 1):
					html += '<span class="strange">' + strangeCountToString(item.item_strangeCount) + '</span>'
				elif (item.item_rarity == 2):
					html += '<span class="unusual">'+ 'Unusual' + '</span>'
				elif (item.item_rarity == 3):
					html += '<span class="vintage">' + 'Vintage' + '</span>'
				elif (item.item_rarity == 4):
					self.redirect('/') #거래할 수 없다.
				html += '</td></tr>'
				
				item_info = ndb.Key(ItemEntity, item.item_name).get()
				html += '<tr><td>'
				html += '<span class="%s" style="font-size:28px;"><b>' %rarityIntegerConvert(item.item_rarity) + item_info.item_nickname + '</b></span>'
				html += '</td></tr>'

				html += '<tr><td>'
				if	(item.item_rarity == 1):
					html += '<span class="%s">' %rarityIntegerConvert(item.item_rarity) + strangeTypeToString(item.item_strangeType) + ': ' + str(item.item_strangeCount) + '</span>'
				elif (item.item_rarity == 2):
					html += '<span class="%s">' %rarityIntegerConvert(item.item_rarity) + 'Unusual Effect: ' + unusualTypeToString(item.item_effect) + '</span>'
				html += '</td></tr>'
				
				#즉시구매 가격
				html += '<tr><td>'
				html += '<form method="GET">'
				html += 'Instabuy price: '
				html += '<input type="number" id="form_coin" value="100" step="10" max="10000" size="4" onchange="makeTen()">'
				html += ' Coins'
				html += '</td></tr>'
				
				#판매 종료 기간
				html += '<tr><td>'
				today = datetime.date.today()
				try:
					enddate = datetime.date(today.year, today.month, today.day + self.trade_duration)
				except ValueError:
					if today.month == 12:
						enddate = datetime.date(today.year + 1, 1, (today.day + self.trade_duration) % 31)
					elif today.month in [1, 3, 5, 7, 8, 10, 11]:
						enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 31)
					elif today.month == 2:
						if today.year % 400:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 28)
						elif today.year % 100:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 28)
						elif today.year % 4:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 28)
						else:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 29)
					else:
						enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 30)
				
				html += 'Your trade will end in <date style="color: tomato">' + enddate.strftime("%b.%d") + '</date>'
				html += '</td></tr>'
				html += '</table>'
				
				html += '<div style="clear: left;">'
				html += '<button type="submit" style="background: none; border: none;" id="okayButton" onClick="limit();">'
				html += '<img src="/images/buttons_okay.png" style="width: 48px; margin: 30px;"/>'
				html += '</button>'
				html += '<a href="javascript:history.back()"><img src="/images/buttons_nope.png" style="width: 48px; margin: 30px;"></a>'
				html += '</div>'
				html += '</form>'
		
			html += '</body>'
			html += '</html>'
			self.response.out.write(html)
			
	def post(self):
		coin = self.request.get('coin')
		if (coin.isdigit()):
			coin = int(eval(coin))
		else:
			self.redirect('/')
		
		current_user = users.get_current_user()
		item_url = self.request.get('item')
		item = ndb.Key(urlsafe=item_url).get()
		
		if (not item) or (not current_user):
			self.redirect('/')
		else:
			if not (item.is_trading):
				trade = TradeEntity()
				trade.trade_item = item.key.id()
				if (coin % 10):
					coin = 10*(coin // 10)
				if (coin <= 0):
					coin = 10;
				if (coin >= 10000):
					coin = 10000;
				trade.trade_coin = coin
				today = datetime.date.today()
				try:
					enddate = datetime.date(today.year, today.month, today.day + self.trade_duration)
				except ValueError:
					if today.month == 12:
						enddate = datetime.date(today.year + 1, 1, (today.day + self.trade_duration) % 31)
					elif today.month in [1, 3, 5, 7, 8, 10, 11]:
						enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 31)
					elif today.month == 2:
						if today.year % 400:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 28)
						elif today.year % 100:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 28)
						elif today.year % 4:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 28)
						else:
							enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 29)
					else:
						enddate = datetime.date(today.year, today.month + 1, (today.day + self.trade_duration) % 30)
				trade.trade_enddate = enddate
				trade.trade_itemname = item.item_name
				trade.trade_owner = current_user
				trade.put()
				
				item.is_trading = True
				item.put()
				
				self.redirect('/mytrade')
			else:
				self.redirect('/')
			
#거래 제안 생성 페이지
class MakeOfferPage(webapp2.RequestHandler):
	css = '''
	<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
	<style>
		html{
			display: table;
			margin: auto;
		}
		body{
			background-color: #454545;
			color: white;
			text-align: center;
			font-family: 'Press Start 2P', sans-serif, cursive;
			vertical-align: middle;
		}
		img{
			image-rendering: crisp-edges;
			image-rendering: pixelated;
		}
		p.logobig{
			text-align: center;
			display: table;
			margin: auto;
			margin-top: 50px;
			margin-bottom: 50px;
		}
		fieldset{
			text-align: left;
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
		}
		td{

		}
		td.normal{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #F7DC07;
		}
		td.strange{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #CF6A32;
		}
		td.unusual{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #8650AC;
		}
		td.vintage{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #476291;
		}
		td.self-made{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #70B04A;
		}
		span.normal{
			color: #F7DC07;
		}
		span.strange{
			color: #CF6A32;
		}
		span.unusual{
			color: #8650AC;
		}
		span.vintage{
			color: #476291;
		}
		span.self-made{
			color: #70B04A;
		}
	</style>
	'''
	def get(self):
		trade_url = self.request.get('item')
		current_user = users.get_current_user()
		trade = ndb.Key(urlsafe=trade_url).get()
		
		if (not trade) or (not current_user):
			self.redirect('/')
		else:
			html = '<html>'
			html += '<frameset rows="*,200">'
			html += '<frame id="frame_top" src="/offer?item=%s' %trade_url + '" noresize>'
			html += '<frame id="frame_bottom" src="/offerbackpack" noresize>'
			html += '</frameset>'
			html += '</html>'
			self.response.out.write(html)
	
	def post(self):
		current_user = users.get_current_user()
		user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
		
		if not user:
			self.redirect('/')
		else:
			offer = OfferEntity()
			item_list = self.request.get('item_list')
			if (item_list):
				trade = ndb.Key(urlsafe=self.request.get('trade')).get()
				if not (trade.trade_owner == current_user):
					offer_count = ndb.gql('SELECT __key__ FROM OfferEntity WHERE offer_target=:1 AND offer_owner=:2', trade.key.id(), current_user).count()
					if not offer_count:
						offer.offer_owner = current_user
						offer.offer_target = trade.key.id()
						offer.offer_item = item_list
						
						item_list = item_list.split(',')
						key_list = []
						for item in item_list:
							key_list.append(ndb.Key(BackpackEntity, int(item)))
						item_list = ndb.get_multi(key_list)
						for item in item_list:
							item.is_trading = True
						ndb.put_multi(item_list)
						
						offer.offer_targetuser = trade.trade_owner
						offer.put()
		self.redirect('/mytrade')
	
#프레임셋 안에 표시될 거래제안 내용
class OfferPage(webapp2.RequestHandler):
	css = '''
	<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
	<style>
		html{
			display: table;
			margin: auto;
		}
		body{
			background-color: #454545;
			color: white;
			text-align: center;
			font-family: 'Press Start 2P', sans-serif, cursive;
			vertical-align: middle;
		}
		img{
			image-rendering: crisp-edges;
			image-rendering: pixelated;
			width: 128px;
		}
		p.logobig{
			text-align: center;
			display: table;
			margin: auto;
			margin-top: 50px;
			margin-bottom: 50px;
		}
		fieldset{
			text-align: left;
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
		}
		td.none{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #2B2726;
			background-color: #3C352E;
			width: 128px;
			height: 128px;
		}
		td.normal{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #F7DC07;
			background-color: #4B4314;
		}
		td.strange{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #CF6A32;
			background-color: #472B1F;
		}
		td.unusual{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #8650AC;
			background-color: #372A3C;
		}
		td.vintage{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #476291;
			background-color: #292D36;
		}
		td.self-made{
			padding: auto;
			margin: 10px;
			Border: 5px;
			border-style: solid;
			border-radius:0.4em;
			Border-color: #70B04A;
			background-color: #2B3E24;
		}
		span.normal{
			color: #F7DC07;
		}
		span.strange{
			color: #CF6A32;
		}
		span.unusual{
			color: #8650AC;
		}
		span.vintage{
			color: #476291;
		}
		span.self-made{
			color: #70B04A;
		}
	</style>
	'''
	def get(self):
		trade_url = self.request.get('item')
		script = """
			<script type="text/javascript">
			function Offer(){
				this.offer_list = [];
				var index = 0;
				
				this.offer_clear = function(){
					this.offer_list = [];
					index = 0;
					for (var i = 0; i < 10; i += 1)
					{
						document.getElementById(i.toString()).src = '';
						document.getElementById(i.toString()).width = 128;
						document.getElementById(i.toString()).height = 128;
						document.getElementById('td_' + i.toString()).className = 'none';
						document.getElementById('td_' + i.toString()).height = 128;
					}
					window.top.frames[1].reset_button();
				}
				
				this.offer_append = function(id, key){
					if (index < 10)
					{
						var image = window.top.frames[1].document.getElementById('image_' + id);
						var td = window.top.frames[1].document.getElementById('td_' + id);
						document.getElementById(index.toString()).src = image.src + '#' + new Date().getTime();
						document.getElementById('td_' + index.toString()).className = td.className;
						this.offer_list.push(key);
						index += 1;
					}
				}
			}

			var offer = new Offer();
			
			function create_offer(){
				if (offer.offer_list.length > 0)
				{
					if (confirm('Confirm?'))
					{
						document.getElementById('okayButton').disabled=true;
						var form = window.top.document.createElement('form');
						form.method = 'POST';
						form.action = '/makeoffer';
						var item_list = window.top.document.createElement('input');
						item_list.name = 'item_list';
						item_list.type = 'hidden';
						
						var item_str = '';
						for (var i = 0; i < offer.offer_list.length; i += 1)
						{
							item_str += offer.offer_list[i];
							if (i != offer.offer_list.length - 1)
							{
								item_str += ',';
							}
						}
						
						item_list.value = item_str;
						
						var trade = window.top.document.createElement('input');
						trade.name = 'trade';
						trade.type = 'hidden';
						trade.value = '""" + trade_url + """';
						
						form.appendChild(item_list);
						form.appendChild(trade);
						document.body.appendChild(form);
						form.submit();
					}
				}
			}
			</script>
		"""
		current_user = users.get_current_user()
		
		trade = ndb.Key(urlsafe=trade_url).get()
		item = ndb.Key(BackpackEntity, trade.trade_item).get()
		user = ndb.Key(UserEntity, item.item_owner).get()
		html = '<!DOCTYPE html>'
		html += '<html>'
		html += '<HEAD>' + '<TITLE>GG2S:Offer</TITLE>' + self.css + script + '</HEAD>'
		html += '<body onload="initiate()">'
		html += '</div>'
		html += '<table>'
		
		#파는 물건
		html += '<tr>'
		html += '<td style="font-size: 24px; margin-bottom: 24px;">' + user.user_id + '\'s deal:' + '</td>'
		html += '<td class="%s">' %rarityIntegerConvert(item.item_rarity)
		html += '<img src="/itemthumb/' + item.item_name + '.png" style="width: 128px; height: 128px;">'
		html += '</td>'
		html += '</tr>'
		
		#거래 제안
		html += '<tr>'
		html += '<td style="font-size: 24px; margin-bottom: 24px;">Your Offer:</td>'
		for i in range(5):
			html += '<td class="none" id="td_' + str(i) + '"><img id="' + str(i) + '"></td>'
		html += '</tr>'
		html += '<tr>'
		html += '<td style="font-size: 24px; margin-bottom: 24px;"></td>'
		for i in range(5):
			html += '<td class="none" id="td_' + str(i + 5) + '"><img id="' + str(i + 5) + '"></td>'
		html += '</tr>'
		html += '</table>'
		
		html += '<button style="background: none; border: none; margin-right: 30px; margin-top: 10px;" id="okayButton" onClick="create_offer();">'
		html += '<img src="/images/buttons_okay.png" style="width: 48px;" />'
		html += '</button>'
		html += '<button type="reset" style="background: none; border: none; margin-right: 30px; margin-top: 10px;" onClick="offer.offer_clear();">'
		html += '<img src="/images/buttons_nope.png" style="width: 48px;" />'
		html += '</button>'

		html += '</body>'
		html += '</html>'
		self.response.out.write(html)

#프레임2, 자신의 백팩 내용물 표시
class OfferBackpackPage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					background-color: #454545;
					color: white;
					font-family: 'Press Start 2P', sans-serif, cursive;
					vertical-align: middle;
				}
				img{
					image-rendering: crisp-edges;
					image-rendering: pixelated;
				}
				p.logobig{
					text-align: center;
					display: table;
					margin: auto;
					margin-top: 50px;
					margin-bottom: 50px;
				}
				fieldset.backpack{
					margin: auto;
					background-color: #2B2726;
					width: 870px;
				}
				table{
					border-collapse: seperate;
					cellpadding: 0px;
					border-spacing: 10px;
				}
				td{
					padding: auto;
					width: 64px;
					height: 76px;
					Border: 5px;
					border-style: solid;
					border-radius:0.4em;
				}
				td.none{
					Border-color: #2B2726;
					background-color: #3C352E;
				}
				td.normal{
					Border-color: #F7DC07;
					background-color: #4B4314;
				}
				td.strange{
					Border-color: #BB7343;
					background-color: #472B1F;
				}
				td.unusual{
					Border-color: #835699;
					background-color: #372A3C;
				}
				td.vintage{
					Border-color: #476291;
					background-color: #292D36;
				}
				td.self-made{
					Border-color: #70B04A;
					background-color: #2B3E24;
				}
				button{
					background: none;
					border: none;
				}
				#trading{
					border-style: dashed;
				}
			</style>
		"""
		script = """
			<script type="text/javascript">
			function offer_add_item(idx, key){
				var button = document.getElementById('button_' + idx);
				var image = document.getElementById('image_' + idx);
				button.disabled = true;
				window.top.frames[0].offer.offer_append(idx, key);
			}
			function reset_button(){
				buttons = document.getElementsByClassName('button')
				for (var i = 0; i < buttons.length; i += 1)
				{
					buttons[i].disabled = false;
				}
			}
			</script>
		"""
		current_user = users.get_current_user()
		user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
		if not user:
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S:Backpack</TITLE>' + css + '</HEAD>'
			html += '<body>'
			html += 'Client not found!'
			html += '</body>'
			html += '</html>'
		else:
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S:Backpack</TITLE>' + css + script + '</HEAD>'
			html += '<body>'
			html += '<fieldset class="backpack">'
			html += '<table>'
			cnt = 0
			item_list = ndb.gql('SELECT * FROM BackpackEntity WHERE item_owner=:1', user.key.id())
			html += '<tr>'
			for item in item_list:
				if (not (item.item_rarity == 4)) and (not (item.is_trading)):
					html += '<td id="td_' + str(cnt) + '" class="' + rarityIntegerConvert(item.item_rarity) + '">'
					html += '<button class="button" id="button_' + str(cnt) +'" onclick="offer_add_item(' + str(cnt) + ',' + str(item.key.id()) + ');">'
					html += '<img id="image_' + str(cnt) + '" style="width: 64px; height: 64px;" src="/itemthumb/' + item.item_name + '.png">'
					html += '</button>'
				else:
					html += '<td id="trading" class="' + rarityIntegerConvert(item.item_rarity) + '" id="trading">'
					html += '<img style="width: 64px; height: 64px;" src="/itemthumb/' + item.item_name + '.png">'
				html += '</td>'
				cnt += 1
				if cnt % 10 == 0:
					html += '</tr><tr>'
			while(cnt % 10):
				cnt += 1
				html += '<td class="none">' + '</td>'
			html += '</tr>'
			html += '</table>'
			html += '</fieldset>'
			html += '</div>'
			self.response.out.write(html)

#클라이언트측 거래 제거 페이지			
class RemoveTradePage(webapp2.RequestHandler):
	def get(self):
		css = '''
		<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
		<style>
			html{
				display: table;
				margin: auto;
			}
			body{
				background-color: #454545;
				color: white;
				text-align: center;
				font-family: 'Press Start 2P', sans-serif, cursive;
				vertical-align: middle;
			}
			img{
				image-rendering: crisp-edges;
				image-rendering: pixelated;
			}
			p.logobig{
				text-align: center;
				display: table;
				margin: auto;
				margin-top: 50px;
				margin-bottom: 50px;
			}
		</style>
		'''
		script = """
			<script type="text/javascript">
			function limit(){
				document.getElementById('okayButton').disabled=true;
				var form = document.createElement('form');
				form.method = 'POST';
				form.action = '/removetrade';
				var input = document.createElement('input');
				input.type = 'hidden';
				input.name = 'trade';
				input.value = '""" + self.request.get('trade') +	"""';
				form.appendChild(input);
				document.body.appendChild(form);
				form.submit();
			}
			</script>
		"""
		trade_url = self.request.get('trade')
		current_user = users.get_current_user()
		if (not trade_url) or (not current_user):
			self.redirect('/')
		else:
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S: Trade</TITLE>' + css + script + '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			html += '<div>'
			html += 'Do you really want to remove this trade?'
			html += '</div><br>'
			html += '<button type="submit" style="background: none; border: none;" id="okayButton" onClick="limit();">'
			html += '<img src="/images/buttons_okay.png" style="width: 48px;">'
			html += '</button>'
			html += '<a href="javascript:history.back()"><img src="/images/buttons_nope.png" style="width: 48px;"></a>'
			html += '</form>'
			self.response.out.write(html)

	def post(self):
		trade_url = self.request.get('trade')
		if trade_url:
			trade = ndb.Key(urlsafe=trade_url).get()
			current_user = users.get_current_user()
			
			if (trade.trade_owner == current_user):
				user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
				
				ndb_put_list = []
				ndb_delete_list = []
				
				user_item = ndb.Key(BackpackEntity, trade.trade_item).get()
				user_item.is_trading = False
				ndb_put_list.append(user_item)
					
				offer_list = ndb.gql('SELECT * FROM OfferEntity WHERE offer_target=:1', trade.key.id())
				for each_offer in offer_list:
					item_offer_list = each_offer.offer_item.split(',')
					key_list = []
					for item_offer in item_offer_list:
						key_list.append(ndb.Key(BackpackEntity, int(item_offer)))
					item_offer_list = ndb.get_multi(key_list)
					for item_offer in item_offer_list:
						item_offer.is_trading = False
					ndb_put_list += item_offer_list
					ndb_delete_list.append(ndb.Key(OfferEntity, each_offer.key.id()))
					
					log = LogEntity() #로그 기록
					log.log_owner = each_offer.offer_owner
					log.log_content = 'Offer for trade <span id="' + rarityIntegerConvert(user_item.item_rarity) + '">' + trade.trade_itemname 
					log.log_content += '</span> is removed by its owner.'
					ndb_put_list.append(log)
					
				ndb_delete_list.append(ndb.Key(TradeEntity, trade.key.id()))
				
				ndb.put_multi(ndb_put_list)
				ndb.delete_multi(ndb_delete_list)

				self.redirect('/mytrade')
			
			else:
				self.redirect('/')

		else:
			self.redirect('/')
			
#클라이언트측 제안 제거 페이지			
class RemoveOfferPage(webapp2.RequestHandler):
	def get(self):
		css = '''
		<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
		<style>
			html{
				display: table;
				margin: auto;
			}
			body{
				background-color: #454545;
				color: white;
				text-align: center;
				font-family: 'Press Start 2P', sans-serif, cursive;
				vertical-align: middle;
			}
			img{
				image-rendering: crisp-edges;
				image-rendering: pixelated;
			}
			p.logobig{
				text-align: center;
				display: table;
				margin: auto;
				margin-top: 50px;
				margin-bottom: 50px;
			}
		</style>
		'''
		script = """
			<script type="text/javascript">
			function limit(){
				document.getElementById('okayButton').disabled=true;
				var form = document.createElement('form');
				form.method = 'POST';
				form.action = '/removeoffer';
				var input = document.createElement('input');
				input.type = 'hidden';
				input.name = 'offer';
				input.value = '""" + self.request.get('offer') +	"""';
				form.appendChild(input);
				document.body.appendChild(form);
				form.submit();
			}
			</script>
		"""
		offer_url = self.request.get('offer')
		current_user = users.get_current_user()
		if (not offer_url) or (not current_user):
			self.redirect('/')
		else:
			html = '<html>'
			html += '<HEAD>' + '<TITLE>GG2S: Trade</TITLE>' + css + script + '</HEAD>'
			html += '<body>'
			html += '<div class="logo">'
			html += '<p class="logobig">'
			html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
			html += '</p>'
			html += '</div>'
			html += '<div>'
			html += 'Do you really want to remove this offer?'
			html += '</div><br>'
			html += '<button type="submit" style="background: none; border: none;" id="okayButton" onClick="limit();">'
			html += '<img src="/images/buttons_okay.png" style="width: 48px;">'
			html += '</button>'
			html += '<a href="javascript:history.back()"><img src="/images/buttons_nope.png" style="width: 48px;"></a>'
			html += '</form>'
			self.response.out.write(html)

	def post(self):
		offer_url = self.request.get('offer')
		if offer_url:
			offer = ndb.Key(urlsafe=offer_url).get()
			current_user = users.get_current_user()
			
			if (offer.offer_owner == current_user):
				item_offer_list = offer.offer_item.split(',')
				key_list = []
				for item_offer in item_offer_list:
					key_list.append(ndb.Key(BackpackEntity, int(item_offer)))
				item_offer_list = ndb.get_multi(key_list)
				for item_offer in item_offer_list:
					item_offer.is_trading = False
				ndb.put_multi(item_offer_list)
				ndb.Key(OfferEntity, offer.key.id()).delete()

				self.redirect('/mytrade')
			
			else:
				self.redirect('/')

		else:
			self.redirect('/')

#Cron activity용 거래 제거 페이지
class DeleteTradePage(webapp2.RequestHandler):
	def get(self):
		today = datetime.date.today()
		trade_list = ndb.gql('SELECT * FROM TradeEntity WHERE trade_enddate<=:1', today)
		ndb_delete_list = list()
		ndb_put_list = list()
		
		for trade in trade_list:
			item = ndb.Key(BackpackEntity, trade.trade_item).get()
			item.is_trading = False
			ndb_put_list.append(item)
			ndb_delete_list.append(ndb.Key(TradeEntity, trade.key.id()))
			
			log = LogEntity() #로그 기록
			log.log_owner = trade.trade_owner
			log.log_content = 'Trade for item <span id="' + rarityIntegerConvert(item.item_rarity) + '">' + trade.trade_itemname 
			log.log_content += '</span> is overdated and deleted.'
			ndb_put_list.append(log)
		
			offer_list = ndb.gql('SELECT * FROM OfferEntity WHERE offer_target=:1', trade.key.id())
			for offer in offer_list:
				item_offer_list = offer.offer_item.split(',')
				key_list = []
				
				log = LogEntity() #로그 기록
				log.log_owner = offer.offer_owner
				log.log_content = 'Offer for item <span id="' + rarityIntegerConvert(item.item_rarity) + '">' + trade.trade_itemname 
				log.log_content += '</span> is overdated and deleted.'
				ndb_put_list.append(log)
				
				for item_offer in item_offer_list:
					key_list.append(ndb.Key(BackpackEntity, int(item_offer)))
				item_offer_list = ndb.get_multi(key_list)
				for item_offer in item_offer_list:
					item_offer.is_trading = False
				ndb_put_list += item_offer_list
				ndb_delete_list.append(ndb.Key(OfferEntity, offer.key.id()))
		
		'''
		today = datetime.datetime.today()
		log_list = ndb.gql('SELECT * FROM LogEntity')
		for log in log_list:
			if log.log_date is not None:
				if (log.log_date - today).days >= 30: #30일이 지난 로그는 삭제
					ndb_delete_list.append(ndb.Key(LogEntity, log.key.id()))
		'''
		
		ndb.delete_multi(ndb_delete_list)
		ndb.put_multi(ndb_put_list)
					
#가챠페이지, 100코인에 1회
class GachaPage(webapp2.RequestHandler):
	gacha_price = 100
	
	def get(self):
		current_user = users.get_current_user()
		user_logged_on = False
		if current_user:
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
			if user:
				user_logged_on = True
		if (user_logged_on):
			html = '<!DOCTYPE HTML>'
			html += '<HTML>'
			html += '<HEAD>'
			html += '<TITLE>GG2S: GACHA</TITLE>'
			html += '<script src="/js/jquery.js"></script>'
			html += '<script src="/js/gacha.js"></script>'
			html += '<link rel="stylesheet" type="text/css" href="/css/gacha.css">'
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS : GACHA</span></a>'
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper
			
			def gachaPutPartPossibility(part, rarity, possibility):
				content = '<div class="gacha-possibility-menu" id="{}">'.format(rarity)
				content += '<span id="part">' + part + '</span>'
				content += '<span id="possibility">' + possibility + '</span>'
				content += '</div>'
				return content
			
			html += '<div class="gacha-menu">'
			html += gachaPutPartPossibility('HAT', 'normal', '70%')
			html += gachaPutPartPossibility('TORSO/LEG/WEAPON', 'normal', '27%')
			html += gachaPutPartPossibility('MISC/TAUNT/DEATH ANIM/HUMILIATION', 'normal', '1.5%')
			html += gachaPutPartPossibility('STRANGE WEAPON', 'strange', '0.9%')
			html += gachaPutPartPossibility('PET', 'normal', '0.3%')
			html += gachaPutPartPossibility('UNUSUAL HAT', 'unusual', '0.3%')
			html += '</div>' #gacha-menu
			
			if user.user_coin >= self.gacha_price:
				html += '<div class="gacha-price-wrapper" id="available">'
			else:
				html += '<div class="gacha-price-wrapper" id="unavailable">'
			
			if user.user_coin >= self.gacha_price:
				html += '<span class="gacha-price" id="{}">{} / {} COINS</span>'.format("available", user.user_coin, self.gacha_price)
			else:
				html += '<span class="gacha-price" id="{}">{} / {} COINS</span>'.format("unavailable", user.user_coin, self.gacha_price)
			html += '</div>' #gacha-price
			html += '<div class="gacha-button-wrapper">'
			html += '<form id="gacha-button-form" method="POST">'
			if user.user_coin >= self.gacha_price:
				html += '<button id="gacha-button" onClick="disable();">GACHA!</button>'
			else:
				html += '<button id="gacha-button" disabled>GACHA!</button>'
			html += '</form>'
			html += '</div>' #gacha-button-wrapper
			
			html += '</BODY>'
			html += '</HTML>'
			
			self.response.out.write(html)
		else:
			self.redirect('/')
		
	def post(self):
		current_user = users.get_current_user()
		user_logged_on = False
		if current_user:
			user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
			if current_user:
				user_logged_on = True
		if (user_logged_on):
			is_unusual = False
			is_strange = False
			if (randint(0, 9) < 3): #30%의 확률로 진입
				rare_possibility = randint(0, 99)
				if (rare_possibility < 1): #언유: 1%의 확률
					item_query = ndb.gql('SELECT * FROM ItemEntity WHERE item_part=0 AND can_get=True')
					is_unusual = True
					rarity = 2 #unusual
				elif (rare_possibility < 2): #펫: 1%의 확률을 추가로
					item_query = ndb.gql('SELECT * FROM ItemEntity WHERE item_part=6 AND can_get=True')
					rarity = 0
				elif (rare_possibility < 5): #스트레인지: 3%의 확률을 추가로
					item_query = ndb.gql('SELECT * FROM ItemEntity WHERE item_part=3 AND can_get=True')
					is_strange = True
					rarity = 1 #strange
				elif (rare_possibility < 10): #나머지: 5%의 확률을 추가로
					item_query = ndb.gql('SELECT * FROM ItemEntity WHERE item_part>3 AND item_part!=6 AND can_get=True')
					rarity = 0
				else: #나머지: 몸통&다리&무기
					item_query = ndb.gql('SELECT * FROM ItemEntity WHERE item_part<4 AND item_part!=0 AND can_get=True')
					rarity = 0
			else:
				item_query = ndb.gql('SELECT * FROM ItemEntity WHERE can_get=True AND item_part=0')
				rarity = 0

			pass_count = randint(0, item_query.count() - 1)
			i = 0
			for item in item_query:
				if (i >= pass_count):
					break
				else:
					i += 1
			if not is_unusual and not is_strange and item.is_vintage:
				rarity = 3

			new_item = self.doGacha(user.key, item, rarity, is_unusual, is_strange)
			
			if new_item:
				user.user_coin -= 100 #표시만 싱크로하기 위함, 실제로 감산해서 저장하지는 않음
				html = '<!DOCTYPE HTML>'
				html += '<HTML>'
				html += '<HEAD>'
				html += '<TITLE>GG2S: GACHA</TITLE>'
				html += '<script src="/js/jquery.js"></script>'
				html += '<script src="/js/gacha.js"></script>'
				html += '<link rel="stylesheet" type="text/css" href="/css/gacha_result.css">'
				html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
				html += '</HEAD>'
				
				html += '<BODY>'
				html += '<div class="head-wrapper">'
				html += '<div class="head-gg2s-text">'
				html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
				html += '<a href="/"><span>GANG GARRISON 2 STATS : GACHA</span></a>'
				html += '</div>' #head-gg2s-text
				html += '</div>' #head-wrapper
				
				html += '<div class="result-wrapper">'
				html += '<div class="result-header-wrapper"><span id="result-header">YOU GOT...</span></div>'
				if (new_item.item_part == 6):
					html += '<div class="result-item-wrapper" id="{}">'.format('unusual')
				else:
					html += '<div class="result-item-wrapper" id="{}">'.format(rarityIntegerConvert(new_item.item_rarity))
				html += '<img id="result-item" src="/itemthumb/{}.png">'.format(new_item.item_name)
				html += '</div>' 
				
				if (new_item.item_rarity == 1):
					html += '<div class="result-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('strange', strangeCountToString(new_item.item_strangeCount).upper())
				elif (new_item.item_rarity == 2):
					html += '<div class="result-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('unusual', 'UNUSUAL')
				elif (new_item.item_rarity == 3):
					html += '<div class="result-rairity-wrapper"><span id="{}" class="rarity-string">{}</span></div>'.format('vintage', 'VINTAGE')
				if (new_item.item_part == 6):
					html += '<div class="result-name-wrapper"><span id="{}" class="name-string">{}</span></div>'.format('unusual', item.item_nickname.upper())
				else:
					html += '<div class="result-name-wrapper"><span id="{}" class="name-string">{}</span></div>'.format(rarityIntegerConvert(new_item.item_rarity), item.item_nickname.upper())
				html += '<div class="result-level-wrapper"><span id="level-string">LEVEL {} {}</span></div>'.format(new_item.item_level, partToString(item.item_part).upper())
				if	(new_item.item_rarity == 1):
					html += '<div class="result-strangetype-wrapper"><span id="{}" class="strangetype-string">{}: {}</span></div>'.format(rarityIntegerConvert(new_item.item_rarity), strangeTypeToString(new_item.item_strangeType).upper(), new_item.item_strangeCount)
				elif (new_item.item_rarity == 2):
					html += '<div class="result-unusualtype-wrapper"><span id="{}" class="unusualtype-string">UNUSUAL EFFECT: {}</span></div>'.format(rarityIntegerConvert(new_item.item_rarity), unusualTypeToString(new_item.item_effect).upper())
				html += '<div class="result-desc-wrapper"><span id="desc-string">{}</span></div>'.format(item.item_desc.upper())
				html += '<div class="result-classlist-wrapper"><span id="classlist-string">'
				if (item.item_classlist.split(',') == _CLASSES):
					html += 'ITEM FOR: ALL CLASSES'
				elif (item.item_classlist.split(',') + ["Quote"] == _CLASSES):
					html += 'ITEM FOR: ALL CLASSES EXCEPT QUOTE'
				else:
					html += 'ITEM FOR: {}'.format(item.item_classlist.upper())
				html += '</span></div>'
				html += '</div>' #result-wrapper
				
				html += '<div class="result-coin-wrapper">'
				if user.user_coin >= self.gacha_price:
					html += '<span class="coin-string" id="{}">{} / {} COINS</span>'.format("available", user.user_coin, self.gacha_price)
				else:
					html += '<span class="coin-string" id="{}">{} / {} COINS</span>'.format("unavailable", user.user_coin, self.gacha_price)
				html += '</div>' #result-coin-wrapper
				
				html += '<div class="gacha-button-wrapper">'
				html += '<form id="gacha-button-form" method="POST">'
				if user.user_coin >= self.gacha_price:
					html += '<button id="gacha-button" onClick="disable();">GACHA!</button>'
				else:
					html += '<button id="gacha-button" disabled>GACHA!</button>'
				html += '</form>'
				
				if (new_item.item_rarity == 2 or new_item.item_rarity == 6):
					subject = user.user_id + ' got special item'
					if (new_item.item_rarity == 2):
						log = LogEntity()
						log.log_content = 'Got Unusual <span id="unusual">' + item.item_nickname + '(' + unusualTypeToString(new_item.item_effect) + ')</span>' 
						log.log_owner = current_user
						log.put()
						body = user.user_id + ' got Unusual ' + item.item_nickname + '(' + unusualTypeToString(new_item.item_effect) + ')'
					
					if (new_item.item_part == 6):
						log = LogEntity()
						log.log_content = 'Got Pet <span id="normal">' + item.item_nickname + '</span>' 
						log.log_owner = current_user
						log.put()
						body = user.user_id + ' got Pet ' + item.item_nickname
					
					user_address = "WN <saiyu915@naver.com>"
					sender_address = "GG2S Support <noreply@gg2statsapp.appspotmail.com>"
					mail.send_mail(sender_address, user_address, subject, body)
					
					
				self.response.out.write(html)
			else:
				self.redirect('/gacha')
		else:
			self.redirect('/gacha')

	@ndb.transactional(xg=True)
	def doGacha(self, user_key, item, rarity, is_unusual, is_strange):
		user = user_key.get()
		if (user.user_coin >= self.gacha_price):
			user.user_coin -= self.gacha_price
			new_item = BackpackEntity()
			new_item.item_name = item.key.id()
			new_item.item_rarity = rarity
			new_item.item_level = randint(1, 99)
			new_item.item_part = item.item_part
			new_item.item_owner = user.key.id()
			if is_unusual:
				new_item.item_effect = choice(_UNUSUALS)
			if is_strange:
				if item.item_classlist == 'Healer':
					if (randint(0, 1) < 1): #2분의 1 확률
						new_item.item_strangeType = 12
					else:
						new_item.item_strangeType = 0
				elif item.item_classlist == 'Infiltrator':
					if (randint(0, 1) < 1): #2분의 1 확률
						new_item.item_strangeType = 13
					else:
						new_item.item_strangeType = 0
				else:
					new_item.item_strangeType = 0
				new_item.item_strangeCount = 0
			new_item.put()
			user.put()
		else:
			new_item = None
		return new_item
			
#아이템 갤러리
class GalleryPage(webapp2.RequestHandler):
	def get(self):
		html = '<html>'
		html += '<head>'
		html += '<TITLE>GG2S: Item Gallery</TITLE>'
		html += '<link rel="stylesheet" type="text/css" href="/css/gallery.css">'
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</head>'
		html += '<body>'
		
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '</div>' #head-wrapper
		
		#Memcache Read
		item_sorted = memcache.get('item_gallery')
		if item_sorted is None:
			item_list = ndb.gql('SELECT * FROM ItemEntity')

			item_sorted = [list() for i in range(11)]
			for item in item_list:
				if item.item_classlist == "Runner":
					item_sorted[0].append(item.key.id())
				elif item.item_classlist == "Firebug":
					item_sorted[1].append(item.key.id())
				elif item.item_classlist == "Rocketman":
					item_sorted[2].append(item.key.id())
				elif item.item_classlist == "Overweight":
					item_sorted[3].append(item.key.id())
				elif item.item_classlist == "Detonator":
					item_sorted[4].append(item.key.id())
				elif item.item_classlist == "Healer":
					item_sorted[5].append(item.key.id())
				elif item.item_classlist == "Constructor":
					item_sorted[6].append(item.key.id())
				elif item.item_classlist == "Infiltrator":
					item_sorted[7].append(item.key.id())
				elif item.item_classlist == "Rifleman":
					item_sorted[8].append(item.key.id())
				elif item.item_classlist == "Quote":
					item_sorted[9].append(item.key.id())
				else:
					item_sorted[10].append(item.key.id())

			if not memcache.add('item_gallery', item_sorted, 86400):
				logging.error('Memcache set failed for ITEM_GALLERY')
					
		html += '<div class="gallery-body-wrapper">'
		i = 0
		for class_string in (_CLASSES + ['']):
			cnt = 0
			html += '<div class="class-wrapper">'
			html += '<div class="class-string-wrapper">'
			if i != 10:
				html += '<span id="class-string">' + class_string.upper() + '</span>'
			else:
				html += '<span id="class-string">' + 'ALL' + '</span>'
			html += '</div>' #class-string-wrapper
			
			html += '<div class="class=items-wrapper">'
			for item in item_sorted[i]:
				html += '<div class="item-wrapper">'
				html += '<a href="/iteminfo?item=' + item + '">'
				html += '<img class="item" src="/itemthumb/' + item + '.png">'
				html += '</a>'
				html += '</div>'
				cnt += 1
			i += 1
			html += '</div>' #class-items-wrapper
			
			html += '</div>' #class-wrapper
		html += '</div>' #gallery-body-wrapper
		
		html += '</body>'
		html += '</html>'
		
		self.response.out.write(html)
			
#아이템업로드 페이지
class ItemUploadPage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					font-family: 'Press Start 2P', sans-serif, cursive;
					display: table-cell;
					vertical-align: middle;
					text-align: center;
				}
				div{
					margin-bottom: 20px;
				}
			</style>
		"""
		html = '<html>'
		html += '<HEAD>' + '<TITLE>GG2S:Item Upload</TITLE>' + css + '</HEAD>'
		html += '<body>'
		html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
		html += '<div>'
		html += '<form method ="post" enctype="multipart/form-data">'
		html += 'Item Name: ' +  '<input type="text" name="item_name">' + '<div>'
		html += 'Item Nickname for web: ' +  '<input type="text" name="item_nickname">' + '<div>'
		html += 'Item Desc: ' +  '<textarea rows="4" cols="50" name="item_desc" resize="vertical" wrap="hard"></textarea>' + '<div>'
		html += 'Item Author' + '<input type="text" name="item_author" maxlength="20">' + '<div>'
		html += 'Item Part: <br>' + '<select name="item_part" size="6">'
		html += '<option value=0>Head</option>'
		html += '<option value=1>Torso</option>'
		html += '<option value=2>Leg</option>'
		html += '<option value=3>Weapon</option>'
		html += '<option value=4>Misc</option>'
		html += '<option value=5>Taunt</option>'
		html += '<option value=6>Pet</option>'
		html += '<option value=7>Death Anim</option>'
		html += '<option value=8>Humiliation</option>'
		html += '</select>' + '<div>'
		html += 'Item Classlist<br>' + '<select name="item_classlist" size="10" multiple>'
		for classes in _CLASSES:
			html += '<option value=' + classes + '>' + classes + '</option>'
		html += '</select><br>'
		html += 'Can Get:' + '<input type="radio" name="canget" value="0" selected>Yes&nbsp' + '<input type="radio" name="canget" value="1">No<br>'
		html += 'Vintage:' + '<input type="radio" name="vintage" value="0">Yes&nbsp' + '<input type="radio" name="vintage" value="1" selected>No<br>'
		html += '<input type="submit" value="Update">'
		html += '</form>'
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)
		
	def post(self):
		item = ItemEntity()
		item_name = self.request.get('item_name')
		item.key = ndb.Key(ItemEntity, item_name)
		item.item_nickname = self.request.get('item_nickname')
		item.item_desc = self.request.get('item_desc')
		item.item_author = self.request.get('item_author')
		item.item_part = int(self.request.get('item_part'))
		can_get = int(self.request.get('canget'))
		if (can_get == 0):
			item.can_get = True
		else:
			item.can_get = False
		vintage = int(self.request.get('vintage'))
		if (vintage == 0):
			item.is_vintage = True
		else:
			item.is_vintage = False
		item_classlist = self.request.params.getall('item_classlist')
		class_str = ''
		for _class in item_classlist:
			class_str += _class+','
		class_str = class_str[:-1]
		item.item_classlist = class_str

		item.put()
		
		html = 'Item is created'
		html += 'Item Name: ' + item.key.id()
		html += '<br>'
		html += 'Item NickName: ' + item.item_nickname
		html += '<br>'
		html += 'Item Author: ' + item.item_author
		html += '<br>'
		html += 'Item Part: ' + str(item.item_part)
		html += '<br>'
		if item.can_get:
			html += 'This item is gettable'
		else:
			html += 'This item isn\'t gettable'
		html += '<br>'
		if item.is_vintage:
			html += 'This item is Vintage'
		else:
			html += 'This item is Normal'
		html += '<br>'
		
		# 아이템 제작자에게 Self-Made 퀄리티의 아이템을 제공
		# item_author는 실제 유저의 닉네임과 동일해야 한다
		if not (item.item_author == ''):
			author_item = BackpackEntity()
			author_item.item_name = item_name
			author_item.item_rarity = 4
			author_item.item_level = 50
			author_item.item_part = item.item_part
			author = ndb.gql('SELECT * from UserEntity WHERE user_id=:1', item.item_author).get()
			author_item.item_owner = author.key.id()
			author_item.put()
			
			html += '<br>'
			html += 'Item has been given to ' + item.item_author + ' : ' + str(author.key.id())
		
		self.response.out.write(html)

#아이템포맷 제공 페이지
class ItemFormatPage(webapp2.RequestHandler):
	def get(self):
		html = '''
		<html>
		<style>
		html{width: 100%; height: 100%; text-align: center;}
		.column-left, .column-right{display: inline-block; margin: 10px;}
		.column-left{width: 40%;}
		.column-right{width: 40%;}
		</style>
		<body>

		<form method ="post" enctype="multipart/form-data">
		<div class="column-left">
		Item Identifier
		</div>
		<div class="column-right">
		<input type="text" name="item_name">
		</div>

		<div class="column-left">
		Item Nickname
		</div>
		<div class="column-right">
		<input type="text" name="item_nickname">
		</div>

		<div class="column-left">
		Item Desc
		</div>
		<div class="column-right">
		<textarea rows="4" cols="50" name="item_desc" resize="vertical" wrap="hard"></textarea>
		</div>

		<div class="column-left">
		Item Author
		</div>
		<div class="column-right">
		<input type="text" name="item_author" maxlength="20">
		</div>

		<div class="column-left">
		Item Part
		</div>
		<div class="column-right">
		<select name="item_part" size="6">
		<option value=0>Head</option>
		<option value=1>Torso</option>
		<option value=2>Leg</option>
		<option value=3>Weapon</option>
		<option value=4>Misc</option>
		<option value=5>Taunt</option>
		<option value=6>Pet</option>
		<option value=7>Death Anim</option>
		<option value=8>Humiliation</option>
		</select>
		</div>

		<div class="column-left">
		Item Classlist
		</div>
		<div class="column-right">
		<select name="item_classlist" size="10" multiple>
		<option value=Runner>Runner</option>
		<option value=Firebug>Firebug</option>
		<option value=Rocketman>Rocketman</option>
		<option value=Overweight>Overweight</option>
		<option value=Detonator>Detonator</option>
		<option value=Healer>Healer</option>
		<option value=Constructor>Constructor</option>
		<option value=Infiltrator>Infiltrator</option>
		<option value=Rifleman>Rifleman</option>
		<option value=Quote>Quote</option>
		</select>
		</div>

		<div class="column-left">
		Can Get
		</div>
		<div class="column-right">
		<input type="radio" name="canget" value="0" checked>Yes&nbsp  <input type="radio" name="canget" value="1">No<br>
		</div>

		<div class="column-left">
		Vintage
		</div>
		<div class="column-right">
		<input type="radio" name="vintage" value="0">Yes&nbsp  <input type="radio" name="vintage" value="1" checked>No<br>
		</div>

		<div>
		<input type="submit">
		<input type="reset">
		</div>
		</form>

		</body>
		</html>
		'''
		self.response.out.write(html)
	
	def post(self):
		item_name = self.request.get('item_name')
		item_nickname = self.request.get('item_nickname')
		item_desc = self.request.get('item_desc').replace('\n', '<br>')
		item_author = self.request.get('item_author')
		item_part = self.request.get('item_part')
		can_get = int(self.request.get('canget'))
		if (can_get == 0):
			can_get = 'T'
		else:
			can_get = 'F'
		vintage = int(self.request.get('vintage'))
		if (vintage == 0):
			is_vintage = 'T'
		else:
			is_vintage = 'F'
		item_classlist = self.request.params.getall('item_classlist')
		class_str = ''
		for _class in item_classlist:
			class_str += _class+'_'
		class_str = class_str[:-1]
		item_classlist = class_str
		
		html = "%s{nickname: %s, desc: %s, author: %s, part: %s, class: %s, can_get: %s, is_vintage: %s}" %(item_name, item_nickname, item_desc, item_author, item_part, item_classlist, can_get, is_vintage)
		
		self.response.out.write(html)

#아이템 획득 페이지(인게임)
class GetItemPage(webapp2.RequestHandler):
	def post(self):
		unique_key = self.request.get('unique_key')
		try:
			unique_key = int(unique_key)
			item_list = ndb.gql('SELECT * FROM ItemEntity WHERE can_get=True AND item_part=0')
			item_count = item_list.count()
			cnt = randint(0, item_count - 1)
			for item in item_list:
				if (cnt <= 0):
					break
				else:
					cnt -= 1
			new_item = BackpackEntity()
			new_item.item_name = item.key.id()
			new_item.item_rarity = 0 #Normal
			if (item.is_vintage):
				new_item.item_rarity = 3 #Vintage
			new_item.item_level = randint(1, 99)
			new_item.item_part = item.item_part
			new_item.item_owner = unique_key
			new_item.put()
			self.response.out.write(item.item_nickname)
		except ValueError:
			self.response.out.write('Nothing. Login to get Item!')
		except:
			self.response.out.write('Nothing. Contact WN for further information.')

#테스트페이지
class TestPage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					font-family: 'Press Start 2P', sans-serif, cursive;
					display: table-cell;
					vertical-align: middle;
					text-align: center;
				}
				div{
					margin-bottom: 20px;
				}
			</style>
		"""
		html = '<html>'
		html += '<HEAD>' + '<TITLE>GG2S:Item Add</TITLE>' + css + '</HEAD>'
		html += '<body>'
		html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
		html += '<div>'
		html += '<form method ="post">'
		html += 'Item Name: ' +  '<input type="text" name="item_name">' + '<div>'
		html += 'Item Part: ' + '<select name="item_part" size="6">'
		html += '<option value=0>Head</option>'
		html += '<option value=1>Torso</option>'
		html += '<option value=2>Leg</option>'
		html += '<option value=3>Weapon</option>'
		html += '<option value=4>Misc</option>'
		html += '<option value=5>Taunt</option>'
		html += '<option value=6>Pet</option>'
		html += '<option value=7>Death Anim</option>'
		html += '<option value=8>Humiliation</option>'
		html += '</select>' + '<div>'
		html += 'Item Rarity: ' + '<select name="item_rarity" size="3">'
		html += '<option value=0>Normal</option>'
		html += '<option value=1>Strange</option>'
		html += '<option value=2>Unusual</option>'
		html += '<option value=3>Vintage</option>'
		html += '<option value=4>Self-Made</option>'
		html += '</select>' + '<div>'
		html += 'Item Effect(If Unusual): ' + '<select name="item_effect" size="5">'
		for effects in _UNUSUALS:
			html += '<option value=' + str(effects) + '>' + unusualTypeToString(effects) + '</option>'
		html += '</select>' + '<div>'
		html += 'Strange type(If Strange): ' + '<select name="item_strangeType" size="5">'
		html += '<option value=0>Kill</option>'
		html += '<option value=1>Runners Killed</option>'
		html += '<option value=2>Firebugs Killed</option>'
		html += '<option value=3>Rocketmans Killed</option>'
		html += '<option value=4>Overweights Killed</option>'
		html += '<option value=5>Detonators Killed</option>'
		html += '<option value=6>Healers Killed</option>'
		html += '<option value=7>Constructors Killed</option>'
		html += '<option value=8>Infiltrators Killed</option>'
		html += '<option value=9>Riflemans Killed</option>'
		html += '<option value=10>Quotes Killed</option>'
		html += '<option value=11>Sentries Destroyed</option>'
		html += '<option value=12>Invulns</option>'
		html += '<option value=13>Knife Kills</option>'
		html += '</select>' + '<div>'
		html += '<input type="submit">'
		html += '</form>'
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)
		
	def post(self):
		user_list = ndb.gql('SELECT * FROM UserEntity')
		item_name = self.request.get('item_name')
		item_part = int(self.request.get('item_part'))
		item_rarity = int(self.request.get('item_rarity'))
		for user in user_list:
			user_key = user.key.id()
			item = BackpackEntity()
			item.item_name = item_name
			item.item_owner = user_key
			item.item_part = item_part
			item.item_rarity = item_rarity
			item.item_level = randint(1, 100)
			if (item_rarity == 1): #Strange
				strange_type = self.request.get('item_strangeType')
				if (strange_type == ''):
					raise(TypeError())
				else:
					item.item_strangeType = int(strange_type)
			elif (item_rarity == 2): #Unusual
				effect = self.request.get('item_effect')
				if (effect == ''):
					raise(TypeError())
				else:
					item.item_effect = int(effect)
			item.put()
		self.response.out.write('DONE')

#잡일 담당
class PleasePage(webapp2.RequestHandler):
	def get(self):
		user_list = ndb.gql('SELECT * FROM UserEntity')
		stat_list = []
		for user in user_list:
			season = ndb.gql('SELECT * FROM SeasonStatEntity WHERE season_owner=:1 AND season=:2', user.key.id(), GG2S_CURRENT_SEASON - 1).get()
			stat_list.append(season)
		
		best_point = []
		best_playtime = []
		best_playcount = []
		best_heal = []
		best_stab = []
		best_wl = []
		
		for i in range(5):
			best_point.append([0, 0])
			best_playtime.append([0, 0])
			best_playcount.append([0, 0])
			best_heal.append([0, 0, 0])
			best_stab.append([0, 0, 0])
			best_wl.append([0, 0, 0, 0])
		
		best_kda = []
		for i in range(11):
			best_kda.append([[0, 0, 0, 0, 0],[0, 0, 0, 0, 0],[0, 0, 0, 0, 0],[0, 0, 0, 0, 0],[0, 0, 0, 0, 0]])
		
		for stat in stat_list:
			if stat:
				for i in range(5):
					if stat.user_point > best_point[i][0]:
						for j in range(4, i, -1):
							best_point[j][0] = best_point[j - 1][0]
							best_point[j][1] = best_point[j - 1][1]
						best_point[i][0] = stat.user_point
						best_point[i][1] = stat.season_owner
						break
				
				for i in range(5):
					if stat.user_playtime > best_playtime[i][0]:
						for j in range(4, i, -1):
							best_playtime[j][0] = best_playtime[j - 1][0]
							best_playtime[j][1] = best_playtime[j - 1][1]
						best_playtime[i][0] = stat.user_playtime
						best_playtime[i][1] = stat.season_owner
						break
				
				for i in range(5):
					if stat.user_playcount > best_playcount[i][0]:
						for j in range(4, i, -1):
							best_playcount[j][0] = best_playcount[j - 1][0]
							best_playcount[j][1] = best_playcount[j - 1][1]
						best_playcount[i][0] = stat.user_playcount
						best_playcount[i][1] = stat.season_owner
						break

				for i in range(5):
					if stat.user_healing > best_heal[i][0]:
						for j in range(4, i, -1):
							best_heal[j][0] = best_heal[j - 1][0]
							best_heal[j][1] = best_heal[j - 1][1]
							best_heal[j][2] = best_heal[j - 1][2]
						best_heal[i][0] = stat.user_healing
						best_heal[i][1] = stat.user_invuln
						best_heal[i][2] = stat.season_owner
						break

				for i in range(5):
					if stat.user_stab > best_stab[i][0]:
						for j in range(4, i, -1):
							best_stab[j][0] = best_stab[j - 1][0]
							best_stab[j][1] = best_stab[j - 1][1]
							best_stab[j][2] = best_stab[j - 1][2]
						best_stab[i][0] = stat.user_stab
						best_stab[i][1] = stat.class_kill.split(',')[7]
						best_stab[i][2] = stat.season_owner
						break
					
				if (stat.user_win >= 100):
					wl_ratio = 100*(stat.user_win / float(stat.user_win + stat.user_lose))
					for i in range(5):
						if wl_ratio > best_wl[i][0]:
							for j in range(4, i, -1):
								best_wl[j][0] = best_wl[j - 1][0]
								best_wl[j][1] = best_wl[j - 1][1]
								best_wl[j][2] = best_wl[j - 1][2]
								best_wl[j][3] = best_wl[j - 1][3]
							best_wl[i][0] = wl_ratio
							best_wl[i][1] = stat.user_win
							best_wl[i][2] = stat.user_lose
							best_wl[i][3] = stat.season_owner
							break
					
				if (stat.user_kill >= 300):
					kda = (stat.user_kill + stat.user_assist) / float(stat.user_death)
					for i in range(5):
						if kda > best_kda[0][i][0]:
							for j in range(4, i, -1):
								best_kda[0][j][0] = best_kda[0][j - 1][0]
								best_kda[0][j][1] = best_kda[0][j - 1][1]
								best_kda[0][j][2] = best_kda[0][j - 1][2]
								best_kda[0][j][3] = best_kda[0][j - 1][3]
								best_kda[0][j][4] = best_kda[0][j - 1][4]
							best_kda[0][i][0] = kda
							best_kda[0][i][1] = stat.user_kill
							best_kda[0][i][2] = stat.user_death
							best_kda[0][i][3] = stat.user_assist
							best_kda[0][i][4] = stat.season_owner
							break
					
						
				class_kill = stat.class_kill.split(',')
				class_death = stat.class_death.split(',')
				class_assist = stat.class_assist.split(',')
				for i in range(10):
					class_kill[i] = int(class_kill[i])
					class_death[i] = int(class_death[i])
					class_assist[i] = int(class_assist[i])
					
					kill_limit = 300
					
					for j in range(5):
						if (class_kill[i] + class_assist[i] >= kill_limit):
							if class_death[i] is not 0:
								class_kda = (class_kill[i] + class_assist[i])/float(class_death[i])
							else:
								class_kda = class_kill[i] + class_assist[i]
							if class_kda > best_kda[i + 1][j][0]:
								for k in range(4, j, -1):
									best_kda[i + 1][k][0] = best_kda[i + 1][k - 1][0]
									best_kda[i + 1][k][1] = best_kda[i + 1][k - 1][1]
									best_kda[i + 1][k][2] = best_kda[i + 1][k - 1][2]
									best_kda[i + 1][k][3] = best_kda[i + 1][k - 1][3]
									best_kda[i + 1][k][4] = best_kda[i + 1][k - 1][4]
								best_kda[i + 1][j][0] = class_kda
								best_kda[i + 1][j][1] = class_kill[i]
								best_kda[i + 1][j][2] = class_death[i]
								best_kda[i + 1][j][3] = class_assist[i]
								best_kda[i + 1][j][4] = stat.season_owner
								break
								
		html = ''
		html += '['
		for i in range(5):
			html += '[{},ndb.Key(UserEntity,{})],'.format(best_point[i][0], best_point[i][1])
		html = html[:-1]
		html += ']'
		
		html += '<br>'
		
		html += '['
		for i in range(5):
			html += '[{},ndb.Key(UserEntity,{})],'.format(best_playtime[i][0], best_playtime[i][1])
		html = html[:-1]
		html += ']'
		
		html += '<br>'
		
		html += '['
		for i in range(5):
			html += '[{},ndb.Key(UserEntity,{})],'.format(best_playcount[i][0], best_playcount[i][1])
		html = html[:-1]
		html += ']'
		
		html += '<br>'
		
		html += '['
		for i in range(5):
			html += '[{},{},ndb.Key(UserEntity,{})],'.format(best_heal[i][0], best_heal[i][1], best_heal[i][2])
		html = html[:-1]
		html += ']'
		
		html += '<br>'
		
		html += '['
		for i in range(5):
			html += '[{},{},ndb.Key(UserEntity,{})],'.format(best_stab[i][0], best_stab[i][1], best_stab[i][2])		
		html = html[:-1]
		html += ']'
			
		html += '<br>'
		
		html += '['
		for i in range(5):
			html += '[{:.2f},{},{},ndb.Key(UserEntity,{})],'.format(best_wl[i][0], best_wl[i][1], best_wl[i][2], best_wl[i][3])
		html = html[:-1]
		html += ']'
		
		html += '<br>'
		
		html += '['
		for i in range(5):
			html += '[{:.2f},{},{},{},ndb.Key(UserEntity,{})],'.format(best_kda[0][i][0], best_kda[0][i][1], best_kda[0][i][2], best_kda[0][i][3], best_kda[0][i][4])	
		html = html[:-1]
		html += ']'
		
		html += '<br>'
		
		for i in range(10):
			html += '['
			for j in range(5):
				html += '[{:.2f},{},{},{},ndb.Key(UserEntity,{})],'.format(best_kda[i + 1][j][0], best_kda[i + 1][j][1], best_kda[i + 1][j][2], best_kda[i + 1][j][3], best_kda[i + 1][j][4])
			html = html[:-1]
			html += ']'
			
			html += '<br>'
		self.response.out.write(html)
			
class PleasePage2(webapp2.RequestHandler):
	def get(self):
		html = ''
		user_list = ndb.gql('SELECT * FROM UserEntity')
		ndb_put_list = []
		for user in user_list:
			new_season = SeasonStatEntity()
			new_season.season = GG2S_CURRENT_SEASON
			new_season.season_owner = user.key.id()
			ndb_put_list.append(new_season)

		ndb.put_multi(ndb_put_list)
		html += 'DONE'
		
		self.response.out.write(html)
		
#Generate Big Data for season
class PleasePage3(webapp2.RequestHandler):
	def get(self):
		TARGET_SEASON = GG2S_CURRENT_SEASON - 1
		season_list = ndb.gql('SELECT * FROM SeasonStatEntity WHERE season=:1', TARGET_SEASON)
		
		# Initiate each datas
		kill = 0
		death = 0
		assist = 0
		cap = 0
		destruction = 0
		stab = 0
		healing = 0
		defense = 0
		invuln = 0
		playcount = 0
		playtime = 0
		redtime = 0
		bluetime =0
		spectime = 0
		win = 0
		lose = 0
		stalemate = 0
		escape = 0
		class_kill = [0 for i in range(10)]
		class_death = [0 for i in range(10)]
		class_assist = [0 for i in range(10)]
		class_playtime = [0 for i in range(10)]
		
		for season in season_list:
			kill += season.user_kill
			death += season.user_death
			assist += season.user_assist
			cap += season.user_cap
			destruction += season.user_destruction
			stab += season.user_stab
			healing += season.user_healing
			defense += season.user_defense
			invuln += season.user_invuln
			playcount += season.user_playcount
			playtime += season.user_playtime
			redtime += season.user_redtime
			bluetime += season.user_bluetime
			spectime += season.user_spectime
			win += season.user_win
			lose += season.user_lose
			stalemate += season.user_stalemate
			escape += season.user_escape
			ck = season.class_kill.split(',')
			cd = season.class_death.split(',')
			ca = season.class_assist.split(',')
			cp = season.class_playtime.split(',')
			for i in range(10):
				class_kill[i] += int(ck[i])
				class_death[i] += int(cd[i])
				class_assist[i] += int(ca[i])
				class_playtime[i] += int(cp[i])
				
		html = ''
		html += 'KILL : {}<br>'.format(kill)
		html += 'DEATH : {}<br>'.format(death)
		html += 'ASSIST : {}<br>'.format(assist)
		html += 'CAP : {}<br>'.format(cap)
		html += 'DESTRUCTION : {}<br>'.format(destruction)
		html += 'STAB : {}<br>'.format(stab)
		html += 'HEALING : {:.2f}<br>'.format(healing)
		html += 'DEFENSE : {}<br>'.format(defense)
		html += 'INVULN : {}<br>'.format(invuln)
		html += 'PLAYCOUNT : {}<br>'.format(playcount)
		html += 'PLAYTIME : {}<br>'.format(makePlaytimeTemplate(playtime))
		html += 'TIME_RED : {}<br>'.format(makePlaytimeTemplate(redtime))
		html += 'TIME_BLUE : {}<br>'.format(makePlaytimeTemplate(bluetime))
		html += 'TIME_SPECTATE : {}<br>'.format(makePlaytimeTemplate(spectime))
		html += 'WIN : {}<br>'.format(win)
		html += 'LOSE : {}<br>'.format(lose)
		html += 'STALEMATE : {}<br>'.format(stalemate)
		html += 'ESCAPE : {}<br>'.format(escape)
		for i in range(10):
			html += '{} KILL : {}<br>'.format(_CLASSES[i], class_kill[i])
			html += '{} DEATH : {}<br>'.format(_CLASSES[i], class_death[i])
			html += '{} ASSIST : {}<br>'.format(_CLASSES[i], class_assist[i])
			html += '{} PLAYTIME : {}<br>'.format(_CLASSES[i], makePlaytimeTemplate(class_playtime[i]))
		
		self.response.out.write(html)
		
#트로피 수여
class GiveTrophyPage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Press+Start+2P' rel='stylesheet' type='text/css'>
			<style>
				html{
					display: table;
					margin: auto;
				}
				body{
					font-family: 'Press Start 2P', sans-serif, cursive;
					display: table-cell;
					vertical-align: middle;
					text-align: center;
				}
				div{
					margin-bottom: 20px;
				}
			</style>
		"""
		html = '<html>'
		html += '<HEAD>' + '<TITLE>GG2S:Item Add</TITLE>' + css + '</HEAD>'
		html += '<body>'
		html += '<a href="/"><img src="/images/GG2SLogoBig.png"></a>'
		html += '<div>'
		html += '<form method ="post">'
		html += 'Trophy Index: ' +  '<input type="text" name="trophy_index">' + '<br>'
		html += 'Target Name(GIVEALL to give all): ' + '<input type="text" name="target_user">' + '<br>'
		html += '<input type="submit">'
		html += '</form>'
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)
		
	def post(self):
		trophy_index = int(self.request.get('trophy_index'))
		target_user = self.request.get('target_user')
		if (target_user=="GIVEALL"):
			user_list = ndb.gql('SELECT * FROM UserEntity')
			for user in user_list:
				trophy = TrophyEntity()
				trophy.trophy_index = trophy_index
				trophy.trophy_owner = user.key.id()
				trophy.put()
		else:
			user = ndb.gql('SELECT * FROM UserEntity WHERE user_id=:1', target_user).get()
			if (user):
				trophy = TrophyEntity()
				trophy.trophy_index = trophy_index
				trophy.trophy_owner = user.key.id()
				trophy.put()
		self.response.out.write('DONE')
		
#다운로드 페이지
class DownloadPage(webapp2.RequestHandler):
	def get(self):
		html = '<html>'
		html += '<head>'
		html += '<TITLE>GG2S: Download</TITLE>'
		html += '<link rel="stylesheet" type="text/css" href="/css/download.css">'
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet" type="text/css">'
		html += '</head>'
		
		html += '<body>'
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_white.png" />'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '</div>' #head-wrapper
		html += '<div class="body-wrapper">'
		html += '<div class="download-content-wrapper">'
		html += 'GG2S PLUGIN : ' + '<a href="/download/GG2StatsGAE.gml">' + 'DOWNLOAD' + '</a>'
		html += '</div>'
		html += '<div class="download-content-wrapper">'
		html += 'ITEM SPRITE : ' + '<a href="/download/items.zip">' + 'DOWNLOAD' + '</a>'
		html += '</div>'
		html += '<div class="download-content-wrapper">'
		html += 'CHARACTER SPRITE : ' + '<a href="https://www.dropbox.com/s/tj5b5fk2wfjji2r/Characters.zip?dl=0">' + 'DOWNLOAD' + '</a>'
		html += '</div>'
		html += '<div class="download-content-wrapper">'
		html += 'WEAPON SPRITE : ' + '<a href="https://www.dropbox.com/s/lu2zs1gcnguepaj/Weapons.zip?dl=0">' + 'DOWNLOAD' + '</a>'
		html += '</div>'
		html += '</div>' #body-wrapper
		html += '</body>'
		html += '</html>'
		
		self.response.out.write(html)
		
#아이템 제작
class CraftPage(webapp2.RequestHandler):
	def get(self):
		css = """
			<link href='https://fonts.googleapis.com/css?family=Audiowide' rel='stylesheet' type='text/css'>
			<link href='https://fonts.googleapis.com/css?family=Fascinate' rel='stylesheet' type='text/css'>
			<style>
				html {width: 100%; text-align: center; background-color: #000;}
				.craft-title-logo {
				  margin: 20px 0 20px 0;
				  display: inline-block;
				  padding: 0 40px 0 40px;
				  border: 10px solid white;
				  border-radius: 20px;
				  font-family: 'Audiowide', sans-serif;
				  font-size: 60px;
				  color: white;
				  text-shadow: 0 0 10px orange,
							   0 0 20px orange,
							   0 0 30px orange,
							   0 0 40px orange;
				  box-shadow: 0 0px 20px orange,
							  0 0px 40px orange,
						inset 0 0px 20px orange,
						inset 0 0px 40px orange;
				}
				.craft-content-wrapper {display: block; width: 100%; height: 420px; position: relative; margin: auto;}
				.craft-content-menu {
				  width: 25%;
				  height: 400px;
				  margin-right: 5%;
				  display: inline-block;
				  border: 10px solid white;
				  border-radius: 5px;
				  box-shadow: 0 0px 20px orange,
							  0 0px 40px orange,
						inset 0 0px 20px orange,
						inset 0 0px 40px orange;
				  text-align: center;
				  font-size: 40px;
				  font-family: 'Fascinate', sans-serif;
				  color: royalblue;
				}
				.craft-content {
				  #visibility: hidden;
				  width: 50%;
				  height: 400px;
				  display: inline-block;
				  border: 10px solid white;
				  border-radius: 5px;
				  box-shadow: 0 0px 20px orange,
							  0 0px 40px orange,
						inset 0 0px 20px orange,
						inset 0 0px 40px orange;
				  text-align: center;
				  font-size: 40px;
				  font-family: 'Fascinate', sans-serif;
				  color: white;
				}
				.craft-menu {
				  width: 100%;
				}
				.craft-menu:hover {
				  background-color: white;
				  cursor: pointer;
				}
			</style>
		"""
		html = '<!DOCTYPE html>'
		html += '<html>'
		html += '<head><title>GG2S: Crafting</title>' + css + '</head>'
		html += '<body>'
		
		html += '<div class="craft-title-logo">'
		html += 'CRAFTING'
		html += '</div>'
		
		html += '<div class="craft-content-wrapper">'
		html += '<div class="craft-content-menu">'
		craft_menu = ['scrap', 'recycle', 'refined']
		for craft in craft_menu:
			html += '<div class="craft-menu">'
			html += craft
			html += '</div>'
		html += '</div>' #<!--craft-content-menu-->
		
		html += '<div class="craft-content">'
		html += 'CONTENT'
		html += '</div>' #<!--craft-content-->
		html += '</div>'
		
		html += '</body>'
		html += '</html>'
		self.response.out.write(html)
		
#로그 제공
class LogDispatcherPage(webapp2.RequestHandler):
	def get(self):
		LOG_PER_PAGE = 5
		user = ndb.Key(urlsafe=self.request.get('id')).get()
		cursor = ndb.Cursor(urlsafe=self.request.get('cursor', default_value=None))
		dir = self.request.get('dir');
		if not dir in ['', '0', '1']:
			return;
		if (dir == '0'):
			cursor = cursor.reversed();
			reverse_log = LogEntity.query(LogEntity.log_owner == user.google_id).order(LogEntity.log_date)
			log_list, next_cursor, prev_has_more = reverse_log.fetch_page(2*LOG_PER_PAGE, start_cursor=cursor)
			cursor = next_cursor.reversed();
		all_log = LogEntity.query(LogEntity.log_owner == user.google_id).order(-LogEntity.log_date)
		log_list, next_cursor, has_more = all_log.fetch_page(LOG_PER_PAGE, start_cursor=cursor)
		if has_more:
			next_c = next_cursor.urlsafe()
		else:
			next_c = ''
		html = '<div id="log-content">'
		for log in log_list:
			html += '<div class="activity-wrapper">'
			html += '<i class="ion ion-ios-bolt"></i> '
			html += '<span class="activity-log">' + log.log_date.strftime("%b.%d") + ' - ' + log.log_content + '</span>'
			html += '</div>'
		if (dir == '0'):
			if prev_has_more:
				html += '<div class="log-left" id="1">'
			else:
				html += '<div class="log-left" id="0">'
		html += '<div class="log-next" id="' + next_c + '"></div>'
		html += '</div>'
		self.response.out.write(html)
		
#댓글 제공
class ReplyDispatcherPage(webapp2.RequestHandler):
	def get(self):
		REPLY_PER_PAGE = 5
		user = ndb.Key(urlsafe=self.request.get('id')).get()
		cursor = ndb.Cursor(urlsafe=self.request.get('cursor', default_value=None))
		dir = self.request.get('dir');
		if not dir in ['', '0', '1']:
			return;
		if (dir == '0'):
			cursor = cursor.reversed();
			reverse_reply = ReplyEntity.query(ReplyEntity.reply_target == user.google_id).order(ReplyEntity.reply_date)
			reply_list, next_cursor, prev_has_more = reverse_reply.fetch_page(2*REPLY_PER_PAGE, start_cursor=cursor)
			cursor = next_cursor.reversed();
		all_reply = ReplyEntity.query(ReplyEntity.reply_target == user.google_id).order(-ReplyEntity.reply_date)
		reply_list, next_cursor, has_more = all_reply.fetch_page(REPLY_PER_PAGE, start_cursor=cursor)
		if has_more:
			next_c = next_cursor.urlsafe()
		else:
			next_c = ''
		current_user = users.get_current_user()
		reply_checking = False
		if user.google_id == current_user:
			reply_checking = True
			
		ndb_put_list = []
		html = '<div id="reply-content">'
		for reply in reply_list:
			reply_owner = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', reply.reply_owner).get()
			if reply.reply_owner != current_user:
				html += '<div class="reply-wrapper">'
				html += '<a href="/profile?id={}">'.format(reply_owner.user_id)
				if reply_owner.user_avatar:
					html += '<img class="reply-avatar" src="/upload?img_id=%s"></img>' %reply_owner.key.urlsafe()
				else:
					html += '<img class="reply-avatar" src="/images/gg2slogo_green.png">'
				html += '</a>'
				html += '<a href="/profile?id={}">'.format(reply_owner.user_id)
				html += '<span class="reply-id">' + reply_owner.user_id + '</span>'
				html += '</a>'
				html += '<p class="reply-content"'
				if reply_owner == user:
					html += ' id="owner"'
				html += '>'
				html += reply.reply_content + '</p>'
				html += '<span class="reply-date">' + reply.reply_date.strftime("%b.%d") + '</span>'
				if reply_checking and not reply.reply_checked:
					html += '<span class="reply-check">' + 'new' + '</span>'
					reply.reply_checked = True
					ndb_put_list.append(reply)
				html += '</div>' #reply-wrapper
			else:
				html += '<div class="reply-wrapper" id="own">'
				html += '<a href="/profile?id={}">'.format(reply_owner.user_id)
				html += '<span class="reply-id">' + reply_owner.user_id + '</span>'
				html += '</a>'
				html += '<span class="reply-date">' + reply.reply_date.strftime("%b.%d") + '</span>'
				html += '<p class="reply-content"'
				if reply_owner == user:
					html += ' id="owner"'
				html += '>'
				html += reply.reply_content + '</p>'
				html += '<a href="/profile?id={}">'.format(reply_owner.user_id)
				if reply_owner.user_avatar:
					html += '<img class="reply-avatar" src="/upload?img_id=%s"></img>' %reply_owner.key.urlsafe()
				else:
					html += '<img class="reply-avatar" src="/images/gg2slogo_green.png">'
				html += '</a>'
				if reply_checking and not reply.reply_checked:
					html += '<span class="reply-check">' + 'new' + '</span>'
					reply.reply_checked = True
					ndb_put_list.append(reply)
				html += '</div>' #reply-wrapper
		if ndb_put_list:
			ndb.put_multi(ndb_put_list)
		if (dir == '0'):
			if prev_has_more:
				html += '<div class="reply-left" id="1">'
			else:
				html += '<div class="reply-left" id="0">'
		html += '<div class="reply-next" id="' + next_c + '"></div>'
		html += '</div>'
		self.response.out.write(html)

#댓글 등록
class NewReplyPage(webapp2.RequestHandler):
	def post(self):
		user = ndb.Key(urlsafe=self.request.get('id')).get()
		current_user = users.get_current_user()
		reply_content = self.request.get('content')
		reply_content = reply_content.replace('<', '&lt')
		reply_content = reply_content.replace('>', '&gt')
		reply = ReplyEntity()
		reply.reply_content = reply_content
		reply.reply_owner = current_user
		reply.reply_target = user.google_id
		reply.put()

#게시판		
class BoardPage(webapp2.RequestHandler):
	@classmethod
	def articleTypeIcon(cls, index):
		icon_string = ''
		if index == 0:
			icon_string = 'ion-chatboxes'
		elif index == 1:
			icon_string = 'ion-cash'
		elif index == 2:
			icon_string = 'ion-android-bulb'
		elif index == 3:
			icon_string = 'ion-person'
		elif index == 4:
			icon_string = 'ion-flag'
		elif index == 5:
			icon_string = 'ion-trophy'
		return icon_string
		
		
	def get(self):
		ARTICLE_PER_PAGE = 20
		current_page = self.request.get('page')
		try:
			current_page = int(current_page)
		except:
			current_page = 1
		
		html = '<!DOCTYPE html>'
		html += '<HTML>'
		
		html += '<HEAD>'
		html += '<TITLE>GG2S: BOARD</TITLE>'
		html += '<link rel="stylesheet" type="text/css" href="/css/board.css">'
		html += "<link rel='stylesheet prefetch' href='https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css'>"
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</HEAD>'
		
		html += '<BODY>'
		
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_palegreen.png" />'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '</div>' #head-wrapper
		
		boardInfo = memcache.get('board:{}'.format(current_page))
		articleCount = memcache.get('article_count')
		if boardInfo is None:
			article_list = ndb.gql('SELECT * FROM ArticleEntity ORDER BY article_date DESC LIMIT 20 OFFSET {}'.format(ARTICLE_PER_PAGE * (current_page - 1)))
			article_list = [article for article in article_list]
			user_list = []
			for article in article_list:
				user = article.article_owner
				user_list.append(user)
			user_list = ndb.get_multi(user_list)
			boardInfo = [article_list, user_list]
			memcache.add('board:{}'.format(current_page), boardInfo, 43200) #12 hours
		else:
			article_list = boardInfo[0]
			user_list = boardInfo[1]
		if articleCount is None:
			articleCount = ndb.gql('SELECT __key__ FROM ArticleEntity').count()
			memcache.add('article_count', articleCount, 43200) #12 hours
		
		html += '<div class="body-wrapper">'
		html += '<div class="body-article-wrapper">'
		
		cnt = 0
		for article in article_list:
			html += '<div class="article-wrapper">'
			html += '<div class="article-index-wrapper">{}</div>'.format(articleCount - ARTICLE_PER_PAGE * (current_page - 1) - cnt)
			html += '<div class="article-type-wrapper"><i class="ion {}"></i></div>'.format(BoardPage.articleTypeIcon(article.article_type))
			if len(user_list[cnt].user_id) > 13:
				html += '<div class="article-author-wrapper"><a href="/profile?id={}">{}</a></div>'.format(user_list[cnt].user_id, user_list[cnt].user_id[:13] + "..")
			else:
				html += '<div class="article-author-wrapper"><a href="/profile?id={0}">{0}</a></div>'.format(user_list[cnt].user_id)
			if article.article_replycnt:
				html += '<div class="article-title-wrapper"><a href="/board/article?index={}">{}<span id="article-replycnt">({})</span></a></div>'.format(article.key.urlsafe(), article.article_title, article.article_replycnt)
			else:
				html += '<div class="article-title-wrapper"><a href="/board/article?index={}">{}</a></div>'.format(article.key.urlsafe(), article.article_title)
			html += '<div class="article-date-wrapper">{}</div>'.format(article.article_date.strftime("%b.%d"))
			html += '</div>' #article-wrapper
			cnt += 1
		
		html += '</div>' #body-article-wrapper
		
		html += '<div class="body-footer-wrapper">'
		html += '<div class="footer-menu-left">'
		for i in range(((articleCount - 1) // ARTICLE_PER_PAGE) + 1):
			if current_page == i + 1:
				html += '<div class="menu-page-wrapper"><span id="selected" href="/board?page={0}">{0}</span></div>'.format(i + 1)
			else:
				html += '<div class="menu-page-wrapper"><a href="/board?page={0}">{0}</a></div>'.format(i + 1)
		html += '</div>'
		html += '<div class="footer-menu-right">'
		html += '<div class="menu-new-wrapper"><a href="/board/new">NEW ARTICLE</a></div>'
		html += '</div>'
		html += '</div>' #body-footer-wrapper
		
		
		html += '</div>' #body-wrapper
		
		html += '</BODY>'
		html += '</HTML>'
		
		self.response.out.write(html)

#새 게시글	
class NewArticlePage(webapp2.RequestHandler):
	def get(self):
		action = self.request.get('action')
		article_modifying = False
		if action == 'modify':
			article_modifying = True
		
		if article_modifying:
			article = ndb.Key(urlsafe=self.request.get('index')).get()
			if not article:
				article_modifying = False
		
		html = '<!DOCTYPE html>'
		html += '<HTML>'
		
		html += '<HEAD>'
		html += '<TITLE>GG2S: BOARD</TITLE>'
		html += '<link rel="stylesheet" type="text/css" href="/css/board_article.css">'
		html += "<link rel='stylesheet prefetch' href='https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css'>"
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</HEAD>'
		
		html += '<BODY>'
		
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<img class="gg2s-small-logo" src="/images/gg2slogo_palegreen.png" />'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '</div>' #head-wrapper
		
		html += '<div class="body-wrapper">'
		html += '<form method ="post" enctype="multipart/form-data">'
		html += '<div class="article-title-wrapper">'
		html += '<div class="title-string-wrapper"><span id="title-string">TITLE</span></div>'
		if article_modifying:
			html += '<div class="title-input-wrapper"><input type="text" name="article-title" size="80" maxlength="80" value="{}" /></div>'.format(article.article_title)
		else:
			html += '<div class="title-input-wrapper"><input type="text" name="article-title" size="80" maxlength="80" /></div>'
		html += '</div>' #article-title-wrapper
		
		html += '<div class="article-content-wrapper">'
		if article_modifying:
			html += '<textarea rows="20" cols="110" name="article-content" resize="none" wrap="hard">{}</textarea>'.format(article.article_content)
		else:
			html += '<textarea rows="20" cols="110" name="article-content" resize="none" wrap="hard"></textarea>'
		html += '</div>' #article-content-wrapper
		
		def checkArticleType(article, index):
			html = ''
			if article.article_type == index:
				html += '<input type="radio" name="article-type" value="{}" checked />'.format(index)
			else:
				html += '<input type="radio" name="article-type" value="{}" />'.format(index)
			return html
			
		if article_modifying:
			html += '<input type="hidden" name="action" value="modify" />'
			html += '<input type="hidden" name="index" value="{}" />'.format(self.request.get('index'))
		html += '<div class="article-menu-wrapper">'
		html += '<div class="menu-type-wrapper">'
		html += '<div class="type chat-wrapper">'
		html += '<i class="ion ion-chatboxes"></i>'
		if article_modifying:
			html += checkArticleType(article, 0)
		else:
			html += '<input type="radio" name="article-type" value="0" checked />'
		html += '</div>'
		html += '<div class="type trade-wrapper">'
		html += '<i class="ion ion-cash"></i>'
		if article_modifying:
			html += checkArticleType(article, 1)
		else:
			html += '<input type="radio" name="article-type" value="1" />'
		html += '</div>'
		html += '<div class="type suggestion-wrapper">'
		html += '<i class="ion ion-android-bulb"></i>'
		if article_modifying:
			html += checkArticleType(article, 2)
		else:
			html += '<input type="radio" name="article-type" value="2" />'
		html += '</div>'
		html += '<div class="type person-wrapper">'
		html += '<i class="ion ion-person"></i>'
		if article_modifying:
			html += checkArticleType(article, 3)
		else:
			html += '<input type="radio" name="article-type" value="3" />'
		html += '</div>'
		html += '<div class="type flag-wrapper">'
		html += '<i class="ion ion-flag"></i>'
		if article_modifying:
			html += checkArticleType(article, 4)
		else:
			html += '<input type="radio" name="article-type" value="4" />'
		html += '</div>'
		html += '<div class="type trophy-wrapper">'
		html += '<i class="ion ion-trophy"></i>'
		if article_modifying:
			html += checkArticleType(article, 5)
		else:
			html += '<input type="radio" name="article-type" value="5" />'
		html += '</div>'
		html += '</div>' #menu-type-wrapper		
		
		html += '<div class="menu-submit-wrapper"><input class="menu-button" type="submit" value="SUBMIT" /></div>'
		html += '</div>' #article-menu-wrapper
		
		html += '</form>'
		html += '</div>' #body-wrapper
		
		html += '</BODY>'
		html += '</HTML>'
		
		self.response.out.write(html)
	
	def post(self):
		current_user = users.get_current_user()
		user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
		user_have_id = False
		if user:
			user_have_id = True

		if user_have_id:
			action = self.request.get('action')
			article_modifying = False
			if action == 'modify':
				article_modifying = True
			
			if article_modifying:
				article = ndb.Key(urlsafe=self.request.get('index')).get()
				if not article:
					self.redirect('/board')
				else:
					if not current_user != article.article_owner:
						self.redirect('/board')
			article_title = self.request.get('article-title')
			article_title = article_title.replace('<', '&lt')
			article_title = article_title.replace('>', '&gt')
			
			article_content = self.request.get('article-content')
			article_content = article_content.replace('<', '&lt')
			article_content = article_content.replace('>', '&gt')
			article_type = int(self.request.get('article-type'))
			try:
				article_title.decode('ascii')
				if not article_title:
					article_title = 'BLANK'
				article_content.decode('ascii')
				if not article_modifying:
					new_article = ArticleEntity()
					new_article.article_title = article_title
					new_article.article_content = article_content
					new_article.article_type = article_type
					new_article.article_owner = ndb.Key(UserEntity, user.key.id())
					new_article.put()
					
					articleCount = memcache.get('article_count')
					if articleCount is None:
						articleCount = ndb.gql('SELECT __key__ FROM ArticleEntity').count()
					for i in range((articleCount - 1)//20 + 1):
						memcache.delete('board:{}'.format(i + 1))
					memcache.delete('article_count')
					
					user_address = "WN <saiyu915@naver.com>"
					sender_address = "GG2S Support <noreply@gg2statsapp.appspotmail.com>"
					subject = user.user_id + " has made an article."
					body = user.user_id + " has made an article:\n\n"
					body += article_title + "\n\n"
					body += article_content + "\n"
					body += "https://gg2statsapp.appspot.com/board/article?index={}".format(new_article.key.urlsafe())
					mail.send_mail(sender_address, user_address, subject, body)
				
					self.redirect('/board/article?index={}'.format(new_article.key.urlsafe()))
				else:
					article.article_title = article_title
					article.article_content = article_content
					article.article_type = article_type
					article.put()
					
					self.redirect('/board/article?index={}'.format(article.key.urlsafe()))
			except:
				html = '<script type="text/javascript">'
				html += 'alert("{}");'.format("You should use only English letters!")
				if not article_modifying:
					html += 'location.href="/board/new";'
				else:
					html += 'location.href="/board/article?index={}";'.format(article.key.urlsafe())
				html += '</script>'
				self.response.out.write(html)
		else:
			self.redirect('/')

#게시글 보기			
class ArticlePage(webapp2.RequestHandler):
	def get(self):
		article = ndb.Key(urlsafe=self.request.get('index')).get()
		if article:
			user = article.article_owner.get()
			html = '<!DOCTYPE html>'
			html += '<HTML>'
			
			html += '<HEAD>'
			html += '<TITLE>GG2S: BOARD</TITLE>'
			html += '<script type="text/javascript" src="/js/article.js"></script>'
			html += '<script type="text/javascript" src="/js/jquery.js"></script>'
			html += '<link rel="stylesheet" type="text/css" href="/css/board_article.css">'
			html += "<link rel='stylesheet prefetch' href='https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css'>"
			html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
			html += '</HEAD>'
			
			html += '<BODY>'
			
			html += '<div class="head-wrapper">'
			html += '<div class="head-gg2s-text">'
			html += '<img class="gg2s-small-logo" src="/images/gg2slogo_palegreen.png" />'
			html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
			html += '</div>' #head-gg2s-text
			html += '</div>' #head-wrapper
			
			html += '<div class="body-wrapper">'
			
			#현재 사용자가 글 작성자와 동일한지 체크하고, 동일시 상단 메뉴를 추가
			current_user = users.get_current_user()
			if user.google_id == current_user or users.is_current_user_admin():
				html += '<div class="body-headermenu-wrapper">'
				html += '<form method="POST" id="delete-form">'
				html += '<input type="hidden" name="index" value="{}" />'.format(self.request.get('index'))
				html += '<div class="menu-wrapper modify-wrapper"><a href="/board/new?action=modify&index={}"><input class="menu-button" id="button-modify" type="button" value="MODIFY" /></a></div>'.format(article.key.urlsafe())
				html += '<div class="menu-wrapper delete-wrapper"><input class="menu-button" id="button-delete" type="button" value="DELETE" onClick="deletePrompt();" /></div>'
				html += '</form>'
				html += '</div>' #body-headermenu-wrapper
			
			html += '<div class="article-title-wrapper">'
			html += '<div class="title-string-wrapper"><span id="title-string">TITLE</span></div>'
			html += '<div class="title-input-wrapper"><input type="text" id="article-title" size="80" maxlength="80" value="{}" disabled /></div>'.format(article.article_title)
			html += '</div>' #article-title-wrapper
			html += '<div class="title-author-wrapper"><a href="/profile?id={0}">{0}</a></div>'.format(user.user_id)
			
			html += '<div class="article-content-wrapper">'
			html += '<textarea rows="20" cols="110" id="article-content" resize="none" wrap="hard" disabled>{}</textarea>'.format(article.article_content)
			html += '</div>' #article-content-wrapper
			
			html += '<div class="article-reply-wrapper">'
			
			replyInfo = memcache.get('article:{}'.format(article.key.id()))
			if replyInfo is None:
				reply_list = ndb.gql('SELECT * FROM ArticleReplyEntity WHERE reply_target=:1 ORDER BY reply_date ASC', ndb.Key(ArticleEntity, article.key.id()))
				reply_list = [[reply] for reply in reply_list]
				for reply_innerlist in reply_list:
					reply_sublist = ndb.gql('SELECT * FROM ArticleReplyEntity WHERE reply_target=:1 ORDER BY reply_date ASC', ndb.Key(ArticleReplyEntity, reply_innerlist[0].key.id()))
					for subreply in reply_sublist:
						reply_innerlist.append(subreply)
				user_list = []
				for reply_innerlist	in reply_list:
					for reply in reply_innerlist:
						user_list.append(reply.reply_owner)
				user_list = ndb.get_multi(user_list)
				replyInfo = [reply_list, user_list]
				memcache.add('article:{}'.format(article.key.urlsafe()), replyInfo, 43200) #12 hours
			else:
				reply_list = replyInfo[0]
				user_list = replyInfo[1]
			
			total_reply_counter = 0
			for reply_innerlist in reply_list:
				for subreply in reply_innerlist:
					total_reply_counter += 1

			index = 0
			for reply_innerlist in reply_list:
				html += '<div class="reply-positioner">'
				html += '<div class="reply-wrapper">'
				cnt = 0
				for subreply in reply_innerlist:
					if not cnt:
						html += '<div class="reply-main-wrapper">'
					else:
						html += '<div class="reply-sub-wrapper">'
					reply_user = user_list[index]
					html += '<div class="reply-author-wrapper">'
					if not cnt:
						html += '<div class="author-string"><a href="/profile?id={}">{}</a></div>'.format(reply_user.user_id, reply_user.user_id.upper())
					else:
						html += '<div class="author-string" id="author-sub"><a href="/profile?id={}">{}</a></div>'.format(reply_user.user_id, reply_user.user_id.upper())
					html += '<div class="author-subreply-wrapper"><i class="ion ion-ios-redo" onClick="makeReplyForm({}, \'{}\', \'{}\', \'{}\', {});"></i></div>'.format(index, article.key.urlsafe(), reply_innerlist[0].key.urlsafe(), reply_user.key.urlsafe(), total_reply_counter)
					html += '</div>' #reply-author-wrapper
					html += '<div class="reply-content-wrapper">'
					if not cnt:
						html += '<div class="reply-content">'
					else:
						html += '<div class="reply-content" id="subreply">'
					html += subreply.reply_content
					if reply_user.google_id == current_user or users.is_current_user_admin():
						html += '<div class="reply-deletemenu-wrapper">'
						html += '<form method="POST" action="/deletearticlereply" id="reply-delete-form-{}">'.format(index)
						html += '<input type="hidden" name="reply" value="{}">'.format(subreply.key.urlsafe())
						html += '<input type="hidden" name="article" value="{}">'.format(article.key.urlsafe())
						html += '<i class="ion ion-close-circled" onclick="deleteReplyPrompt({})"></i>'.format(index)
						html += '</form>'
						html += '</div>'
					html += '</div>' #reply-content
					html += '</div>' #reply-content-wrapper
					html += '</div>' #reply-main or sub-wrapper
					
					html += '<div class="reply-subnew-wrapper" id="reply-new-{}">'.format(index)
					html += '</div>' #reply-subnew-wrapper
					cnt += 1
					index += 1
				html += '</div>' #reply-wrapper
				html += '</div>' #reply-positioner
			html += '<form method="POST" action="/newboardreply">'
			html += '<input type="hidden" name="article" value="{}" />'.format(article.key.urlsafe())
			html += '<input type="hidden" name="target" value="{}" />'.format(article.key.urlsafe())
			html += '<input type="hidden" name="type" value="new" />'
			html += '<div class="reply-new-wrapper">'
			html += '<div class="reply-newform-wrapper">'
			html += '<div class="reply-newtext-wrapper">'
			html += '<textarea id="reply-newreply-content" name="reply-newreply-content" placeholder="Leave a comment..." resize="none" wrap="hard"></textarea>'
			html += '</div>' #reply-newtext-wrapper
			html += '<div class="reply-newsubmit-wrapper">'
			html += '<input type="submit" id="reply-newreply-submit" value="SUBMIT" />'
			html += '</div>' #reply-newsubmit-wrapper
			html += '</div>' #reply-newform-wrapper
			html += '</div>' #reply-new-wrapper
			html += '</form>'

			html += '</div>' #article-reply-wrapper
			
			html += '<div class="body-footermenu-wrapper">'
			html += '<div class="menu-wrapper list-wrapper"><a href="/board"><input class="menu-button" type="button" value="LIST" /></a></div>'
			html += '</div>' #body-footermenu-wrapper
			html += '</div>' #body-wrapper
			
			html += '<script>hideDeleteForm();</script>'
			
			html += '</BODY>'
			html += '</HTML>'
			
			self.response.out.write(html)
		else:
			self.redirect('/board')
	
	#게시글 삭제
	def post(self):
		article = ndb.Key(urlsafe=self.request.get('index')).get()
		user = article.article_owner.get()
		current_user = users.get_current_user()
		if article:
			if user.google_id == current_user or users.is_current_user_admin():
				#삭제
				ndb.Key(ArticleEntity, article.key.id()).delete()
				articleCount = memcache.get('article_count')
				if articleCount is None:
					articleCount = ndb.gql('SELECT __key__ FROM ArticleEntity').count()
				for i in range((articleCount - 1)//20 + 1):
					memcache.delete('board:{}'.format(i + 1))
				memcache.delete('article_count')
		self.redirect('/board')
				
#게시글 댓글 생성
class NewBoardReplyPage(webapp2.RequestHandler):
	def post(self):
		current_user = users.get_current_user()
		user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
		article_urlsafe = self.request.get('article')
		article = ndb.Key(urlsafe=article_urlsafe).get()
		newreply_target = ndb.Key(urlsafe=self.request.get('target'))
		newreply_content = self.request.get('reply-newreply-content')
		newreply_content = newreply_content.replace('<', '&lt')
		newreply_content = newreply_content.replace('>', '&gt')

		try:
			newreply_content.decode('ascii')
			newreply = ArticleReplyEntity()
			if str(newreply_target.kind()) == 'ArticleReplyEntity':
				newreply_content = '<div class="reply-target-wrapper">{}</div>{}'.format(ndb.Key(urlsafe=self.request.get('targetuser')).get().user_id, newreply_content)
			newreply_content = newreply_content.replace('\n', '<br />')
			newreply.reply_content = newreply_content
			newreply.reply_target = newreply_target
			newreply.reply_owner = ndb.Key(UserEntity, user.key.id())
			newreply.put()
			
			article.article_replycnt += 1
			article.put()
			
			memcache.delete('article:{}'.format(article_urlsafe))
			
			self.redirect('/board/article?index={}'.format(article_urlsafe))
		
		except:
			html = '<script type="text/javascript">'
			html += 'alert("{}");'.format("You should use only ascii letters!")
			html += 'location.href="/board/article?index={}";'.format(article_urlsafe)
			html += '</script>'
			self.response.out.write(html)
			
class DeleteArticleReplyPage(webapp2.RequestHandler):
	def post(self):
		current_user = users.get_current_user()
		user = ndb.gql('SELECT * FROM UserEntity WHERE google_id=:1', current_user).get()
		if not user:
			self.redirect('/board')
		else:
			article_urlsafe = self.request.get('article')
			article = ndb.Key(urlsafe=article_urlsafe).get()
			reply_urlsafe = self.request.get('reply')
			reply = ndb.Key(urlsafe=reply_urlsafe).get()
			
			if reply.reply_owner == user.key or users.is_current_user_admin():
				#check whether there was a subreply to this reply
				subreply_list = ndb.gql('SELECT __key__ FROM ArticleReplyEntity WHERE reply_target=:1', reply.key)
				if subreply_list.count():
					ndb_put_list = []
					reply_save = DeletedArticleReplyEntity()
					reply_save.reply_owner = reply.reply_owner
					reply_save.reply_content = reply.reply_content
					reply_save.reply_target = reply.reply_target
					ndb_put_list.append(reply_save)
					
					article.article_replycnt -= 1
					ndb_put_list.append(article)
					
					reply.reply_content = '<div id="reply-deleted"></div>'
					ndb_put_list.append(reply)
					ndb.put_multi(ndb_put_list)
				else:
					reply_save = DeletedArticleReplyEntity()
					reply_save.reply_owner = reply.reply_owner
					reply_save.reply_content = reply.reply_content
					reply_save.reply_target = reply.reply_target
					reply_save.put()
					
					article.article_replycnt -= 1
					article.put()
					
					ndb.Key(ArticleReplyEntity, reply.key.id()).delete()
				self.redirect('/board/article?index={}'.format(article_urlsafe))
			else:
				html = '<script type="text/javascript">'
				html += 'alert("{}");'.format("An error occured while handling your request!")
				html += 'location.href="/board/article?index={}";'.format(article_urlsafe)
				html += '</script>'
				self.response.out.write(html)

class AwardPage(webapp2.RequestHandler):
	def get(self):
		point = [[49542,ndb.Key(UserEntity,5165497909772288)],[28746,ndb.Key(UserEntity,4658379846844416)],[28228,ndb.Key(UserEntity,5649050225344512)],[24783,ndb.Key(UserEntity,5772979426295808)],[22144,ndb.Key(UserEntity,4764076106317824)]]
		playtime = [[23232140,ndb.Key(UserEntity,5131370334519296)],[22087724,ndb.Key(UserEntity,5165497909772288)],[17555917,ndb.Key(UserEntity,6553068162252800)],[12738893,ndb.Key(UserEntity,4664447964545024)],[12323495,ndb.Key(UserEntity,4658379846844416)]]
		playcount = [[2086,ndb.Key(UserEntity,5165497909772288)],[1659,ndb.Key(UserEntity,4658379846844416)],[1520,ndb.Key(UserEntity,5131370334519296)],[1316,ndb.Key(UserEntity,6553068162252800)],[1213,ndb.Key(UserEntity,4664447964545024)]]
		heal = [[3593021.25,1582,ndb.Key(UserEntity,4658379846844416)],[1032545.43,465,ndb.Key(UserEntity,6553068162252800)],[961412.05,392,ndb.Key(UserEntity,5131370334519296)],[681380.3,355,ndb.Key(UserEntity,5656313283477504)],[535113.89,255,ndb.Key(UserEntity,4954392348327936)]]
		stab = [[679,2022,ndb.Key(UserEntity,5650665401483264)],[629,1542,ndb.Key(UserEntity,6014343971864576)],[563,1059,ndb.Key(UserEntity,5374761936879616)],[444,1033,ndb.Key(UserEntity,6327160700665856)],[405,1410,ndb.Key(UserEntity,6553068162252800)]]
		wl = [[90.00,999,111,ndb.Key(UserEntity,5374761936879616)],[88.67,180,23,ndb.Key(UserEntity,4822111315034112)],[77.67,692,199,ndb.Key(UserEntity,5649050225344512)],[76.71,761,231,ndb.Key(UserEntity,4764076106317824)],[75.83,182,58,ndb.Key(UserEntity,6532882352832512)]]
		kda = []
		kda.append([[5.06,11196,2918,3561,ndb.Key(UserEntity,5649050225344512)],[4.01,928,255,95,ndb.Key(UserEntity,5634472569470976)],[3.94,9760,3304,3244,ndb.Key(UserEntity,5772979426295808)],[3.70,2556,1158,1729,ndb.Key(UserEntity,5656313283477504)],[3.64,7187,2803,3015,ndb.Key(UserEntity,4764076106317824)]])
		kda.append([[3.04,405,164,93,ndb.Key(UserEntity,5649050225344512)],[2.87,469,216,151,ndb.Key(UserEntity,5656313283477504)],[2.67,7009,3312,1837,ndb.Key(UserEntity,5165497909772288)],[2.65,867,428,267,ndb.Key(UserEntity,5772979426295808)],[2.57,830,417,241,ndb.Key(UserEntity,4764076106317824)]])
		kda.append([[4.82,1533,441,592,ndb.Key(UserEntity,5649050225344512)],[4.71,880,262,353,ndb.Key(UserEntity,5656313283477504)],[4.02,1533,553,691,ndb.Key(UserEntity,4764076106317824)],[3.61,1780,699,745,ndb.Key(UserEntity,5772979426295808)],[3.59,3495,1296,1152,ndb.Key(UserEntity,5165497909772288)]])
		kda.append([[5.10,4286,1091,1282,ndb.Key(UserEntity,5649050225344512)],[5.06,4508,1166,1390,ndb.Key(UserEntity,5772979426295808)],[3.83,4519,1484,1167,ndb.Key(UserEntity,5165497909772288)],[3.83,384,117,64,ndb.Key(UserEntity,5656313283477504)],[3.73,1100,400,392,ndb.Key(UserEntity,4764076106317824)]])
		kda.append([[5.67,2218,520,733,ndb.Key(UserEntity,5649050225344512)],[4.93,1027,292,412,ndb.Key(UserEntity,4764076106317824)],[4.71,1530,417,435,ndb.Key(UserEntity,5165497909772288)],[4.30,446,149,194,ndb.Key(UserEntity,5725273211273216)],[3.92,442,146,130,ndb.Key(UserEntity,5650665401483264)]])
		kda.append([[3.37,1562,599,455,ndb.Key(UserEntity,5772979426295808)],[2.63,1002,481,263,ndb.Key(UserEntity,5165497909772288)],[2.50,214,128,106,ndb.Key(UserEntity,4764076106317824)],[2.06,405,261,132,ndb.Key(UserEntity,5650665401483264)],[1.34,234,230,74,ndb.Key(UserEntity,6553068162252800)]])
		kda.append([[4.24,100,242,927,ndb.Key(UserEntity,5656313283477504)],[4.03,100,109,339,ndb.Key(UserEntity,4764076106317824)],[2.79,1056,2271,5269,ndb.Key(UserEntity,4658379846844416)],[2.44,522,799,1427,ndb.Key(UserEntity,5131370334519296)],[2.20,358,858,1531,ndb.Key(UserEntity,6553068162252800)]])
		kda.append([[4.66,401,116,140,ndb.Key(UserEntity,5649050225344512)],[4.36,332,113,161,ndb.Key(UserEntity,4822111315034112)],[4.29,1382,458,583,ndb.Key(UserEntity,4764076106317824)],[3.32,633,259,228,ndb.Key(UserEntity,5165497909772288)],[3.09,337,149,123,ndb.Key(UserEntity,5772979426295808)]])
		kda.append([[4.49,605,175,180,ndb.Key(UserEntity,5649050225344512)],[2.47,608,318,176,ndb.Key(UserEntity,5165497909772288)],[2.40,379,200,101,ndb.Key(UserEntity,4822111315034112)],[2.08,381,215,66,ndb.Key(UserEntity,4764076106317824)],[2.07,1542,902,324,ndb.Key(UserEntity,6014343971864576)]])
		kda.append([[6.32,1382,275,356,ndb.Key(UserEntity,5649050225344512)],[3.26,498,192,128,ndb.Key(UserEntity,4764076106317824)],[2.87,2262,966,511,ndb.Key(UserEntity,5165497909772288)],[2.63,390,189,107,ndb.Key(UserEntity,4785510274826240)],[1.26,380,389,109,ndb.Key(UserEntity,5505326358986752)]])
		kda.append([[4.59,122,39,57,ndb.Key(UserEntity,4764076106317824)],[4.42,205,60,60,ndb.Key(UserEntity,5649050225344512)],[2.10,247,154,76,ndb.Key(UserEntity,5650665401483264)],[1.95,184,130,70,ndb.Key(UserEntity,6014343971864576)],[1.73,131,108,56,ndb.Key(UserEntity,6553068162252800)]])

		user_list = memcache.get('award_user_list')
		if user_list is None:
			award_list = [point, playtime, playcount, heal, stab, wl]
			user_list = []
			for award in award_list:
				for i in award:
					user_list.append(i[-1])
			for i in kda:
				for j in i:
					user_list.append(j[-1])
			user_list = ndb.get_multi(user_list)
			memcache.add('award_user_list', user_list, 43200) #12 hours
			
		for i in range(len(user_list)):
			try:
				user_list[i].user_avatar
			except:
				user_list[i] = UserEntity()
				user_list[i].user_id = ""
	
		html = '<!DOCTYPE HTML>'
		html += '<HTML>'
		html += '<HEAD>'
		html += '<TITLE>GG2S</TITLE>'
		html += '<link rel="stylesheet" type="text/css" href="/css/award.css">'
		html += "<link rel='stylesheet prefetch' href='https://code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css'>"
		html += '<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">'
		html += '</HEAD>'
		
		html += '<BODY>'
		html += '<div class="head-wrapper">'
		html += '<div class="head-gg2s-text">'
		html += '<a href="/"><span>GANG GARRISON 2 STATS</span></a>'
		html += '</div>' #head-gg2s-text
		html += '-SEASON {} AWARDS-'.format(GG2S_CURRENT_SEASON - 1)
		html += '</div>' #head-wrapper
		
		cnt = 0
		
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST POINT'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span> POINTS</span>'.format(point[i][0])
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}</span> POINTS</span>'.format(point[i][0])
			html += '</div>'
			cnt += 1
		html += '</div>'
			
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST PLAYTIME'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span></span>'.format(makePlaytimeTemplate(playtime[i][0]).upper())
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}</span></span>'.format(makePlaytimeTemplate(playtime[i][0]).upper())
			html += '</div>'
			cnt += 1
		html += '</div>'
		
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST PLAYCOUNT'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span> ROUNDS</span>'.format(playcount[i][0])
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}</span> ROUNDS</span>'.format(playcount[i][0])
			html += '</div>'
			cnt += 1
		html += '</div>'
		
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST HEALER'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span> HEALS</span>'.format(heal[i][0])
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span> INVULNS</span>'.format(heal[i][1])
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}</span> HEALS</span>'.format(heal[i][0])
				html += '<span class="award-spec"><span id="spec-detail">{}</span> INVULNS</span>'.format(heal[i][1])
			html += '</div>'
			cnt += 1
		html += '</div>'
		
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST BACKSTABBER'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span> STABS</span>'.format(stab[i][0])
				html += '<span class="award-spec" id="first">OUT OF {} KILLS</span>'.format(stab[i][1])
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}</span> STABS</span>'.format(stab[i][0])
				html += '<span class="award-spec">OUT OF {} KILLS</span>'.format(stab[i][1])
			html += '</div>'
			cnt += 1
		html += '</div>'
		
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST WINRATE'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}%</span></span>'.format(wl[i][0])
				html += '<span class="award-spec" id="first">({}/{})</span>'.format(wl[i][1], wl[i][2])
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}%</span></span>'.format(wl[i][0])
				html += '<span class="award-spec">({}/{})</span>'.format(wl[i][1], wl[i][2])
			html += '</div>'
			cnt += 1
		html += '</div>'
		
		html += '<div class="award-wrapper">'
		html += '<div class="award-name">'
		html += 'BEST KDA'
		html += '</div>'
		for i in range(5):
			if i == 0:
				html += '<div class="award-winner-wrapper" id="first">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span></span>'.format(kda[0][i][0])
				html += '<span class="award-spec" id="first">({}/{}/{})</span>'.format(kda[0][i][1], kda[0][i][2], kda[0][i][3])
			else:
				html += '<div class="award-winner-wrapper">'
				if user_list[cnt].user_avatar:
					html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
				else:
					html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
				html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
				html += '<span class="award-spec"><span id="spec-detail">{}</span></span>'.format(kda[0][i][0])
				html += '<span class="award-spec">({}/{}/{})</span>'.format(kda[0][i][1], kda[0][i][2], kda[0][i][3])
			html += '</div>'
			cnt += 1
		html += '</div>'
		
		for j in range(1, 11):
			html += '<div class="award-wrapper">'
			html += '<div class="award-name">'
			html += 'BEST {} KDA'.format(_CLASSES[j - 1].upper())
			html += '</div>'
			for i in range(5):
				if i == 0:
					html += '<div class="award-winner-wrapper" id="first">'
					if user_list[cnt].user_avatar:
						html += '<img class="winner-avatar" id="first" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
					else:
						html += '<img class="winner-avatar" id="first" src="/images/gg2slogo_palegreen.png" />'
					html += '<span class="award-id" id="first">{}</span>'.format(user_list[cnt].user_id.upper())
					html += '<span class="award-spec" id="first"><span id="spec-detail">{}</span></span>'.format(kda[j][i][0])
					html += '<span class="award-spec" id="first">({}/{}/{})</span>'.format(kda[j][i][1], kda[j][i][2], kda[j][i][3])
				else:
					html += '<div class="award-winner-wrapper">'
					if user_list[cnt].user_avatar:
						html += '<img class="winner-avatar" src="/upload?img_id={}" />'.format(user_list[cnt].key.urlsafe())
					else:
						html += '<img class="winner-avatar" src="/images/gg2slogo_palegreen.png" />'
					html += '<span class="award-id">{}</span>'.format(user_list[cnt].user_id.upper())
					html += '<span class="award-spec"><span id="spec-detail">{}</span></span>'.format(kda[j][i][0])
					html += '<span class="award-spec">({}/{}/{})</span>'.format(kda[j][i][1], kda[j][i][2], kda[j][i][3])
				html += '</div>'
				cnt += 1
			html += '</div>'
		
		html += '</HTML>'
		self.response.out.write(html)
		
class BanPage(webapp2.RequestHandler):
	def get(self):
		current_user = users.get_current_user()
		html = '<HTML>'
		html += '<body>'
		html += '<form method="POST">'
		html += 'INPUT ID TO BAN:'
		html += '<input type="text" name="user_id" />'
		html += str(current_user)
		html += '<input type="submit" />'
		html += '</form>'
		html += '</body>'
		html += '</HTML>'
		self.response.out.write(html)
		
	def post(self):
		ndb_delete_list = []
		user_id = self.request.get("user_id")
		user = ndb.gql("SELECT * FROM UserEntity WHERE user_id=:1", user_id).get()
		user_key = user.key.id()
		user_google = user.google_id
		
		ndb_delete_list.append(ndb.Key(UserEntity, user_key))
		ndb_delete_list.append(ndb.Key(TodayEntity, user_key))
		ndb_delete_list.append(ndb.Key(UserStatEntity, user_key))
		ndb_delete_list.append(ndb.Key(ClassEntity, user_key))
		ndb_delete_list.append(ndb.Key(LoadoutEntity, user_key))
		season_list = ndb.gql("SELECT * FROM SeasonStatEntity WHERE season_owner=:1", user_key)
		for season in season_list:
			ndb_delete_list.append(ndb.Key(SeasonStatEntity, season.key.id()))
		quest_list = ndb.gql("SELECT * FROM DailyquestEntity WHERE quest_owner=:1", user_key)
		for quest in quest_list:
			ndb_delete_list.append(ndb.Key(DailyquestEntity, quest.key.id()))
		match_list = ndb.gql("SELECT * FROM MatchEntity WHERE match_owner=:1", user_key)
		for match in match_list:
			ndb_delete_list.append(ndb.Key(MatchEntity, match.key.id()))
		backpack_list = ndb.gql("SELECT * FROM BackpackEntity WHERE item_owner=:1", user_key)
		for backpack in backpack_list:
			ndb_delete_list.append(ndb.Key(BackpackEntity, backpack.key.id()))
		trophy_list = ndb.gql("SELECT * FROM TrophyEntity WHERE trophy_owner=:1", user_key)
		for trophy in trophy_list:
			ndb_delete_list.append(ndb.Key(TrophyEntity, trophy.key.id()))
		trade_list = ndb.gql("SELECT * FROM TradeEntity WHERE trade_owner=:1", user_google)
		for trade in trade_list:
			ndb_delete_list.append(ndb.Key(TradeEntity, trade.key.id()))
		offer_list = ndb.gql("SELECT * FROM OfferEntity WHERE offer_owner=:1", user_google)
		for offer in offer_list:
			ndb_delete_list.append(ndb.Key(OfferEntity, offer.key.id()))
		log_list = ndb.gql("SELECT * FROM LogEntity WHERE log_owner=:1", user_google)
		for log in log_list:
			ndb_delete_list.append(ndb.Key(LogEntity, log.key.id()))
		reply_list = ndb.gql("SELECT * FROM ReplyEntity WHERE reply_owner=:1", user_google)
		for reply in reply_list:
			ndb_delete_list.append(ndb.Key(ReplyEntity, reply.key.id()))
		articlereply_list = ndb.gql("SELECT * FROM ArticleReplyEntity WHERE reply_owner=:1", user.key)
		for articlereply in articlereply_list:
			ndb_delete_list.append(ndb.Key(ArticleReplyEntity, articlereply.key.id()))
		ndb.delete_multi(ndb_delete_list)
		
		
		html = '<html>'
		html += 'SELECTED ID: '
		html += self.request.get("user_id")
		html += '<br>'
		html += 'DONE'
		html += '</html>'
		self.response.out.write(html)
				
app = webapp2.WSGIApplication([
	('/', MainPage2),
	('/main', MainPage2),
	('/test', TestPage),
	('/login', LoginPage),
	('/register', RegisterPage),
	('/getstat', GetStatPage),
	('/statupdate', StatUpdatePage),
	('/testupdate', TestUpdatePage),
	('/pointview', PointViewPage),
	('/search', SearchPage),
	('/searchresult', SearchResultPage),
	('/rank', RankPage),
	('/rank2', RankPage2),
	('/profile', ProfilePage2),
	('/overall', ProfileOverall),
	('/match', ProfileMatch),
	('/stat', ProfileStat),
	('/profilebackpack', ProfileBackpack),
	('/profileloadout', ProfileLoadout),
	('/myprofile', MyProfilePage),
	('/profilesetting', ProfileSettingPage),
	('/backpack', BackpackPage),
	('/loadout', LoadoutPage),
	('/changeloadout', LoadoutChangePage),
	('/item', ItemPage),
	('/iteminfo', ItemInfoPage),
	('/buy', ItemBuyPage),
	('/sell', ItemSellPage),
	('/market', MarketPage),
	('/trade', TradePage),
	('/offer', OfferPage),
	('/mytrade', MyTradePage),
	('/maketrade', MakeTradePage),
	('/makeoffer', MakeOfferPage),
	('/offerbackpack', OfferBackpackPage),
	('/removetrade', RemoveTradePage),
	('/removeoffer', RemoveOfferPage),
	('/itemformat', ItemFormatPage),
	('/itemupload', ItemUploadPage),
	('/tasks/todayentity', ResetTodayEntityPage),
	('/tasks/makequest', MakeDailyQuestPage),
	('/tasks/deletetrade', DeleteTradePage),
	('/upload', ImagePage),
	('/avatar', AvatarPage),
	('/getloadout', GetLoadoutPage),
	('/gotpresent', GetItemPage),
	('/givetrophy', GiveTrophyPage),
	('/gacha', GachaPage),
	('/gallery', GalleryPage),
	('/down', DownloadPage),
	('/please', PleasePage),
	('/please2', PleasePage2),
	('/please3', PleasePage3),
	('/updatestrange', UpdateStrangePage),
	('/craft', CraftPage),
	('/log', LogDispatcherPage),
	('/reply', ReplyDispatcherPage),
	('/newreply', NewReplyPage),
	('/board', BoardPage),
	('/board/new', NewArticlePage),
	('/board/article', ArticlePage),
	('/newboardreply', NewBoardReplyPage),
	('/deletearticlereply', DeleteArticleReplyPage),
	('/award', AwardPage),
	('/ban', BanPage),
], debug = True)