Below is a **clean updated README** that enforces using a **Python virtual environment (`venv`)** before running the visualizer UI.
Users will:

1. Create a virtual environment
2. Activate it
3. Install dependencies
4. Run the UI

You can copy this directly into  **README.md** .

---

# README.md

```markdown
# USR Graph Visualizer

The **USR Graph Visualizer** converts **USR (Universal Semantic Representation)** formatted annotations into **graph visualizations** using Graphviz.

It parses USR data and generates **dependency graphs in SVG format**, allowing linguists and researchers to visually inspect semantic relations between tokens.

The tool supports:

- Dependency relations
- Construction clusters
- Inter-sentence relations (coreference / discourse)
- Visualization using Graphviz
- A simple web UI to paste USR and generate graphs instantly

---

# Requirements

- Python 3.8+
- Graphviz (system installation)
- Python packages:
  - graphviz
  - flask

---

# Installing Graphviz

Graphviz must be installed **on the system** before running the tool.

Official website:

https://graphviz.org/

---

# Install Graphviz on Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install graphviz
```

Verify installation:

```bash
dot -V
```

Example output:

```
dot - graphviz version X.X
```

---

# Install Graphviz on Windows

### Step 1 – Download Graphviz

Download from:

[https://graphviz.org/download/](https://graphviz.org/download/)

Example installer:

```
graphviz-10.x.x-win64.exe
```

---

### Step 2 – Install Graphviz

Run the installer.

Default installation path:

```
C:\Program Files\Graphviz\
```

---

### Step 3 – Add Graphviz to PATH

Add this directory to  **System PATH** :

```
C:\Program Files\Graphviz\bin
```

---

### Step 4 – Verify installation

Open **Command Prompt** and run:

```
dot -V
```

Expected output:

```
dot - graphviz version X.X
```

---

# Setup Python Virtual Environment

It is recommended to run the visualizer inside a  **Python virtual environment** .

Navigate to the project directory:

```bash
cd Visualizer
```

---

## Create virtual environment

Linux / macOS:

```bash
python3 -m venv venv
```

Windows:

```bash
python -m venv venv
```

---

## Activate virtual environment

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

After activation you should see:

```
(venv)
```

in your terminal.

---

# Install Python Dependencies

After activating the virtual environment install dependencies:

```bash
pip install flask graphviz
```

---

# Running the Web UI

After activating the virtual environment run:

```bash
python app.py
```

The server will start:

```
Running on http://127.0.0.1:5000
```

Open in browser:

```
http://127.0.0.1:5000
```

---

# Using the Visualizer

1. Paste the **USR annotation** into the text box
2. Enter the **segment ID**
3. Click **Generate Graph**
4. The graph will appear below

Features:

* Zoom in / zoom out
* Scroll large graphs
* View semantic relations visually

---

# Example USR Input

```
<segment_id=chapter_1_living_world_004>

AraMBika_9 1 - - 2:mod - - - -
manuRya_1(man_7) 2 anim - 28:k1 - - - -
kuCa_1(some_2) 4 - - 6:quant - - - -
nirjIva_2(inanimate_2) 5 - - 6:mod - - - -
paxArWa_2(substance_4) 6 - - 33:rn - def - -

banA_10(do_3)-yA_WA_1(en_had_1) 28 - - 0:main - - - -

</segment_id>
```

Segment ID to enter in the UI:

```
chapter_1_living_world_004
```

---

# Output

The tool generates a graph in  **SVG format** :

```
sentence_<segment_id>.svg
```

Example:

```
sentence_chapter_1_living_world_004.svg
```



# Running the Tool Using Shell Script

The project includes a shell script **`USR_to_Graph.sh`** that allows you to generate graphs directly from the terminal.

### Make the script executable

<pre class="overflow-visible! px-0!" data-start="1445" data-end="1481"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span class="ͼs">chmod</span><span></span><span class="ͼn">+</span><span>x USR_to_Graph.sh</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

### Run the script

<pre class="overflow-visible! px-0!" data-start="1503" data-end="1558"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>./USR_to_Graph.sh input_file.txt segment_id</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

### Example

<pre class="overflow-visible! px-0!" data-start="1573" data-end="1630"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>./USR_to_Graph.sh chapter_1.txt chapter_1_001</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Where:

* **`input_file.txt`** → File containing the USR annotation
* **`segment_id`** → The specific segment identifier to visualize

The script will:

1. Extract the specified **segment**
2. Parse the **USR structure**
3. Generate a **dependency graph**
4. Export the graph as an **SVG file**

---

# Project Structure

```
Visualizer
│
├── app.py
├── USR_to_Graph_original.py
├── USR_to_Graph.sh
├── templates
│   └── index.html
├── static
│   └── graphs
├── input.txt
└── README.md
```

---

# Deactivating the Virtual Environment

When finished you can deactivate the environment:

```bash
deactivate
```

---

# License

This project is part of the  **LC Platform Visualizer** .

```

---

✅ This README now clearly tells users:

- install **Graphviz system-wide**
- create **venv**
- **activate venv**
- install dependencies
- run **UI with `python app.py`**

---

If you want, I can also help you add **one extremely useful feature** to your visualizer:

**Auto-detect `<segment_id>` from pasted USR and populate the dropdown automatically.**

This removes the need for users to manually type segment IDs.
```
