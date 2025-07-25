# YouTube Trends Analysis System

An intelligent system that analyzes YouTube content to extract trending insights, early adopter products, emerging topics, and behavioral patterns using AI-powered query generation and transcript processing.

## 🚀 Quick Start

```bash
# Clone and setup
cd youtube_trends
pip install -r requirements.txt

# Add your API keys to .env file
echo "YOUTUBE_API_KEY=your_youtube_api_key" >> .env
echo "CLAUDE_API_KEY=your_claude_api_key" >> .env

# Run analysis
python run_analysis.py "AI coding tools"
python run_parallel_analysis.py "AI coding tools"
```

## 📊 What It Does

The system takes a natural language query and:

1. **🤖 AI Query Generation** - Generates multiple optimized YouTube search queries using Claude AI
2. **🔍 Multi-Query Search** - Searches YouTube using official API with multiple strategies
3. **📝 Transcript Extraction** - Downloads video transcripts using youtube-transcript-api
4. **💡 Insight Processing** - Extracts structured insights using DSPy and Claude AI
5. **📈 Trend Analysis** - Scores trends from -1.0 (declining) to +1.0 (rising)
6. **📋 Results Export** - Saves comprehensive results with full visibility

## 🎯 Core Features

### Multi-Strategy Search
- Generates **15 different search queries** from your input
- Each query limited to **10 words** for better API compatibility
- **2 videos per query** = up to 30 videos total
- **Query results table** shows success/failure per query

### AI-Powered Analysis
- **5 insight categories**: Early adopter products, emerging topics, problem spaces, behavioral patterns, educational demand
- **Bidirectional trend scoring**: Captures both rising and declining trends
- **Smart transcript chunking**: Processes long videos efficiently
- **Emphasis on early adopter products** throughout analysis

### Comprehensive Results
```
results/YYYYMMDD_HHMMSS/
├── trend_results.csv      # Main insights with trend scores
├── query_results.csv      # Query-by-query breakdown  
├── youtube_log.csv        # All video metadata
├── ai_prompt.txt          # AI-generated queries + reasoning
├── prompt.txt             # Your original query
└── errors.txt             # Error log (if any)
```

## ⚡ Processing Options

### Regular Processing
```bash
python run_analysis.py "your query here"
```
- Sequential video processing
- Reliable and stable
- Best for smaller video sets

### Parallel Processing (Faster)
```bash
python run_parallel_analysis.py "your query here"
```
- **Parallel transcript extraction** for faster network I/O
- **Sequential insight processing** (DSPy thread safety limitation)
- Significant speedup for large video sets
- Same output quality as regular processing

## 🔧 Configuration

All settings are centralized in `src/youtube_trends/config.py`:

```python
# Query Generation
QUERY_WORD_LIMIT = 10           # max words per query
DEFAULT_NUM_QUERIES = 15        # number of queries to generate

# Video Processing  
DEFAULT_MAX_VIDEOS = 10         # videos to process
VIDEOS_PER_QUERY = 2           # videos per search query

# Parallel Processing
MAX_PARALLEL_VIDEOS = 4        # concurrent threads
PARALLEL_TIMEOUT = 300         # timeout per video
```

## 📈 Example Output

### Query Results Table (`query_results.csv`)
```csv
query_number,query_text,videos_found,date_filter,status
1,AI coding assistant comparison GitHub Copilot review,2,2024,success
2,programming productivity tools developer workflow guide,2,2024,success  
3,automated code generation machine learning developers,0,2024,failed
```

### Trend Results (`trend_results.csv`)
```csv
date,category,information,score
2024-01-12,early_adopter_products,GitHub Copilot,0.95
2024-01-15,educational_demand,AI programming skills training,0.88
2024-01-10,behavioral_patterns,Developer workflow automation adoption,0.72
```

## 🏗️ Architecture

### Core Components
- **`pipeline.py`** - Main sequential processing pipeline
- **`parallel_pipeline.py`** - Parallel processing version
- **`youtube_query_generation.py`** - AI-powered query optimization
- **`youtube_search.py`** - Official YouTube Data API v3 integration
- **`transcript.py`** - Video transcript extraction
- **`transcript_processing.py`** - DSPy-powered insight extraction
- **`config.py`** - Centralized configuration management

### Data Flow
```
User Query → AI Query Generation → Multi-Query Search → 
Transcript Extraction → Insight Processing → Results Export
```

