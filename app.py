from flask import Flask, render_template, request
app = Flask(__name__, template_folder='template')


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

        return render_template('index.html')

if __name__=="__main__":
    app.run(debug=True)