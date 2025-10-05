# Product Mission

## Pitch

RAG Builder is a knowledge base optimization tool that helps AI developers and teams prepare documentation for GPT Assistants by converting PDFs and web content into optimized markdown files that maximize the 40M token limit (20 files × 2M tokens per file).

## Users

### Primary Customers

- **AI Application Developers**: Teams building GPT-powered applications who need to manage large knowledge bases efficiently
- **Technical Documentation Teams**: Organizations converting legacy documentation into AI-ready formats
- **Small Businesses & Startups**: Cost-conscious teams needing maximum value from GPT Assistant's free knowledge base tier

### User Personas

**AI Engineer** (25-40 years old)
- **Role:** Full-stack Developer / AI Integration Specialist
- **Context:** Building customer-facing GPT Assistant applications with extensive product documentation
- **Pain Points:** Manual PDF extraction is time-consuming, inconsistent formatting reduces retrieval quality, hitting 2M token-per-file limits with poorly optimized content
- **Goals:** Automate knowledge base preparation, maximize information density within size limits, improve RAG retrieval accuracy

**Documentation Manager** (30-50 years old)
- **Role:** Technical Writer / Knowledge Management Lead
- **Context:** Maintaining internal knowledge bases and support documentation across multiple formats
- **Pain Points:** Converting hundreds of legacy PDFs manually, ensuring consistent formatting for AI consumption, validating content extraction accuracy
- **Goals:** Batch process existing documentation, maintain content quality during conversion, integrate with existing GPT Assistants

## The Problem

### Inefficient Knowledge Base Preparation

GPT Assistants limit knowledge bases to 2M tokens per file (40M tokens total across 20 files), but raw PDFs and web content contain significant formatting overhead and redundant data. Teams waste hours manually extracting and optimizing content, often hitting token limits with poorly utilized space.

**Our Solution:** Automated extraction and intelligent consolidation into 20 optimized markdown files (~8MB each), maximizing token efficiency and information density.

### Poor Tokenization Quality

Unstructured PDFs with complex layouts, tables, and images produce poor-quality text extraction that reduces RAG retrieval accuracy. Teams struggle with garbled tables, lost context, and formatting artifacts.

**Our Solution:** GPT-powered parsing that preserves semantic structure and converts complex layouts into clean, tokenization-friendly markdown.

### Manual, Time-Consuming Workflows

Processing documents one-by-one, formatting content, and uploading to GPT Assistants requires repetitive manual work that doesn't scale. Teams need batch processing with automated assistant integration.

**Our Solution:** Folder-based input system with automated OpenAI processing and direct assistant upload capabilities.

## Differentiators

### Maximizes OpenAI's Token Budget

Unlike general document converters, we specifically optimize for GPT Assistant's 2M token-per-file limit by intelligently consolidating content into 20 markdown files. This results in fitting 2-3x more usable content within token constraints compared to raw PDF uploads, while staying under the 40M total token limit.

### GPT-Native Processing with Semantic Grouping

Unlike traditional PDF parsers, we use OpenAI's own models to extract, optimize, and semantically categorize content into thematic buckets. This produces significantly better RAG performance than regex-based extraction tools, while intelligent grouping improves retrieval accuracy.

### Zero-Configuration Automation

Unlike complex RAG pipelines requiring vector databases and embedding management, we provide a simple folder-drop workflow that automatically processes and uploads to existing GPT Assistants. This eliminates infrastructure overhead for small teams.

## Key Features

### Core Features

- **PDF Batch Processing:** Drop unlimited PDFs into a folder for automated extraction and consolidation
- **Web Content Scraping:** Provide URLs in a file for automated website content extraction
- **GPT-Powered Optimization:** Each document is parsed and optimized by GPT-4 for clean structure and token efficiency
- **Semantic Bucket Consolidation:** AI-categorized thematic grouping into max 20 markdown "buckets", each optimized for ~2M tokens (~8MB)
- **Token-Aware Packing:** Real-time token counting as content fills semantic buckets, preventing 2M token limit errors

### Integration Features

- **GPT Assistant Upload:** Direct API integration to upload processed files to existing OpenAI Assistants
- **Format Preservation:** Maintains tables, lists, code blocks, and hierarchical structure in markdown
- **Metadata Tracking:** Preserves source document references and creation dates for traceability

### Workflow Features

- **Folder-Based Input:** Simple drag-and-drop interface for PDFs and document lists
- **Processing Pipeline:** Automated OpenAI API-based extraction and transformation
- **Progress Monitoring:** Real-time feedback on processing status and file generation
