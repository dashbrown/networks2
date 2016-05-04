"""Simlulate the matchmaking and queue of League of Legends"""

import random
import pickle
import os
from flow_network import *

"""Enumeration for each role"""
class RoleEnum(object):
  TOP = "t"
  JUN = "j"
  MID = "m"
  ADC = "a"
  SUP = "s"


"""An individual player. Has preferences for first and second choice of role, 
set according to global constants for each."""
class Player(object):

  # the number out of 100 players that prefer this role
  RATIO_TOP = 20
  RATIO_JUN = 20
  RATIO_MID = 25
  RATIO_ADC = 20
  RATIO_SUP = 15

  def __init__(self):
    roles = Player.role_list()
    self.first = random.choice(roles)
    self.second = self.first
    while self.second == self.first:
      self.second = random.choice(roles)
    self.third = self.second
    while self.third == self.second or self.third == self.first:
      self.third = random.choice(roles)
    self.fourth = self.second
    while self.fourth == self.second or self.fourth == self.third or self.fourth == self.first:
      self.fourth = random.choice(roles)
    self.fifth = self.second
    while self.fifth == self.first or self.fifth == self.second or self.fifth == self.third or self.fifth == self.fourth:
      self.fifth = random.choice(roles)
    self.assigned = None
    self.time_in_queue = 0
    self.checked = False

  def asshole(self):
    if self.first != RoleEnum.MID:
      self.second = RoleEnum.MID

  def __repr__(self):
    return str(self.first) + " " + str(self.second)

  def increment_time_in_queue(self):
    self.time_in_queue+=1

  def pick_pref_role(self, roles):
    if self.first in roles:
      self.assigned = self.first
      roles.remove(self.assigned)
    elif self.second in roles:
      self.assigned = self.second
      roles.remove(self.assigned)
    elif self.third in roles:
      self.assigned = self.third
      roles.remove(self.assigned)
    elif self.fourth in roles:
      self.assigned = self.fourth
      roles.remove(self.assigned)
    elif self.fifth in roles:
      self.assigned = self.fifth
      roles.remove(self.assigned)

  def happiness(self):
    if self.first == self.assigned:
      return 10
    if self.second == self.assigned:
      return 7
    if self.third == self.assigned:
      return 5
    if self.fourth == self.assigned:
      return 3
    return 0


  @staticmethod
  def custom_player(first, second):
    player = Player()
    player.first = first
    player.second = second
    return player


  """Create a list used to randomly assign role preferences based on given ratios"""
  @staticmethod
  def role_list():
    roles = []
    for i in xrange(Player.RATIO_TOP):
      roles.append(RoleEnum.TOP)
    for i in xrange(Player.RATIO_JUN):
      roles.append(RoleEnum.JUN)
    for i in xrange(Player.RATIO_MID):
      roles.append(RoleEnum.MID)
    for i in xrange(Player.RATIO_ADC):
      roles.append(RoleEnum.ADC)
    for i in xrange(Player.RATIO_SUP):
      roles.append(RoleEnum.SUP)
    return roles


"""Represents a game. Has two teams of 5 Players, 
each role on each team is represented"""
class Game(object):

  def __init__(self, red, blue):
    self.red = red
    self.blue = blue


"""A matchmaking queue. When a game can be created it removes the players
 from the queue. Only begins a game when both teams can be filled"""
