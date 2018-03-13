/*
 *	GG2Stats with GAE support
 *	Author: WoodNeck
 *	If you having any problems, please contact me via steam:
 *	http://steamcommunity.com/id/woodneck/
 *	or E-mail:
 *	saiyu915@naver.com
 */

global.unique_key = '';
global.gg2stats_version = 'v1.5.0';
global.gg2stats_basehttp = 'https://gg2statsapp.appspot.com';


//Auto Log-in
ini_open('gg2.ini');
global.unique_key = ini_read_string('GG2Stats', 'KEY', '');
ini_close();

if(global.unique_key != '') //if Auto Log-in info exists in .ini
{
	//Check if the key's correct
	http = global.gg2stats_basehttp + '/login';
	login_buffer = buffer_create();
	write_string(login_buffer, 'user_key=' + global.unique_key);
	write_string(login_buffer, '&plugin_version=' + global.gg2stats_version);
	httpHandler = http_new_post(http, login_buffer, 'application/x-www-form-urlencoded');
	while(!http_step(httpHandler)) 
	{
		sleep(floor(1000/30));
		io_handle();
	} 
	// Errored
	if (http_status_code(httpHandler) != 200)
	{
		global.unique_key = ''
		show_message('Downloading update failed!#' + string(http_status_code(httpHandler)) + ' ' + http_reason_phrase(httpHandler));
		room_goto_fix(Menu);
	}
	body_str = read_string(http_response_body(httpHandler), http_response_body_size(httpHandler));
	http_destroy(httpHandler);
	if (body_str == 'Need to Update!') //IF LOGIN SUCCESS, WEBAPP RETURNS EMPTY STRING
	{
		http = global.gg2stats_basehttp + '/download/GG2StatsGAE.gml';
		httpHandler = http_new_get(http);
		while(!http_step(httpHandler)) 
		{
			sleep(floor(1000/30));
			io_handle();
		}
		// Errored
		if (http_status_code(httpHandler) != 200)
		{
			global.unique_key = ''
			show_message('Downloading update failed!#' + string(http_status_code(httpHandler)) + ' ' + http_reason_phrase(httpHandler));
			room_goto_fix(Menu);
		}
		write_buffer_to_file(http_response_body(httpHandler), working_directory + '\Plugins\GG2StatsGAE.gml');
		http_destroy(httpHandler);
		show_message('Found new version of GG2StatsGAE! Game will be restarted...');
		room_goto_fix(Menu);
		execute_program('Gang Garrison 2.exe', '', false);
		game_end();
	}
	else if body_str == 'Login Failed'
	{
		global.unique_key = '';
		show_message('Key is incorrect! Please check gg2.ini file or visit https://gg2statsapp.appspot.com');
	}
	else if body_str == ''
	{
		//Do Nothing!
	}
	else
	{
		global.unique_key = '';
		show_message(body_str);
	}
	room_goto_fix(Menu);
}

