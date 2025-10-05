# Product Roadmap

## Phase 1: Core Processing Pipeline

**Goal:** Build functional CLI tool that processes PDFs and websites into optimized markdown files

**Success Criteria:** Successfully convert 100+ PDFs and 20+ websites into consolidated markdown files under 40M tokens total (20 files × 2M tokens each)

### Features

- [ ] Project setup and TypeScript configuration - `XS`
- [ ] Token counting integration (tiktoken library) - `S`
- [ ] PDF extraction using pdf-parse - `S`
- [ ] Web content scraping with Cheerio/Axios - `S`
- [ ] GPT-4 content optimization pipeline (extract → optimize → compress) - `M`
- [ ] Semantic categorization using GPT-4 (topic detection and grouping) - `M`
- [ ] Markdown generation and formatting - `S`
- [ ] Bucket consolidation with token-aware packing (max 20 buckets, ~2M tokens each) - `M`
- [ ] Basic CLI interface with folder input/output - `S`

### Dependencies

- OpenAI API access and key
- Node.js 20.x environment
- Sample PDFs and URLs for testing

## Phase 2: GPT Assistant Integration

**Goal:** Enable direct upload to existing OpenAI Assistants and optimize content quality

**Success Criteria:** Automated upload to GPT Assistant with 90%+ successful file acceptance rate, all files under 2M token limit

### Features

- [ ] OpenAI Assistants API integration - `M`
- [ ] Assistant file upload functionality with token validation - `S`
- [ ] Environment configuration for API keys and Assistant ID - `XS`
- [ ] Enhanced content structure preservation (tables, lists, code blocks) - `M`
- [ ] Metadata tracking and source references - `S`
- [ ] Error handling and retry logic for API calls and token limit errors - `S`
- [ ] Token budget monitoring across all 20 files - `S`

### Dependencies

- Phase 1 completion
- OpenAI Assistant created and configured
- Testing with production-scale documents

## Phase 3: Quality & Automation

**Goal:** Improve processing quality, add monitoring, and streamline workflows

**Success Criteria:** Processing accuracy >95%, batch processing of 1000+ documents without intervention

### Features

- [ ] Progress monitoring and status reporting with token usage stats - `S`
- [ ] Batch processing optimization with parallel API calls - `M`
- [ ] Content validation and quality checks - `M`
- [ ] Smart token optimization (remove redundancy, compress whitespace) - `M`
- [ ] Configuration file for processing rules and token budgets - `S`
- [ ] Logging and error reporting - `S`
- [ ] Unit and integration testing suite - `M`

### Dependencies

- Phase 2 completion
- User feedback on processing quality
- Performance benchmarks from real-world usage
