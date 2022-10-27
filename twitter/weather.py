def cwb_weather_data(weather_data):
	location = weather_data['records']['location']

	taiwan_weather = []
	for i in location:
		city = i['locationName']
		wx12 = i['weatherElement'][0]['time'][0]['parameter']['parameterName'] # 天氣現象
		pop12 = i['weatherElement'][1]['time'][0]['parameter']['parameterName'] # 降雨機率
		minT12 = i['weatherElement'][2]['time'][0]['parameter']['parameterName'] # 最低溫
		maxT12 = i['weatherElement'][4]['time'][0]['parameter']['parameterName'] # 最高溫
		
		weather_dict = {
			'city':city,
			'wx12':wx12,
			'pop12':pop12,
			'minT12':minT12,
			'maxT12':maxT12
		}
		# print(f'{city} {wx12} 氣溫 {maxT12} - {minT12} 度  降雨機率 {pop12} %')
		taiwan_weather.append(weather_dict)
	return taiwan_weather