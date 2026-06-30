# Competitive Research: Legal AI And Contract Review Stores

Date: 2026-06-30

Purpose: identify the crowded feature surface around legal AI apps, contract review, and legal operations tooling, then choose the strongest public proof feature for this repo.

## Search Surfaces

- GitHub repository search for `legal AI agent`, `contract review AI`, and `legal ops`.
- Apple App Store official iTunes Search API for `legal AI` and `contract review`.
- Google Play public search pages for `legal AI` and `contract review`.
- Chrome Web Store, Google Workspace Marketplace, and Slack Marketplace public searches for `legal AI`.
- Microsoft AppSource and Amazon Appstore were attempted from the CLI. Both blocked automated access during this pass, so they are treated as coverage boundaries rather than inspected result sets.

## GitHub Signals

- `Paparusi/legal-ai-agent`: high-star legal AI agent result, active near the research date.
- `sure-scale/doc-haus`: local-document legal AI agent with Word redline positioning.
- `NEU-ZHA/legal-ai-skills`: legal AI skills for citation and DOCX workflows.
- `anylegal-ai/anylegal-oss`: open-source legal AI agent harness.
- `xiaodingfeng/contract-review-v2`: contract upload, AI pre-analysis, OnlyOffice preview, knowledge retrieval, Q&A, and controlled web search.
- Contract-review searches also returned many small demos focused on clause extraction, risk scoring, upload flows, Gemini-based review, and MCP-style contract review.

The GitHub market is deepest around agent harnesses, redlining, legal research helpers, and contract-review demos. Legal operations control evidence is comparatively sparse.

## App Store Signals

Apple App Store results include consumer and small-business legal tools such as Legal AI Assistant, AI Legal Documents Generator, Rocket Lawyer, Vikk, Lexis+ with Protege Mobile, AI Lawyer, Contract Genius, ClauseLens, Contract Assistant, BeforeSend, BeforeYouSign, Sign Wise, Simply, Contract AI, and CounselVault.

Google Play public search showed similar clusters: AI lawyer apps, Rocket Lawyer, LegalAI-style explainers, ClauseLens, ContractEasy, Contractly, and AI contract analyzers.

The mobile market is crowded around consumer legal Q&A, document generation, contract explanation, and lightweight contract review.

## Marketplace Signals

Chrome Web Store and Google Workspace Marketplace results emphasize legal simplification, privacy-policy analysis, redlining, document review, legal Q&A, and hallucination-watch style browser utilities.

Slack Marketplace surfaced legal assistant and legal hold style entries. That signal is more workflow integration than evidence design.

The enterprise-adjacent stores favor document workflows, browser or workspace convenience, and collaboration add-ons. They give less reviewer-facing proof of source boundaries, approval gates, disabled external actions, and artifact integrity.

## Product Implication

The strongest public proof feature for `legal-ops-agent` is a Trust Cockpit:

- One reviewer-facing output that shows status, review state, export gate, source boundary, external-action block, commitments, owners, SLA, and artifact digests.
- JSON and Markdown outputs generated through the canonical CLI path.
- A controlled MCP tool for the same evidence surface.
- A dated committed snapshot using the synthetic SaaS MSA deviation fixture.

This positions the repo around operational trust and legal workflow control, where the competitive field is thinner than consumer chat, document generation, redlining, or generic contract analysis.

## Source Links

- GitHub legal AI agent search: <https://github.com/search?q=legal+AI+agent&type=repositories>
- GitHub contract review AI search: <https://github.com/search?q=contract+review+AI&type=repositories>
- GitHub legal ops search: <https://github.com/search?q=legal+ops&type=repositories>
- Apple App Store legal AI API: <https://itunes.apple.com/search?term=legal%20AI&country=us&entity=software&limit=20>
- Apple App Store contract review API: <https://itunes.apple.com/search?term=contract%20review&country=us&entity=software&limit=20>
- Google Play legal AI search: <https://play.google.com/store/search?q=legal%20AI&c=apps&hl=en_US&gl=US>
- Google Play contract review search: <https://play.google.com/store/search?q=contract%20review&c=apps&hl=en_US&gl=US>
- Chrome Web Store legal AI search: <https://chromewebstore.google.com/search/legal%20AI>
- Google Workspace Marketplace legal AI search: <https://workspace.google.com/marketplace/search/legal%20AI>
- Slack Marketplace legal AI search: <https://slack.com/marketplace/search?q=legal%20ai>
- Microsoft AppSource legal AI search attempted: <https://appsource.microsoft.com/en-us/marketplace/apps?search=legal%20AI&page=1>
- Amazon Appstore legal AI search attempted: <https://www.amazon.com/s?k=legal+AI&i=mobile-apps>
