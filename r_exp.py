"""
Description:
This script is to simulate a very, very simplified society wherein racism is the sole decision engine.

Author Comments:
I have no agenda in writing this. It is simple scientific curiosity that drives me to write this-
	to see if a societal asymptote exists and if it does, what it is depending on a number of starting criteria.
This is an incredibly simplified view of society and does not serve as a metric for it.
This script was designed to get an overarching view of society. 
Who knows how accurate it is...

Todo:
	- Generational impact + Unit aging
	- Multiple communities interacting with each other
	- 
"""

# Script metadata
__author__ = "Vincent Zhen"
__version__ = "0.1"
__email__ = "vincent.zhen@nyu.edu"
__status__ = "Prototype"

# Imports
import random
import argparse
import math
import numpy
import pprint
import sys

"""
[*] - Class definitions start here
"""
# Unit - the standard individual containing all of the properties and characteristics
#   of that individual.
class Unit:

	DEFAULT_GATE_VAL = 100

	INIT_RSCALE_MEAN = 50
	INIT_RSCALE_SIGMA = 20

	# Unit objection initialization
	# Start off with a score of 0 and be part of a community
	def __init__(self, community, race=None, rScale=None, influencerLevel=None, gate=None, entrenchment=None):
		# Ensure 'community' is a Community object
		if isinstance(community, Community):
			self.community = community
			self.community.addUnit(self)
		else:
			raise TypeError("'community' parameter must be of object type Community")
		self.setRace(race)

		# rScale (Racism Scale) - An dictionary of races and their respective racism levels
		# 	rLevel: integer between 0 and 100 (0: will 100% work with this race, 100: will 100% NOT work with this race)
		#	gate: how entrenched a Unit is to their view. It is a threshold that needs to be reached for rLevel to change
		# 	ions: the amount of influence upon a Unit to reach the 'gate' threshold
		"""
		rScale = {
			'RaceA': {
				'rLevel': 0 to 100,
				'gate': DEFAULT = 100,
				'ion': -'gate' to 'gate'
			},
			'RaceB': {
				'rLevel': 0 to 100,
				'gate': DEFAULT = 100,
				'ion': -'gate' to 'gate'
			}
		}
		"""
		self.rScale = dict()
		self.initrScale(rScale)
		# influencerLevel - The amount of influence the Unit has on the Community
		self.setInfluencerLevel(influencerLevel)
		self.iden = self.community.unitList.index(self)

	# Setting the race of the Unit
	def setRace(self, race=None):
		if race is None:
			self.race = self.community.getRandomRace()
		else:
			retval = self.community.isRace(race)
			if retval is None:
				print("[!] - Race '{}' is not available in this community. Setting self.race to a random available race.".format(race))
				self.race = self.community.getRandomRace()
			else:
				self.race = retval

	# Initializing the racism scale of the Unit
	# MODE: Gaussian curve
	def initrScale(self, rScale=None):
		for race in self.community.RACE_LIST:
			self.rScale[race] = dict()
			# If rScale is None, set it to a random rScale
			if rScale is None:
				# Generate a list of racism levels by MODE
				nums = [int(random.gauss(self.INIT_RSCALE_MEAN, self.INIT_RSCALE_SIGMA)) for _ in range(len(self.community.RACE_LIST))]
				# Set bounds for the nums array
				arr = numpy.array(nums)
				arr = numpy.clip(arr, 0, 100, out=arr)
				arr = list(arr)
				self.rScale[race]["rLevel"] = arr.pop()
			# Else, generic set function
			else:
				self.rScale[race]["rLevel"] = rScale
			self.rScale[race]["gate"] = self.DEFAULT_GATE_VAL
			self.rScale[race]["ion"] = 0

	def setInfluencerLevel(self, influencerLevel=None):
		if influencerLevel is None:
			self.influencerLevel = random.randint(-10, 10)
		else:
			self.influencerLevel = influencerLevel

	def addrLevel(self, race, addrLevel):
		currentrLevel = self.rScale[race]["rLevel"] + addrLevel
		self.rScale[race]["rLevel"] = currentrLevel
		if currentrLevel > 100:
			self.rScale[race]["rLevel"] = 100
		if currentrLevel < 0:
			self.rScale[race]["rLevel"] = 0

	def addIons(self, race, addIons):
		currentIonCount = self.rScale[race]["ion"] + addIons
		self.rScale[race]["ion"] = currentIonCount
		# If you hit the 'gate' threshold, add/subtract from racism scale
		currentGate = self.rScale[race]["gate"]
		if abs(currentIonCount) >= currentGate:
			newrLevel = int(currentIonCount / 100)
			newIon = currentIonCount % 100
			self.addrLevel(race, newrLevel)
			self.rScale[race]["ion"] = newIon

	def rScale_pprint(self):
		ans = list()
		for key, value in self.rScale.iteritems():
			ans.append("\trLevel -{}: {}".format(key, value))
		return '\n'.join(ans)

	# Debugging
	def setrLevel(self, race, newrLevel):
		self.rScale[race]["rLevel"] = newrLevel
	def setInfluence(self, newInfluence):
		self.influencerLevel = newInfluence

	# Override default print
	def __str__(self):
		output = list()
		output.append("\tRace: {}".format(self.race))
		output.append("{}".format(self.rScale_pprint()))
		output.append("\tInfluencer Level: {}".format(self.influencerLevel))
		output.append("")
		return '\n'.join(output)



