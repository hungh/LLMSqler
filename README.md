# LLM SQLer

Fine-tuning Qwen models for SQL query generation using the Spider dataset.

## Overview

This project fine-tunes Qwen2.5 models to generate SQL queries from natural language questions. Using QLoRA (4-bit quantization) for efficient training on consumer GPUs.

## Features

- **Model**: Qwen2.5-1.5B-Instruct (fine-tuned for text-to-SQL)
- **Dataset**: Spider dataset for cross-domain SQL generation
- **Training**: QLoRA with 4-bit quantization
- **Target**: Generate valid PostgreSQL SQL from natural language questions

## Installation

```bash
conda env create -f environment.yaml
conda activate llmsqler
```

## Quick Start

```bash
python src/pretraining/main_qwen_ft.py
```

## Project Structure 
```markdown
src/
├── pretraining/
│   ├── qwen_ft.py          # Model loading and LoRA config
│   ├── spider_ds.py        # Dataset tokenization
│   └── main_qwen_ft.py    # Training loop
└── tgi/
    └── __init__.py         # Text Generation Inference setup

```
## Training Configuration
- Batch Size: 2 (effective 16 with gradient accumulation)
- Learning Rate: 2e-4
- Max Steps: 300 (MVP run)
- Memory: Optimized for RTX 5060 Ti + 32GB RAM