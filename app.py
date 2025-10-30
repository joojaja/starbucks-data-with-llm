from flask import Flask, render_template, request, jsonify
from groq_api import groq_summarise_nutrition
from load_data import *
from process_data import *

app = Flask(__name__)

# dataframe variables
df_food = None
df_drinks = None

@app.route('/', methods=['GET', 'POST'])
def home():
    global df_food, df_drinks

    if df_food is None:
        # Load default file
        df_food = load_csv_file_into_dataframe('dataset/starbucks-menu-nutrition-food.csv')

    if df_drinks is None:
        # Load default file
        df_drinks = load_csv_file_into_dataframe('dataset/starbucks-menu-nutrition-drinks.csv')

    # Convert whole dataframe to list of dict records
    food_data_list = df_food.reset_index().to_dict(orient='records')
    drink_data_list = df_drinks.reset_index().to_dict(orient='records')
    
    # Get averages
    food_avg = get_average_nutrition_each_column(df_food)
    drink_avg = get_average_nutrition_each_column(df_drinks)

    # Default: show all nutrients
    all_nutrients = get_union_of_keys(df_food, df_drinks)
    selected_nutrients = all_nutrients
    
    # Build comparison data filtered by selection
    table_data = []
    for n in selected_nutrients:
        table_data.append({
            'nutrient': n,
            'food_avg': food_avg.get(n, "None provided in data file"),
            'drink_avg': drink_avg.get(n, "None provided in data file"),
        })

    food_items = df_food.index.tolist()
    drink_items = df_drinks.index.tolist()

    return render_template('index.html',
                           ## used for showing data and filtering
                           food_data=food_data_list, 
                           drink_data=drink_data_list,

                           # used for showing comparison 
                           table_data=table_data,
                           all_nutrients=all_nutrients,
                           selected=selected_nutrients,

                           # used for bar chart
                           food_items=food_items,
                           drink_items=drink_items)

@app.route('/compare_items')
def compare_items():
    food_item = request.args.get('food')
    drink_item = request.args.get('drink')

    # Get nutrition row for each (handle if not found)
    food_row = df_food.loc[food_item] if food_item in df_food.index else None
    drink_row = df_drinks.loc[drink_item] if drink_item in df_drinks.index else None

    nutrients = ['Calories', 'Fat', 'Carb.', 'Fiber', 'Protein', 'Fat-to-Protein Ratio']

    response = {"food": {}, "drink": {}}
    if food_row is not None:
        for n in nutrients:
            response["food"][n] = food_row.get(n, None) if n in food_row else None
    if drink_row is not None:
        for n in nutrients:
            response["drink"][n] = drink_row.get(n, None) if n in drink_row else None

    return jsonify(response)

# used to call the LLM API
@app.route('/llm_summary', methods=['POST'])
def llm_summary():
    data = request.json
    user_prompt = data.get("prompt", "")

    try:
        summary = groq_summarise_nutrition(user_prompt, df_food, df_drinks)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# used for manual uploading of files
@app.route('/upload_files', methods=['POST'])
def upload_files():
    if 'food_file' not in request.files or 'drink_file' not in request.files:
        return {"error": "Missing one or both files"}, 400

    food_file = request.files['food_file']
    drink_file = request.files['drink_file']

    # Save file streams into pandas DataFrames:
    try:
        global df_food, df_drinks  # reassign global variables
        df_food = load_csv_file_into_dataframe(food_file)
        df_drinks = load_csv_file_into_dataframe(drink_file)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}, 500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
