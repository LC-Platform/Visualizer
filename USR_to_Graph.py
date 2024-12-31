import re
import json
from graphviz import Digraph
import sys


def parse_usrs(usrs_text):
    sentences = {}
    current_sentence_id = None
    current_tokens = []
    main_token = None
    inter_relations = []

    for line in usrs_text.strip().splitlines():
        line = line.strip()

        # Handle sentence ID (lines starting with <sent_id=)
        if line.startswith("<sent_id="):
            if current_sentence_id:
                sentences[current_sentence_id] = create_json(current_tokens, main_token, inter_relations)
            current_sentence_id = re.search(r"<sent_id=\s*(\S+)>", line).group(1)
            current_tokens = []
            main_token = None
            inter_relations = []
        
        # Skip lines with 1 column (comments, sentence markers, etc.)
        elif len(line.split("\t")) == 1:
            continue  
        
        elif not line.startswith(("#", "<", "%")) and line:
            line = re.sub(r'\s+', '\t', line).strip()  

            token_data = line.split("\t")
            token_id = token_data[0]
            word = token_data[1]
            semantic_category = token_data[2] if len(token_data) > 2 else "-"
            dependency_info = token_data[4] if len(token_data) > 4 else "-"
            construction_info = token_data[8] if len(token_data) > 8 else "-"
            
            # Prepare info with the required columns
            info = {
                "semantic_category": semantic_category,
                "morpho_semantic": token_data[3] if len(token_data) > 3 else "-",
                "speakers_view": token_data[6] if len(token_data) > 6 else "-",
                "additional_info": token_data[5] if len(token_data) > 5 else "-"
             }

            relations = []
            # Check for relations in dependency info
            if dependency_info and dependency_info != "-":
                for dep in dependency_info.split("|"):
                    target, label = dep.split(":")
                    relations.append({"target": target, "label": label})
                    
            # Check for relations in the construction column
            elif construction_info and construction_info != "-":
                for dep in construction_info.split("|"):
                    target, label = dep.split(":")
                    relations.append({"target": target, "label": label})
            
            # Identify the main token
            if dependency_info.endswith("0:main"):
                main_token = token_id

            current_tokens.append({"id": token_id, "word": word, "relations": relations, "info": info})

            # Process inter-relations from the additional_info field
            if info["additional_info"] != "-":
                inter_relations += parse_inter_relations(info["additional_info"], token_id, current_sentence_id, sentences)


        if current_sentence_id:
            sentences[current_sentence_id] = create_json(current_tokens, main_token, inter_relations)
    
    return sentences

def parse_inter_relations(data, source_token, source_sentence, sentences):
    inter_relations = []
    for relation in data.split("|"):
        if ":" in relation:
            target_sentence_id, relation_type = relation.split(":")

            # Case 1: Target is within the same sentence (e.g., "1:coref")
            if target_sentence_id.isdigit():
                target_sentence = source_sentence  # Same sentence
                target_token = target_sentence_id  # Token ID in the same sentence
            # Case 2: Target is in a different sentence (e.g., "2.3:coref")
            elif '.' in target_sentence_id:
                target_sentence, target_token = target_sentence_id.split(".")
            else:
                target_sentence, target_token = target_sentence_id, None

            target_sentence_found = None
            target_word = None

            # Check if the target is within the current sentence
            if target_sentence == source_sentence:
                target_sentence_found = source_sentence  # Same sentence

                # Locate the target word within the current sentence
                for token in sentences[source_sentence].get("tokens", []):
                    if token["id"] == target_token:  # Match token ID
                        target_word = token["word"]
                        break
            else:
                # Otherwise, look for the target in other sentences
                for sentence_id in sentences:
                    if target_sentence in sentence_id:
                        target_sentence_found = sentence_id
                        break

                if target_sentence_found and target_token:
                    # Locate the target word in the identified sentence
                    for token in sentences[target_sentence_found].get("tokens", []):
                        if token["id"] == target_token:
                            target_word = token["word"]
                            break

            inter_relations.append({
                "source_token": source_token,
                "target_token": target_token,
                "target_word": target_word,
                "source_sentence": source_sentence,
                "target_sentence": target_sentence_found if target_sentence_found else target_sentence,
                "relation": relation_type
            })
    return inter_relations