## 🔍 Technical Details

### APIs Used
- **YouTube Data API v3** - Official video search (more restrictive than web search)
- **Claude AI (Anthropic)** - Query generation and insight extraction
- **youtube-transcript-api** - Transcript extraction

### AI Processing
- **DSPy Framework** - Structured LLM outputs without regex parsing
- **Claude 3.5 Sonnet** - Latest model for optimal performance
- **Modular signatures** - Separate processing for each insight category

### Search Strategy
- **Multiple query approach** - Diversifies results beyond single search
- **No deduplication** - Popular videos processed multiple times for richer insights
- **Date filtering** - Configurable time-based filtering (2024, 2023, etc.)
- **View count sorting** - Gets most popular videos first

## ⚙️ Key Insights

### Why YouTube Data API vs Web Search?
The official API is **much more restrictive** than YouTube's web search:
- Long queries often return 0 results
- Requires exact keyword matching
- No query relaxation or "did you mean" suggestions
- This is why we use **shorter, focused queries** (10 words max)

### Performance Optimizations
- **Parallel transcript extraction** - Network I/O bottleneck addressed
- **Smart chunking** - Handles long transcripts efficiently  
- **Centralized config** - Easy performance tuning
- **Query results visibility** - Debug which searches succeed/fail

### Trend Scoring System
- **-1.0**: Declining/losing momentum/failing trends
- **0.0**: Neutral/stable/unclear direction  
- **+1.0**: Rising/gaining momentum/hot trends
- **Bidirectional**: Captures both growth AND decline patterns

## 🎛️ Customization

### Adjust Query Strategy
```python
# More queries, shorter length
DEFAULT_NUM_QUERIES = 20
QUERY_WORD_LIMIT = 8

# Fewer queries, more videos each  
DEFAULT_NUM_QUERIES = 10
VIDEOS_PER_QUERY = 3
```

### Processing Performance
```python
# Faster parallel processing
MAX_PARALLEL_VIDEOS = 6
PARALLEL_TIMEOUT = 600

# More comprehensive analysis
DEFAULT_MAX_VIDEOS = 20
TRANSCRIPT_MAX_CHUNK_SIZE = 6000
```

## 📋 Requirements

- Python 3.8+
- YouTube Data API v3 key
- Claude API key (Anthropic)
- Dependencies: `anthropic`, `google-api-python-client`, `youtube-transcript-api`, `dspy-ai`, `pandas`

## 🎯 Use Cases

- **Market Research** - Identify trending products and technologies
- **Competitive Analysis** - Track competitor mentions and sentiment
- **Product Development** - Understand user problems and demands
- **Content Strategy** - Find popular topics and formats
- **Trend Forecasting** - Early detection of emerging patterns
- **Academic Research** - Analyze discourse and behavioral patterns

## 🚧 Current Limitations

1. **Language Support** - English transcripts only (many videos have other languages)
2. **API Quotas** - YouTube API has daily limits
3. **DSPy Thread Safety** - Insight processing must be sequential in parallel mode
4. **Query Complexity** - Simple queries work better than complex ones
5. **Transcript Availability** - Not all videos have transcripts enabled

## 🔮 Future Enhancements

- **Multi-language support** - Process non-English transcripts
- **Chunk-level parallelization** - Parallel processing within transcript analysis
- **Alternative search methods** - Complement API with other data sources  
- **Real-time monitoring** - Continuous trend tracking
- **Advanced analytics** - Sentiment analysis, entity extraction
- **Web interface** - GUI for non-technical users

## 📊 Performance Benchmarks

- **Sequential Processing**: ~30-60 seconds per video
- **Parallel Processing**: ~40% faster for transcript extraction
- **Query Generation**: ~2-5 seconds for 15 queries
- **Video Search**: ~1-3 seconds per query
- **Insight Processing**: ~20-40 seconds per video (DSPy + Claude)

## 🎉 Success Stories

The system successfully identifies:
- ✅ **Emerging AI tools** before mainstream adoption
- ✅ **Developer workflow changes** and productivity trends  
- ✅ **Educational demand patterns** for new technologies
- ✅ **Product adoption barriers** and user pain points
- ✅ **Industry sentiment shifts** and behavioral changes

---

*Built with Claude AI, DSPy, and the YouTube Data API for comprehensive trend analysis.*
