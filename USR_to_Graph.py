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
            token_id = token_data[1]
            word = token_data[0]
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
            
            
            # print(f"Processing token: {word} (ID: {token_id})")
            # Identify the main token
            if "0:main" in dependency_info:
                main_token = word
                # print(main_token)
                # print(f"Main token identified: {word} (ID: {token_id})")

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
            if  target_sentence_id.isdigit():
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
    print(inter_relations);
    return inter_relations


def create_json(tokens, main_token, inter_relations):
    # Create a mapping from token words to their IDs
    index_to_word = {token["id"]: token["word"] for token in tokens}
    
    # Create a mapping from token IDs to their corresponding words
    index_to_token = {token["id"]: token for token in tokens}

    updated_tokens = []
    for token in tokens:
        updated_relations = []
        for relation in token.get("relations", []):
            target_index = relation["target"]
            # Map target index to ID
            if target_index in index_to_word:
                updated_relations.append({
                    "target": index_to_word[target_index],  # Target word
                    "target_id": target_index,  # Target ID (added this line)
                    "label": relation["label"]
                })
        updated_tokens.append({
            "id": token["id"],
            "word": token["word"],
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

    # Identify the main token by combining the word and its ID
    if main_token:
        main_token_word = main_token
        main_token_id = None
        # Find the token ID of the main token
        for token in tokens:
            if token['word'] == main_token_word:
                main_token_id = token['id']
                break
        # If the main token exists in the sentence, combine the word and ID
        main_token_combined = f"{main_token_word}_{main_token_id}" if main_token_id else None
    else:
        main_token_combined = None

    return {
        "tokens": updated_tokens,
        "main": main_token_combined,  # Combine the main token with its ID
        "inter_relations": sentence_relations
    }

def convert_usr_to_dot(usr_data):
    dot = Digraph(comment='USR Representation')
    
    dot.attr(node='*', width='1.5', height='0.75', fontsize='6')

    # Process each sentence
    for sent_id, sentence in usr_data.items():
        sent_node = f'sent_{sent_id}'
        dot.node(sent_node, f'Sentence {sent_id}', shape='ellipse', color='blue', fillcolor='lightblue', style='filled')

        main_token = sentence['main']
        if main_token:
            main_token_combined = main_token  # main_token already combines the word and ID in the previous processing step
            main_node = f'{main_token_combined}'  # Use the combined word and ID for the main token
            dot.node(main_node, label=main_token_combined, shape='ellipse', fillcolor='lightgray')
            print(f"Connecting sentence node {sent_node} to main token {main_node}")
            dot.edge(sent_node, main_node, label='main', fontsize='8')  # Connect sentence to main token

        # Handle special constructions
        special_construction_clusters = {}

        # Create nodes for all tokens in the sentence
        for token in sentence['tokens']:
            token_word = token["word"]
            token_node = f'{token_word}_{token["id"]}'  # Unique node for each token using ID

            tooltip_info = f"semCat: {token['info']['semantic_category']}\n" \
                            f"morphSem: {token['info']['morpho_semantic']}\n" \
                            f"speakersView: {token['info']['speakers_view']}\n" \
                            f"Additional Info: {token['info']['additional_info']}"

            # Modify the label to include the token's word and its ID
            label = f"{token['word']}_{token['id']}"
            
            # Log the creation of each node
            print(f"Created token node: {token_node} (Word: {token['word']}, ID: {token['id']})")

            if '[' in token['word'] and ']' in token['word']:
                special_construction_clusters[token_node] = {"concept": f'{token["word"]}_{token["id"]}', "connected_nodes": set()}
                dot.node(token_node, label=label, shape='box', tooltip=tooltip_info)
            else:
                dot.node(token_node, label=label, tooltip=tooltip_info)

        # Add edges for token relationships
        for token in sentence['tokens']:
            token_word = token["word"]
            token_node = f'{token_word}_{token["id"]}'
            for relation in token['relations']:
                target_word = relation['target']
                target_id = relation['target_id']  # Use target ID as well
                label = relation['label']
                
                
                # Create edge between target and source token using both word and ID
                target_token_node = f'{target_word}_{target_id}'
                print(f"Creating edge: {token_node} -> {target_token_node} (Label: {label})")
                dot.edge(target_token_node, token_node, label=label, fontcolor="blue")

                if '[' in target_token_node and ']' in target_token_node:
                    if target_token_node in special_construction_clusters:
                        if label in {"op1", "op2", "op3", "op4", "op5", "op7", "op8", "start", "end", "mod", "head", "count", "unit", "component1", "component2", "component3", "component4", "component5", "component6", "unit_value", "unit_every", "whole", "part", "kriyAmUla", "verbalizer"}:
                            special_construction_clusters[target_token_node]["connected_nodes"].add(token_node)

        # Create clusters for special constructions
        for cluster_token, cluster_data in special_construction_clusters.items():
            cluster_name = f'cluster_{cluster_token}'
            with dot.subgraph(name=cluster_name) as cluster:
                cluster.attr(style='filled,dashed', color='black', fillcolor='lightgray', label=f'Construction: {cluster_data["concept"]}')
                cluster.node(cluster_token, label=cluster_data["concept"], shape='box')
                for node in cluster_data["connected_nodes"]:
                    cluster.node(node)

        # Add coreference edges
        for token in sentence['tokens']:
            if 'coref' in token['relations']:
                for coref_relation in token['relations']['coref']:
                    source_token_node = f'{token["word"]}_{token["id"]}'
                    target_token_node = f'{coref_relation["target_word"]}_{coref_relation["target_id"]}'
                    print(f"Creating coref edge: {source_token_node} -> {target_token_node}")
                    dot.edge(source_token_node, target_token_node, label='coref', color='red', style='dashed')

    return dot



# Code 2: Filter and generate graph
def process_and_visualize(usrs_text, sent_id_filter):
    # Parse the input text
    parsed_data = parse_usrs(usrs_text) 

    # Filter by sent_id and find discourse-related sentences
    filtered_data = {}
    if sent_id_filter in parsed_data:
        filtered_data[sent_id_filter] = parsed_data[sent_id_filter]

    # Check for any inter-sentence relations and include them
    for relation in parsed_data.get(sent_id_filter, {}).get("inter_relations", []):
        target_sentence = relation["target_sentence"]
        if target_sentence and target_sentence not in filtered_data:
            filtered_data[target_sentence] = parsed_data[target_sentence]

    # Convert filtered data to DOT format
    dot = convert_usr_to_dot(filtered_data)

    return dot

# Main code execution
if __name__ == '__main__':
    input_file = sys.argv[1]
    sent_id_filter = sys.argv[2]

    with open(input_file, "r") as file:
        usrs_text = file.read()

    # Process and visualize
    dot = process_and_visualize(usrs_text, sent_id_filter)

    # Save the output as an SVG file``
    output_file = f"sentence_{sent_id_filter}"
    dot.render(output_file, format="svg")
    print(f"Graph saved as {output_file}")