# Community - A list of Unit objects + properties of the community like the available races and such
class Community:

	DEFAULT_MAX_UNITS = 25
	# RACE_LIST - List of available races in the community (using NATO phoenetic alphabet)
	RACE_LIST = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]

	# Set initialization for Community class
	def __init__(self, name, maxUnits=None, unit=None):
		# name - Name of the Community
		self.name = name
		# unitList - List of Unit objects which make up the Community
		self.unitList = list()
		# maxUnits - Maximum number of members this community can afford (default = 25)
		self.maxUnits = int()
		# score - Score of the community (?)
		self.score = int()

		if maxUnits is None:
			self.maxUnits = self.DEFAULT_MAX_UNITS
		else:
			self.maxUnits = maxUnits

		# If 'unit' parameter is None, leave unitList empty
		# Else, ensure that 'unit' is a Unit object then append
		if unit is not None:
			if isinstance(unit, Unit):
				self.unitList.append(unit)
			else:
				raise TypeError("'unit' parameter must be of object type Unit")

	# Return a random race from RACE_LIST
	def getRandomRace(self):
		return random.choice(self.RACE_LIST)

	# Return 'race' if race exists in community. 'None' otherwise
	def isRace(self, race):
		if race in self.RACE_LIST:
			return race
		else:
			return None

	# Add a Unit to the unitList
	def addUnit(self, newUnit):
		if len(self.unitList) < self.maxUnits:
			self.unitList.append(newUnit)
			return True
		else:
			print("[!] - Cannot add another Unit to the Community '{}' as it has reached maximum capacity".format(self.name))
			return False

	# Override default print
	def __str__(self):
		output = list()
		output.append("----------\nCommunity: {}\n----------".format(self.name))
		output.append("Number of Units: {}/{}".format(len(self.unitList), self.maxUnits))
		for index, unit in enumerate(self.unitList):
			output.append("-----\nUnit#{}\n-----".format(index))
			output.append(str(unit))
		return '\n'.join(output)


"""
[*] - Standalone methods start here
"""
# Define the probability of interaction + probability of good/bad interaction between two Units
# Include probability using random integer within normal curve
def pInteract(a, b):

	DEFAULT_STD_MEAN = 0 
	DEFAULT_STD_SIGMA = 10

	pInteraction = a.rScale[b.race]["rLevel"]
	diceRoll = random.randint(0, 100) + int(random.gauss(DEFAULT_STD_MEAN, DEFAULT_STD_SIGMA))
	if diceRoll > pInteraction:
		return True
	else:
		return False

