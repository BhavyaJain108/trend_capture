# YouTube Trends Analysis - Complete Command Reference

## 🚀 **MAIN ENTRY POINT (`bin/analyze`)**

### **Core Workflows**
```bash
# Full analysis pipeline
./bin/analyze run "AI productivity tools 2024"

# Load results to vector database (recommended)
./bin/analyze load

# Search your trend collections
./bin/analyze search

# Test with single video
./bin/analyze test "machine learning tutorials"
```

### **Manual Grading (Optional)**
```bash
# Manual grading workflow: CSV → Review → Vector DB
./bin/analyze grade
```

### **Demos and Utilities**
```bash
# Feature demonstrations
./bin/analyze demo grading       # Demo grading system
./bin/analyze demo clustering    # Demo semantic clustering  
./bin/analyze demo vector        # Demo vector database

# Statistics and help
./bin/analyze stats              # Show grading statistics
./bin/analyze help               # Show help
```

---

## 📁 **DIRECT SCRIPT USAGE**

### **Analysis Runners (`scripts/`)**

#### **Main Analysis (Recommended)**
```bash
# Parallel processing pipeline (fastest)
python scripts/run_parallel_analysis.py "day in my life nyc vlog"

# Legacy single-threaded pipeline
python scripts/run_analysis.py "your query"

# Simple runner
python scripts/run_analysis_simple.py "your query"
```

#### **Append to Existing Analysis**
```bash
# Append-enabled runner with folder selection
python scripts/run_analysis_append.py "new related query"
python scripts/run_analysis_append.py --append "related content"
python scripts/run_analysis_append.py -a "more related content"
```

### **Vector Database Tools (`tools/`)**

#### **Load Results to Vector Database**
```bash
# Load latest results automatically
python tools/load_to_vector_db.py auto

# Load specific CSV file
python tools/load_to_vector_db.py results/nyc_vlogs/trend_results.csv
```

#### **Search Vector Database**
```bash
# Search specific results databases (recommended)
python tools/search_results.py

# General interactive search
python tools/interactive_search.py
```

#### **Append Analysis to Existing Folders**
```bash
# Interactive append to existing analysis
python tools/append_analysis.py "related query"
```

#### **Manual Grading System**
```bash
# Start grading session (any 50 trends)
python tools/trend_grader.py grade

# Grade specific category
python tools/trend_grader.py grade emerging_topics

# Grade specific number of trends
python tools/trend_grader.py grade early_adopter_products 100

# Review graded trends
python tools/trend_grader.py review
python tools/trend_grader.py review interesting
python tools/trend_grader.py review uninteresting

# Check grading progress
python tools/trend_grader.py stats
```

#### **Manual Grading + Vector DB Workflow**
```bash
# Complete manual grading workflow
python tools/grade_and_store.py auto
python tools/grade_and_store.py results/nyc_vlogs/trend_results.csv
```

#### **Folder Management**
```bash
# Rename results folders
python tools/rename_folder.py 20250803_230008 nyc_vlogs
python tools/rename_folder.py 20250804_120000 ai_productivity_tools
```

#### **Test Single Video**
```bash
# Test on single video
python tools/test_single_video_grading.py
python tools/test_single_video_grading.py "productivity setup tour"
```

#### **Vector Database Examples**
```bash
# Usage examples and demos
python tools/use_trends_vector_db.py
```

### **Demo Scripts (`demos/`)**
```bash
# Semantic clustering demo
python demos/demo_semantic_explorer.py

# Grading system demo  
python demos/demo_trend_grader.py

# Other demos
python demos/demo_date_filtering.py
python demos/demo_simple_vector.py
```

---

## 🔄 **COMPLETE WORKFLOWS**

### **Workflow 1: New Topic Analysis**
```bash
# 1. Create new analysis
python scripts/run_parallel_analysis.py "AI productivity tools"

# 2. Rename for organization (optional)
python tools/rename_folder.py 20250804_120000 ai_productivity_tools

# 3. Load to vector database
python tools/load_to_vector_db.py auto

# 4. Search and explore
python tools/search_results.py
```

### **Workflow 2: Expand Existing Topic**
```bash
# 1. Add related content to existing analysis
python tools/append_analysis.py "time management apps"
# (Interactive: select which folder to append to)

# 2. Search expanded collection
python tools/search_results.py
```

### **Workflow 3: Manual Quality Control**
```bash
# 1. Run analysis
python scripts/run_parallel_analysis.py "productivity tools"

# 2. Manual grading workflow
python tools/grade_and_store.py auto
# (Interactive: grade each trend y/n/s/q)

# 3. Search curated results
python tools/search_results.py
```

### **Workflow 4: Using Main CLI**
```bash
# Unified interface (simplest)
./bin/analyze run "productivity apps"     # Create analysis
./bin/analyze load                        # Load to vector DB
./bin/analyze search                      # Search trends
```

---

## 🔍 **SEARCH COMMANDS**

### **Interactive Search Options**
Once in search mode (`python tools/search_results.py`):

```bash
# Basic search
search AI tools

# Search with category filter
search python in early_adopter_products

# Search with date filter
search machine learning after 2024-08-01

# Combined filters
search "AI tools" in emerging_topics after 2024-09-01

# Get trending topics
trending
trending in emerging_topics

# Analyze specific category
analyze behavioral_patterns

# Database statistics
stats
```

### **Vector Database Query Parameters**
```python
# Programmatic access
db.search(
    query="AI productivity tools",
    top_k=10,                    # Number of results
    category="emerging_topics",   # Filter by category
    min_score=0.7,               # Minimum trend score
    after_date="2024-08-01",     # Date range start
    before_date="2024-12-01"     # Date range end
)
```