class Matchmaking_Queue(object):

  def __init__(self):
    self.all_players = []
    self.can_top = []
    self.can_jun = []
    self.can_mid = []
    self.can_adc = []
    self.can_sup = []
    self.teams = []
    self.games = []

  def add_player(self, new_player):
    self.all_players.append(new_player)
    if new_player.first == RoleEnum.TOP or new_player.second == RoleEnum.TOP:
      self.can_top.append(new_player)
    if new_player.first == RoleEnum.JUN or new_player.second == RoleEnum.JUN:
      self.can_jun.append(new_player)
    if new_player.first == RoleEnum.MID or new_player.second == RoleEnum.MID:
      self.can_mid.append(new_player)
    if new_player.first == RoleEnum.ADC or new_player.second == RoleEnum.ADC:
      self.can_adc.append(new_player)
    if new_player.first == RoleEnum.SUP or new_player.second == RoleEnum.SUP:
      self.can_sup.append(new_player)

  def add_new_player(self):
    player = Player()
    player.asshole()
    self.add_player(player)

  def all_roles_represented(self, n):
    top = False
    jun = False
    mid = False
    adc = False
    sup = False
    for player in self.all_players[:n]:
      if player.first == RoleEnum.TOP or player.second == RoleEnum.TOP:
        top = True
      if player.first == RoleEnum.JUN or player.second == RoleEnum.JUN:
        jun = True
      if player.first == RoleEnum.MID or player.second == RoleEnum.MID:
        mid = True
      if player.first == RoleEnum.ADC or player.second == RoleEnum.ADC:
        adc = True
      if player.first == RoleEnum.SUP or player.second == RoleEnum.SUP:
        sup = True
    return top and jun and mid and adc and sup

  def create_team(self):
    if len(self.all_players) < 5:
      return
    team = []
    for i in xrange(5,len(self.all_players)+1):
      if not self.all_roles_represented(i):
        continue
      fn = self.create_flow_network(i)
      mf = fn.max_flow('x','y')
      if mf == 5:
        for edge in fn.flow:
          if fn.flow[edge] == 1 and (edge.source).isdigit():
            player = self.all_players[int(edge.source)]
            player.assigned = edge.sink
            team.append(player)
        for player in team:
          self.all_players.remove(player)
        self.teams.append(team)

  def create_team_matching(self):
    if len(self.all_players) < 5:
      return
    team = []
    for i in xrange(5):
      team.append(self.all_players.pop())
    available_roles = [RoleEnum.TOP,RoleEnum.JUN,RoleEnum.MID,RoleEnum.ADC,RoleEnum.SUP]
    for player in team:
      player.pick_pref_role(available_roles)
    self.teams.append(team)


  def create_game(self):
    if len(self.teams) > 1:
      game = Game(self.teams[0], self.teams[1])
      self.teams.remove(self.teams[1])
      self.teams.remove(self.teams[0])
      self.games.append(game)

  def create_flow_network(self, n):
    g = FlowNetwork()
    string = ['x'] + self.build_keys(n) + ['t','j','m','a','s','y']
    [g.add_vertex(v) for v in string]
    for i in xrange(n):
      g.add_edge('x',str(i),1)
    for i in xrange(n):
      g.add_edge(str(i), self.all_players[i].first, 1)
      g.add_edge(str(i), self.all_players[i].second, 1)
      # g.add_edge(str(i), self.all_players[i].third, 1)
      # g.add_edge(str(i), self.all_players[i].fourth, 1)
      # g.add_edge(str(i), self.all_players[i].fifth, 1)
    for r in ['t','j','m','a','s']:
      g.add_edge(r,'y',1)
    return g

  def build_keys(self, n):
    k = []
    for i in xrange(n):
      k.append(str(i))
    return k

  def increment_time(self):
    # print self.all_players
    for player in self.all_players:
      player.increment_time_in_queue()
    for team in self.teams:
      for player in team:
        player.increment_time_in_queue()

  def average_wait(self):
    total_time = 0
    for game in self.games:
      for red_player in game.red:
        total_time+=red_player.time_in_queue
      for blue_player in game.blue:
        total_time+=blue_player.time_in_queue
    return float(total_time) / (len(self.games) * 10)

  def average_wait_pos(self, position):
    total_time = 0
    for game in self.games:
      for red_player in game.red:
        if red_player.assigned == position:
          total_time += red_player.time_in_queue
      for blue_player in game.blue:
        if blue_player.assigned == position:
          total_time += blue_player.time_in_queue
    return float(total_time) / (len(self.games) * 2)

  def preferences(self):
    first_choice = 0
    second_choice = 0
    for game in self.games:
      for red_player in game.red:
        if red_player.assigned == red_player.first:
          first_choice += 1
        else:
          second_choice += 1
      for blue_player in game.blue:
        if blue_player.assigned == blue_player.first:
          first_choice += 1
        else:
          second_choice += 1
    return first_choice, second_choice

  def pref_pos(self, position):
    first_choice = 0
    second_choice = 0
    for game in self.games:
      for red_player in game.red:
        if red_player.assigned == red_player.first and red_player.assigned == position:
          first_choice += 1
        elif red_player.first == position:
          second_choice += 1
      for blue_player in game.blue:
        if blue_player.assigned == blue_player.first and blue_player.assigned == position:
          first_choice += 1
        elif blue_player.first == position:
          second_choice += 1
    return float(first_choice) / (first_choice + second_choice)

  def average_happiness(self):
    # print len(self.games)
    total_happiness = 0
    for game in self.games:
      for red_player in game.red:
        total_happiness += red_player.happiness()
      for blue_player in game.blue:
        total_happiness += blue_player.happiness()
    return float(total_happiness) / (len(self.games) * 10)



