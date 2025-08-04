# YouTube Trends Analysis - Project Structure

## 📂 Directory Organization

```
youtube_trends/
├── 📁 src/youtube_trends/          # Core library modules
│   ├── config.py                  # Configuration and settings
│   ├── parallel_pipeline.py       # Main analysis pipeline
│   ├── youtube_search.py          # YouTube API client
│   ├── transcript_processing*.py  # Transcript analysis
│   ├── trends_vector_db.py        # Vector database for trends
│   └── semantic_explorer.py       # Semantic clustering tools
│
├── 📁 tools/                      # Interactive user tools
│   ├── grade_and_store.py         # CSV → Grade → Vector DB workflow
│   ├── trend_grader.py            # Manual trend grading interface
│   ├── interactive_search.py      # Search trends in vector DB
│   ├── use_trends_vector_db.py    # Vector DB usage examples
│   └── test_single_video_grading.py # Single video testing
│
├── 📁 demos/                      # Demonstration scripts
│   ├── demo_semantic_explorer.py  # Semantic clustering demo
│   ├── demo_trend_grader.py       # Grading system demo
│   └── demo_*.py                  # Other feature demos
│
├── 📁 scripts/                    # Utility and runner scripts
│   ├── run_analysis.py            # Basic analysis runner
│   ├── run_parallel_analysis.py   # Parallel processing runner
│   └── run_*.py                   # Other utility runners
│
├── 📁 tests/                      # Test files
├── 📁 results/                    # Analysis output (CSV files)
├── 📁 vector_db/                  # ChromaDB storage
└── 📁 docs/                       # Documentation (if added)
```

## 🚀 Quick Start Workflows

### **1. Complete Analysis Pipeline**
```bash
# Run full trend discovery
python -m youtube_trends.parallel_pipeline "AI productivity tools"

# Grade discovered trends
python tools/grade_and_store.py auto

# Search and explore
python tools/interactive_search.py
```

### **2. Test with Single Video**
```bash
# Test on one video
python tools/test_single_video_grading.py

# Grade the results
python tools/trend_grader.py grade
```

### **3. Explore Semantic Regions**
```bash
# Demo semantic clustering
python demos/demo_semantic_explorer.py

# Interactive search
python tools/interactive_search.py
```

## 📋 File Descriptions

### **Core Library (`src/youtube_trends/`)**
- **`config.py`** - All configuration, API keys, prompts
- **`parallel_pipeline.py`** - Main analysis orchestrator
- **`youtube_search.py`** - YouTube API interactions
- **`transcript_processing_claude.py`** - Claude-based trend extraction
- **`trends_vector_db.py`** - Vector database with manual grading
- **`semantic_explorer.py`** - DBSCAN/OPTICS clustering for trend regions

### **User Tools (`tools/`)**
- **`grade_and_store.py`** - Main workflow: CSV → Grade → Vector DB
- **`trend_grader.py`** - Interactive grading interface (y/n decisions)
- **`interactive_search.py`** - Search trends with filters
- **`use_trends_vector_db.py`** - Vector DB usage guide
- **`test_single_video_grading.py`** - Single video testing

### **Demos (`demos/`)**
- **`demo_semantic_explorer.py`** - Shows clustering algorithms in action
- **`demo_trend_grader.py`** - Demonstrates grading system
- **`demo_*.py`** - Other feature demonstrations

### **Scripts (`scripts/`)**
- **`run_analysis.py`** - Simple pipeline runner
- **`run_parallel_analysis.py`** - Parallel processing runner
- **`run_*.py`** - Other utility scripts

## 🎯 Common Usage Patterns

### **New User Setup**
1. **Configure API keys** in environment variables
2. **Test with single video**: `python tools/test_single_video_grading.py`
3. **Grade the trends**: `python tools/trend_grader.py grade`
4. **Explore results**: `python tools/interactive_search.py`

### **Production Workflow**
1. **Run analysis**: `python -m youtube_trends.parallel_pipeline "query"`
2. **Grade trends**: `python tools/grade_and_store.py auto`
3. **Search/explore**: `python tools/interactive_search.py`

### **Research & Exploration**
1. **Semantic clustering**: `python demos/demo_semantic_explorer.py`
2. **Vector search**: `python tools/use_trends_vector_db.py`
3. **Grading stats**: `python tools/trend_grader.py stats`

## 📈 Data Flow

```
User Query
    ↓
YouTube Search → Videos → Transcripts
    ↓
Claude Analysis → Trend Extraction → CSV Files
    ↓
Manual Grading → Quality Filter → Vector Database
    ↓
Search & Exploration → Semantic Clustering
```

## 🔧 Development

- **Add new features** to `src/youtube_trends/`
- **Create demos** in `demos/`
- **Add utilities** in `tools/`
- **Write tests** in `tests/`

## 📊 Output Locations

- **Raw results**: `results/YYYYMMDD_HHMMSS/`
- **Vector database**: `vector_db/`
- **Logs**: Console output and error files