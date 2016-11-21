import numpy as np
import pandas as pd


#Read course-217-events.csv file
events = pd.read_csv('data/course-217-events.csv', header = 0)
#Read course-217-structure.csv file
structure = pd.read_csv('data/course-217-structure.csv', header = 0)

#Some constants that we will need
max_time = events['time'].max()
max_user_id = events['user_id'].max()
number_of_events = events['user_id'].count()

#For each user find the first time he/she visit this course
first_time_visit = events.groupby('user_id').aggregate({'time': 'min'})

#For each event find it's cost
full_events_info = pd.merge(events, structure, on='step_id', how='inner')

#Add new column 'real_cost', because user will get step_cost only if he/she finish the task (action = 'passed')
full_events_info['real_cost'] = 0
full_events_info['real_cost'] = full_events_info[['action', 'step_cost']].apply(lambda x: x['step_cost'] if x['action'] == "passed" else 0, axis = 1)

#Create new array total_sum to set summary cost of the all previous steps for each user
total_sum = np.zeros(max_user_id + 1).astype(np.int)
#Create new array final_time to set time, when user ended course (when his/her total_sum[id_user] = 24)
final_time = np.zeros(max_user_id + 1).astype(np.int)

#Before filling two previous arrays we need to sort full_events_info dataframe by time
full_events_info = full_events_info.sort_values(by = ['time'])
full_events_info.index = np.array(range(number_of_events))

#Now we're ready to fill final_time array
for row in range(number_of_events):
	id = full_events_info['user_id'][row].astype(np.int)
	cost = full_events_info['real_cost'][row].astype(np.int)
	total_sum[id] += cost
	if total_sum[id] == 24:
		if final_time[id] == 0:
			final_time[id] = full_events_info['time'][row].astype(np.int)

#Create user_id_seq as a sequence from 0 to max_user_id to set as 'user_id' column in the final_time_df dataframe
user_id_seq = np.array(range(max_user_id + 1))

#Create dataframe with two columns: user_id and time, when user ended course
final_time_df = pd.DataFrame({'user_id': user_id_seq, 'final_time': final_time})

#Create resul_df dataframe as merge result of two dataframes to combine for each user time of his/her first visit and time, when he/she ended course
result_df = pd.merge(pd.DataFrame(first_time_visit), pd.DataFrame(final_time_df), left_index = True, right_index = True)

#Add new column for the course duration and fill it with the difference between final time and first time (if the user doesn't finish the course, we will fill this with max_time)
result_df['course_duration'] = 0
result_df['course_duration'] = result_df[['time', 'final_time']].apply(lambda x: x['final_time'] - x['time'] if x['final_time'] != 0 else max_time, axis = 1)

#Sort results
result_df = result_df.sort_values(by = 'course_duration')

#Get first ten values
result_array = np.array(result_df['user_id'].head(10))
print(result_array)