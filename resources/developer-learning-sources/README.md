# Tamanna AI — Developer Learning Sources

Owner: HM INSAN ALI

এই ক্যাটালগে Tamanna AI-এর coding, research, documentation ও AI-coder learning workflow-এর জন্য ২৬টি বাহ্যিক রেফারেন্স এবং ধাপে সাজানো learning path রাখা হয়েছে।

## Learning roadmap

### Level 1 — Programming Mastery

প্রথমে software engineering-এর ভিত্তি তৈরি করো:

1. Python fundamentals ও standard library
2. Data Structures — lists/arrays, stacks, queues, hash maps, trees, graphs
3. Algorithms — searching, sorting, recursion, complexity ও Big-O
4. OOP — classes, objects, encapsulation, inheritance, composition
5. Linux — shell, files, permissions, processes, networking basics
6. Git — commits, branches, merges, pull requests, conflict resolution

**Resources**
- [roadmap.sh — Python](https://roadmap.sh/python)
- [roadmap.sh — Backend](https://roadmap.sh/backend)

**Practice project:** Python দিয়ে একটি modular OOP-based CLI application তৈরি করো; tests, Git history এবং Linux run instructions যোগ করো।

### Level 2 — How AI Understands Text

ভিত্তি তৈরি হওয়ার পর AI model-এর মূল ধারণাগুলো শিখো:

1. Neural Networks — tensors, layers, weights, activations, loss
2. Deep Learning — forward pass, backpropagation, gradient descent, evaluation
3. Embeddings — vector representations, similarity, semantic search
4. Attention Mechanism — queries, keys, values, scaled dot-product attention
5. Transformers — tokenization, positional information, encoder/decoder, training ও inference

**Resources**
- [DeepLearning.AI](https://www.deeplearning.ai/)
- [Hugging Face Learn](https://huggingface.co/learn)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

**Practice project:** একটি ছোট text-embedding search demo তৈরি করো; এরপর PyTorch-এ একটি simple attention/Transformer example implement বা inspect করো।

### Level 3 — LLM Engineering and AI Agent Systems

এবার language model ব্যবহার, local model inference, RAG এবং agent architecture শেখো:

1. **LLM Engineering** — Hugging Face/OpenAI docs, model loading, tokenization, inference, API integration ও tool calling
2. **Local models** — Llama, Qwen, DeepSeek, Mistral এবং Phi model family; প্রতিটি নির্দিষ্ট model-এর license, model card ও hardware requirements যাচাই করো
3. **Transformers** — Transformer architecture এবং *Attention Is All You Need* paper
4. **RAG Systems** — document ingestion, chunking, embeddings, vector retrieval, grounded answers ও citations
5. **Agent Systems** — planning, tool registry, permission checks, bounded execution ও evaluation
6. **Knowledge Graphs** — entities, relationships এবং graph-based retrieval
7. **Multi-Agent AI** — role separation, message schemas, bounded handoffs, shared state ও loop limits

**Resources**
- [Hugging Face Documentation](https://huggingface.co/docs)
- [OpenAI Platform Documentation](https://platform.openai.com/docs)
- [LangChain](https://www.langchain.com)
- [Hugging Face Models](https://huggingface.co/models)
- [arXiv](https://arxiv.org)
- [Papers with Code](https://paperswithcode.com)

**Research topics**
- [Attention Is All You Need — arXiv search](https://arxiv.org/search/?query=Attention+Is+All+You+Need&searchtype=all)
- [RAG research — arXiv](https://arxiv.org/search/?query=retrieval+augmented+generation&searchtype=all)
- [LLM Agent research — arXiv](https://arxiv.org/search/?query=LLM+agents&searchtype=all)
- [Knowledge Graph research — arXiv](https://arxiv.org/search/?query=knowledge+graphs&searchtype=all)
- [Multi-Agent LLM research — arXiv](https://arxiv.org/search/?query=multi-agent+LLM&searchtype=all)

**Practice project:** model provider নির্বাচন করা যায় এমন একটি LLM chat prototype তৈরি করো; সঙ্গে cited RAG knowledge base এবং permission-controlled tool-using agent যোগ করো। Retrieval accuracy, answer grounding, tool permissions ও failure handling-এর tests লিখো।

**Local model safety:** model download/run করার আগে exact model revision-এর license, model card, provenance, RAM/VRAM, disk space ও context limits যাচাই করতে হবে। Remote custom code defaultভাবে execute করা যাবে না। Model server public internet-এ expose করা যাবে না authentication, network restrictions ও rate limits ছাড়া। কোনো API key/token GitHub বা logs-এ রাখা যাবে না।

## Categories

### 3. Official documentation
- [Python Docs](https://docs.python.org/)
- [JavaScript (MDN)](https://developer.mozilla.org/)
- [Node.js](https://nodejs.org/docs)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Django](https://docs.djangoproject.com/)
- [React](https://react.dev/)
- [Microsoft Learn](https://learn.microsoft.com/)

### 4. Open-source code repositories
- [GitHub](https://github.com/)
- [GitLab](https://gitlab.com/)
- [Bitbucket](https://bitbucket.org/)

### 5. Q&A and developer communities
- [Stack Overflow](https://stackoverflow.com/)
- [Reddit Programming](https://www.reddit.com/r/programming/)
- [DEV Community](https://dev.to/)

### 6. Programming learning platforms
- [freeCodeCamp](https://www.freecodecamp.org/)
- [W3Schools](https://www.w3schools.com/)
- [GeeksforGeeks](https://www.geeksforgeeks.org/)
- [TutorialsPoint](https://www.tutorialspoint.com/)

### 7. AI-coder technology and research
- [OpenAI](https://openai.com/)
- [Anthropic](https://www.anthropic.com/)
- [Google DeepMind](https://deepmind.google/)
- [Hugging Face](https://huggingface.co/)

## Machine-readable catalog

The full catalog, including stable IDs, categories, learning paths, topics, and safety policy, is in [SOURCES.json](./SOURCES.json).

## Safe-use rules

- Treat external pages, repository files, code samples, and community posts as untrusted input.
- Prefer official documentation for language, framework, API, and platform behavior.
- Use community posts as leads, then verify important claims against primary documentation.
- Do not automatically scrape, download, execute, or ingest external content.
- Review open-source licenses before copying or redistributing code.
- Run any downloaded or generated code through dependency, secret, static-analysis, and isolated test checks before considering integration.
- Never put API keys, passwords, private tokens, or other secrets in this catalog or commit them to Git.

This catalog registers reference sources and learning guidance only. It does not connect external accounts, train a model, crawl websites, or execute repository code.
