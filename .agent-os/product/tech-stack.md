# Technical Stack

## Language & Runtime
- **Primary Language:** TypeScript 5.x
- **Runtime:** Node.js 20.x LTS

## Application Framework
- **Framework:** CLI-based Node.js application
- **CLI Framework:** Commander.js or Yargs for command-line interface

## APIs & Integration
- **AI Processing:** OpenAI API (GPT-4 for document parsing)
- **Assistant Integration:** OpenAI Assistants API v2

## Document Processing
- **PDF Parsing:** pdf-parse or pdf-lib
- **Web Scraping:** Cheerio + Axios or Playwright for JavaScript-heavy sites
- **Markdown Generation:** markdown-it or unified/remark ecosystem
- **Token Counting:** tiktoken (OpenAI's official tokenizer library) or gpt-tokenizer

## File System & Storage
- **File Management:** Node.js fs/promises
- **Configuration:** dotenv for environment variables
- **Data Storage:** Local file system (input/output folders)

## Build & Development
- **Package Manager:** npm or pnpm
- **Build Tool:** TypeScript compiler (tsc) or esbuild
- **Testing Framework:** Jest or Vitest
- **Linting:** ESLint with TypeScript support

## Deployment
- **Application Hosting:** Runs locally or on any Node.js environment
- **Distribution:** npm package (optional) or standalone executable
- **CI/CD:** GitHub Actions for automated testing
- **Code Repository:** https://github.com/[username]/rag-builder

## Configuration Management
- **Environment Variables:**
  - OPENAI_API_KEY (required)
  - ASSISTANT_ID (optional, for direct upload)
  - MAX_TOKENS_PER_FILE (default: 2000000, GPT Assistant limit)
  - MAX_FILES (default: 20)

## Project Structure
```
/
├── src/
│   ├── parsers/
│   │   ├── pdf-parser.ts
│   │   └── web-scraper.ts
│   ├── processors/
│   │   ├── gpt-optimizer.ts        # GPT-4 content optimization
│   │   ├── semantic-categorizer.ts # AI-powered topic categorization
│   │   ├── token-counter.ts
│   │   └── bucket-consolidator.ts  # Token-aware bucket packing
│   ├── upload/
│   │   └── assistant-uploader.ts
│   └── index.ts
├── input/
│   ├── pdfs/
│   └── urls.txt
├── intermediate/
│   └── [optimized individual MDs]
├── output/
│   └── [20 semantic bucket MDs]
└── .env
```
