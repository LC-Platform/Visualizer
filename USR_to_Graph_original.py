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

        if line.startswith("<segment_id="):
            if current_sentence_id:
                sentences[current_sentence_id] = create_json(current_tokens, main_token, inter_relations)
            current_sentence_id = re.search(r"<segment_id=\s*(\S+)>", line).group(1)
            current_tokens = []
            main_token = None
            inter_relations = []
        
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
            
            info = {
                "semantic_category": semantic_category,
                "morpho_semantic": token_data[3] if len(token_data) > 3 else "-",
                "speakers_view": token_data[6] if len(token_data) > 6 else "-",
                "additional_info": token_data[5] if len(token_data) > 5 else "-"
             }

            relations = []
            if dependency_info and dependency_info != "-":
                for dep in dependency_info.split("|"):
                    target, label = dep.split(":")
                    relations.append({"target": target, "label": label})
                    
            elif construction_info and construction_info != "-":
                for dep in construction_info.split("|"):
                    target, label = dep.split(":")
                    relations.append({"target": target, "label": label})
            
            if "0:main" in dependency_info:
                main_token = word

            current_tokens.append({"id": token_id, "word": word, "relations": relations, "info": info})

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

            if target_sentence_id.isdigit():
                target_sentence = source_sentence
                target_token = target_sentence_id
            elif '.' in target_sentence_id:
                target_sentence, target_token = target_sentence_id.split(".")
            else:
                target_sentence, target_token = target_sentence_id, None

            target_sentence_found = None
            target_word = None

            if target_sentence == source_sentence:
                target_sentence_found = source_sentence
                for token in sentences[source_sentence].get("tokens", []):
                    if token["id"] == target_token:
                        target_word = token["word"]
                        break
            else:
                for sentence_id in sentences:
                    if target_sentence in sentence_id:
                        target_sentence_found = sentence_id
                        break

                if target_sentence_found and target_token:
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
    print(inter_relations)
    return inter_relations


def create_json(tokens, main_token, inter_relations):
    index_to_word = {token["id"]: token["word"] for token in tokens}
    index_to_token = {token["id"]: token for token in tokens}

    updated_tokens = []
    for token in tokens:
        updated_relations = []
        for relation in token.get("relations", []):
            target_index = relation["target"]
            if target_index in index_to_word:
                updated_relations.append({
                    "target": index_to_word[target_index],
                    "target_id": target_index,
                    "label": relation["label"]
                })
        updated_tokens.append({
            "id": token["id"],
            "word": token["word"],
            "relations": updated_relations,
            "info": token.get("info", {})
        })

    sentence_relations = []
    for relation in inter_relations:
        sentence_relations.append({
            "source_token": relation["source_token"],
            "target_token": relation["target_token"],
            "target_word": relation["target_word"],
            "source_sentence": relation["source_sentence"],
            "target_sentence": relation["target_sentence"],
            "relation": relation["relation"]
        })

    if main_token:
        main_token_word = main_token
        main_token_id = None
        for token in tokens:
            if token['word'] == main_token_word:
                main_token_id = token['id']
                break
        main_token_combined = f"{main_token_word}_{main_token_id}" if main_token_id else None
    else:
        main_token_combined = None

    return {
        "tokens": updated_tokens,
        "main": main_token_combined,
        "inter_relations": sentence_relations
    }