def boundInt(queryInt, boundInt, lowBound=True):
	if lowBound:
		if queryInt < (-1 * boundInt):
			return (-1 * boundInt)
	elif queryInt > boundInt:
		return boundInt
	else:
		return queryInt

def allSet(community, newrLevel=20):
	for unit in community.unitList:
		for race in community.RACE_LIST:
			unit.setrLevel(race, newrLevel)
		unit.setInfluence(0)

"""
Interactions functions
"""
# interaction01 - Basic interaction.
# srcUnit interacts with all other Units. Add score based on influencerLevel and rScale
def interaction01(srcUnit, community):

	# Generate a random integer using a normal distribution for addIons
	BASE_ADD_SCORE_MEAN = 10
	DERIVED_ADD_SCORE = int(random.gauss(BASE_ADD_SCORE_MEAN, BASE_ADD_SCORE_MEAN/2))

	for dstUnit in community.unitList:
		# Don't interact with the self
		if srcUnit is not dstUnit:

			# Chance of interaction
			if pInteract(srcUnit, dstUnit):

				# Chance of good/bad encounter
				if pInteract(srcUnit, dstUnit):
					# Good interaction

					# If same race - halve the addIon
					if srcUnit.race is dstUnit.race:

						srcUnit.addIons(dstUnit.race, (-1 * (DERIVED_ADD_SCORE/2)))

						# Diffusion of racism via influence
						influence = srcUnit.influencerLevel
						for rKey, rValue in dstUnit.rScale.iteritems():
							tmpGate = rValue["gate"]/2
							if influence != 0:
								addVal = (srcUnit.rScale[rKey]["rLevel"] - (tmpGate)) * (tmpGate/influence)
								dstUnit.addIons(rKey, ((srcUnit.rScale[rKey]["rLevel"] - (tmpGate)) * (tmpGate/influence))/2)

						# dstUnit reciprocation
						dstUnit.addIons(srcUnit.race, (-1 * (DERIVED_ADD_SCORE/4)))

					# If not the same race
					else:

						srcUnit.addIons(dstUnit.race, (-1 * DERIVED_ADD_SCORE))

						# Diffusion of racism via influence
						influence = srcUnit.influencerLevel
						for rKey, rValue in dstUnit.rScale.iteritems():
							tmpGate = rValue["gate"]/2
							if influence != 0:
								addVal = (srcUnit.rScale[rKey]["rLevel"] - (tmpGate)) * (tmpGate/influence)
								dstUnit.addIons(rKey, ((srcUnit.rScale[rKey]["rLevel"] - (tmpGate)) * (tmpGate/influence)))

						# dstUnit reciprocation
						dstUnit.addIons(srcUnit.race, (DERIVED_ADD_SCORE/2))
				
				# Bad interaction
				else:

					# If same race - halve the addIon
					if srcUnit.race is dstUnit.race:
						srcUnit.addIons(dstUnit.race, (DERIVED_ADD_SCORE/2))

						# dstUnit reciprocation
						dstUnit.addIons(srcUnit.race, (-1 * (DERIVED_ADD_SCORE/4)))

					# If not the same race
					else:
						srcUnit.addIons(dstUnit.race, (DERIVED_ADD_SCORE))

						#dstUnit reciprocation
						dstUnit.addIons(srcUnit.race, (DERIVED_ADD_SCORE/2))