//Attempts Log-in
if !variable_global_exists('LoginAttempt')
{
	global.LoginAttempt = object_add();
	object_event_add(global.LoginAttempt, ev_create,0,"
		//Access to login server with post method
		http = global.gg2stats_basehttp + '/login';
		gg2s_key = get_string('Type your unique key: ', '');
		if (gg2s_key != '')
		{
			global.unique_key = gg2s_key;
			login_buffer = buffer_create();
			write_string(login_buffer, 'user_key=' + global.unique_key);
			write_string(login_buffer, '&plugin_version=' + global.gg2stats_version);
			httpHandler = http_new_post(http, login_buffer, 'application/x-www-form-urlencoded');
			while(!http_step(httpHandler)) 
			{
				sleep(floor(1000/30));
				io_handle();
			} 
			// Errored
			if (http_status_code(httpHandler) != 200)
			{
				show_message('Downloading update failed!#' + string(http_status_code(httpHandler)) + ' ' + http_reason_phrase(httpHandler));
				global.unique_key = '';
				room_goto_fix(Menu);
				instance_destroy();
			}
			body_str = read_string(http_response_body(httpHandler), http_response_body_size(httpHandler));
			http_destroy(httpHandler);
			if body_str == 'Need to Update!' //IF LOGIN SUCCESS, WEBAPP RETURNS EMPTY STRING
			{
				http = global.gg2stats_basehttp + '/download/GG2StatsGAE.gml';
				httpHandler = http_new_get(http);
				while(!http_step(httpHandler)) 
				{
					sleep(floor(1000/30));
					io_handle();
				}
				// Errored
				if (http_status_code(httpHandler) != 200)
				{
					global.unique_key = ''
					show_message('Downloading update failed!#' + string(http_status_code(httpHandler)) + ' ' + http_reason_phrase(httpHandler));
					room_goto_fix(Menu);
				}
				write_buffer_to_file(http_response_body(httpHandler), working_directory + '\Plugins\GG2StatsGAE.gml');
				http_destroy(httpHandler);
				show_message('Found new version of GG2StatsGAE! Game will be restarted...');
				room_goto_fix(Menu);
				execute_program('Gang Garrison 2.exe', '', false);
				game_end();
			}
			else if body_str == 'Login Failed'
			{
				global.unique_key = '';
				show_message('Key is incorrect! Please check gg2.ini file or visit https://gg2statsapp.appspot.com');
			}
			else if body_str == ''
			{
				ini_open('gg2.ini');
				ini_write_string('GG2Stats', 'KEY', gg2s_key);
				ini_close();
				show_message('Login Successful! Your ID is saved in gg2.ini for auto-login.');
			}
			else
			{
				global.unique_key = '';
				show_message(body_str);
			}
			room_goto_fix(Menu);
			instance_destroy();
		}
		else
		{
			room_goto_fix(Menu);
			instance_destroy();
		}
	")
}

//Simple Log-out
if !variable_global_exists('LogoutAttempt')
{
	global.LogoutAttempt = object_add();
	object_event_add(global.LogoutAttempt, ev_create,0,"
		//set global variables to empty string
		global.unique_key = '';
		show_message('Logout Successful!');
		room_goto_fix(Menu);
		instance_destroy();
	")
}

//Add Login or Logout Menu to Main Menu
if !variable_global_exists("LoginMenu") 
{
	object_event_add(MainMenuController, ev_create, 0,"
		if (global.unique_key == '')
		{
			menu_addlink('Login', '
				instance_create(0, 0, global.LoginAttempt);
			');
		}
		else
		{
			menu_addlink('Logout', '
				instance_create(0, 0, global.LogoutAttempt);
			');
		}
	");
}

//Update your stats to server if map ends
object_event_add(WinBanner, ev_create, 0,"
	//If unique key exists
	if(global.unique_key != '')
	{
		//exclude map types...
		if (string_copy(global.currentMap, 0, 2) != 'dj' and
		    string_copy(global.currentMap, 0, 2) != 'rj' and
		    string_copy(global.currentMap, 0, 2) != 'rr' and
		    string_copy(global.currentMap, 0, 2) != 'qr' and
		    string_copy(global.currentMap, 0, 4) != 'gg2w')
		{
			//Check if unapplied stat exists
			with (global.myself)
			{
				if (variable_local_exists('class'))
				{
					if (stats[KILLS] != old_kill)
						class_kills[class] += stats[KILLS] - old_kill;
					if (stats[DEATHS] != old_death)
						class_deaths[class] += stats[DEATHS] - old_death;
					if (stats[ASSISTS] != old_assist)
						class_assists[class] += stats[ASSISTS] - old_assist;
				}
			}
			//Set minimal time
			if (global.myself.timer < 30*60)
			{
				with (global.myself)
					event_user(5);
				exit;
			}
			//Access to update server
			httpHandler = instance_create(0, 0, global.httpStepper);
			httpHandler.http = global.gg2stats_basehttp + '/statupdate';
			httpHandler.http_buffer = buffer_create();
			write_string(httpHandler.http_buffer, 'user_key=' + global.unique_key);
			overall_stat = string(global.myself.stats[KILLS]) + ',' + string(global.myself.stats[DEATHS]) + ',' + string(global.myself.stats[ASSISTS]) + ',' + string(global.myself.stats[CAPS])
							   + ',' + string(global.myself.stats[DESTRUCTION]) + ',' + string(global.myself.stats[STABS]) + ',' + string(global.myself.stats[HEALING]) + ','
							   + string(global.myself.stats[DEFENSES]) + ',' + string(global.myself.stats[INVULNS]);
			write_string(httpHandler.http_buffer, '&overall_stat=' + overall_stat);
			timer_string = string(global.myself.timer) + ',' + string(global.myself.team_timer[TEAM_RED]) + ',' + string(global.myself.team_timer[TEAM_BLUE]) + ',' + string(global.myself.team_timer[TEAM_SPECTATOR]);
			for (i = 0; i < 10; i += 1)
			{
				timer_string += ',' + string(global.myself.class_timer[i]);
			}
			write_string(httpHandler.http_buffer, '&overall_playtime=' + timer_string);
			if (global.myself.stats[KILLS] > 0 or global.myself.stats[ASSISTS] > 0)
			{
				class_timerstr = '';
				class_killstr = '';
				class_deathstr = '';
				class_assiststr = '';
				for (i = 0; i  < 10; i += 1)
				{
					class_timerstr += string(global.myself.class_timer[i]);
					class_killstr += string(global.myself.class_kills[i]);
					class_deathstr += string(global.myself.class_deaths[i]);
					class_assiststr += string(global.myself.class_assists[i]);
					if (i != 9)
					{
						class_timerstr += ',';
						class_killstr += ',';
						class_deathstr += ',';
						class_assiststr += ',';
					}
				}
				write_string(httpHandler.http_buffer, '&class_timer=' + class_timerstr);
				write_string(httpHandler.http_buffer, '&class_kills=' + class_killstr);
				write_string(httpHandler.http_buffer, '&class_deaths=' + class_deathstr);
				write_string(httpHandler.http_buffer, '&class_assists=' + class_assiststr);

				if (global.myself.gg2s_latest_team == global.winners)
					write_string(httpHandler.http_buffer, '&team_win=' + '0'); //WIN
				else if (1 - global.myself.gg2s_latest_team == global.winners)
					write_string(httpHandler.http_buffer, '&team_win=' + '1'); //LOSE
				else
					write_string(httpHandler.http_buffer, '&team_win=' + '2'); //STALEMATE
					
				//Match Info
				write_string(httpHandler.http_buffer, '&server_name=' + global.joinedServerName);
				write_string(httpHandler.http_buffer, '&map_name=' + global.currentMap);
				
				if(instance_exists(CTFHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'CTF');
					write_string(httpHandler.http_buffer, '&match_score=' + string(global.redCaps) + ':' + string(global.blueCaps));
				}
				else if(instance_exists(ControlPointHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'CP');
					cp_red_captured = 0;
					cp_blue_captured = 0;
					for (i=1; i<= global.totalControlPoints; i+=1)
					{
						if (global.cp[i].team == TEAM_RED)
							cp_red_captured += 1;
						else if (global.cp[i].team == TEAM_BLUE)
							cp_blue_captured += 1;
					}
					write_string(httpHandler.http_buffer, '&match_score=' + string(cp_red_captured) + ':' + string(cp_blue_captured));
				}
				else if(instance_exists(ArenaHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'ARENA');
					write_string(httpHandler.http_buffer, '&match_score=' + string(ArenaHUD.redWins) + ':' + string(ArenaHUD.blueWins));
				}
				else if(instance_exists(GeneratorHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'GEN');
					gen_red_health = 0;
					gen_blue_health = 0;
					if instance_exists(GeneratorRed) {
						gen_red_health = GeneratorRed.hp*100/GeneratorRed.maxHp;
					}
					if instance_exists(GeneratorBlue) {
						gen_blue_health = GeneratorBlue.hp*100/GeneratorBlue.maxHp;
					}
					write_string(httpHandler.http_buffer, '&match_score=' + string(gen_red_health) + ':' + string(gen_blue_health));
				}
				else if(instance_exists(KothHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'KOTH');
					write_string(httpHandler.http_buffer, '&match_score=' + string(KothHUD.redTimer) + ':' + string(KothHUD.blueTimer));
				}
				else if(instance_exists(DKothHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'DKOTH');
					write_string(httpHandler.http_buffer, '&match_score=' + string(DKothHUD.redTimer) + ':' + string(DKothHUD.blueTimer));
				}
				else if(instance_exists(TeamDeathmatchHUD))
				{
					write_string(httpHandler.http_buffer, '&match_mode=' + 'TDM');
					write_string(httpHandler.http_buffer, '&match_score=' + string(global.redCaps) + '/' + string(TeamDeathmatchHUD.killLimit) + ':' + string(global.blueCaps) + '/' + string(TeamDeathmatchHUD.killLimit));
				}
				else
					write_string(httpHandler.http_buffer, '&match_mode=' + 'NULL');
					
				match_myself = -1;
				match_redteam = '';
				match_blueteam = '';
				gg2s_player = -1;
				gg2s_redteam = ds_priority_create();
				gg2s_blueteam = ds_priority_create();  
				
				for(i=0; i<ds_list_size(global.players); i+=1)
				{
					gg2s_player = ds_list_find_value(global.players, i);
					
					if(gg2s_player.team == TEAM_RED)
						ds_priority_add(gg2s_redteam, gg2s_player, gg2s_player.stats[POINTS]);
					else if (gg2s_player.team == TEAM_BLUE)
						ds_priority_add(gg2s_blueteam, gg2s_player, gg2s_player.stats[POINTS]);
					else
					{
						if(gg2s_player.gg2s_latest_team == TEAM_RED)
							ds_priority_add(gg2s_redteam, gg2s_player, gg2s_player.stats[POINTS]);
						else if (gg2s_player.gg2s_latest_team == TEAM_BLUE)
							ds_priority_add(gg2s_blueteam, gg2s_player, gg2s_player.stats[POINTS]);
					}
				}
				
				team_offset = ds_priority_size(gg2s_redteam);
				
				//RED
				for (i = 0; ds_priority_size(gg2s_redteam) > 0; i += 1)
				{
					gg2s_player = ds_priority_delete_max(gg2s_redteam);
					player_name = gg2s_player.name;
					player_name = string_replace_all(player_name, '!cm', ' ');
					player_name = string_replace_all(player_name, '!cl', ' ');
					player_name = string_replace_all(player_name, ',', '!cm');
					player_name = string_replace_all(player_name, ':', '!cl');
					match_redteam += player_name;
					match_redteam += ',';
					match_redteam += string(gg2s_player.stats[POINTS]);
					match_redteam += ':';
					
					if (gg2s_player == global.myself)
						match_myself = i;
				}
				//BLUE
				for (i = 0; ds_priority_size(gg2s_blueteam) > 0; i += 1)
				{
					gg2s_player = ds_priority_delete_max(gg2s_blueteam);
					player_name = gg2s_player.name;
					player_name = string_replace_all(player_name, '!cm', ' ');
					player_name = string_replace_all(player_name, '!cl', ' ');
					player_name = string_replace_all(player_name, ',', '!cm');
					player_name = string_replace_all(player_name, ':', '!cl');
					match_blueteam += player_name;
					match_blueteam += ',';
					match_blueteam += string(gg2s_player.stats[POINTS]);
					match_blueteam += ':';
					
					if (gg2s_player == global.myself)
						match_myself = team_offset + i;
				}
				ds_priority_destroy(gg2s_redteam);
				ds_priority_destroy(gg2s_blueteam);
				
				write_string(httpHandler.http_buffer, '&match_myself=' + string(match_myself));
				write_string(httpHandler.http_buffer, '&match_redteam=' + match_redteam);
				write_string(httpHandler.http_buffer, '&match_blueteam=' + match_blueteam);
			}
			
			with (httpHandler)
				event_user(0); //do http thing
			
			with (global.myself)
				event_user(5); //reset all stats
		}
	}
");
object_event_add(WinBanner, ev_destroy, 0,"
	global.myself.gg2s_updated = false;
");

//Http Stepper Class(Updates stat to server)
if !variable_global_exists('httpStepper')
{
	global.httpStepper = object_add();
	object_event_add(global.httpStepper, ev_step, ev_step_begin, "
		if (working)
		{
			if(http_step(connection))
			{
				working = false;
				// Errored
				if (http_status_code(connection) != 200)
				{
					show_message('GG2Stats Update Failed!: ' + string(http_status_code(connection)));
				}
				http_destroy(connection);
			}
		}
	");
	
	object_event_add(global.httpStepper, ev_other, ev_user0, "
		connection = http_new_post(http, http_buffer, 'application/x-www-form-urlencoded');
		working = true;
	");
}

//Add time value&stats array tracking for each class for Player object
object_event_add(Player, ev_create, 0, "
	timer = 0;
	team_timer[TEAM_RED] = 0;
	team_timer[TEAM_BLUE] = 0;
	team_timer[TEAM_SPECTATOR] = 0;

	for (i = 0; i < 10; i += 1)
	{
		class_timer[i] = 0;
		class_kills[i] = 0;
		class_deaths[i] = 0;
		class_assists[i] = 0;
	}

	old_kill = 0;
	old_death = 0;
	old_assist = 0;
	gg2s_state = '-1';
	gg2s_updated = false;
	gg2s_latest_team = TEAM_SPECTATOR;
");

object_event_add(Player, ev_step, ev_step_normal, "
	if (id == global.myself)
	{
		timer += 1 * global.delta_factor;
		//if character exists
		if (object != -1)
			class_timer[class] += 1 * global.delta_factor;
		if (team != TEAM_ANY)
			team_timer[team] += 1 * global.delta_factor;
	}
");

object_event_add(Player, ev_step, ev_step_end, "
	if (id == global.myself)
	{
		if (stats[KILLS] != old_kill)
		{
			class_kills[class] += stats[KILLS] - old_kill;
			old_kill = stats[KILLS];
		}
		if (stats[DEATHS] != old_death)
		{
			class_deaths[class] += stats[DEATHS] - old_death;
			old_death = stats[DEATHS];
		}
		if (stats[ASSISTS] != old_assist)
		{
			class_assists[class] += stats[ASSISTS] - old_assist;
			old_assist = stats[ASSISTS];
		}
	}
	//Check user's latest team on (RED OR BLUE)
	if (gg2s_latest_team != team)
	{
		if (team != TEAM_ANY and team != TEAM_SPECTATOR)
			gg2s_latest_team = team;
	}
");

object_event_add(Player, ev_destroy, 0, "
	gg2s_state = '2';
	event_user(4);
");

object_event_add(Player, ev_other, ev_game_end, "
	gg2s_state = '3';
	event_user(4);
");

object_event_add(Player, ev_other, ev_user4, "
	if (id == global.myself && !gg2s_updated)
	{
		//If unique key exists
		if(global.unique_key != '')
		{
			//exclude map types...
			if (string_copy(global.currentMap, 0, 2) != 'dj' and
				string_copy(global.currentMap, 0, 2) != 'rj' and
				string_copy(global.currentMap, 0, 2) != 'rr' and
				string_copy(global.currentMap, 0, 2) != 'qr' and
				string_copy(global.currentMap, 0, 4) != 'gg2w')
			{
				//Check if unapplied stat exists
				if (variable_local_exists('class'))
				{
					if (stats[KILLS] != old_kill)
						class_kills[class] += stats[KILLS] - old_kill;
					if (stats[DEATHS] != old_death)
						class_deaths[class] += stats[DEATHS] - old_death;
					if (stats[ASSISTS] != old_assist)
						class_assists[class] += stats[ASSISTS] - old_assist;
				}
				//Set minimal time
				if (global.myself.timer < 30*60)
					exit;
				//Access to update server
				http = global.gg2stats_basehttp + '/statupdate';
				http_buffer = buffer_create();
				write_string(http_buffer, 'user_key=' + global.unique_key);
				overall_stat = string(global.myself.stats[KILLS]) + ',' + string(global.myself.stats[DEATHS]) + ',' + string(global.myself.stats[ASSISTS]) + ',' + string(global.myself.stats[CAPS])
								   + ',' + string(global.myself.stats[DESTRUCTION]) + ',' + string(global.myself.stats[STABS]) + ',' + string(global.myself.stats[HEALING]) + ','
								   + string(global.myself.stats[DEFENSES]) + ',' + string(global.myself.stats[INVULNS]);
				write_string(http_buffer, '&overall_stat=' + overall_stat);
				timer_string = string(timer) + ',' + string(team_timer[TEAM_RED]) + ',' + string(team_timer[TEAM_BLUE]) + ',' + string(team_timer[TEAM_SPECTATOR]);
				for (i = 0; i < 10; i += 1)
				{
					timer_string += ',' + string(class_timer[i]);
				}
				write_string(http_buffer, '&overall_playtime=' + timer_string);
				
				if (stats[KILLS] > 0 or stats[ASSISTS] > 0)
				{				
					class_timerstr = '';
					class_killstr = '';
					class_deathstr = '';
					class_assiststr = '';
					for (i = 0; i  < 10; i += 1)
					{
						class_timerstr += string(class_timer[i]);
						class_killstr += string(class_kills[i]);
						class_deathstr += string(class_deaths[i]);
						class_assiststr += string(class_assists[i]);
						if (i != 9)
						{
							class_timerstr += ',';
							class_killstr += ',';
							class_deathstr += ',';
							class_assiststr += ',';
						}
					}
					write_string(http_buffer, '&class_timer=' + class_timerstr);
					write_string(http_buffer, '&class_kills=' + class_killstr);
					write_string(http_buffer, '&class_deaths=' + class_deathstr);
					write_string(http_buffer, '&class_assists=' + class_assiststr);
					write_string(http_buffer, '&team_win=' + gg2s_state);
					write_string(http_buffer, '&server_name=' + global.joinedServerName);
					write_string(http_buffer, '&map_name=' + global.currentMap);
					
					if(instance_exists(CTFHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'CTF');
						write_string(http_buffer, '&match_score=' + string(global.redCaps) + ':' + string(global.blueCaps));
					}
					else if(instance_exists(ControlPointHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'CP');
						cp_red_captured = 0;
						cp_blue_captured = 0;
						for (i=1; i<= global.totalControlPoints; i+=1)
						{
							if (global.cp[i].team == TEAM_RED)
								cp_red_captured += 1;
							else if (global.cp[i].team == TEAM_BLUE)
								cp_blue_captured += 1;
						}
						write_string(http_buffer, '&match_score=' + string(cp_red_captured) + ':' + string(cp_blue_captured));
					}
					else if(instance_exists(ArenaHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'ARENA');
						write_string(http_buffer, '&match_score=' + string(ArenaHUD.redWins) + ':' + string(ArenaHUD.blueWins));
					}
					else if(instance_exists(GeneratorHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'GEN');
						gen_red_health = 0;
						gen_blue_health = 0;
						if instance_exists(GeneratorRed) {
							gen_red_health = GeneratorRed.hp*100/GeneratorRed.maxHp;
						}
						if instance_exists(GeneratorBlue) {
							gen_blue_health = GeneratorBlue.hp*100/GeneratorBlue.maxHp;
						}
						write_string(http_buffer, '&match_score=' + string(gen_red_health) + ':' + string(gen_blue_health));
					}
					else if(instance_exists(KothHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'KOTH');
						write_string(http_buffer, '&match_score=' + string(KothHUD.redTimer) + ':' + string(KothHUD.blueTimer));
					}
					else if(instance_exists(DKothHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'DKOTH');
						write_string(http_buffer, '&match_score=' + string(DKothHUD.redTimer) + ':' + string(DKothHUD.blueTimer));
					}
					else if(instance_exists(TeamDeathmatchHUD))
					{
						write_string(http_buffer, '&match_mode=' + 'TDM');
						write_string(http_buffer, '&match_score=' + string(global.redCaps) + '/' + string(TeamDeathmatchHUD.killLimit) + ':' + string(global.blueCaps) + '/' + string(TeamDeathmatchHUD.killLimit));
					}
					else
						write_string(http_buffer, '&match_mode=' + 'NULL');

					match_myself = -1;
					match_redteam = '';
					match_blueteam = '';
					gg2s_player = -1;
					var gg2s_redteam;
					var gg2s_blueteam;
					gg2s_redteam = ds_priority_create();
					gg2s_blueteam = ds_priority_create();  
					
					
					with (Player)
					{
						if(team == TEAM_RED)
							ds_priority_add(gg2s_redteam, id, stats[POINTS]);
						else if (team == TEAM_BLUE)
							ds_priority_add(gg2s_blueteam, id, stats[POINTS]);
						else
						{
							if(gg2s_latest_team == TEAM_RED)
								ds_priority_add(gg2s_redteam, id, stats[POINTS]);
							else if (gg2s_latest_team == TEAM_BLUE)
								ds_priority_add(gg2s_blueteam, id, stats[POINTS]);
						}
					}
					
					team_offset = ds_priority_size(gg2s_redteam);
					
					//RED
					for (i = 0; ds_priority_size(gg2s_redteam) > 0; i += 1)
					{
						gg2s_player = ds_priority_delete_max(gg2s_redteam);
						player_name = gg2s_player.name;
						player_name = string_replace_all(player_name, '!cm', ' ');
						player_name = string_replace_all(player_name, '!cl', ' ');
						player_name = string_replace_all(player_name, ',', '!cm');
						player_name = string_replace_all(player_name, ':', '!cl');
						match_redteam += player_name;
						match_redteam += ',';
						match_redteam += string(gg2s_player.stats[POINTS]);
						match_redteam += ':';
						
						if (gg2s_player == global.myself)
							match_myself = i;
					}
					//BLUE
					for (i = 0; ds_priority_size(gg2s_blueteam) > 0; i += 1)
					{
						gg2s_player = ds_priority_delete_max(gg2s_blueteam);
						player_name = gg2s_player.name;
						player_name = string_replace_all(player_name, '!cm', ' ');
						player_name = string_replace_all(player_name, '!cl', ' ');
						player_name = string_replace_all(player_name, ',', '!cm');
						player_name = string_replace_all(player_name, ':', '!cl');
						match_blueteam += player_name;
						match_blueteam += ',';
						match_blueteam += string(gg2s_player.stats[POINTS]);
						match_blueteam += ':';
						
						if (gg2s_player == global.myself)
							match_myself = team_offset + i;
					}
					
					ds_priority_destroy(gg2s_redteam);
					ds_priority_destroy(gg2s_blueteam);				
					write_string(http_buffer, '&match_myself=' + string(match_myself));
					write_string(http_buffer, '&match_redteam=' + match_redteam);
					write_string(http_buffer, '&match_blueteam=' + match_blueteam);

					httpHandler = http_new_post(http, http_buffer, 'application/x-www-form-urlencoded');
					while(!http_step(httpHandler)) 
					{
						sleep(floor(1000/30));
						io_handle();
					} 
					// Errored
					if (http_status_code(httpHandler) != 200)
					{
						show_message('Stat update failed!#' + string(http_status_code(httpHandler)) + ' ' + http_reason_phrase(httpHandler));
					}
				}
			}
		}
	}
");

//RESET ALL STATS
object_event_add(Player, ev_other, ev_user5, "
	timer = 0;
	team_timer[TEAM_RED] = 0;
	team_timer[TEAM_BLUE] = 0;
	team_timer[TEAM_SPECTATOR] = 0;
	for (i = 0; i  < 10; i += 1)
	{
		class_timer[i] = 0;
		class_kills[i] = 0;
		class_deaths[i] = 0;
		class_assists[i] = 0;
	}
	old_kill = 0;
	old_death = 0;
	old_assist = 0;
	gg2s_state = '-1';
	gg2s_updated = true;
	gg2s_latest_team = TEAM_SPECTATOR;
");