def convert_usr_to_dot(usr_data):
    dot = Digraph(comment='USR Representation')
    dot.attr(rankdir='TB')
    dot.attr(node='*', width='1.5', height='0.75', fontsize='6')

    # ── Collect all cross-sentence pairs so we can place them side by side ──
    # Build a set of (sent_a, sent_b) pairs that share an inter-relation
    cross_pairs = set()
    for sent_id, sentence in usr_data.items():
        for rel in sentence.get("inter_relations", []):
            src = rel["source_sentence"]
            tgt = rel["target_sentence"]
            if src and tgt and src != tgt and src in usr_data and tgt in usr_data:
                pair = tuple(sorted([src, tgt]))
                cross_pairs.add(pair)

    # For each such pair, we'll emit a subgraph with rank=same so Graphviz
    # places their sentence-root nodes on the same rank (side by side).
    already_ranked = set()
    for pair in cross_pairs:
        sent_a, sent_b = pair
        subgraph_name = f"same_rank_{sent_a}_{sent_b}"
        with dot.subgraph(name=subgraph_name) as sg:
            sg.attr(rank='same')
            sg.node(f'sent_{sent_a}')
            sg.node(f'sent_{sent_b}')
        already_ranked.add(sent_a)
        already_ranked.add(sent_b)

    # ── Now render each sentence as before ──
    for sent_id, sentence in usr_data.items():
        sent_node = f'sent_{sent_id}'
        dot.node(sent_node, f'Sentence {sent_id}', shape='ellipse',
                 color='blue', fillcolor='lightblue', style='filled')

        if sentence['main']:
            dot.node(sentence['main'], label=sentence['main'],
                     shape='ellipse', fillcolor='lightgray')
            dot.edge(sent_node, sentence['main'], label='main', fontsize='8')

        special_construction_clusters = {}

        for token in sentence['tokens']:
            token_node = f'{token["word"]}_{token["id"]}'
            label = f"{token['word']}:{token['id']}\n"
            tooltip_info = (
                f"semCat: {token['info']['semantic_category']}\n"
                f"morphSem: {token['info']['morpho_semantic']}\n"
                f"speakersView: {token['info']['speakers_view']}\n"
                f"Additional Info: {token['info']['additional_info']}"
            )

            if '[' in token['word'] and ']' in token['word']:
                special_construction_clusters[token_node] = {
                    "concept": label,
                    "connected_nodes": set()
                }
                dot.node(token_node, label=label, shape='box', tooltip=tooltip_info)
            else:
                dot.node(token_node, label=label, tooltip=tooltip_info)

        for token in sentence['tokens']:
            token_node = f'{token["word"]}_{token["id"]}'
            for relation in token['relations']:
                if 'target' in relation and 'target_id' in relation:
                    target_node = f'{relation["target"]}_{relation["target_id"]}'
                    dot.edge(target_node, token_node, label=relation['label'], fontcolor="blue")

                    if '[' in target_node and ']' in target_node:
                        if target_node in special_construction_clusters:
                            if relation['label'] in {
                                "op1", "op2", "op3", "op4", "op5", "op7", "op8",
                                "start", "end", "mod", "head", "count", "unit",
                                "component1", "component2", "component3", "component4",
                                "component5", "component6", "unit_value", "unit_every",
                                "whole", "part", "kriyAmUla", "verbalizer"
                            }:
                                special_construction_clusters[target_node]["connected_nodes"].add(token_node)

        for cluster_token, cluster_data in special_construction_clusters.items():
            with dot.subgraph(name=f'cluster_{cluster_token}') as cluster:
                cluster.attr(
                    style='filled,dashed',
                    color='black',
                    fillcolor='lightgray',
                    label=f'Construction: {cluster_data["concept"]}'
                )
                cluster.node(cluster_token, label=cluster_data["concept"], shape='box')
                for node in cluster_data["connected_nodes"]:
                    cluster.node(node)

        for relation in sentence.get("inter_relations", []):
            source_token = f'{relation["source_token"]}'
            target_token = f'{relation["target_token"]}'
            target_sentence = relation["target_sentence"]

            if not target_token or not target_sentence:
                continue

            source_node = None
            target_node = None

            for token in sentence['tokens']:
                if str(token['id']) == source_token:
                    source_node = f'{token["word"]}_{token["id"]}'
                    break

            if target_sentence in usr_data:
                for token in usr_data[target_sentence]['tokens']:
                    if str(token['id']) == target_token:
                        target_node = f'{token["word"]}_{token["id"]}'
                        break

            if source_node and target_node:
                dot.edge(source_node, target_node,
                         label=relation["relation"], color="red", fontcolor="red")

    return dot


def process_and_visualize(usrs_text, sent_id_filter):
    parsed_data = parse_usrs(usrs_text)

    filtered_data = {}
    if sent_id_filter in parsed_data:
        filtered_data[sent_id_filter] = parsed_data[sent_id_filter]

    for relation in parsed_data.get(sent_id_filter, {}).get("inter_relations", []):
        target_sentence = relation["target_sentence"]
        if target_sentence and target_sentence not in filtered_data:
            filtered_data[target_sentence] = parsed_data[target_sentence]

    dot = convert_usr_to_dot(filtered_data)
    return dot


if __name__ == '__main__':
    input_file = sys.argv[1]
    sent_id_filter = sys.argv[2]

    with open(input_file, "r") as file:
        usrs_text = file.read()

    dot = process_and_visualize(usrs_text, sent_id_filter)

    output_file = f"sentence_{sent_id_filter}"
    dot.render(output_file, format="svg")
    print(f"Graph saved as {output_file}")