---

## 📂 **RESULTS DIRECTORY STRUCTURE**

### **Analysis Results**
```
results/
├── nyc_vlogs/                   # Renamed folder (was 20250803_230008)
│   ├── trend_results.csv        # Main insights (746 trends)
│   ├── query_results.csv        # Query breakdown
│   ├── youtube_log.csv          # Video metadata
│   ├── vector_db/               # Vector database
│   │   ├── chroma.sqlite3
│   │   └── embeddings...
│   ├── ai_prompt.txt            # AI-generated queries
│   ├── prompt.txt               # Original query
│   └── errors.txt               # Error log
├── ai_productivity_tools/       # Another analysis
│   └── ...
```

### **File Descriptions**
- **`trend_results.csv`** - Main insights with trend scores (-1.0 to +1.0)
- **`query_results.csv`** - Search query breakdown and success rates
- **`youtube_log.csv`** - Video metadata (title, channel, views, etc.)
- **`vector_db/`** - ChromaDB database for semantic search
- **`ai_prompt.txt`** - AI-generated search queries + reasoning
- **`prompt.txt`** - Your original query
- **`errors.txt`** - Processing errors (if any)

---

## ⚙️ **CONFIGURATION OPTIONS**

### **Analysis Configuration (`src/youtube_trends/config.py`)**
```python
# Query Generation
DEFAULT_NUM_QUERIES = 5         # Number of search queries to generate
QUERY_WORD_LIMIT = 8            # Maximum words per query

# Video Processing
DEFAULT_MAX_VIDEOS = 25         # Maximum videos to process
VIDEOS_PER_QUERY = 5           # Videos per search query
DEFAULT_VIDEO_SEARCH_LIMIT = 10 # YouTube search limit per query

# Parallel Processing  
MAX_PARALLEL_VIDEOS = 8        # Concurrent processing threads
PARALLEL_TIMEOUT = 500         # Timeout per video (seconds)

# Vector Database
VECTOR_DB_PATH = "vector_db"   # Default vector DB location
VECTOR_SEARCH_TOP_K = 20       # Default search results
```

### **API Configuration**
```bash
# Environment variables (.env file)
YOUTUBE_API_KEY=your_youtube_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
```

---

## 📊 **DATA ANALYSIS CATEGORIES**

### **Insight Categories**
All trends are categorized into:

1. **`early_adopter_products`** - Specific products, tools, platforms, apps
2. **`emerging_topics`** - Trending concepts, innovation areas, themes  
3. **`problem_spaces`** - Pain points, challenges, limitations
4. **`behavioral_patterns`** - Usage patterns, workflow changes, behaviors
5. **`educational_demand`** - Learning needs, skill gaps, training demands

### **Trend Scoring**
- **+1.0** - Highly trending/rising/growing/urgent
- **0.0** - Neutral/stable/unclear direction
- **-1.0** - Declining/losing momentum/solved/obsolete

---

## 🎯 **COMMON USE CASES**

### **Market Research**
```bash
./bin/analyze run "productivity apps 2024"
./bin/analyze load
# Search for specific tools, adoption patterns, user feedback
```

### **Competitive Analysis**
```bash
python tools/append_analysis.py "notion alternatives"
python tools/append_analysis.py "obsidian vs roam research"
# Build comprehensive competitor landscape
```

### **Trend Discovery**
```bash
python tools/search_results.py
# Search: "AI tools in emerging_topics"
# Find: Latest AI innovations before mainstream adoption
```

### **Content Strategy**
```bash
python scripts/run_parallel_analysis.py "youtube creator tools"
# Analyze: What tools creators are actually using
# Identify: Gaps in current tool ecosystem
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**
```bash
# No results found
python tools/load_to_vector_db.py auto
# → Check if you have any CSV files in results/

# Import errors
pip install -r requirements.txt
# → Ensure all dependencies installed

# API key errors  
echo "YOUTUBE_API_KEY=your_key" >> .env
echo "CLAUDE_API_KEY=your_key" >> .env
# → Check .env file exists and has correct keys

# Path issues
cd /path/to/youtube_trends
./bin/analyze run "query"
# → Run from project root directory
```

### **Performance Optimization**
```bash
# Faster processing
MAX_PARALLEL_VIDEOS = 8         # Increase concurrent threads
PARALLEL_TIMEOUT = 600          # Increase timeout for complex videos

# More comprehensive results
DEFAULT_MAX_VIDEOS = 50         # Process more videos
DEFAULT_NUM_QUERIES = 10        # Generate more search queries
```

---

## 📈 **ADVANCED USAGE**

### **Programmatic Access**
```python
# Direct pipeline usage
from youtube_trends.parallel_pipeline import ParallelYouTubeTrendsPipeline
pipeline = ParallelYouTubeTrendsPipeline()
results = pipeline.run_analysis("your query")

# Vector database access
from youtube_trends.trends_vector_db import TrendsVectorDB
db = TrendsVectorDB("results/nyc_vlogs/vector_db")
trends = db.search("coffee shops", category="emerging_topics")

# Semantic clustering
from youtube_trends.semantic_explorer import SemanticRegionExplorer
explorer = SemanticRegionExplorer(db)
regions = explorer.discover_dense_regions_adaptive()
```

### **Batch Processing**
```bash
# Process multiple topics
queries=("AI tools" "productivity apps" "remote work setup")
for query in "${queries[@]}"; do
    python scripts/run_parallel_analysis.py "$query"
    python tools/load_to_vector_db.py auto
done
```

---

This comprehensive reference covers **every command and option** available in the YouTube Trends Analysis system! 🚀