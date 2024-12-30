import re
import json
from graphviz import Digraph
import sys

# Code 1: Parsing function
def parse_usrs(usrs_text):
    sentences = {}
    current_sentence_id = None
    current_tokens = []
    main_token = None
    discourse_relations = []

    for line in usrs_text.strip().splitlines():
        line = line.strip()

        # Handle sentence ID (lines starting with <sent_id=)
        if line.startswith("<sent_id="):
            if current_sentence_id:
                sentences[current_sentence_id] = create_json(current_tokens, main_token, discourse_relations)
            current_sentence_id = re.search(r"<sent_id=(\S+)>", line).group(1)
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
            part_of_speech = token_data[2] if len(token_data) > 2 else "-"
            dependency_info = token_data[4] if len(token_data) > 4 else "-"
            construction_info = token_data[8] if len(token_data) > 8 else "-"
            
            # Prepare info with the required columns
            info = {
                "part_of_speech": part_of_speech,
                "dependency": dependency_info,
                "extra_info": token_data[3] if len(token_data) > 3 else "-",
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

            print(f"Appending token: {token_id} - {word}")
            current_tokens.append({"id": token_id, "word": word, "relations": relations, "info": info})

            # Process inter-relations from the additional_info field
            if info["additional_info"] != "-":
                discourse_relations += parse_discourse_relations(info["additional_info"], token_id, current_sentence_id, sentences)


        if current_sentence_id:
            sentences[current_sentence_id] = create_json(current_tokens, main_token, discourse_relations)
    
    return sentences



def parse_discourse_relations(data, source_token, source_sentence, sentences):
    discourse_relations = []
    
    # Split the input data (additional_info) into individual relations
    for relation in data.split("|"):
        if ":" in relation:
            target_sentence_id, relation_type = relation.split(":")
            
            # Handle relations within the same sentence
            if target_sentence_id.isdigit():
                target_sentence = source_sentence  # Same sentence as source_sentence
                target_token = target_sentence_id  # Token ID in the same sentence

                # Debug: Ensure target token exists
                print(f"Searching for target token ID: {target_token}") 
                
                # Iterate over all tokens in the current sentence
                target_word = None
                for token in sentences[source_sentence].get("tokens", []):
                    print(f"Comparing token ID: {token['id']} with target token: {target_token}")
                    # Ensure we're comparing as integers, not strings
                    if int(token["id"]) == int(target_token):  # Convert both to integers for comparison
                        target_word = token["word"]
                
                # Debug: Output target token match
                if target_word:
                    print(f"Found target token: {target_word} (ID: {target_token})")
                else:
                    print(f"No match found for Target Token ID: {target_token} in sentence {source_sentence}")

            # Handle relations across sentences (if applicable)
            else:
                target_sentence = target_sentence_id  # Assuming it’s across sentences
                target_token = None
                target_word = None

                # If target_sentence contains a '.', it's a reference to a token in a different sentence
                if '.' in target_sentence_id:
                    target_sentence, target_token = target_sentence_id.split(".")
                else:
                    target_sentence, target_token = target_sentence_id, None

                # Search for the target sentence
                target_sentence_found = None
                for sentence_id in sentences:
                    if target_sentence in sentence_id:
                        target_sentence_found = sentence_id
                        break

                if target_sentence_found and target_token:
                    # Iterate over tokens in the found target sentence to match the target token
                    for token in sentences[target_sentence_found].get("tokens", []):
                        if int(token["id"]) == int(target_token):
                            target_word = token["word"]
                            

            # Add the inter-relation to the list
            discourse_relations.append({
                "source_token": source_token,
                "target_token": target_token,
                "target_word": target_word,
                "source_sentence": source_sentence,
                "target_sentence": target_sentence,
                "relation": relation_type
            })

    print(f"Final Inter-Relations: {discourse_relations}")
    return discourse_relations





def create_json(tokens, main_token, discourse_relations):
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
    for relation in discourse_relations:
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
        "discourse_relations": sentence_relations
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
            tooltip_info = f"POS: {token['info']['part_of_speech']}\n" \
                           f"Dependency: {token['info']['dependency']}\n" \
                           f"Extra Info: {token['info']['extra_info']}\n" \
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
        for relation in sentence['discourse_relations']:
            source_token_node = f'{relation["source_sentence"]}_{relation["source_token"]}'
            target_token_node = f'{relation["target_sentence"]}_{relation["target_word"]}'
            dot.edge(source_token_node, target_token_node, label=relation["relation"], color='red', style='dotted')

    return dot



# Example usage
if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print("Usage: python USR_to_Graph.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r", encoding="utf-8") as file:
        usrs_text = file.read()

    parsed_data = parse_usrs(usrs_text)
    dot_graph = convert_usr_to_dot(parsed_data)
    dot_graph.render('output_graph', format='svg', cleanup=True)
    print("Graph rendered as output_graph.svg")
