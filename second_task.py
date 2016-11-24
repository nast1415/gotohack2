import numpy as np
import pandas as pd


#Read course-217-events.csv file
events = pd.read_csv('data/course-217-events.csv', header = 0)
#Read course-217-structure.csv file
structure = pd.read_csv('data/course-217-structure.csv', header = 0)

#Constants for number of steps in the 217 course and number of events
number_of_steps = structure['step_id'].count()
number_of_events = events['user_id'].count()

#First of all we need to find real position for every step
#For this sort values in the orde module-lesson-step position
step_position = pd.DataFrame(structure[['module_position', 'lesson_position', 'step_position', 'step_id']])
sorted_step_position = step_position.sort_values(by = ['module_position', 'lesson_position', 'step_position'])
sorted_step_position.index = np.array(range(number_of_steps))

#Add a new column 'step_order' to the sorted_step_posotion dataframe 
step_order = np.array(range(233)).astype(np.int)
sorted_step_position['step_order'] = step_order

#Create new dataframe, which includes step_id and it's real position in the course (step_order)
step_info = pd.DataFrame(sorted_step_position[['step_id', 'step_order']])

#Merge step_info and events dataframes (to have in events table foe each step it's real position)
events_info = pd.merge(events, step_info, on='step_id', how='inner')
#Sort values in a new dataframe first by user_id and then by time (to have real time sorted history of events for each user)
events_info = events_info.sort_values(by = ['user_id', 'time'])
#Fix indexes in the sorted dataframe
events_info.index = np.array(range(number_of_events))

#Define numpy array size of number_of_steps, full of nulls as null_array
null_array = np.zeros(number_of_steps).astype(np.int)

#Create new dataframe for calculating percent of returns for each step
#step_return_info dataframe has three main columns: 'step_id', 'number_of_visitors' and 'number_of_returns' and three other supporting columns 
#for calculating for each step 'number_of_visitors' and 'number_of_returns'
step_return_info = pd.DataFrame({'step_id': null_array, 'number_of_visitors': null_array, 
	'number_of_returns': null_array, 'is_visited': null_array, 'is_return': null_array, 'user_id': null_array})

step_return_info['step_id'] = step_info[['step_id']].apply(lambda x: x)

#We're going to calculate the result during processing the data from events_info dataframe
for event in range(number_of_events):
	step_pos = events_info['step_order'][event]
	user = events_info['user_id'][event]
	
	#If we have event with new user in our table of events (remember, that all users were sorted), we will null all supporting columns (except 'user_id' because it's not neccessary)
	if (event != 0) and (events_info['user_id'][event] != events_info['user_id'][event - 1]):
		step_return_info['is_visited'] = null_array
		step_return_info['is_return'] = null_array

	#If user enter the step for the first time, we increment number of visitors on this step and make a note that this user was on this step (at the 'user_id' column)
	if step_return_info['user_id'][step_pos] != user:
		step_return_info['number_of_visitors'][step_pos] += 1
		step_return_info['user_id'][step_pos] = user

	#If user enter the step for the first time, set flag in the 'is_visited' column to the 1 and check - is it true, that this user was on the previous step. If it is true 
	#set 'is_return' flag to 1 for the previous step
	if step_return_info['is_visited'][step_pos] == 0:
		step_return_info['is_visited'][step_pos] = 1
		
		#Check, is it true, that this user was on the previous step and there were not any returns on the previous step ('is_return' flag != -1). 
		#If it is true - set 'is_return' flag to 1 for the previous step
		if (step_pos != 0) and (step_return_info['is_visited'][step_pos - 1] == 1) and (step_return_info['is_return'][step_pos - 1] != -1):
			step_return_info['is_return'][step_pos - 1] = 1

	#If user enter the step not for the first time
	else:
		#We have the same check for the privious step
		if (step_pos != 0) and (step_return_info['is_visited'][step_pos - 1] == 1) and (step_return_info['is_return'][step_pos - 1] != -1):
			step_return_info['is_return'][step_pos - 1] = 1
		#If we have 'is_visited' and 'is_return' flags for this step equal to 1, it means that we were at this step before, then we were at the next step 
		#and now we return to the previous step, so, it is return and we increment value 'number_of_returns' for this step.
		#Then we set 'is_return' flag to -1. It means that this user have return on this step 
		#and we shouldn't count any other returns of this user on this step (and when we will move to the next user all flags will be set at 0)		
		if step_return_info['is_return'][step_pos] == 1:
			step_return_info['number_of_returns'][step_pos] += 1
			step_return_info['is_return'][step_pos] = -1

#Add new column in the dataframe for the result
step_return_info['result'] = 0

#Calculating the result
returns = np.array(step_return_info['number_of_returns']).astype(np.float)
visitors = np.array(step_return_info['number_of_visitors']).astype(np.float)
result = 100.0 * returns / visitors

#Set result values to the 'result' column of the dataframe, then sort dataframe values by 'result' from big to small
step_return_info['result'] = result
step_return_info = step_return_info.sort_values(by = 'result', ascending = False)

#Create a numpy array from top-10 step_id with biggest result and print it
np_result = np.array(step_return_info['step_id'].head(10))
print(np_result)