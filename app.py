from flask import Flask, render_template, request
from flask_apscheduler import APScheduler
from config import Config
import database



app = Flask(__name__, template_folder='templates')
scheduler = APScheduler()

@app.route("/", methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':
        
        setting_dict = {}
        setting_dict["latitude"]           = request.form['latitude']
        setting_dict["longitude"]          = request.form['longitude']
        setting_dict["threshold_value"]    = request.form['threshold_value']
        setting_dict["check_in_frequency"] = request.form['check_in_frequency']
        
        setting_text_template= """# Location Information\nlatitude = {latitude}\nlongitude = {longitude}\n# Application Settings\nthreshold_value = {threshold_value}\ncheck_in_frequency = {check_in_frequency}""".format(
            latitude = setting_dict["latitude"] ,
            longitude = setting_dict["longitude"],
            threshold_value = setting_dict["threshold_value"],
            check_in_frequency = setting_dict["check_in_frequency"])
        

        func = database.process(latitude = setting_dict["latitude"], longitude = setting_dict["longitude"],
                        threshold_value = setting_dict["threshold_value"], check_in_frequency = setting_dict["check_in_frequency"],
                        database_name="290120221asdakif")
        func.clean_sql_database()

        with open('settings.txt', "w") as textfile:
            textfile.write(setting_text_template)

        
    else:
        a_file = open("settings.txt", "r")
        list_of_lines = a_file.readlines()
        a_file.close()

        set_dict = {} 
        for i in range(len(list_of_lines)):
            for j in range(len(list_of_lines[i].split("= "))):
                
                temp_variable = list_of_lines[i].split("= ")[j].strip()
                if(temp_variable == "latitude" or 
                temp_variable == "longitude" or
                temp_variable == "threshold_value" or
                temp_variable == "check_in_frequency"):
                    set_dict[temp_variable] = list_of_lines[i].split("= ")[j+1].replace("\n","")

        func = database.process(latitude = set_dict["latitude"], longitude = set_dict["longitude"],
                                threshold_value = set_dict["threshold_value"], check_in_frequency = set_dict["check_in_frequency"],
                                database_name="290120221asdakif")

    first_10_list, request_text = func.main_process()
    return render_template('template.html', table=tuple(first_10_list), data=str(request_text))

def scheduledTask():
    print("This task is running every 5 seconds")

if __name__=="__main__":
    scheduler.add_job(id ='Scheduled task', func = scheduledTask, trigger = 'interval', seconds = 5)
    scheduler.start()
    app.run(debug=True)
