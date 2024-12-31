# USR Visualizer

This project provides a Python-based tool to parse USR (Universal Sentence Representation) data and visualize its hierarchical structure using Graphviz. The parser processes tokenized sentence data with dependency relations and generates a graphical representation in the form of an SVG file.

---

## Features
- **Parsing USR Data**: Handles USR data with tokens, their dependencies, and inter-sentence relations.
- **Graph Visualization**: Visualizes sentence structure using Graphviz, with clear indications of token dependencies and relationships.
- **Construction and Inter-relations**: Supports construction clusters and inter-sentence relations for a comprehensive view.

---

## Project Structure

- `USR_to_Graph.py`: The main Python script for parsing USR data and generating the Graphviz representation.
- `USR_to_Graph.sh`: A shell script to automate the process of running the parser and generating the SVG visualization.
- `input_file.txt`: Example input file containing USR data.
- `output_graph.svg`: The resulting SVG file generated after running the script.

---

## Requirements

- **Python 3.x**  
- **Graphviz**  
  Install it via your package manager or [Graphviz Downloads](https://graphviz.gitlab.io/download/).
- Install the required Python libraries:
    ```bash
    pip install graphviz
    ```

---

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

### Step 2: Create a Virtual Environment
```bash
#for windows
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activat

# for linux

sudo apt update
sudo apt install python3-venv

python3 -m venv venv

source venv/bin/activate

```


### Step 3: Install Requirements
```bash
pip install graphviz   #windows
```

```bash
sudo apt update
sudo apt install graphviz   # for linux
```

### Step 4: Make the Shell Script Executable
```bash
chmod +x USR_to_Graph.sh
```

---

## How to Use

### Step 1: Prepare Your Input File
Create a text file (`input_file.txt`) containing the USR data in the  vertical format. For example:

```
<sent_id=3>
#राम और मोहन पास के एक स्कूल में पढ़ते हैं ।
#Ram and Mohan study in a nearby school ।
rAma	6	per/male	-	-	-	-	-	1:op1
mohana	7	per/male	-	-	-	-	-	1:op2
[conj_1]	1	-	-	5:k1	-	-	-	-
pAsa_1(nearby_1)	2	-	-	4:r6	-	-	-	-
eka_1(a_2)	3	-	-	4:quant	-	-	-	-
skUla_1(school_10)	4	-	-	5:k7p	-	-	-	-
paDZa_1-wA_hE_1(study_3-pres)	5	-	-	0:main	-	-	-	-
%affirmative
</sent_id>
```

### Step 2: Run the Shell Script
Run the shell script with the path to your input file:
```bash
./USR_to_Graph.sh input_file.txt Geonios_ch_0006   #incase of single sentences
```
```bash
./USR_to_Graph.sh input.txt Geonios_ch_0006 Geonios_ch_0007a    # incase of multiple sentences
```
### Step 3: View the Output
After running the script, the generated visualization will be saved as `output_graph.svg` in the same directory. Open the SVG file in a browser or vector graphic editor to view the parsed sentence structure.

Open the svg file using a browser to view the svg graph
---

## Example Input and Output

### Example Input (`input_file.txt`)
```plaintext
<sent_id=3>
#राम और मोहन पास के एक स्कूल में पढ़ते हैं ।
#Ram and Mohan study in a nearby school ।
rAma	6	per/male	-	-	-	-	-	1:op1
mohana	7	per/male	-	-	-	-	-	1:op2
[conj_1]	1	-	-	5:k1	-	-	-	-
pAsa_1(nearby_1)	2	-	-	4:r6	-	-	-	-
eka_1(a_2)	3	-	-	4:quant	-	-	-	-
skUla_1(school_10)	4	-	-	5:k7p	-	-	-	-
paDZa_1-wA_hE_1(study_3-pres)	5	-	-	0:main	-	-	-	-
%affirmative
</sent_id>
```

### Output
The output will be an SVG file named `output_graph.svg`, visually representing token dependencies and inter-sentence relations.



![Screenshot from 2024-12-28 10-10-32](https://github.com/user-attachments/assets/c1df192a-d75f-40e8-aa17-f71be4adf356)

---

## Acknowledgments

- **Graphviz**: Used for visualizing sentence structures.
- **Python**: The primary language used for the parser and visualizer.
