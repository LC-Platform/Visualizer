# USR Parser and Visualizer

This project provides a Python-based tool to parse USR (Universal Sentence Representation) data and visualize its hierarchical structure using Graphviz. The parser processes tokenized sentence data with dependency relations, and then generates a graphical representation in the form of an SVG file.

## Features
- **Parsing USR Data**: The parser handles USR data with tokens, their dependencies, and inter-sentence relations.
- **Graph Visualization**: Visualizes the sentence structure using Graphviz, with clear indications of token dependencies and relationships.
- **Construction and Inter-relations**: The tool also supports construction clusters and inter-sentence relations for a more comprehensive view.

## Project Structure


## Requirements

- **Python 3.x**  
- **Graphviz**  
  Install it via your package manager or [Graphviz Downloads](https://graphviz.gitlab.io/download/).

- Install the required Python libraries:
    ```bash
    pip install graphviz
    ```

## How to Use

### Step 1: Prepare Your Input File

Create a text file (`input_file.txt`) containing the USR data. This should be in the format defined by the parser, with sentences, tokens, part-of-speech tags, dependencies, etc.

### Step 2: Run the Shell Script

1. Make the shell script executable:
    ```bash
    chmod +x USR_to_Graph.sh
    ```

2. Run the script with the path to your input file:
    ```bash
    ./USR_to_Graph.sh input_file.txt
    ```

### Step 3: View the Output

After running the script, the generated visualization will be saved as `output_graph.svg` in the same directory. You can open this SVG file in any browser or vector graphic editor to view the parsed sentence structure.

## Example Input

Here’s an example of how the input might look:

<sent_id=Geonios_ch_0002>
#उसका एक दोस्त मोहन है ।
$wyax	1	-	-	3:rhh	1.1:coref	-	-	-
eka_1(a_2)	2	-	-	3:quant	-	-	-	-
xoswa_1(friend_1)	3	-	-	5:k1	-	-	-	-
mohana	4	per/male	-	5:k1s	-	-	-	-
hE_1-pres(state_copula_1-pres)	5	-	-	0:main	-	-	-	-
%affirmative
</sent_id>






## Output

The output will be an SVG file (`output_graph.svg`), representing the token dependencies and inter-sentence relations in a graphical form.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgments

- **Graphviz**: Used for visualizing sentence structures.
- **Python**: The primary language used for the parser and visualizer.

