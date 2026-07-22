from flask import Flask, render_template, jsonify
import os
import json

app = Flask(__name__, template_folder='../web', static_folder='../web')

# Load plant data
def load_plant_data():
    plant_data = {}
    species_dir = 'data/species'

    for filename in os.listdir(species_dir):
        if filename.endswith('.json'):
            with open(os.path.join(species_dir, filename), 'r') as f:
                data = json.load(f)
                plant_data[data['scientific_name']] = data

    return plant_data

plant_data = load_plant_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plant_data')
def get_plant_data():
    return jsonify(plant_data)

@app.route('/api/care_info/<species>')
def get_care_info(species):
    if species in plant_data:
        return jsonify(plant_data[species]['care'])
    return jsonify({'error': 'Species not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)