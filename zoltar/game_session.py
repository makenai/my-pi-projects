import random

class game_session :
	
	def __init__(self):
		"does shit"
		self.questions = []
		self.answers = []
	
		self.questions.append({
			'image': 'assets/gender.png',
			'left': 'female',
			'right': 'male'
		})
		self.questions.append({
			'image': 'assets/cost.png',
			'left': 'expensive',
			'right': 'cheap'
		})
		self.questions.append({
			'image': 'assets/colour.png',
			'left': 'colourful',
			'right': 'drab'
		})
		self.questions.append({
			'image': 'assets/fanciness.png',
			'left': 'fancy',
			'right': 'casual'
		})
		self.questions.append({
			'image': 'assets/weather.png',
			'left': 'warm',
			'right': 'cold'
		})
		random.shuffle(self.questions)

	def next_question(self):
		"returns the next question"
		try:
			return self.questions.pop()
		except IndexError:
			return None

	def store_answer(self, answer):
		"stores answer into an array"			
		self.answers.append(answer)
		