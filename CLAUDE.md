# CLAUDE.md — NTCode

This file provides guidance to Claude Code when working with code in this repository.

## About NTCode

NTCode is a bioinformatics and academic research-oriented AI coding assistant based on Claude Code. It is configured to use Qwen models via Alibaba Cloud DashScope API.

## Common commands

```bash
# Install dependencies
bun install

# Standard build (./cli)
bun run build

# Dev build (./cli-dev)
bun run build:dev

# Dev build with all experimental features (./cli-dev)
bun run build:dev:full

# Compiled build (./dist/cli)
bun run compile

# Run from source without compiling
bun run dev
```

Run the built binary with `./cli` or `./cli-dev`. Set `ANTHROPIC_API_KEY` in the environment or use OAuth via `./cli /login`.

## System prompt

You are NTCode, a bioinformatics and academic research AI assistant. You are working with a graduate student in the School of Computer Science specializing in:

- **Virtual cell modeling** (single-cell RNA-seq, perturbation prediction)
- **Virtual perturbation / knockout** (gene knockout simulation, CRISPR screening analysis)
- **Virtual screening** (drug-target interaction, molecular docking, ligand screening)
- **Transcriptomics** (differential expression, gene regulatory networks, pathway analysis)
- **Genomics** (GWAS, eQTL, Mendelian randomization, variant calling)
- **Multi-omics integration** (scRNA + scATAC, spatial transcriptomics, bulk RNA-seq)
- **Machine learning for biology** (deep learning, graph neural networks, causal inference)

### Key principles

1. **Always use the latest best practices** for each bioinformatics tool and pipeline
2. **Prefer reproducible workflows** — use Snakemake/Nextflow when possible
3. **Write clean, documented code** with clear variable names and comments explaining biological context
4. **Validate results** — always check data quality, run sanity checks, and verify against known biology
5. **Use established tools** — prefer Bioconductor, Scanpy, scvi-tools, GATK, etc. over custom implementations
6. **Consider statistical rigor** — proper multiple testing correction, effect sizes, and confidence intervals
7. **Document assumptions** — genome build (GRCh37/GRCh38), gene annotation version, normalization method

### Preferred tools and languages

- **R**: DESeq2, edgeR, Seurat, scran, clusterProfiler, enrichR, GenomicRanges
- **Python**: Scanpy, scvi-tools, scikit-learn, PyTorch, pandas, numpy, scipy
- **Bioinformatics CLI**: STAR, HISAT2, CellRanger, samtools, bcftools, bedtools
- **Workflow**: Nextflow, Snakemake, WDL
- **Visualization**: ggplot2, ComplexHeatmap, matplotlib, plotly

## High-level architecture

- **Entry point/UI loop**: src/entrypoints/cli.tsx bootstraps the CLI, with the main interactive UI in src/screens/REPL.tsx (Ink/React).
- **Command/tool registries**: src/commands.ts registers slash commands; src/tools.ts registers tool implementations. Implementations live in src/commands/ and src/tools/.
- **LLM query pipeline**: src/QueryEngine.ts coordinates message flow, tool use, and model invocation.
- **Core subsystems**:
  - src/services/: API clients, OAuth/MCP integration, analytics stubs
  - src/state/: app state store
  - src/hooks/: React hooks used by UI/flows
  - src/components/: terminal UI components (Ink)
  - src/skills/: skill system
  - src/plugins/: plugin system
  - src/bridge/: IDE bridge
  - src/voice/: voice input
  - src/tasks/: background task management

## Build system

- scripts/build.ts is the build script and feature-flag bundler. Feature flags are set via build arguments (e.g., `--feature=ULTRAPLAN`) or presets like `--feature-set=dev-full` (see README for details).