if __name__ == '__main__':

  print "RATIO_TOP", Player.RATIO_TOP
  print "RATIO_JUN", Player.RATIO_JUN
  print "RATIO_MID", Player.RATIO_MID
  print "RATIO_ADC", Player.RATIO_ADC
  print "RATIO_SUP", Player.RATIO_SUP
  print ""

  times = []
  prefs = []
  time_top = []
  time_jun = []
  time_mid = []
  time_adc = []
  time_sup = []
  pref_top = []
  pref_jun = []
  pref_mid = []
  pref_adc = []
  pref_sup = []
  avg_happy = []
  num_games = []

  aggregate_times = []
  aggregate_prefs = []
  aggregate_time_top = []
  aggregate_time_jun = []
  aggregate_time_mid = []
  aggregate_time_adc = []
  aggregate_time_sup = []
  aggregate_pref_top = []
  aggregate_pref_jun = []
  aggregate_pref_mid = []
  aggregate_pref_adc = []
  aggregate_pref_sup = []
  aggregate_avg_happy = []
  aggregate_num_games = []

  for k in xrange(1):
    for j in xrange(1):
      mmq = Matchmaking_Queue()
      for i in xrange(100):
        mmq.increment_time()
        mmq.add_new_player()
        mmq.create_team()
        # mmq.create_team_matching()
        mmq.create_game()
      
      times.append(mmq.average_wait())
      time_top.append(mmq.average_wait_pos(RoleEnum.TOP))
      time_jun.append(mmq.average_wait_pos(RoleEnum.JUN))
      time_mid.append(mmq.average_wait_pos(RoleEnum.MID))
      time_adc.append(mmq.average_wait_pos(RoleEnum.ADC))
      time_sup.append(mmq.average_wait_pos(RoleEnum.SUP))

      prefs.append(mmq.preferences())
      pref_top.append(mmq.pref_pos(RoleEnum.TOP))
      pref_jun.append(mmq.pref_pos(RoleEnum.JUN))
      pref_mid.append(mmq.pref_pos(RoleEnum.MID))
      pref_adc.append(mmq.pref_pos(RoleEnum.ADC))
      pref_sup.append(mmq.pref_pos(RoleEnum.SUP))

      avg_happy.append(mmq.average_happiness())
      num_games.append(len(mmq.games))
      
      directory = "pickles/" + str(Player.RATIO_TOP) + "_" + str(Player.RATIO_JUN) + "_" + str(Player.RATIO_MID) + "_" + str(Player.RATIO_ADC) + "_" + str(Player.RATIO_SUP) + "/"
      if not os.path.exists(directory):
        os.makedirs(directory)
      with open(directory + str(k) + "_" + str(j) + ".p", "w") as f:
        pickle.dump(mmq.games, f)
    
    aggregate_times.append(sum(times) / len(times))
    aggregate_time_top.append(sum(time_top) / len(time_top))
    aggregate_time_jun.append(sum(time_jun) / len(time_jun))
    aggregate_time_mid.append(sum(time_mid) / len(time_mid))
    aggregate_time_adc.append(sum(time_adc) / len(time_adc))
    aggregate_time_sup.append(sum(time_sup) / len(time_sup))

    first = [x for (x,y) in prefs]
    second = [y for (x,y) in prefs]
    aggregate_prefs.append((float(sum(first) / len(first))) / (sum(first) / len(first) + sum(second) / len(second)))
    aggregate_pref_top.append(sum(pref_top) / len(pref_top))
    aggregate_pref_jun.append(sum(pref_jun) / len(pref_jun))
    aggregate_pref_mid.append(sum(pref_mid) / len(pref_mid))
    aggregate_pref_adc.append(sum(pref_adc) / len(pref_adc))
    aggregate_pref_sup.append(sum(pref_sup) / len(pref_sup))

    aggregate_avg_happy.append(sum(avg_happy) / len(avg_happy))
    aggregate_num_games.append(sum(num_games) / len(num_games))

    # print "AVERAGE TIME: " + str(sum(times) / len(times))
    # print "PREFERENCES: " + str(sum(first) / len(first)) + " " + str(sum(second) / len(second))
    # print ""
  print "AVERAGE TIME: " + str(sum(aggregate_times) / len(aggregate_times))[:4]
  print "AVERAGE TIME TOP: " + str(sum(aggregate_time_top) / len(aggregate_time_top))[:4]
  print "AVERAGE TIME JUN: " + str(sum(aggregate_time_jun) / len(aggregate_time_jun))[:4]
  print "AVERAGE TIME MID: " + str(sum(aggregate_time_mid) / len(aggregate_time_mid))[:4]
  print "AVERAGE TIME ADC: " + str(sum(aggregate_time_adc) / len(aggregate_time_adc))[:4]
  print "AVERAGE TIME SUP: " + str(sum(aggregate_time_sup) / len(aggregate_time_sup))[:4]

  print "AVERAGE PREF: " + str(sum(aggregate_prefs) / len(aggregate_prefs))[:4]
  print "AVERAGE PREF TOP: " + str(sum(aggregate_pref_top) / len(aggregate_pref_top))[:4]
  print "AVERAGE PREF JUN: " + str(sum(aggregate_pref_jun) / len(aggregate_pref_jun))[:4]
  print "AVERAGE PREF MID: " + str(sum(aggregate_pref_mid) / len(aggregate_pref_mid))[:4]
  print "AVERAGE PREF ADC: " + str(sum(aggregate_pref_adc) / len(aggregate_pref_adc))[:4]
  print "AVERAGE PREF SUP: " + str(sum(aggregate_pref_sup) / len(aggregate_pref_sup))[:4]

  print "AVERAGE HAPPINESS: " + str(sum(aggregate_avg_happy) / len(aggregate_avg_happy))[:4]

  print "NUMBER OF GAMES: " + str(sum(aggregate_num_games) / len(aggregate_num_games))[:4]