"""
[*] - Main function starts here
"""
def main(community):

	hold = None

	# Step n times and do interactions
	def s(n=1):
		print "[+] - Stepping {} cycles...".format(n)
		for step in range(n):
			for unit in community.unitList:
				interaction01(unit, community)


	# Print one Unit by index
	def p(unitIndex):
		print community.unitList[unitIndex]

	# Print all
	def pa():
		print community

	# Save Unit into variable
	def h(unitIndex):
		hold = community.unitList[unitIndex]

	def ph():
		if hold is None:
			print "[!] - There is nothing in the 'hold' variable"
		else:
			print hold

	# Simulate an event that throws a positive light upon a race
	def tp(race, addIons=25):
		print "[+] - Simulating positive event for race: {}".format(race)
		if community.isRace(race):
			for unit in community.unitList:
				unit.addIons(race, (-1 * addIons))
		else:
			print "[!] - '{}' doesn't seem to be an available race in this community"

	# Simulate an event that throws a negative light upon a race
	def tn(race, addIons=25):
		print "[+] - Simulating negative event for race: {}".format(race)
		if community.isRace(race):
			for unit in community.unitList:
				unit.addIons(race, addIons)
		else:
			print "[!] - '{}' doesn't seem to be an available race in this community"

	def printOptions():
		print("""
			s [n] - Step n times (default 1)
			h $INDEX_OF_UNIT - Saves unit printout into variable
			p $INDEX_OF_UNIT - Print unit
			ph - Print saved unit 
			pa - Print entire community
			tp $RACE - Simulate a positive event for a race
			tn $RACE - Simulate a negative event for a race
			q/exit - Quit
			? - Show options
			""")

	# Main loop
	while True:
		res = raw_input("What do you want to do? ([?] for options) ")
		res = res.strip().split()
		if res[0] == "s":
			try:
				s(int(res[1]))
			except:
				s()
		elif res[0] == "h":
			try:
				h(int(res[1]))
			except:
				print "[!] - Unable to hold this Unit"
		elif res[0] == "p":
			try:
				p(int(res[1]))
			except:
				print "[!] - Unable to print this Unit"
		elif res[0] == "ph":
			ph()
		elif res[0] == "pa":
			pa()
		elif res[0] == "tp":
			try:
				tp(res[1])
			except:
				print "[!] - Unable to simulate positive event"
		elif res[0] == "tn":
			try:
				tn(res[1])
			except:
				print "[!] - Unable to simulate negative event"
		# Quitting
		elif res[0] == "q" or res[0] == "exit":
			print "Bye!"
			exit(0)
		elif res[0] == "?":
			printOptions()
		else:
			print "[!] - Unknown command. Please use '?' to show all options"



"""
[*] - Testing starts here
"""
if __name__ == "__main__":
	print("Starting {} test...".format("COMM-A"))

	t = Community("COMM-A")

	"""
	# Random
	n1 = Unit(race="Alpha", community=t)
	n2 = Unit(race="Alpha", community=t)
	n3 = Unit(race="Bravo", community=t)
	n4 = Unit(race="Delta", community=t)
	n5 = Unit(race="Charlie", community=t)
	"""


	# OIS
	n1 = Unit(race="Alpha", community=t)
	n2 = Unit(race="Alpha", community=t)
	n3 = Unit(race="Alpha", community=t)
	n4 = Unit(race="Bravo", community=t)
	n5 = Unit(race="Charlie", community=t)
	n6 = Unit(race="Delta", community=t)
	n7 = Unit(race="Delta", community=t)
	n8 = Unit(race="Delta", community=t)

	setNeutral(t)

	n1.setInfluence(5)
	n6.setInfluence(3)

	"""
	n1 = Unit(race="Alpha", community=t)
	n2 = Unit(race="Alpha", community=t)
	n3 = Unit(race="Bravo", community=t)
	n4 = Unit(race="Delta", community=t)

	n1.setrLevel("Bravo", 80)
	"""
	"""
	n1 = Unit(race="Alpha", community=t)
	n2 = Unit(race="Alpha", community=t)
	n3 = Unit(race="Bravo", community=t)
	n4 = Unit(race="Bravo", community=t)
	n5 = Unit(race="Alpha", community=t)

	allSet(t, 0)

	n1.setrLevel("Bravo", 100)
	n1.setInfluence(10)
	"""

	main(t)
