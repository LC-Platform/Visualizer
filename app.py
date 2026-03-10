from flask import Flask, render_template, request
import os
from USR_to_Graph_original import process_and_visualize

app = Flask(__name__)

GRAPH_FOLDER = "static/graphs"
os.makedirs(GRAPH_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():

    graph_file = None

    if request.method == "POST":

        usr_text = request.form.get("usr")
        sent_id = request.form.get("sent_ids")

        dot = process_and_visualize(usr_text, sent_id)

        output_name = f"sentence_{sent_id}"
        output_path = os.path.join(GRAPH_FOLDER, output_name)

        dot.render(output_path, format="svg", cleanup=True)

        graph_file = f"graphs/{output_name}.svg"

    return render_template("index.html", graph_file=graph_file)


if __name__ == "__main__":
    app.run(debug=True)