def create_json(tokens, main_token, inter_relations):
    # Create a mapping from token words to their IDs
    index_to_id = {token["word"]: token["id"] for token in tokens}

    updated_tokens = []
    for token in tokens:
        updated_relations = []
        for relation in token.get("relations", []):
            target_index = relation["target"]
            # Map target index to ID
            if target_index in index_to_id:
                updated_relations.append({
                    "target": index_to_id[target_index],
                    "label": relation["label"]
                })
        updated_tokens.append({
            "id": token["word"],
            "word": token["id"],
            "relations": updated_relations,
            "info": token.get("info", {})
        })

    # Process inter-relations (sentence-level relations)
    sentence_relations = []
    for relation in inter_relations:
        sentence_relations.append({
            "source_token": relation["source_token"],
            "target_token": relation["target_token"],
            "target_word": relation["target_word"],  # Include target word
            "source_sentence": relation["source_sentence"],
            "target_sentence": relation["target_sentence"],
            "relation": relation["relation"]
        })

    return {
        "tokens": updated_tokens,
        "main": main_token,
        "inter_relations": sentence_relations
    }


# Code 2: Graph visualization
def convert_usr_to_dot(usr_data):
    dot = Digraph(comment='USR Representation')
    
    def natural_sort_key(s):
    # Extract numbers and characters for sorting
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    # Sort the sentences by their IDs
    sorted_sentence_ids = sorted(usr_data.keys(), key=natural_sort_key)
    

    for sent_id in sorted_sentence_ids:
        sentence = usr_data[sent_id]
        sent_node = f'sent_{sent_id}'
        dot.node(sent_node, f'Sentence {sent_id}', shape='ellipse')

        # Main predicate of the sentence
        main_token = sentence['main']
        main_node = f'{sent_id}_{main_token}'
        dot.node(main_node, label=main_token, shape='ellipse')

        # Connect the sentence node to the main predicate
        dot.edge(sent_node, main_node, label='main', fontsize='10')

        # Identify all special constructions and their connected nodes with specific relations
        special_construction_clusters = {}

        # Create nodes for all the tokens in the sentence
        for token in sentence['tokens']:
            token_node = f'{sent_id}_{token["word"]}'

            # Tooltip info
            tooltip_info = f"semCat: {token['info']['semantic_category']}\n" \
                           f"morphSem: {token['info']['morpho_semantic']}\n" \
                           f"speakersView: {token['info']['speakers_view']}\n" \
                           f"Additional Info: {token['info']['additional_info']}"
                           
                        
            if '[' in token['word'] and ']' in token['word']:
                special_construction_clusters[token_node] = {"concept": token['word'], "connected_nodes": set()}
                dot.node(token_node, label=token['word'], shape='box', tooltip=tooltip_info)
            else:
                dot.node(token_node, label=token['word'], tooltip=tooltip_info)

        # Add edges for token relationships
        for token in sentence['tokens']:
            token_node = f'{sent_id}_{token["word"]}'
            for relation in token['relations']:
                target_token = f'{sent_id}_{relation["target"]}'
                label = relation['label']
                dot.edge(target_token, token_node, label=label)

                if '[' in target_token and ']' in target_token:
                    if target_token in special_construction_clusters:
                        if label in { "op1","op2","op3","op4","op5","op7","op8","start","end","mod","head","count","unit","component1","component2","component3","component4","component5","component6","unit_value","unit_every","whole","part","kriyAmUla","verbalizer"}:
                            special_construction_clusters[target_token]["connected_nodes"].add(token_node)

        # Create clusters for special constructions
        for cluster_token, cluster_data in special_construction_clusters.items():
            cluster_name = f'cluster_{cluster_token}'
            with dot.subgraph(name=cluster_name) as cluster:
                cluster.attr(style='filled,dashed', color='black', fillcolor='lightgray', label=f'Construction: {cluster_data["concept"]}')
                cluster.node(cluster_token, label=cluster_data["concept"], shape='box')
                for node in cluster_data["connected_nodes"]:
                    cluster.node(node)

        # Add inter-sentence relationships
        for relation in sentence['inter_relations']:
            source_token_node = f'{relation["source_sentence"]}_{relation["source_token"]}'
            target_token_node = f'{relation["target_sentence"]}_{relation["target_word"]}'
            dot.edge(source_token_node, target_token_node, label=relation["relation"], color='red', style='dotted')

    return dot



# Example usage
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python USR_to_Graph.py <input_file> <sent_id>")
        sys.exit(1)

    input_file = sys.argv[1]
    sent_id_filter = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as file:
        usrs_text = file.read()

    # Parse the data
    parsed_data = parse_usrs(usrs_text)

    # Filter by sent_id
    if sent_id_filter not in parsed_data:
        print(f"Error: Sentence ID '{sent_id_filter}' not found in the input file.")
        sys.exit(1)

    filtered_data = {sent_id_filter: parsed_data[sent_id_filter]}

    # Generate the graph
    dot_graph = convert_usr_to_dot(filtered_data)
    output_file = f'output_graph_{sent_id_filter}'
    dot_graph.render(output_file, format='svg', cleanup=True)
    print(f"Graph rendered as {output_file}.svg")
